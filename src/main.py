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


import matplotlib as mpl
mpl.rcParams['font.family'] = ['serif']
mpl.rcParams['font.serif'] = ['Times New Roman']
mpl.rcParams['image.cmap']='jet'


from window import AppWindow
import time
import sounddevice as sd
from audio_device import AudioStream, get_devices
import asyncio

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
        
        self.audiostream.run_buffer(int(40*1024))
        
        
        
        
        
        
                   
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
        axis.legend(loc ='center right', fontsize = 16, bbox_to_anchor=(1.25, 0.5))    
        #axis.set_animated(True)
        #axis.axis((0, 22000, 0, 10))
        axis.set_xlim(10,22500)
        #axis.set_xlim(0,4)
        #axis.set_ylim(0,1)
        axis.set_ylim(-150, 1) #db
        #axis.axis((0, 1024, -2, 2))
        axis.autoscale_view(False, False)
        fig.subplots_adjust( bottom=0.25, right=.82) 
        
    
    
    
 
                
                
    
    
   
    
     
        
        
        
    
    
    


   

def main(version):
    app = Analisador_de_sinaisApplication()
    return app.run(sys.argv)



if __name__ == '__main__':
    main(0)
    
    
    
   