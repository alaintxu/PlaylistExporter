#!/usr/bin/python
'''
Created on Dec 20, 2011

@author: alain
'''

import sys
import getopt
import os
from lxml import etree
import gtk
import urllib
import xml.etree.ElementTree

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
        self.plpath = file.replace("file://",'')
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
        self.noftracks = int(self.getcontent(lines[2]))
        
        # zfill sais how much numbers has each song (1,01,001,0001...)
        self.zfill = len(str(self.noftracks))
        
        if(self.interface.checkbox.get_active()):
            self.expath = self.expath+"/"+self.plname
            os.system("mkdir "+self.expath)
        
        for i in range(1, self.noftracks+1):
            #Prepare and execute command
            trackuri = self.getcontent(lines[2*i+1])
            trackname = self.getcontent(lines[2*i+2])
            
            self.copy_command(i, trackuri, trackname)
            
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
    
    def copy_command(self,track,uri,name):
            #Change progress bar
            self.interface.progressbar.set_text(str(track)+" of "+str(self.noftracks))
            self.interface.progressbar.set_fraction(float(track)/float(self.noftracks))
            while gtk.events_pending():
                gtk.main_iteration()
            cpcommand = 'cp "'+uri+'" "'+self.expath+'/'+str(track).zfill(self.zfill)+' - '+name+'.mp3"'
            print cpcommand
            os.system(cpcommand)
        
        
class PlaylistInterface():
    # Playlists Path
    plpath = ""
    
    
    def __init__(self,arg):
        filter = gtk.FileFilter()
        filter.set_name("Playlists")
        filter.add_pattern("*.m3u")
        filter.add_pattern("*.pls")
        filter.add_pattern("*.xspf")
        
        self.plpath = arg
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Playlist Exporter")
        self.window.set_default_size(512,215)
        
        self.vbox = gtk.VBox(False,5)
        self.window.add(self.vbox)
        
        hseparator0 = gtk.HSeparator()
        self.vbox.add(hseparator0)
        
        #Playlist label
        self.pllabel = gtk.Label("Playlist file")
        self.vbox.add(self.pllabel)
        
        #Playlist file chooser button
        self.plfcb = gtk.FileChooserButton("Browse")
        self.plfcb.set_title("Playlist file")
        self.plfcb.add_filter(filter)
        print self.plfcb.set_uri("file://"+self.plpath)
        self.vbox.add(self.plfcb)
        
        hseparator1 = gtk.HSeparator()
        self.vbox.add(hseparator1)
        
        #Export folder label
        self.explabel = gtk.Label("Export folder")
        self.vbox.add(self.explabel)
        
        #Export folder file chooser button
        self.expfcb = gtk.FileChooserButton("Browse")
        self.expfcb.set_title("Export folder")
        self.expfcb.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.expfcb.set_current_folder(os.getenv("HOME")+"/PlaylistExporter")
        self.vbox.add(self.expfcb)
        
        self.checkbox = gtk.CheckButton("Create subfolder with playlist name", use_underline=True)
        self.vbox.add(self.checkbox)
        
        hseparator2 = gtk.HSeparator()
        self.vbox.add(hseparator2)

        #Button
        self.button = gtk.Button("Export files")
        self.button.connect("clicked",self.export,None)
        self.button.set_size_request(80,30)
        
        #Progress Bar
        self.progressbar = gtk.ProgressBar(adjustment=None)
        self.vbox.add(self.progressbar)
        
        self.vbox.add(self.button)
        
        self.window.show_all()
    
    def main(self):
        gtk.main()
        
    def export(self,widget,data=None):
        exporter = PlaylistExporter(self.plfcb.get_uri(),self.expfcb.get_uri(),self)
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
    
    
        

    
