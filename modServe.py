import SimpleHTTPServer
import SocketServer
import os
import thread
import threading
import subprocess
from subprocess import Popen, PIPE
import time

class ModServe(object):
	server = None
	p = None

	def start(self, path, confPort):
		os.chdir(path)
		self.p = subprocess.Popen(['python', '-m', 'SimpleHTTPServer', confPort])
		time.sleep(1)

	def stop(self):
		self.p.kill()
		print 'Modserver stopped'
