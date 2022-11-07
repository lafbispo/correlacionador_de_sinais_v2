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
import matplotlib.pyplot as plt
#plt.style.use('seaborn')

import numpy as np
import scipy.fft as fft
from scipy.signal import welch, butter,filtfilt, find_peaks, freqz, freqs


import matplotlib as mpl
mpl.rcParams['font.family'] = ['serif']
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['image.cmap']='jet'


from window import AppWindow
import time
import sounddevice as sd
from audio_device import AudioStream, get_devices, butter_lowpass_filter,butter_highpass_filter, butter_bandpass_filter
import asyncio
import threading

class Analisador_de_sinaisApplication(Gtk.Application):
    
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="linux.AppWindow",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, 
                         **kwargs)     
        
        self.loop = asyncio.get_event_loop()
            
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
        
        
        
           
                   
            
        
        
        
        
        
          
        
        
        pass
        

    def do_activate(self):
        
        # self.do_startup()
        #INICIO ----------------------------        
        win = self.props.active_window
        if not win:              
            win = AppWindow(application=self, title = 'Analisador de Sinais')         
        # -------------------------------------------    
        
        #cria psd plot area
        figPSD, axisPSD = self.embedded_plot(win.drawingArea_PSDplot)  
        self.aplica_psd_plot_settings(figPSD, axisPSD) 
        
        #mostra nome do dispositivo de audio utlizado na interface gráfica
        name = self.audiostream.name
        liststore = Gtk.ListStore(str)
        liststore.append([name])
        win.choose_input_device.set_model(liststore)
        win.choose_input_device.set_active(0)
        
        win.channelSwitch.set_model(self.liststorechannels)
        win.channelSwitch.set_active(0)
        
        # create an instance of an event
        win.eventStop = threading.Event()
        
        lowband_widget = win.lowBandScale
        highband_widget = win.highBandScale
        p1 = GLib.idle_add(self.callback_updatePlot, figPSD, axisPSD,        
                           win.RMS_levelBar, lowband_widget, highband_widget,
                           int(30*1024), win.eventStop)
        
        # self.callback_updatePlot( figPSD, axisPSD, 
        #                    int(40*1024))
        #self.audiostream.run_buffer(int(40*1024))
        
        
        
        
        
        
                   
        #FIM -------------------------------
        win.present()         
        win.show_all()   
        pass
    
    
    def embedded_plot(self, widget,  figsize = (5.5,3.0), dpi = 81, 
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
        #axis.grid()
        axis.grid(True,which="both", axis="both",ls="-")
        pos = axis.get_position()
        axis.set_position([pos.x0, pos.y0, pos.width * 0.9, pos.height * .9])
        # axis.legend(loc ='center right', fontsize = 16, bbox_to_anchor=(1.25, 0.5))    
        #axis.set_animated(True)
        #axis.axis((0, 22000, 0, 10))
        axis.set_xlim(10,22500)
        #axis.set_xlim(0,4)
        #axis.set_ylim(0,1)
        axis.set_ylim(-150, 1) #db
        #axis.axis((0, 1024, -2, 2))
        axis.autoscale_view(False, False)
        fig.subplots_adjust( bottom=0.25, right=.82) 
        
        
    def callback_updatePlot(self, fig, axis, RMS_levelBar, lowband_widget,
                            highband_widget,
                            buffersize, eventStop):
        
        blocksizeM = 1024
        fs = self.audiostream.default_samplerate
        
        ref = 32767
       
        
        Xf = fft.fftfreq(blocksizeM, 1./fs)[:blocksizeM//2]
        
        line1, = axis.semilogx(Xf[:], np.zeros(blocksizeM//2)[:], 
                               animated = True, label = 'ch1' )
        
        line2, = axis.semilogx(Xf[:], np.zeros(blocksizeM//2)[:], 
                               animated = True, label = 'filtro' )
       
        axis.legend(loc ='center right', fontsize = 16, bbox_to_anchor=(1.25, 0.5))    
        fig.canvas.draw()   
        bg = fig.canvas.copy_from_bbox(fig.bbox)
        fig.canvas.blit(fig.bbox)
        
        buffer = np.ones(10)
        flag =  np.any(buffer)
        
        while flag:
            

            buffer = self.audiostream.run_buffer(buffersize)    
            
            flag =  np.any(buffer)
            
            buffer = buffer.reshape([1, len(buffer)])/ref     
            
            lowbandvalue = lowband_widget.get_value()
            cut_off1 = abs(fs*(1 - (lowbandvalue)/100))   
            #cut_off1 = fs/2*(lowbandvalue/100)
            
                                
            highbandvalue = highband_widget.get_value()
            cut_off2 = fs*(highbandvalue/100)
           # cut_off2 = abs(fs/2*(1 - (highbandvalue)/100))           
            # print(lowbandvalue, cut_off1)
            if lowbandvalue <1 and highbandvalue <1:
                
                line2.set_xdata(Xf)
                line2.set_ydata( np.zeros(blocksizeM//2)[:])
                
                pass
            elif lowbandvalue >1 and highbandvalue <1:
                """filtro passa baixa"""
                y, w, h = butter_lowpass_filter(data = buffer, 
                                      cutoff=cut_off1, 
                                      fs = fs, order = 2, Xf=Xf)
                buffer = y
                line2.set_xdata(w)
                line2.set_ydata(20 * np.log10(abs(h+1e-6)))
                pass
                
            elif highbandvalue >1 and  lowbandvalue<1:
                """filtro passa alta"""
                y, w, h = butter_highpass_filter(data = buffer, 
                                      cutoff=cut_off2, 
                                      fs = fs, order = 2, Xf=Xf)
                buffer = y
                line2.set_xdata(w)
                line2.set_ydata(20 * np.log10(abs(h+1e-6)))
                pass
            else:
                """filtro passa banda"""
                cut_off1 = lowbandvalue/100*fs/2
                cut_off2 = ((highbandvalue/100)/2 + .5)*fs
                cutoff = [cut_off1, cut_off2]
                # print(cutoff)
                
                order = 2
                y, w, h = butter_bandpass_filter(buffer, cutoff, fs, order,Xf)                
                
                buffer = y
                line2.set_xdata(w)
                line2.set_ydata(20 * np.log10(abs(h+1e-6)))
                pass
            
            
            
            freq, Pxx_den = welch(buffer, fs=fs, window='blackman', nperseg=blocksizeM, 
                        noverlap=None, nfft=None, detrend='constant', 
                        return_onesided=True, scaling='density', axis=- 1, 
                        average='mean')
            
            Pxx_dendb = 10*np.log10(Pxx_den)
            
            rms_value = np.sqrt(sum(buffer[0,:]**2)/len(buffer[0,:]))                                        
            RMS_levelBar.set_value(rms_value)       
        
        
            
            
            fig.canvas.restore_region(bg) 
            line1.set_ydata(Pxx_dendb[0,1:])
            line1.set_xdata(freq[1:])  
            fig.canvas.draw()
            axis.draw_artist(line1)
            axis.draw_artist(line2)
            fig.canvas.flush_events()
            
            
            
            if eventStop.is_set():
                return False
            
        return False
    
    
    
    
 
                
                
    
    
   
    
     
        
        
        
    
    
    


   

def main(version):
    app = Analisador_de_sinaisApplication()
    return app.run(sys.argv)



if __name__ == '__main__':
    main(0)
    
    
    
   