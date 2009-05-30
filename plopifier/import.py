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
This module helps to fill a database (currently sqlite based)
with the images contained in a directories.
The directories MUST be ordered by YEAR/MONTH/DAY
"""

from pysqlite2 import dbapi2 as sqlite
import re
import sys
import os
from datetime import datetime

FILE_PATTERN = re.compile("video@(?P<year>\d\d\d\d)(?P<month>\d\d)" +
                          "(?P<day>\d\d)(?P<hour>\d\d)(?P<min>\d\d)" + 
                          "(?P<sec>\d\d)\.jpg")

SQFILE = sys.argv[1]
ROOT = sys.argv[2]

CONN = sqlite.connect(SQFILE)
CUR = CONN.cursor()
CONN.row_factory = sqlite.Row

COUNT = 0

CURDIR = ROOT

q = "INSERT into repository (rootfs) VALUES('%s')" % ROOT
CUR.execute(q)
CONN.commit()        

q = "SELECT id FROM repository WHERE rootfs = '%s'" % ROOT
CUR.execute(q)
ROOT_IDX = int(CUR.fetchall()[0][0])
print "root_idx: %d" % ROOT_IDX

INSERT_STR = "INSERT INTO images (relpath,ddate,rootid) VALUES ('%s', '%s', %s)"

for dirpath1, year_dirs, files1 in os.walk(CURDIR):
    for year in year_dirs:
        for dirpath2, month_dirs, files2 in os.walk(os.path.join(dirpath1, year)):
            for month in month_dirs:
                for dirpath3, day_dirs, files3 in os.walk(os.path.join(dirpath2, month)):
                    for day in day_dirs:
                        for dirpath4, dirs4, image_files in os.walk(os.path.join(dirpath3, day)):
                            for filen in image_files:
                                m = FILE_PATTERN.match(filen)
                                if m == None:
                                    continue
                                y, mt, d = int(year), int(month), int(day)
                                h, m, s = int(m.group('hour')), int(m.group('min')), int(m.group('sec'))
                                dt = datetime(y, mt, d, h, m, s)
                                q = INSERT_STR % (os.path.join(year, month, day, filen),
                                                  str(dt),
                                                  str(ROOT_IDX))
                                COUNT += 1
                                CUR.execute(q)
                                if (COUNT % 100) == 0:
                                    print "Count: %.10d\r" % COUNT,

CONN.commit()
CONN.close()
