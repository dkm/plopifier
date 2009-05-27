#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Marc Poulhiès
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Author: Marc Poulhiès

import curl
import hashlib
import xml.etree.ElementTree as ET
import pycurl

base_url = "http://vimeo.com/api/rest"

class VimeoException(Exception):
    pass

class Vimeo:
    def __init__(self, apikey, apisecret):
        self.apikey = apikey
        self.apisecret = apisecret
        self.frob = None

    def getsig(self, method_name):
        m = hashlib.md5()
        l = "%sapi_key%smethod%s" %(self.apisecret, 
                                    self.apikey, 
                                    method_name)
        m.update(l)
        return m.hexdigest()

    def body_callback(self, buf):
        self.buf += buf

    def get_frob_url(self):
        m = "vimeo.auth.getFrob"
        u = self.getsig(m)
        url = base_url + "?api_key=%s&method=%s&api_sig=%s" %(self.apikey,
                                                              m,u)
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEFUNCTION, self.body_callback)
        self.buf = ""
        curl.perform()
        curl.close()

        t = ET.fromstring(self.buf)
        frob = t.find("frob")

        if frob == None:
            raise VimeoException()

        self.frob = frob.text
