#!/usr/bin/env python

from plopifier import vimeo
import sys


# $1 : api key
# $2 : api sig (secret)
v = vimeo.Vimeo(sys.argv[1], sys.argv[2])
v.get_frob_url()
print v.get_auth_url(perms="write")
print "waiting..."
sys.stdin.read(1)
v.get_auth_token()


