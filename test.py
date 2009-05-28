#!/usr/bin/env python

from plopifier import vimeo
import sys


# $1 : api key
# $2 : api sig (secret)

v = vimeo.Vimeo(sys.argv[1], sys.argv[2], sys.argv[3])

v.test_login()
#v.upload("test.avi")

l=[

"4880163",
"4880128",
"4880103",
"4880080",
"4880058",
"4880033",
"4880004",
"4879985",
"4879962",
"4879925",
"4879925",
"4879902",
"4879879"]

for i in l:
    print "video:", i
    v.set_privacy(i)
