#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import gi
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.figure import Figure

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, Gio, GLib

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import time
# from audio_device import AudioStream
import sounddevice as sd


@Gtk.Template.from_file("window.glade")
class AppWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'AppWindow'
    
    filterSwitch: Gtk.Switch = Gtk.Template.Child()    
    lowBandScale : Gtk.Scale = Gtk.Template.Child()
    highBandScale: Gtk.Scale = Gtk.Template.Child()    
    drawingArea_PSDplot: Gtk.Viewport = Gtk.Template.Child()    
    drawingArea_FFTplot: Gtk.Viewport = Gtk.Template.Child()   
    choose_input_device: Gtk.ComboBox = Gtk.Template.Child()
    RMS_levelBar: Gtk.LevelBar = Gtk.Template.Child()
    progressBar: Gtk.ProgressBar = Gtk.Template.Child()  
    channelSwitch:  Gtk.ComboBox = Gtk.Template.Child()
    
    stateRead = True
  
    
    

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.lowBandfiltering_value  = 0
        
        
        
        pass   
     
    
    @Gtk.Template.Callback()  
    def on_AppWindow_destroy(self, widget, *args):
        self.eventStop.set()
        Gtk.main_quit()
        pass
    
    @Gtk.Template.Callback()
    def on_lowBandScale_button_release_event(self, button, user_data,**_kwargs):
        
        self.lowBandfiltering_value = float(self.lowBandScale.get_value())
              
        
        pass  
        
    
    
        
    
        
            
            
        
        
        
        