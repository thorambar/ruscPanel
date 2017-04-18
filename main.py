# Main file of the Web-Controllpanel for Python
# By Thomas Pach aka. Thoramba dae rusc

# ==== Imports ================================
from flask import Flask, url_for, request, render_template, session, redirect, g, Markup
from BeautifulSoup import BeautifulSoup
from user import User
from modServe import ModServe
from facServWrapper import FacServ
import subprocess
import configparser
import os
import sys
import getpass
import hashlib, uuid
from subprocess import Popen, PIPE
import glob
import urllib2
import signal

# ==== Global variables =====================================================================
servState = False
config = configparser.ConfigParser()
config.read("config.ini")
print " - Config Parsed"
webServPort = config.get('SERVER', 'Port')
p_factorio = None

# ==== Signal handler for graceful shutdown =================================================
def handler(signum, frame):
	# shutdown procedure
	print "### ruscPanel has been stopped ###"
	print " - Stoping the modServer"
	modserv.stop()

	sys.exit(0)
	print "Exit successful - Server has gracefully shutdown"
# starting handler	
signal.signal(signal.SIGINT, handler)

# ==== start mod server =====================================================================
# it is a simpleHTTPserver
oldwd = os.getcwd()
modserv = ModServe()
modserv.start(config.get('DIRS', 'ModDir'), config.get('MODSERVER', 'Port'))
print " - Modserver Started"
os.chdir(oldwd)

# ==== Initialise User ======================================================================
user = User()
#user.name 	= raw_input("Enter User name: ") 
#password 	= getpass.getpass('Password: ')
user.name 	= 'tom'
password 	= 'tom'
user.salt 	= uuid.uuid4().hex
user.password = hashlib.sha512(password + user.salt).hexdigest()

# ==== Get all links from mod server with beautifullSoup ====================================
modServUrl 	= config.get('MODSERVER', 'Url') + ":" + config.get('MODSERVER', 'Port')
html_page 	= urllib2.urlopen(modServUrl)
soup 	= BeautifulSoup(html_page)
modList = []
for link in soup.findAll('a'):
	modList.append( (link.get('href').encode('ascii'), modServUrl + "/" + link.get('href').encode('ascii')) )

modIter = iter(modList)
modListSring = ""
for tup in modIter:
	modListSring = modListSring + "<tr>"
	modListSring = modListSring + "<td>" + "<a href=" + tup[1] + ">" + tup[0] + "</a> </td>"
	tup = next(modIter, None)
	if tup:
		modListSring = modListSring + "<td>" + "<a href=" + tup[1] + ">" + tup[0] + "</a> </td>"
		tup = next(modIter, None)
		if tup:
			modListSring = modListSring + "<td>" + "<a href=" + tup[1] + ">" + tup[0] + "</a> </td>"
	modListSring = modListSring + "</tr>"
modMarkup = Markup(modListSring)
print " - Parsed Mods"


# ==== create factory server process ========================================================
oldwd = os.getcwd()
facServ = FacServ()
facServ.init(config.get('DIRS', 'FactDir'))
os.chdir(oldwd)

# ==== start process ========================================================================
def controllProcess():
	print '#### Starting Server ####'
	global servState
	global facServ
	#subprocess.call(['java', '-jar', '/home/tom/Desktop/ruscPanel/mcServ/spigot-1.10.2.jar'])
	if servState == True:
		facServ.stop()
		servState = False
	else:
		facServ.start()
		servState = True

# ==== Create web interface =================================================================
app = Flask(__name__)
app.secret_key = os.urandom(24) # create key for session cookie

# first direct to home as login page
@app.route('/', methods=['GET', 'POST'])
def index():
	if 'user' in session:
		if session['user'] == user.name:
			return redirect(url_for('panel'))
	if request.method == 'POST':
		session.pop('user', None)
		if (hashlib.sha512(request.form['password'] + user.salt).hexdigest() == user.password) and ( request.form['username'] == user.name):
			session['user'] = request.form['username']
			return redirect(url_for('panel'))
	return render_template('index.html')



@app.route('/panel', methods=['GET', 'POST'])
def panel():
	global servState
	global modMarkup
	if request.method == 'POST':
		if request.form['buttons'] == "logout":
			return redirect(url_for('dropsession'))
		elif request.form['buttons'] == "Start" and servState == False:
			print "start"
			controllProcess()
			servState = True
		elif request.form['buttons'] == "Stop" and servState == True:
			print "stop"
			controllProcess()
			servState = False

	if g.user:
		if servState == True:
			sState = "running"
		else:
			sState = "stopped"
		return render_template('panel.html', sState = sState, modStr = modMarkup)
	return redirect(url_for('index'))


# function to be executed before request 
@app.before_request
def before_request():
	g.user = None
	if 'user' in session:
		g.user = session['user']

# code to logout
@app.route('/dropsession')
def dropsession():
	session.pop('user', None)
	return redirect(url_for('index'))

# start main flask server
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=webServPort)







  