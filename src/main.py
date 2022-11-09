#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import gi
from matplotlib.colors import Colormap

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio, GLib

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)

from matplotlib.backends.backend_gtk3 import (
    NavigationToolbar2GTK3 as NavigationToolbar)

from matplotlib.figure import Figure

import numpy as np
from scipy.signal import welch, butter,filtfilt, find_peaks, freqz, freqs


import matplotlib as mpl
mpl.rcParams['font.family'] = ['serif']
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['image.cmap']='jet'


from window import AppWindow
import sounddevice as sd
from audio_device import AudioStream, get_devices, butter_lowpass_filter,butter_highpass_filter, butter_bandpass_filter
import queue
from collections import deque
import threading
import multiprocessing 
import time

class Analisador_de_sinaisApplication(Gtk.Application):
    
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="linux.AppWindow",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, 
                         **kwargs)     
        
        global freq, Pxx_dendb, rms_value
       
        pass       
    
        
    def do_startup(self):
        
        Gtk.Application.do_startup(self)          
        
        # Carrega os devices de input e output
        inputDevice, outputDevice = get_devices()
        names = inputDevice['name']
        if isinstance(names, list):
            pass
        else:
            self.audiostream = AudioStream()
            self.audiostream.load_selected_device(inputDevice.items()) 
            
        liststorechannels = Gtk.ListStore(str)
        channels = self.audiostream.channels
        if channels == 1:
            liststorechannels.append([str(channels)])                
            pass
        else:
            list_channels = []
            for i in range(channels):
                list_channels.append([i +1])
            list_channels.append('all')
            liststorechannels.append(list_channels)   
        
        self.liststorechannels = liststorechannels

        self.buffersize = int(30*1024)
        
        pass
        

    def do_activate(self):
        
        # self.do_startup()
        #INICIO ----------------------------        
        win = self.props.active_window
        if not win:              
            win = AppWindow(application=self, title = 'Analisador de Sinais')         
        # -------------------------------------------    
        
                   
        #FIM -------------------------------
        win.present()         
        win.show_all()   
        pass


    def plotStreamProcess(self, win):

        qRms = multiprocessing.Queue()

        #cria psd plot area
        figPSD, axisPSD = self.embedded_plot(win.drawingArea_PSDplot)  
        self.aplica_psd_plot_settings(figPSD, axisPSD) 


        win.event = threading.Event()
        win.thrd1 = threading.Thread(target=self.up_stream, args=(win.event,))
        win.thrd1.start()

        for i in range(5):
            time.sleep(1)
            axisPSD.plot(freq, Pxx_dendb)
        




        pass

    def embedded_plot(self, widget, figsize = (5.5, 3.0), dpi = 81, 
                       toolbarBool = True):
        
        figure = Figure(figsize, dpi)        
        axis = figure.add_subplot()        
        canvas = FigureCanvas(figure)        
        canvas.set_size_request(figsize[0]*150, figsize[1]*100)         
        vbox = Gtk.VBox()        
        vbox.pack_start(canvas, True, True, 0)  
        
        if toolbarBool is True:            
            # # Create toolbar
            toolbar = NavigationToolbar(canvas, widget)
            vbox.pack_start(toolbar, False, False, 0)            
            widget.add(vbox)   

        return figure, axis 

    def aplica_psd_plot_settings(self, fig, axis):        
       
        fig.suptitle('PSD Stream Audio', fontsize = 20)
        axis.set_xlabel(xlabel= r'frequência $[Hz]$',fontsize = 16)
        axis.set_ylabel(ylabel = r"$dB$", fontsize = 16)
        axis.tick_params(axis='both', which='major', labelsize=16)
        axis.tick_params(axis='both', which='minor', labelsize=14)
        axis.grid(True,which="both", axis="both",ls="-")
        pos = axis.get_position()
        axis.set_position([pos.x0, pos.y0, pos.width * 0.9, pos.height * .9])
        axis.set_xlim(10,22500)
        axis.set_ylim(-150, 1) #db
        axis.autoscale_view(False, False)
        fig.subplots_adjust( bottom=0.25, right=.82) 

    
    def psd_processing(self, event, fig, axis):     

        blocksizeM = 1024
        fs = self.audiostream.default_samplerate     
        ref = 32767     

        buffer = self.audiostream.run_buffer(self.buffersize)

        if event.is_set() or np.any(buffer) == False:
            return False

        buffer = buffer.reshape([1, len(buffer)])/ref 

        freq, Pxx_den = welch(buffer, fs=fs, window='blackman', nperseg=blocksizeM, 
                        noverlap=None, nfft=None, detrend='constant', 
                        return_onesided=True, scaling='density', axis=- 1, 
                        average='mean') 
        
        Pxx_dendb = 10*np.log10(Pxx_den)            
        rms_value = np.sqrt(sum(buffer[0,:]**2)/len(buffer[0,:]))  
        freq = freq

        return False

    
    def up_stream(self, event):

        channels = self.audiostream.channels
        device = self.audiostream.device
        samplerate = self.audiostream.default_samplerate

        blocksize = int(30*1024)
        ref = 32767  

        blocksizeM = int(1024)                
        q = queue.Queue()
        qcalc = deque()

        global freq, Pxx_dendb, rms_value

        def audio_callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            # Fancy indexing with mapping creates a (necessary!) copy:
            q.put(indata[:, channels - 1])

        stream = sd.InputStream(
                device=device, channels=channels,
                samplerate=samplerate, callback=audio_callback, 
                blocksize=0, dtype=np.int16)

        with stream:
            while True:
                if event.is_set():
                    return False
                
                data = q.get()
                qcalc.extend(data)

                if len(qcalc)<blocksize:

                    pass

                else:

                    buffer = [qcalc.popleft() for _i in range(blocksize)]
                    buffer = np.transpose(buffer)/ref

                    freq, Pxx_den = welch(buffer, fs=samplerate, 
                        window='blackman', nperseg=blocksizeM, 
                        noverlap=None, nfft=None, detrend='constant', 
                        return_onesided=True, scaling='density', axis=- 1, 
                        average='mean') 
        
                    Pxx_dendb = 10*np.log10(Pxx_den)            
                    rms_value = np.sqrt(sum(buffer[:]**2)/len(buffer[:]))  
                    








        



              
           



            

            



    

    


    
    
 
def main(version):
    app = Analisador_de_sinaisApplication()
    return app.run(sys.argv)

#%% Main Run
if __name__ == '__main__':
    main(0)
    # Analisador_de_sinaisApplication()
    # Gtk.main()
    
    
    
   