#!/usr/bin/env python

from plopifier import vimeo
import sys


# $1 : api key
# $2 : api sig (secret)

v = vimeo.Vimeo(sys.argv[1], sys.argv[2], sys.argv[3])

v.test_login()
#v.upload("test.avi")

v.set_title("4557213", "Paraglinding near Chamrousse (Belledone, France)")
v.set_tags("4557213", ["paragliding", "parapente", 'chamrousse', 'toto'])


