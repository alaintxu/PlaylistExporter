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
import os
import urllib
from fractions import Fraction
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
    
    def __init__(self, file, expath,interface):
        self.plpath = file
        self.expath = expath.replace("file://",'')
        filebasename = os.path.basename(file)
        self.plname,self.extension = os.path.splitext(filebasename)
        self.interface = interface

    def export(self):
        
        if(self.extension=='.pls'):
            self.export_pls()
        elif(self.extension=='.m3u'):
            self.export_m3u()
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
        f = open(self.plpath, 'r')
        lines = f.readlines()
        
        # Playlist title
        self.plname = self.getcontent(lines[1])
        trackcuantity = int(self.getcontent(lines[2]))
        # zfill sais how much numbers has each song (1,01,001,0001...)
        zfill = len(str(trackcuantity))
        
        for i in range(1, trackcuantity+1):
            #Change progress bar
            self.interface.progressbar.set_text(str(i)+" of "+str(trackcuantity))
            self.interface.progressbar.set_fraction(float(i)/float(trackcuantity))
            while gtk.events_pending():
                gtk.main_iteration()
            #Prepare and execute command
            trackpath = self.getcontent(lines[2*i+1])
            trackname = self.getcontent(lines[2*i+2])
            cpcommand = 'cp "'+trackpath+'" "'+self.expath+'/'+str(i).zfill(zfill)+' - '+trackname+'.mp3"'
            print cpcommand
            os.system(cpcommand)
        
        #set progress bar text like finished
        self.interface.progressbar.set_text("Finished!")
            
    def export_m3u(self):
        print ".m3u extension not supported yet"
    def export_defalut(self):
        print self.extension+" extension not supported"
                
    def getcontent(self,line):
        values = line.split("=")
        content = values[1]
        content = content.rstrip('\n')
        content = content.replace("file://",'')
        content = urllib.unquote(content)
        return content
        
class PlaylistInterface():
    # Playlists Path
    plpath = ""
    
    # Supported file formats
    filepattern = (
                   ("PLS","*.pls"),
                   ("XSPF","*.xspf"),
                   ("All files","*.*")
                   )
    
    def __init__(self,arg):
        self.plpath = arg
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Playlist Exporter")
        self.window.set_default_size(512,215)
        
        self.vbox = gtk.VBox(False,5)
        self.window.add(self.vbox)
        
        hseparator0 = gtk.HSeparator()
        self.vbox.add(hseparator0)
        #hseparator0.show()
        
        #Playlist label
        self.pllabel = gtk.Label("Playlist file")
        self.vbox.add(self.pllabel)
        #self.pllabel.show()
        
        #Playlist file chooser button
        self.plfcb = gtk.FileChooserButton("Browse")
        self.plfcb.set_title("Playlist file")
        print self.plfcb.set_uri("file://"+self.plpath)
        self.vbox.add(self.plfcb)
        #self.plfcb.show()
        
        hseparator1 = gtk.HSeparator()
        self.vbox.add(hseparator1)
        #hseparator1.show()
        
        #Export folder label
        self.explabel = gtk.Label("Export folder")
        self.vbox.add(self.explabel)
        #self.explabel.show()
        
        self.expfcb = gtk.FileChooserButton("Browse")
        self.expfcb.set_title("Export folder")
        self.expfcb.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.expfcb.set_current_folder(os.getenv("HOME")+"/PlaylistExporter")
        self.vbox.add(self.expfcb)
        #self.expfcb.show()
        
        hseparator2 = gtk.HSeparator()
        self.vbox.add(hseparator2)
        #hseparator2.show()
        #Button
        self.button = gtk.Button("Export files")
        self.button.connect("clicked",self.export,None)
        self.button.set_size_request(80,30)
        
        #Progress Bar
        self.progressbar = gtk.ProgressBar(adjustment=None)
        self.vbox.add(self.progressbar)
        
        self.vbox.add(self.button)
        #self.button.show()
        
        #self.vbox.show_all()
        self.window.show_all()
    
    def main(self):
        gtk.main()
        
    def export(self,widget,data=None):
        exporter = PlaylistExporter(self.plpath,self.expfcb.get_uri(),self)
        self.progressbar.set_fraction(0.0)
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
        interface = PlaylistInterface(arg)
        interface.main()
    
    
        

    
