#streamvk.py - default starting file
#it also redirects all stdout and stderr to /tmp/svk_out and /tmp/svk_err
#!/usr/bin/env python
import getopt
import sys
import player
def __init__():
	args_letter = 'l:p:h'
	args_word=['login=','password=', 'help']
	opts, extraparam = getopt.getopt(sys.argv[1:],args_letter,args_word) #getting extraparm
	login = ""
	password = ""
	for o,p in opts:
		if o in ['-l','--login']:
			login = p
		if o in ['-p','--password']:
			password = p
		if o in ['-h','--help']:
			print "Usage: python streamvk.py -l (--login) <login> -p (--password) <password> [-h (--help)]"
			exit()
	sys.stdout = open("/tmp/svk_out","w")
	sys.stderr = open("/tmp/svk_err","w")
	if len(login) == 0: login="NULL"
	if len(password) == 0: password="NULL"
	player.startplayer(login,password)
__init__()
