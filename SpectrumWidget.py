from itertools import chain, product
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk
from tkinter import ttk

def charRange( start, end ):
    'iterate over characters inclusive'
    for c in range( ord( start ), ord( end ) + 1 ):
        yield chr( c )


wholePitchLabels = [ c + str( octave ) for octave, c in product( range( 9 ), chain( charRange( 'C', 'G' ), charRange( 'A', 'B' ) ) ) ]
pitchLabels = []
# add half-steps
for l in wholePitchLabels:
    pitchLabels.append( l )
    if l[ 0 ] not in 'BE':
        pitchLabels.append( '' )

class CircularAudioBuffer( object ):
    def __init__( self, length ):
        self.len = length
        self.buf = np.zeros( self.len )
        self.place = 0
    
    def insert( self, sample ):
        if len( sample ) >= self.len:
            self.buf = sample[ -self.len: ]
            self.place = 0
            return

        totlen = len( sample ) + self.place
        if totlen <= self.len:
            self.buf[ self.place:totlen ] = sample
            self.place = totlen
            return
        
        prelen = self.len - self.place
        postlen = len( sample ) - prelen
        
        self.buf[ self.place: ] = sample [ :prelen ]
        self.buf[ :postlen ] = sample[ -postlen: ]
        self.place = postlen

windows = {
    'human': ( 20, 20000 ),
    'piano': ( 27.5, 4187 ),
    'extendedPiano': ( 16.35, 7903 ), # C0 - B8
    'vocal': ( 125, 8000 ),
    'grandStaff' : ( 87.3, 784 ), # F2 - G5
}

class SpectrumWidget( ttk.Frame ):
    def __init__( self, parent, slen, srate, window='grandStaff', wing=5000, *args, **kwargs ):
        ttk.Frame.__init__( self, parent, *args, **kwargs )
        self.slen = slen
        self.srate = srate
        self.ylim = 0, slen / ( 2 * 100 )
        self.xlim = windows[ window ]
        self.a4 = 440
        self.x = np.fft.rfftfreq( self.slen + 2 * wing, 1 / srate )
        self.wing = wing
        self.embedder = np.zeros( self.slen + 2 * wing )
        self.build()
    
    def build( self ):
        plt.ion()
        self.fig = plt.Figure( figsize=( 20, 5 ) )
        self.chart = FigureCanvasTkAgg( self.fig, self )
        self.chart.get_tk_widget().grid( row=0, column=0, sticky=tk.NSEW )
        self.ax = self.fig.add_subplot( 111 )

        # spectrum line
        self.line, = self.ax.semilogx( self.x, np.zeros_like( self.x ), 'g-o' )

        # pitch lines, C0 - B8 (extended piano)
        pitchFreq = self.a4 * np.power( 2, np.arange( -57, 51 ) / 12 )
        self.ax.vlines( pitchFreq, *self.ylim )
        self.ax.tick_params( 'x', which='minor', bottom=False, top=False, labelbottom=False )
        self.ax.tick_params( 'y', which='both', bottom=False, top=False, labelbottom=False )
        self.ax.set_xticks( list( pitchFreq ) )
        self.ax.set_xticklabels( pitchLabels )
        
        self.ax.set_ylim( *self.ylim )
        self.ax.set_xlim( *self.xlim )
    
    def draw( self, sample ):
        'take raw sample in time, do fft locally'
        self.embedder[ self.wing : -self.wing ] = sample
        spectrum = np.abs( np.fft.rfft( self.embedder ) )
        self.line.set_ydata( spectrum )
        self.chart.draw()
