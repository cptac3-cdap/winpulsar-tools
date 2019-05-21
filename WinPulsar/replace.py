#!/bin/env python27
import shutil, sys, os
h = open(sys.argv[1],'rb')
data = h.read()
h.close()
if sys.argv[2] not in data:
    print >>sys.stderr, "Cannot find replace string"
    sys.exit(1)
shutil.copy(sys.argv[1],sys.argv[1]+'.orig')
data = data.replace(sys.argv[2],sys.argv[3])
wh = open(sys.argv[1],'wb')
wh.write(data)
wh.close()
