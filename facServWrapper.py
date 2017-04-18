import SimpleHTTPServer
import SocketServer
import os
import thread
import threading
import subprocess
from subprocess import Popen, PIPE
import time

class FacServ(object):
	p = None
	path = None

	def init(self, p):
		self.path = p


	def start(self):
		os.chdir(self.path)
		self.p = subprocess.Popen(['java', '-jar', 'spigot-1.10.2.jar'])
		time.sleep(1)

	def stop(self):
		self.p.kill()
		print 'Modserver stopped'
