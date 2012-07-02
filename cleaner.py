#cleaner.py - a cleaner for tmp file
import os
def Remover(path):
	if os.path.exists(path): 
		os.remove(path)
		return 0
	else: return 1 
def Clean():
	p = "/tmp/svk_err"
	Remover(p)
	p = "/tmp/svk_out"
	Remover(p)
	p = "/tmp/songlisg"
	Remover(p)
	return 0