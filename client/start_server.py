from datetime import datetime
from flask import Flask, request, render_template, redirect
from flask_socketio import SocketIO
from random import randint
import socket
import string
import os
import sys
import time
from requests import get

from github_utils import save_code, clear_code_library, get_code_url

# setup flask app
app = Flask(__name__)
socketio = SocketIO(app)

# port and ip are assigned, but updated depending on device. The values are placeholders across all files so that we can string match them
# these are hardcoded, please don't mess with them!

port = 99999 # placeholder
ip = "999.999.999.999" # placeholder

@app.route('/') # show main page
def admin_form():
    return render_template('index.html')

@app.route('/', methods=['POST']) # handle making new code file
def new_file():
    code = request.form['code'] # copy code from body
    return_addr = save_code(code)
    response_code = 404
    while response_code == 302 or response_code == 404:
        try:
            response_code = get(return_addr).status_code
        except:
            pass
        print(response_code)
        time.sleep(1)
    return redirect(return_addr)

code_url = get_code_url()

@app.route('/clear') 
def clear_everything():
    clear_code_library()
    return "cleared library!"

@app.route('/code/<src>')
def get_file(src):
    without_txt = get(code_url+src).status_code
    with_txt = get(code_url+src+".txt").status_code
    if without_txt == 200:
        return redirect(code_url+src)
    elif with_txt == 200:
        return redirect(code_url+src+".txt")
    else:
        return "address not found"



def update_template_address(ip,port): # changes placeholder ip and port values across all files to specified ip and port
    for filename in os.listdir("templates/"):
        template_contents = ""
        with open(os.path.join("templates/", filename), 'r') as template: # get text
            template_contents = template.read()

        # save changed contents to new variable so that it updates
        new_contents = template_contents.replace("999.999.999.999",ip).replace("99999",str(port))

        with open(os.path.join("templates/", filename), 'w') as template: # update text
            template.write(new_contents)
        

def change_templates_back(): # changes specified ip and port values across all files to placeholder ip and port values
    for filename in os.listdir("templates/"):
        template_contents = ""
        with open(os.path.join("templates/", filename), 'r') as template: # get text
            template_contents = template.read()

        # save changed contents to new variable so that it updates
        new_contents = template_contents.replace(ip,"999.999.999.999").replace(str(port),"99999")

        with open(os.path.join("templates/", filename), 'w') as template: # update text
            template.write(new_contents)

def get_ip(): # find the local machine's ip
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    return ip_address

if __name__ == '__main__':
    args = sys.argv
    #port = randint(50000,99999)
    port = 64216
    if len(args) > 2:
        port = int(args[1])
    ip = get_ip()
    update_template_address(ip,port) # update templates
    socketio.run(app, host='0.0.0.0', port=port) # start running the server
    change_templates_back() # change templates back