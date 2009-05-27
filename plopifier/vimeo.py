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
        self.auth_token = None
        self.auth_perms = None
        self.user_dic = None

    def get_url_sig(self, dic):
        tosig = self.apisecret
        url = "?"
        keys = dic.keys()
        keys.sort()
        for i in keys:
            tosig+=i + dic[i]
            url+="%s=%s&" % (i, dic[i])

        m = hashlib.md5()
        m.update(tosig)
        sig = str(m.hexdigest())
        
        url+="api_sig="+sig
        return (url, sig)

    def getsig(self, method_name):
        m = hashlib.md5()
        l = "%sapi_key%smethod%s" %(self.apisecret, 
                                    self.apikey, 
                                    method_name)
        m.update(l)
        return m.hexdigest()

    def body_callback(self, buf):
        self.buf += buf

    def do_request(self, url):
        self.buf = ""
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEFUNCTION, self.body_callback)
        curl.perform()
        curl.close()
        p = self.buf
        self.buf = ""
        return p

    def get_frob_url(self):
        m = "vimeo.auth.getFrob"
        (url, u) = self.get_url_sig({'api_key': self.apikey,
                                     'method' : m})
        url = base_url + url
        res = self.do_request(url)

        t = ET.fromstring(res)
        frob = t.find("frob")

        if frob == None:
            raise VimeoException()

        self.frob = frob.text

    def get_auth_url(self, perms="read"):
        if self.frob == None:
            raise VimeoException()

        burl = "http://vimeo.com/services/auth/" 
        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'perms' : perms,
                                       'frob' : self.frob})
        return burl+url
        
    def get_auth_token(self):
        if self.frob == None:
            raise VimeoException()

        m = "vimeo.auth.getToken"
        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'frob' : self.frob,
                                       'method': m})
        url = base_url + url
        res = self.do_request(url)
        t = ET.fromstring(res)

        self.auth_token = t.findtext("auth/token")
        self.auth_perms = t.findtext("auth/perms")
        unode = t.find("auth/user")

        if None in (self.auth_token, self.auth_perms, unode):
            raise VimeoException()

        self.user_dic = unode.attrib
