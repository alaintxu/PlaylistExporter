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

class PLSExporter():
    def __init__(self,ple):
        self.ple = ple
    
    def export(self):
        f = open(self.ple.plpath, 'r')
        lines = f.readlines()
        
        # Playlist title
        values = lines[1].split("=")
        self.ple.plname = values[1].rstrip('\n')
        self.ple.noftracks = int(lines[2].rstrip('\n'))

        self.ple.prepare_export()
        
        for i in range(1, self.ple.noftracks+1):
            #Prepare and execute command
            trackuri,trackname = self.get_content(lines[2*i+1],lines[2*i+2])
            
            self.ple.copy_command(i, trackuri, trackname)
            
        #set progress bar text like finished
        self.ple.interface.progressbar.set_text("Finished!")
                
    def get_content(self,line1,line2):
        values = line1.split("=")
        uri = values[1].content.replace("file://",'')
        uri = uri.rstrip('\n')
        values = line2.split("=")
        title = values[1].rstrip('\n')
        return uri,title

class M3UExporter():
    def __init__(self,ple):
        self.ple = ple
    
    def export(self):
        f = open(self.ple.plpath, 'r')
        lines = f.readlines()
        self.ple.noftracks = (len(lines)-1)/2
        
        self.ple.prepare_export()
        
        for i in range(1, self.ple.noftracks+1):
            #Prepare and execute command
            trackuri,trackname = self.get_content(lines[2*i-1],lines[2*i])
            
            self.ple.copy_command(i, trackuri, trackname)
            
        #set progress bar text like finished
        self.ple.interface.progressbar.set_text("Finished!")
                
    def get_content(self,line1,line2):
        title = line1.replace("#EXTINF:,",'')
        title = title.rstrip('\n')
        uri = line2.rstrip('\n')
        return uri,title

class XSPFExporter():
    def __init__(self,ple):
        self.ple = ple
    
    def export(self):
        f = open(self.ple.plpath, 'r')
        lines = f.readlines()
        
        # Playlist title
        self.ple.plname = self.get_content(lines[1])
        self.ple.noftracks = int(self.get_content(lines[2]))

        self.ple.prepare_export()
        
        for i in range(1, self.ple.noftracks+1):
            #Prepare and execute command
            trackuri = self.get_content(lines[2*i+1])
            trackname = self.get_content(lines[2*i+2])
            
            self.ple.copy_command(i, trackuri, trackname)
            
        #set progress bar text like finished
        self.ple.interface.progressbar.set_text("Finished!")
                
    def get_content(self,line):
        values = line.split("=")
        content = values[1]
        content = content.rstrip('\n')
        content = content.replace("file://",'')
        content = urllib.unquote(content)
        return content

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
        self.expath = expath
        filebasename = os.path.basename(file)
        self.plname,self.extension = os.path.splitext(filebasename)
        self.interface = interface

    def export(self):
        
        if(self.extension=='.pls'):
            exporter = PLSExporter(self)
        elif(self.extension=='.m3u'):
            exporter = M3UExporter(self)
        elif(self.extension=='.xspf'):
            exporter = XSPFExporter(self)
        else:
            return
        exporter.export()

    def prepare_export(self):
        # zfill sais how much numbers has each song (1,01,001,0001...)
        self.zfill = len(str(self.noftracks))
        
        #Make subdirectory if required
        if(self.interface.checkbox.get_active()):
            self.expath = self.expath+"/"+self.plname
            os.system("mkdir "+self.expath)
    
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
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Playlist Exporter")
        self.window.set_default_size(512,215)
        
        self.vbox = gtk.VBox(False,5)
        
        #Add padding
        alignment = gtk.Alignment(xalign=0.0, yalign=0.0, xscale=1.0, yscale=1.0)
        alignment.add(self.vbox)
        alignment.set_padding(5,5,15,15)
        self.window.add(alignment)
        
        hseparator0 = gtk.HSeparator()
        self.vbox.add(hseparator0)
        
        #Playlist label
        self.pllabel = gtk.Label("Playlist file")
        self.vbox.add(self.pllabel)
        
        #Playlist file chooser button
        self.plfcb = gtk.FileChooserButton("Browse")
        self.plfcb.set_title("Playlist file")
        self.plfcb.add_filter(filter)
        if(arg!=None):
            #Playlist as an argument
            self.plpath = arg
            self.plfcb.set_uri("file://"+self.plpath)
        else:
            #set HOME as default folder to find playlists
            self.plfcb.set_current_folder(os.getenv("HOME"))
        self.vbox.add(self.plfcb)
        
        #Visual separator
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
        self.button.set_size_request(150,30)
        
        #Progress Bar
        self.progressbar = gtk.ProgressBar(adjustment=None)
        self.vbox.add(self.progressbar)
        
        alignment = gtk.Alignment(xalign=0.5, yalign=0.0, xscale=0.0, yscale=0.0)
        alignment.add(self.button)
        self.vbox.add(alignment)
        
        self.window.show_all()
    
    def main(self):
        gtk.main()
        
    def export(self,widget,data=None):
        exporter = PlaylistExporter(self.plfcb.get_filename(),self.expfcb.get_filename(),self)
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
    if(args.__len__()):
        interface = PlaylistInterface(args[0])
    else:
        interface = PlaylistInterface(None)
    interface.main()
    
    
        

    
