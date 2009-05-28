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

"""
This module is used to interract with Vimeo through its API
Full documentation is available here:
 http://vimeo.com/api

This module will be used to upload video. Maybe it will
get more features as they are needed, but it's not the
current goal. Of course, any contribution is welcome !
"""

import curl
import hashlib
import xml.etree.ElementTree as ET
import pycurl
import urllib
base_url = "http://vimeo.com/api/rest"

class VimeoException(Exception):
    pass

class Vimeo:
    def __init__(self, apikey, apisecret, auth_token=None):
        self.apikey = apikey
        self.apisecret = apisecret
        self.frob = None
        self.auth_token = auth_token
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
            print res
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
        print self.auth_token
        self.auth_perms = t.findtext("auth/perms")
        unode = t.find("auth/user")

        if None in (self.auth_token, self.auth_perms, unode):
            print res
            raise VimeoException()

        self.user_dic = unode.attrib

    def test_login(self):
        if self.auth_token == None:
            raise VimeoException()

        m = "vimeo.test.login"
        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'auth_token': self.auth_token,
                                       'method' : m})
        url = base_url + url
        res = self.do_request(url)
        t = ET.fromstring(res)
        un = t.find("user/username")

        if un == None:
            print res
            raise VimeoException()
        uid = t.find("user").attrib['id']

        print "Username: %s [%s]" % (un.text, uid)

    def set_title(self, video_id, title):
        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'auth_token': self.auth_token,
                                       'video_id' : video_id,
                                       'title' : title,
                                       'method' : 'vimeo.videos.setTitle'})



        res = self.do_request(base_url + url)
	print res

    def set_tags(self, video_id, tags):
        print "tagging %s with %s" %(video_id, ",".join(tags))
        ntags=[urllib.quote_plus(tag) for tag in tags]

        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'auth_token': self.auth_token,
                                       'video_id' : video_id,
                                       'tags' : ",".join(ntags),
                                       'method': 'vimeo.videos.addTags'})
        res = self.do_request(base_url + url)
        print res

    def upload(self, video, title, tags=[]):
        if self.auth_token == None:
            raise VimeoException()

        m = "vimeo.videos.getUploadTicket"
        (url, sig) = self.get_url_sig({'api_key' : self.apikey,
                                       'auth_token': self.auth_token,
                                       'method': m})

        res = self.do_request(base_url + url)

        t = ET.fromstring(res)
        upload_ticket = t.find("ticket")
        
        if upload_ticket == None:
            print res
            raise VimeoException()

        upload_ticket = upload_ticket.attrib['id']
        
        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'auth_token': self.auth_token,
                                       'ticket_id': upload_ticket})
                                       

        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, "http://vimeo.com/services/upload")
        c.setopt(c.HTTPPOST, [("video", (c.FORM_FILE, video)),
                              ("api_key", self.apikey),
                              ("auth_token", self.auth_token),
                              ("ticket_id", upload_ticket),
                              ("api_sig", sig)])
        c.setopt(c.WRITEFUNCTION, self.body_callback)
        #c.setopt(c.VERBOSE, 1)
        self.buf=""
        c.perform()
        c.close()
        #print self.buf


        (url, sig) = self.get_url_sig({'api_key': self.apikey,
                                       'auth_token': self.auth_token,
                                       'ticket_id': upload_ticket,
                                       'method' : "vimeo.videos.checkUploadStatus"})
        url = base_url + url
        res = self.do_request(url)
        t = ET.fromstring(res)
        upload_ticket = t.find("ticket")
        if upload_ticket == None:
            print res
            raise VimeoException()

        vid = upload_ticket.attrib['video_id']

        self.set_title(vid, title)

        if len(tags) > 0:
            self.set_tags(vid, tags)
        
        print vid
