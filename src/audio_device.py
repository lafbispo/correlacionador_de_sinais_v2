#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import numpy as np
import sounddevice as sd
import sys
import time
import asyncio
from scipy.signal import welch, butter,filtfilt, find_peaks, freqz, freqs


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
    
    

    
                
                
    
    
    
def butter_lowpass_filter(data, cutoff, fs, order, Xf):

    nyq = fs * 0.5
    normal_cutoff = cutoff / fs
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    w, h = freqz(b, a , Xf)
    y = filtfilt(b, a, data)
    return y, w, h

def butter_highpass_filter(data, cutoff, fs, order, Xf):
    
    nyq = fs * 0.5
    normal_cutoff = cutoff / fs
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    w, h = freqz(b, a , Xf)
    y = filtfilt(b, a, data)
    return y, w, h

def butter_bandpass_filter(data, cutoff, fs, order,Xf):
    
    nyq = fs * 0.5
    normal_cutoff = [cutoff[0]/ fs + .001, abs(cutoff[1] / fs - .001)]
    # Get the filter coefficients 
    # print(normal_cutoff[0], normal_cutoff[1])
    b, a = butter(order, normal_cutoff, btype='bandpass', analog=False)
    w, h = freqz(b, a , Xf)
    y = filtfilt(b, a, data)
    return y,w,h
    # pass



    
    
        


    
