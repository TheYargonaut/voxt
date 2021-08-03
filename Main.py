# TODO: choose source
#       play midi

from SpectrumWidget import SpectrumWidget, CircularAudioBuffer

import tkinter as tk
from tkinter import ttk
import pdb

import sounddevice as sd
fs = 44100 # Sample rate
seconds = 0.03 # Duration of recording
buffsec = 0.10 # Duration to hold in buffer
blocksize = 2048

class MainWindow( tk.Tk ):
    def __init__( self ):
        tk.Tk.__init__( self )
        self.cab = CircularAudioBuffer( int( buffsec * fs ) )
        self.sw = SpectrumWidget( self, int( buffsec * fs ), fs )
        self.sw.grid( row=0, column=0, sticky=tk.NSEW )

        self.stream = sd.InputStream( samplerate=fs, channels=1, blocksize=blocksize )        
        self.stream.start()
        self.after( 1, self.update )

    def update( self ):
        myrecording = self.stream.read( self.stream.read_available )[ 0 ].reshape( -1 )
        if myrecording.size > 0:
            self.cab.insert( myrecording )
            self.sw.draw( self.cab.buf )
        self.after( 1, self.update )

mw = MainWindow()
mw.mainloop()
