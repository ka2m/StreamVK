#!/usr/bin/env python
# -*- coding: utf-8 -*-
#player.py - start player window. main window
from wxPython.wx import * # graphic
import wx 				  # libs
import os #for downloadin
import sys
### my files
import check_id #checking login and password
import getsongs #getting playlist
import check_playlist #forming playlist
import cleaner #remove stuff
###
import thread #for downlaoding 
import pygst 
pygst.require("0.10") # LET THERE BE MUSIC!
import gobject 
gobject.threads_init() 
import gst
class MyAuthDialog(wxDialog):
	def __init__(self,parent,id,title):
		wx.Dialog.__init__(self,parent,id,title)
		self.login = ""
		self.password = ""
		self.ecode = 0
		self.InitDialogUI()
		self.BindDialogAction()
	def InitDialogUI(self):
		#font definition
		self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		self.font.SetPointSize(12)
		dpanel = wx.Panel(self)
		# active text fields
		dhbox1 = wx.BoxSizer(wx.HORIZONTAL)
		
		ltexttext = wxStaticText(dpanel, label='Login: ')
		dhbox1.Add(ltexttext,flag=wx.LEFT,border=3)

		self.LTextField = wxTextCtrl(dpanel, -1,size=(350,30))
		self.LTextField.SetFont(self.font)
		dhbox1.Add(self.LTextField,flag=wx.LEFT|wx.EXPAND,border=3)

		dhbox2 = wx.BoxSizer(wx.HORIZONTAL)
	 	ptexttext = wxStaticText(dpanel, label='Password: ')
		dhbox2.Add(ptexttext,flag=wx.LEFT,border=3)

		self.PTextField = wxTextCtrl(dpanel, -1,size=(300,30), style = wxTE_PASSWORD)
		self.PTextField.SetFont(self.font)
		dhbox2.Add(self.PTextField,flag=wx.LEFT|wx.EXPAND,border=3)
	
		#buttons
		self.OKbutton = wx.Button(dpanel,label='Auth')
		self.CNCbutton = wx.Button(dpanel,label='Cancel')
		
		#sizers
		dvbox = wx.BoxSizer(wx.VERTICAL)
		dvbox.Add(dhbox1,flag=wx.TOP,border=5)
		dvbox.Add(dhbox2,flag=wx.TOP,border=5)
		dvbox.Add(self.OKbutton,flag=wx.TOP|wx.CENTER,border=5)
		dvbox.Add(self.CNCbutton,flag=wx.TOP|wx.CENTER,border=5)
		dpanel.SetSizer(dvbox)
	
	def BindDialogAction(self):
		self.OKbutton.Bind(wx.EVT_BUTTON,self.TryAuth)
		self.CNCbutton.Bind(wx.EVT_BUTTON,self.Cancel)
	
	def TryAuth(self,event):
		self.login = self.LTextField.GetValue()
		self.password = self.PTextField.GetValue()
		if len(self.login) !=0 or len(self.password) != 0:
			self.Close()
		else: wx.MessageBox('Login or password are empty','WARNING!',wx.OK| wx.ICON_ERROR)
	
	def ReturnValue(self):
		return self.ecode,self.login,self.password
	
	def Cancel(self,event):
		self.ecode = 1
		self.Close()

class MyFrame(wxFrame):
	def __init__(self,parent,id, title,l,p): # l - login, p -password
		###variable decaration###
		self.size = (360,405)
		self.l = l
		self.p = p
		self.token =""
		self.id = ""
		self.plpath = ""
		self.ecode = 0
		self.pos = 0
		self.value = 0.5
		self.playlist = [('0','0','0','0')]
		self.dirname = ""
		self.eoft = False
		self.Muted = False
		style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX
		###end of var dec###
		
		#starting frame and drawing it
		wxFrame.__init__(self,parent,id,title,(wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X),wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)),wxSize(self.size[0],self.size[1]),style=style)
		self.InitUI()
		self.BindAction()
		self.epls.Enable(False) #will be ready in 0.5
		
		###PyGST (Gstreamer) init###
		self.player = gst.element_factory_make("playbin", "player")
		fakesink = gst.element_factory_make("fakesink", "fakesink")
		self.player.set_property("video-sink", fakesink)
   		bus = self.player.get_bus()
   		bus.add_signal_watch()
   		bus.connect("message", self.on_message)
		self.time_format = gst.Format(gst.FORMAT_TIME)
		gobject.timeout_add(1000,self.update_time)
   		####

   		#icon
   		favicon = wx.Icon(sys.path[0]+'/favicon.png', wx.BITMAP_TYPE_PNG, 64, 64)
		self.SetIcon(favicon)

	def OnClose(self,event):
		self.StopM()
		self.player.set_state(gst.STATE_NULL)
		self.Close()
		exit()
	
	def InitUI(self):
 		#init [panel] 
		panel = wx.Panel(self)
		#self.font
		self.font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		self.font.SetPointSize(9)
		###Start of eleemnts declaration###
		#init verticalbox
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		#upper panel
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.authb = wx.Button(panel, label="Auth")
		self.authb.SetFont(self.font)
		hbox1.Add(self.authb,flag=wx.LEFT,border=3)
		
		self.streamb = wx.Button(panel, label="Stream")
		self.streamb.SetFont(self.font)
		self.streamb.Enable(False)
		hbox1.Add(self.streamb,flag=wx.LEFT,border=3)
		
		self.openb = wx.Button(panel,label="Open")
		self.openb.SetFont(self.font)
		#self.openb.Enable(False)
		hbox1.Add(self.openb,flag=wx.LEFT,border=3)

		self.saveb = wx.Button(panel,label="Save")
		self.saveb.SetFont(self.font)
		hbox1.Add(self.saveb,flag=wx.LEFT,border=3)

		vbox.Add(hbox1,flag=wx.LEFT,border=3)
		vbox.Add((1,5))
		
		#listbox
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.playlistbox  = wxListBox(panel,size=(350,190))
		self.playlistbox.SetFont(self.font)
		hbox2.Add(self.playlistbox,flag=wx.EXPAND,border=3)
		
		vbox.Add(hbox2,flag=wx.LEFT|wx.EXPAND,border=3)
		vbox.Add((1,5))

		#music elements 
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.paused = True
		self.playb = wx.Button(panel,label=u'\u25b6')
		self.playb.SetFont(self.font)
		hbox3.Add(self.playb,flag=wx.LEFT,border=2)

		self.stop = True
		self.stopb = wx.Button(panel,label=u'\u25A0')
		self.stopb.SetFont(self.font)
		hbox3.Add(self.stopb,flag=wx.LEFT,border=2)
		
		self.IsFirst = True
		self.preb = wx.Button(panel,label='<<')
		self.preb.SetFont(self.font)
		hbox3.Add(self.preb,flag=wx.LEFT,border=2)

		self.IsLast = True
		self.nextb = wx.Button(panel,label='>>')
		self.nextb.SetFont(self.font)
		hbox3.Add(self.nextb,flag=wx.LEFT,border=2)

		vbox.Add(hbox3,flag=wx.LEFT,border=3)
		vbox.Add((-1,5))
		
		#download
		self.downb = wx.Button(panel,label=u'\u25bc')
		self.downb.SetFont(self.font)
		self.downb.Enable(False)
		
		#artist
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		self.aname = "Artist: "
		self.artistname = wxStaticText(panel,label=self.aname)
		self.artistname.SetFont(self.font)
		
		#title
		self.tname = "Title: "
		self.titlename = wxStaticText(panel,label=self.tname)
		self.titlename.SetFont(self.font)
		
		#edit pls
		self.epls = wx.Button(panel,label="Playlist Editor")
		self.epls.SetFont(self.font)
		
		#volumemute
		self.volmuteb = wx.Button(panel,label="Mute",size=(85,25))
		self.volmuteb.SetFont(self.font)
		
		#position
		self.tpos = wxStaticText(panel)
		self.tpos.SetFont(self.font)

		#duration
		self.tdur = wxStaticText(panel)
		self.tdur.SetFont(self.font)


		#path
		self.plpath ="Path: "
		self.pathtext = wxStaticText(panel,label=self.plpath)
		self.pathtext.SetFont(self.font)

		#sizers
		self.seekslider = wx.Slider(panel,-1,minValue=0,maxValue=3600,size=(170,15),style=wx.SL_HORIZONTAL)
		self.seektext = wxStaticText(panel,label="Seek")


		self.volslider = wx.Slider(panel,-1,minValue=0,maxValue=300,value=150,size=(170,15),style=wx.SL_HORIZONTAL)
		self.volstext = wxStaticText(panel,label="Volume")


		
		###lower space sizers
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4.Add((2,0))
		hbox4.Add(self.downb,flag=wx.LEFT,border=3)
		hbox4.Add((5,0))
		
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox1.Add(self.artistname,flag=wx.TOP,border=1)
		vbox1.Add(self.titlename,flag=wx.TOP,border=1)
		vbox1.Add(self.pathtext,flag=wx.TOP,border=1)
		hbox4.Add(vbox1,flag=wx.LEFT)
		hbox4.Add((133,0))
		hbox4.Add(self.epls,flag=wx.LEFT,border=1)
		
		hbox5 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5.Add((35,0))
		hbox5.Add(self.seektext,flag=wx.LEFT,border=1)
		hbox5.Add((30,0))
		hbox5.Add(self.seekslider,flag=wx.LEFT,border=1)
		hbox5.Add((30,0))
		
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		vbox2.Add(self.tpos,flag=wx.TOP,border=1)
		vbox2.Add(self.tdur,flag=wx.TOP,border=1)
		hbox5.Add(vbox2,flag=wx.LEFT,border=1)


		hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		hbox6.Add((30,0))
		hbox6.Add(self.volstext,flag=wx.LEFT,border=1)
		hbox6.Add((18,10))
		hbox6.Add(self.volslider,flag=wx.LEFT,border=1)
		hbox6.Add((5,-10))
		hbox6.Add(self.volmuteb,flag=wx.LEFT,border=1)



		vbox.Add(hbox4)
		vbox.Add((0,10))
		vbox.Add(hbox5)
		vbox.Add((0,10))
		vbox.Add(hbox6)

		
		
		###end of elements declaration###
		panel.SetSizer(vbox)
		###limit boxes
		
	
	#button actions
	def BindAction(self):
		#filling list
		self.authb.Bind(wx.EVT_BUTTON,self.Auth)
		self.streamb.Bind(wx.EVT_BUTTON,self.Streaming)
		self.playlistbox.Bind(wx.EVT_LISTBOX_DCLICK,self.DClick) #to start playing
		self.playlistbox.Bind(wx.EVT_LISTBOX,self.Select) # to select item
		#file operations
		self.openb.Bind(wx.EVT_BUTTON,self.OpenFile) 
		self.saveb.Bind(wx.EVT_BUTTON,self.SaveFile)
		self.downb.Bind(wx.EVT_BUTTON,self.DownFile) #downloading 
		#playing music
		self.playb.Bind(wx.EVT_BUTTON,self.OnSPPress)
		self.stopb.Bind(wx.EVT_BUTTON,self.OnStpPress)
		self.nextb.Bind(wx.EVT_BUTTON,self.OnNxtPress)
		self.preb.Bind(wx.EVT_BUTTON,self.OnPrvPress)
		self.volmuteb.Bind(wx.EVT_BUTTON,self.OnVolMute)
		self.volslider.Bind(wx.EVT_SLIDER,self.OnVolUpd)
		#closing
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	
	def SetMusicText(self):
			atext = "Artist: " +self.playlist[self.pos+1][1]
			ttext = "Title: "+self.playlist[self.pos+1][2]
			atext = self.Shorter(atext,false)
			ttext = self.Shorter(ttext,false)
			self.artistname.SetLabel(atext)
			self.titlename.SetLabel(ttext)
	###IT IS ALL ABOUT THE MUSIC ACTIONS ###
	def StartPause(self):
		self.eoft = False
		if self.paused == True:
			##GUI CHANGE
			self.paused = False
			self.SetMusicText()
			self.playb.SetLabel(u'\u275A \u275A')
			##GUI CHANGE
			self.player.set_property("uri",self.playlist[self.pos+1][0])
			self.player.set_state(gst.STATE_PLAYING)
		else:
			self.paused = True
			self.playb.SetLabel(u'\u25b6')
			self.player.set_state(gst.STATE_PAUSED)

	def on_message(self,bus,message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.StopM()
			self.eoft = True
			self.Next()
	
	def StopM(self):
		atext = "Artist: " 
		ttext = "Title: "
		self.artistname.SetLabel(atext)
		self.titlename.SetLabel(ttext)
		self.player.set_property("uri", '')
		self.player.set_state(gst.STATE_NULL)
		self.playb.SetLabel(u'\u25b6')
		self.paused = True
		
	def Next(self):
		if self.pos != len(self.playlist):
			self.preb.Enable(True)
			self.pos += 1
			self.SetMusicText()
			self.playlistbox.Select(self.pos)
			cstate = self.player.get_state()[1]
			cstate = str(cstate).split(' ')[1]
			if cstate == "GST_STATE_PLAYING" or self.eoft == True:
				self.StopM()
				self.StartPause()
			else: self.StopM()
		else: self.nextb.Enable(False)

	def Previous(self):
		if self.pos != 0:
			self.nextb.Enable(True)
			self.pos -= 1
			self.SetMusicText()
			self.playlistbox.Select(self.pos)
			cstate = self.player.get_state()[1]
			cstate = str(cstate).split(' ')[1]
			if cstate == "GST_STATE_PLAYING":
				self.StopM()
				self.StartPause()
			else: self.StopM()
		else: self.preb.Enable(False)
			
	def VolMute(self):
		if self.Muted == false:
			self.Muted = true
			self.volmuteb.SetLabel("Muted")
			self.player.set_property("volume",0.0)
		else:
			self.Muted = false
			self.volmuteb.SetLabel("Mute")
			self.player.set_property("volume",self.value)
		
	def VolUpd(self):
		lvl =  self.volslider.GetValue()
		self.value = lvl/100.0
		self.player.set_property("volume",self.value)
		if self.value == 0: 
			self.VolMute()
	###MUSIC BUTTONS

	#double click on list
	def DClick(self,event):
		self.StopM()
		self.StartPause()
		
	def OnSPPress(self,event):
		self.StartPause()
	def OnStpPress(self,event):
		self.StopM()
	def OnNxtPress(self,event):
		self.Next()
	def OnPrvPress(self,event):
		self.Previous()
	def OnVolMute(self,event):
		self.VolMute()
	def OnVolUpd(self,event):
		self.VolUpd()

	
	###everything about streaming list	
	def Streaming(self,event):
		self.plpath = getsongs.GetSongs(self.token,self.id)
		self.InitPlaylist()
	
	
	#common playlist workaround
	def InitPlaylist(self):
		self.playlist = [('0','0','0','0')]
		self.playlistbox.Clear()
		try: 
			self.playlist = check_playlist.Check(self.plpath)
			label ="Path: " + self.Shorter(self.plpath,true)
			self.pathtext.SetLabel(label)
		except RuntimeError:
			wx.MessageBox('Playlist error. It can be damaged, old format (pre-0.3.1) or not found','WARNING!',wx.OK| wx.ICON_ERROR)
		self.FillList()
	
	###get list
	def FillList(self):
		self.downb.Enable(False)
		for i in xrange(1,len(self.playlist)):
			self.playlistbox.Append(self.playlist[i][3])	
	#auth
	
	def Auth(self,event):
		if check_id.TPresent(self.l) == False or check_id.TPresent(self.p) == False:
			self.AuthDialogStart()
		while True:
			try:
				self.token, self.id = check_id.GetTokenAndId(self.l,self.p)		
				break	
			except RuntimeError:
				if self.ecode == 1: break
				self.AuthDialogStart()
		
		if self.ecode != 1:
			self.streamb.Enable(True)
		return self.token,self.id	
		
	def AuthDialogStart(self):
		authd = MyAuthDialog(self,-1,'')
		authd.ShowModal()
		self.ecode,self.l, self.p = authd.ReturnValue()
		authd.Destroy()
	
	def OpenFile(self,event):
		opendialog = wx.FileDialog(self,"Choose a playlist",self.dirname,"","*.vkpls",wx.OPEN)
		if opendialog.ShowModal() == wxID_OK:
			newpath=opendialog.GetPath()
		opendialog.Destroy()
		if len(newpath) != 0 or newpath != self.plpath:
			self.plpath = newpath
			self.InitPlaylist()
	
	def SaveFile(self,event):
		savedialog = wx.FileDialog(self,"Save your playlist",self.dirname,"","*.vkpls",wx.SAVE)
		if len(self.plpath) <= 6: wx.MessageBox('No playlist loaded!','WARNING!',wx.OK|wx.ICON_ERROR)
		else:
			if savedialog.ShowModal() == wxID_OK:
				savepath=savedialog.GetPath()
		savedialog.Destroy()
		if str(savepath).find(".vkpls") == -1:
			savepath = savepath+".vkpls"
		savecmd = "cat "+self.plpath+" > "+savepath
		os.popen(savecmd)

	def Select(self,event):
		self.pos = self.playlistbox.GetSelection()
		self.SetMusicText()
		print self.pos
		###dummy next-prev check###
		if self.pos == 0:
		 self.preb.Enable(False)
		 self.IsFirst = True
		else: 
			self.preb.Enable(True)
			self.IsFirst = False
		if self.pos == len(self.playlist)-	2:
			 self.nextb.Enable(False)
			 self.IsLast = True
		else: 
			self.nextb.Enable(True)
			self.IsLast = False
		###dummy next-prev check###
		
	def Shorter(self,text,ispath): #function to check if length is exceeded and change it to abcdef...
	 	text = text.decode('UTF-8')
		if len(text) >= 26:
	 	 	if ispath == False:
	 	 		p = text[0:24]
	 	 		p = p + u"..."
	 	 		return p
	 	 	else:
	 	 		p = text.split("/")
	 	 		return "/.../"+p[-2]+"/"+p[-1] 		
	 	else: return text

	def update_time(self):
		if self.player.get_state() == gst.STATE_NULL:
			self.tdur.SetLabel("NN:NN")
			self.tpos.SetLabel(self.pos)
		else:
			try:
				durint = self.palyer.query_duration(self.time_format,None)[0]
				dur = self.convert_ns(durint)
				self.seekslider.SetRange(0,durint)
			except:
				dur =  "--:--"
			self.tdur.SetLabel(dur)
	
	def convert_ns(self, time_int):
		time_int = time_int / 1000000000
		time_str = ""
		if time_int >= 3600:
			_hours = time_int / 3600
			time_int = time_int - (_hours * 3600)
			time_str = str(_hours) + ":"
		if time_int >= 600:
			_mins = time_int / 60
			time_int = time_int - (_mins * 60)
			time_str = time_str + str(_mins) + ":"
		elif time_int >= 60:
			_mins = time_int / 60
			time_int = time_int - (_mins * 60)
			time_str = time_str + "0" + str(_mins) + ":"
		else: time_str = time_str + "00:"
		if time_int > 9: time_str = time_str + str(time_int)
		else: time_str = time_str + "0" + str(time_int)
		return time_str

	def DownFile(self,event):
	 	if self.pos == -1: wx.MessageBox('No selection. Aborting','Attention!',wx.OK|wx.ICON_INFORMATION)
	 	else: 
	 		a = self.playlist[self.pos+1][0]
	 		s = self.playlist[self.pos+1][1]
	 		s = s[0:-1]+".mp3"
	 		print a,s
	 		savedialog = wx.FileDialog(self,"Save your playlist",self.dirname,s,"*.mp3",wx.SAVE)
			if len(self.plpath) <= 6: wx.MessageBox('No playlist loaded!','WARNING!',wx.OK|wx.ICON_ERROR)
			else:
				if savedialog.ShowModal() == wxID_OK:
					downpath=savedialog.GetDirectory()
		print downpath
		savedialog.Destroy()
	 	thread.start_new_thread(downloadmusic,(a,s,downpath)) #a - url, s - filename, downpath - path to save

def downloadmusic(url,filename,downpath,*args): #parallel thread 
	cmd = "wget -P" + downpath + " " + url 
	#os.popen(cmd)
	
	
	rpath= rpath+filename
	
	try:
		os.rename(dpath,rpath)
	except:
		wx.MessageBox('Can not rename. Leaving original name: '+dpath,'Attenttion!', wx.OK|wx.ICON_ERROR)
def startplayer(l,p):
	app = wxPySimpleApp()
	frame = MyFrame(NULL,-1,"\tStreamVK 0.3.1",l,p)
	frame.Show(true)
	app.MainLoop()
	exit()
#startplayer("","")
