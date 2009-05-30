#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Marc Poulhiès
#
# This file is part of Plopifier.
#
# Plopifier is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Plopifier is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Plopifier.  If not, see <http://www.gnu.org/licenses/>.

"""
This modules provides high level method to access
the images from the database.
"""

from pysqlite2 import dbapi2 as sqlite
#from datetime import datetime
import os.path

class Request:
    def __init__(self, sqfile, absroot=None):
        self.sqfile = sqfile
        self.cnx = sqlite.connect(sqfile)
        self.cur = self.cnx.cursor()
        self.absroot = absroot

    def get_files(self, start, stop):
        q = "SELECT rootfs,relpath FROM images,repository" +\
            " WHERE ddate >= '%s' AND ddate <= '%s'" + \
            " ORDER BY ddate" % (start, stop)
        print q
        self.cur.execute(q)
        if self.absroot != None:
            return [os.path.abspath("%s/%s/%s" % (self.absroot, 
                                                  x[0], 
                                                  x[1])) 
                    for x in self.cur.fetchall()]
        else:
            return [os.path.abspath("/%s/%s" % (x[0], 
                                                x[1])) 
                    for x in self.cur.fetchall()]

    def __del__(self):
        self.cnx.close()
