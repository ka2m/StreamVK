#check_id.py - script to check my id and password for VK
#it should be runned from player.py (on AUTH press) or getdata.py (getdata dialog)
import vkauth2
def TPresent(text): #function to check length or NULL parametr of login or password)
	if len(str(text)) == 0: return False
	elif str(text) == "NULL": return False
	else: return True
def GetTokenAndId(login,password):
	token, user_id = vkauth2.auth(login,password,"2223684", "audio")
	return token,user_id

