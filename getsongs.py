#getsongs.py - get list from VK and return it's path (usually /tmp/songlist)
import os
import webbrowser
import urllib2
import lxml
import lxml.html
import sys
import htmlentitydefs
def Songrename(artist,title):
	print type(artist)
	p = artist + " - " + title
	p = p.replace("&amp;","&")
	return p
def GetSongs(token,user_id):
	url = "https://api.vkontakte.ru/method/audio.get.xml?uid=" + user_id + "&access_token=" + token
	page = urllib2.urlopen(url)
	html = page.read()
	quant = 0
	doc	 = lxml.html.document_fromstring(html)	
	padr = "/tmp/songlist.vkpls"
	playlist = open(padr,'w+')
	for url in doc.cssselect('url'):
		quant += 1
	for q in xrange(0,quant):
		url = doc.cssselect('url')[q].text
		artist = doc.cssselect('artist')[q].text
		title = doc.cssselect('title')[q].text
		artist = artist.encode('UTF-8')
		title = title.encode('UTF-8')
		song = Songrename(artist,title)
		p = str(url + "n:" + artist + "n:" + title + "n:" + song+ "\n")
		playlist.write(p)
	playlist.close()
	return padr


	
