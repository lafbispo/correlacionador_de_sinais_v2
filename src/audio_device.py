#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import numpy as np
import sounddevice as sd
import sys
import time
import asyncio



def get_devices():
    
    devices_INPUT = sd.query_devices(None, 'input')    
    devices_OUTPUT = sd.query_devices(None, 'output')  
    
    return devices_INPUT, devices_OUTPUT   


@dataclass(init=False)
class AudioDevice:
    name: str = None
    hostapi: int = None
    max_input_channels: int = None
    max_output_channels: int = None
    default_low_input_latency: float = None
    default_low_output_latency: float = None
    default_high_input_latency: float = None
    default_high_output_latency: float = None
    default_samplerate: float = None
    
    
    def load_selected_device(self, dict_from_audio_device_info):
        for i in dict_from_audio_device_info:
            key_, value_ = i
            self.__setattr__(key_, value_)

        return 0 
    


@dataclass(init=False)
class AudioStream(AudioDevice):

    channels: int =  field(default=1, 
    metadata= {'help':'input channels to plot (default: the first)' })

    device: str = field(
        default = None, 
        metadata={'help': 'input device (numeric ID or substring)'})

    window: float = field(default= 200,
     metadata={'help': 'visible time slot (default: %(default)s ms)' })

    interval: float = field(default = 30, metadata={
        'help': 'minimum time between plot updates (default: %(default)s ms)'})
    
    blocksize: int = field(default=None, metadata={
        'help':'minimum time between plot updates (default: %(default)s ms)'})    
    
    downsample: int = field(default=10, metadata={
        'help':'display every Nth sample (default: %(default)s)'})  
    
    block_duration: float  = field(default=50, metadata= {
        'help':'block size (default %(default)s milliseconds)'}) 
    
    columns: int = field(default=80, metadata={
        'help':'width of spectrogram'     
    })
    
    gain: float = field(default= 10, metadata={
        'help':'initial gain factor (default %(default)s)'})
    
    
   
                
                
    async def inputstream_generator(self, channels=1, **kwargs):
        """Generator that yields blocks of input data as NumPy arrays."""
        q_in = asyncio.Queue()
        
        loop = asyncio.get_event_loop()
        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))
            
        stream = sd.InputStream(callback=callback, channels=channels, **kwargs)
        with stream:
            while True:
                indata, status = await q_in.get()
                yield indata, status
                
        
    async def record_buffer(self, buffer, **kwargs):
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        idx = 0
        
        def callback(indata, frame_count, time_info, status):
            nonlocal idx
            if status:
                print(status)
            remainder = len(buffer) - idx
            if remainder == 0:
                loop.call_soon_threadsafe(event.set)
                raise sd.CallbackStop
            indata = indata[:remainder]
            buffer[idx:idx + len(indata)] = indata
            idx += len(indata)
            
        stream = sd.InputStream(callback=callback, dtype=buffer.dtype,
                                channels=buffer.shape[1], **kwargs)
        with stream:
            await event.wait()
            
            
    
    async def buffer_analysis_and_plot(self, buffersize, channels = 1,
                                       dtype=np.int16,**kwargs):
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        
        buffer = np.empty((buffersize, channels), dtype=dtype)
        await self.record_buffer(buffer)
        print(len(buffer))
        
        
    
    def run_buffer(self, buffersize, **kwargs):
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        loop.run_until_complete(self.buffer_analysis_and_plot(buffersize))
                       
    



    
    
        


    
