#check_playlist.py - check exisiting playlist and format, then return array
import os
def Check(path):
	playlist = [('0','0','0','0')]
	try:
		with open(path) as f: pass
	except IOError as e:
		raise RuntimeError ("File Not Found")
	f = open(path,"r")
	for line in f:
		try:
			splitted_line = line.split('n:')
		except:
			raise RuntimeError("Wrong file format")
		try:
			playlist.append((str(splitted_line[0]),str(splitted_line[1]),str(splitted_line[2]),str(splitted_line[3])))
		except:
			raise RuntimeError("Wront file identation")
	print playlist
	return playlist



