
import os, sys, os.path, shutil, time, datetime, traceback, gzip, hashlib, subprocess, re, glob
from collections import defaultdict

def timestamp(msg):
    timestamp = datetime.datetime.now().ctime()
    print "[%s] %s"%(timestamp,msg)

def gettail(f):
    if '/' in f:
        return f.rsplit('/',1)[-1]
    return f

def getbase(f):
    return f.rsplit('.',1)[0]

def gzipfile(inputfile,outputfile):
    h = open(inputfile,'rb')
    wh = gzip.open(outputfile,'wb')
    while True:
	buffer = h.read(4096)
	if not buffer:
	    break
	wh.write(buffer)
    wh.close()
    h.close()

def movefile(inputfile,inputfile1):
    attempt = 0
    while not os.path.exists(inputfile1):
        attempt += 1
        print "Move %s to %s"%(inputfile,inputfile1)
        try:
            shutil.move(inputfile,inputfile1)
        except (IOError,OSError):
            print traceback.format_exc()
            if attempt > 2:
                print >>sys.stderr, "[FATAL] Move failed 3 times. Abort."
                sys.exit(1)
            print "Move failed. Trying again in 5 seconds"
        time.sleep(5)
    return

def copyfile(inputfile,inputfile1):
    attempt = 0
    while not os.path.exists(inputfile1):
        attempt += 1
        print "Copy %s to %s"%(inputfile,inputfile1)
        try:
            shutil.copy(inputfile,inputfile1)
        except (IOError,OSError):
            print traceback.format_exc()
            if attempt > 2:
                print >>sys.stderr, "[FATAL] Copy failed 3 times. Abort."
                sys.exit(1)
            print "Copy failed. Trying again in 5 seconds"
        time.sleep(5)
    return

def removefile(filename):
    attempt = 0
    while os.path.exists(filename):
	attempt += 1
        print "Remove %s"%(filename)
	try:
	    os.unlink(filename)
	except (IOError,OSError):
	    print traceback.format_exc()
	    if attempt > 2:
		print >>sys.stderr, "[FATAL] Remove failed 3 times. Abort."
		sys.exit(1)
	    print "Remove failed. Trying again in 5 seconds"
	time.sleep(5)
    return

def gethash(filename):
    md5hash = hashlib.md5()
    sha1hash = hashlib.sha1()
    h = open(filename,'rb')
    while True:
        buffer = h.read(8192)
        if not buffer:
            break
        md5hash.update(buffer)
        sha1hash.update(buffer)
    h.close()
    size = os.path.getsize(filename)
    md5hash = md5hash.hexdigest().lower()
    sha1hash = sha1hash.hexdigest().lower()
    return md5hash,sha1hash,str(size)


def execute(args):
    process = subprocess.Popen(args,
                               stdin=None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               bufsize=1024)

    while True:
        buf = process.stdout.read(1024)
        if not buf:
            break
        sys.stdout.write(buf)

    return process.returncode

simplefieldre = re.compile(r'^(\w+):[(]?(\d+(\.\d+)?(eV|\?)?)[)?]?$')
labelfieldre = re.compile(r'^(TMT10|TMT11|TMT6|iTRAQ4)_')

def extract_reporters_from_TITLE(title,scan2scan=None):
    labeling = None; ab = None; dmzhwhm = None; abfract = None
    r = {}
    if title.startswith('TITLE='):
	title = title[6:]
	title = title.strip()
    rest,filter = title.rsplit('Filter:',1)
    r['Filter'] = filter.strip()
    for keyval in rest.split():                                                                               
        m = simplefieldre.search(keyval)
        if m:
            key = m.group(1)
            try:
                value = m.group(2)
                value = float(m.group(2))
                value = int(m.group(2))
            except ValueError:
                pass
            r[key] = value
            continue
        m = labelfieldre.search(keyval)
	if m:
	    labeling = m.group(1)
	    for m in re.finditer(r'_([^(]+)\(([^)]+)\)',keyval):
	        if m.group(1) == 'ab':
	            ab = m.group(2).split(',')
		    dmzhwhm = ["?"]*len(ab)
		    abfract = "?"
	        elif m.group(1) == 'dMz/HWHM':
	            dmzhwhm = m.group(2).split(',')
	        elif m.group(1) == 'AbFract':
		    abfract = m.group(2)
    
    # print title
    if scan2scan != None:
	scan = scan2scan[r['Scan']]
    else:
	scan = r['Scan']
    # print r.get('Scan'), r.get('PrecursorScan'), labeling, ab, dmzhwhm, abfract
    assert r.get('Scan') != None and labeling != None and ab != None and dmzhwhm != None and abfract != None
    return "\t".join(map(str,[scan,labeling]+ab+dmzhwhm+[abfract]))

#
# ------ Scan 283 ------
# Filter: FTMS + c NSI Full ms [400.0000-1400.0000]
#
#
def ms3scan2ms2scan(mdfile):
    ms3toms2 = dict()
    scan = None
    ms2assigned = set()
    for l in open(mdfile):
	m = re.search(r'^------ Scan (\d+) ------',l)
	if m:
	    assert scan == None
	    scan = int(m.group(1))
	    continue
	m = re.search(r'^Filter: .* (ms|ms2|ms3) .*$',l)
	if m:
	    assert scan != None
	    filterstr = l.split(None,1)[1]
	    if m.group(1) == "ms":
		msLevel = 1
	    else:
		msLevel = int(m.group(1)[2])
	    if msLevel == 1:
                filter2scans = defaultdict(list)
	    elif msLevel == 2:
                m = re.search(r'\s+ms2\s+([^ ]+)\s+',filterstr)
                assert m, "Scan: %s, Bad filter string?\n  %s"%(scan,filterstr,)
                precstr = m.group(1)
                filter2scans[precstr].append(scan)
	    elif msLevel == 3:
                m = re.search(r'\s+ms3\s+([^ ]+)\s+',filterstr)
                assert m, "Scan: %s, Bad filter string?\n  %s"%(scan,filterstr,)
                ms2precstr = m.group(1)
                ms2scans = sorted(filter(lambda s: s not in ms2assigned, filter2scans[ms2precstr]))
                assert len(ms2scans) > 0, "Problem with MS3 scan %s"%(scan,)
                ms3toms2[scan] = ms2scans[0]
                ms2assigned.add(ms2scans[0])
	    scan = None
    return ms3toms2

def printfilelist(pattern):

     print pattern
     for fn in glob.glob(pattern):
	print "  %16d\t%s"%(os.path.getsize(fn),os.path.split(fn)[1])
