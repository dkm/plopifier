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


class Vimeo:
    def __init__(self, login, pass):
        pass

    def upload(self, video):
        self.curl = pycurl.Curl()
        self.request = Request()

        upload_params = {'auth_token' : self.auth_token, 'ticket_id' : self.ticket_id }
        upload_params['api_sig'] = self.generate_signature(upload_params)
        upload_params['video'] = open(filepath, 'rb').read

        self.curl.setopt(self.curl.URL, API_UPLOAD_URL)
        self.curl.setopt(self.curl.POSTFIELDS, urllib.urlencode(upload_params))
        self.curl.setopt(self.curl.WRITEFUNCTION, self.request.body_callback)
        self.curl.setopt(self.curl.VERBOSE, 0)
        self.curl.perform()
        self.curl.close()
