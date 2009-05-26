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


from pysqlite2 import dbapi2 as sqlite
import re
import sys
import os
from datetime import datetime

file_pattern = re.compile("video@(?P<year>\d\d\d\d)(?P<month>\d\d)(?P<day>\d\d)(?P<hour>\d\d)(?P<min>\d\d)(?P<sec>\d\d)\.jpg")


sqfile = sys.argv[1]
root = sys.argv[2]

conn = sqlite.connect(sqfile)
cur = conn.cursor()
conn.row_factory = sqlite.Row

count = 0

curdir = root

q = "INSERT into repository (rootfs) VALUES('%s')" %root
cur.execute(q)
conn.commit()        

q = "SELECT id FROM repository WHERE rootfs = '%s'" %root
cur.execute(q)
root_idx = int(cur.fetchall()[0][0])
print "root_idx: %d" %root_idx

insert_str="INSERT INTO images (relpath,ddate,rootid) VALUES ('%s', '%s', %s)"

def add_image(year,month,day,file):
    pass



for dirpath1,year_dirs,files1 in os.walk(curdir):
    for year in year_dirs:
        for dirpath2,month_dirs,files2 in os.walk(os.path.join(dirpath1,year)):
            for month in month_dirs:
                for dirpath3,day_dirs,files3 in os.walk(os.path.join(dirpath2,month)):
                    for day in day_dirs:
                        for dirpath4,dirs4,image_files in os.walk(os.path.join(dirpath3,day)):
                            for file in image_files:
                                m = file_pattern.match(file)
                                if m == None:
                                    continue
                                y,mt,d = int(year), int(month), int(day)
                                h,m,s = int(m.group('hour')),int(m.group('min')),int(m.group('sec'))
                                dt = datetime(y, mt, d, h, m, s)
                                q = insert_str %(os.path.join(year,month,day,file),
                                                 str(dt),
                                                 str(root_idx))
                                count+=1
                                cur.execute(q)
                                if count%100==0:
                                    print "Count: %.10d\r" %count,




conn.commit()
conn.close()
