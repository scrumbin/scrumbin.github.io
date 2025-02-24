import keyring
from getpass import getpass
from github import Github
from random import choice
from string import ascii_lowercase

# scuffed alphabet for distinct sounding names
vowels = 'aio'
consonants = 'bdghjklmnprstvz'

user = "scrumbin"
token = "I8j2DXAm75FRQESQfNByKD3Q4FyCeGtBQstk73OyM7mxNqkjHKqKIeYJB75_19PIVmZz2U0G0AXT7ZPB11_tap_buhtig"[::-1] # please don't explode this

""" # if used not on scrumbin
user = keyring.get_password("github","user")
if user is None:
    user = input("github user: ")
    keyring.set_password("github","user",user)

token = keyring.get_password("github","token")
if token is None:
    token = input("github token: ")
    keyring.set_password("github","token",token)
"""

g = Github(token)

repo = g.get_user().get_repo(user+".github.io") # repo name



code_log = []

def _fetch_code_log():
    global code_log
    code_log = str(repo.get_contents("code/codelog.txt").decoded_content)[2:-1].replace("\\r","").replace("\\n","\n").split("\n")
    while len(code_log) > 0 and code_log[0] == '':
        code_log = code_log[1:]
    return code_log

def _append_code(file_name,code):
    global code_log
    code_log.append(file_name)
    code_path = "code/"+file_name+".txt"
    try:
        repo.create_file(code_path, "added new code file", code, "main") # attempt to make new file
    except: # uhoh, file already existed
        repo.update_file(code_path, "added new code file", code, "main") # otherwise attempt to update

def _purge_oldest_code():
    global code_log
    #print("oldest code:",code_log[0])
    target = repo.get_contents("code/"+code_log[0]+".txt") # get oldest code ref
    repo.delete_file(target.path, "pruned old code file", target.sha) # delete oldest file
    code_log = code_log[1:] # update queue
    
def _push_codelog():
    global code_log
    repo.update_file("code/codelog.txt", "updated codelog", "\n".join(code_log), repo.get_contents("code/codelog.txt").sha)

def _get_valid_name():
    name = ""
    for _ in range(3):
        name += choice(consonants) + choice(vowels)
    return name + choice(consonants)

def clear_code_library():
    global code_log
    _fetch_code_log()
    while len(code_log) > 0:
        _purge_oldest_code()
    _push_codelog()

def save_code(code):
    global code_log
    _fetch_code_log()
    if len(code_log) > 50:
        #print("attempting to purge")
        _purge_oldest_code()
    file_name = _get_valid_name()
    while file_name in code_log: # in case a duplicate
        file_name = _get_valid_name()
    _append_code(file_name,code)
    _push_codelog()
    return "https://"+user+".github.io/code/"+file_name+".txt"

def get_code_url():
    return "https://"+user+".github.io/code/"

#print(save_code("woah new file"))
#clear_code_library()