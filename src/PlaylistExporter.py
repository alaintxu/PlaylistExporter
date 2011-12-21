#!/usr/bin/python
'''
Created on Dec 20, 2011

@author: alain
'''

import sys
import getopt
import os
from lxml import etree
import pygtk
import gtk
#import xml.etree.ElementTree

class PlaylistExporter():
    # path to the playlist file
    plpath = ""
    
    # Name of the playlist file
    plname = ""
    
    # Extension of the playlist file
    extension = ""
    
    # Export path
    expath = "~/PlaylistExporter"
    
    def __init__(self, file, expath="~"):
        self.plpath = file
        self.expath = expath
        filebasename = os.path.basename(file)
        self.plname,self.extension = os.path.splitext(filebasename)

    def export(self):
        if(self.extension=='.pls'):
            self.export_pls()
        elif(self.extension=='.xspf'):
            self.export_xspf()
        else:
            self.export_defalut()
        
        
    def export_xspf(self):
        print ".xspf extension is being developed"
        plet = etree.parse(self.plpath, parser=None, base_url=None)
        trackList = plet.findall('track')
        print trackList
                
    def export_pls(self):
        print "pls playlists not implemented yet"
        f = open(self.plpath, 'r')
        lines = f.readlines()
        
        # Playlist title
        self.plname = self.getcontent(lines[1])
        trackcuantity = self.getcontent(lines[2])
        print trackcuantity
        for i in range(1, int(trackcuantity)+1):
            trackpath = self.getcontent(lines[2*i+1])
            trackname = self.getcontent(lines[2*i+2])
            cpcommand = "cp "+trackpath+" "+self.expath+"/"+str(i)+"_"+trackname+".mp3"
            print cpcommand
            
    def export_defalut(self):
        print self.extension+" extension not supported"
                
    def getcontent(self,line):
        values = line.split("=")
        content = values[1]
        content = content.rstrip('\n')
        content = content.replace("file://",'')
        return content
        
class PlaylistInterface():
    # Playlists Path
    plpath = ""
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Playlist Exporter")
        
        self.vbox = gtk.VBox(False,5)
        self.window.add(self.vbox)
        
        #Playlist label
        self.pllabel = gtk.Label("Playlist file")
        self.vbox.add(self.pllabel)
        self.pllabel.show()
        
        #Playlist file selection
        self.plfs = gtk.FileSelection(title="Playlist file")
        self.vbox.add(self.plfs)
        self.plfs.show()
        
        #Export folder label
        self.explabel = gtk.Label("Export folder")
        self.vbox.add(self.explabel)
        self.explabel.show()
        
        #Button
        self.button = gtk.Button("Export files")
        self.button.connect("clicked",self.export,None)
        
        self.vbox.add(self.button)
        self.button.show()
        
        self.vbox.show()
        self.window.show()
    
    def main(self):
        gtk.main()
        
    def export(self,widget,data=None):
        exporter = PlaylistExporter(self.plpath)
        exporter.export()
        
        
if __name__ == '__main__':
    #doc1 = parse(open('document.xml'))
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
    # process arguments
    for arg in args:
        interface = PlaylistInterface()
        interface.main()
    
    
        

    
