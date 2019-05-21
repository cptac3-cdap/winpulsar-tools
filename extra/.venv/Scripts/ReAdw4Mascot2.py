
import sys, os, os.path, subprocess, shutil, glob, traceback
from collections import defaultdict
import util

def quote(s):
    return '"%s"'%(s,)


util.timestamp("ReAdw4Mascot2 Start")
print "Arguments:\n   ",
print "\n    ".join(sys.argv[1:])

inputfile = sys.argv[1]
inputfilename = sys.argv[2]

ms2spectra = None
ms3spectra = None
ms1profile = None
reporters = None
mdfile = None

opts = dict()
for a in sys.argv[3:]:
    if ":" in a:
        dest,of = a.split(":",1)
        if dest == "ms2spectra":
            ms2spectra = of
        elif dest == "ms1profile":
            ms1profile = of
        elif dest == "reporters":
            reporters = of
        elif dest == "ms3spectra":
            ms3spectra = of
        elif dest == "mdfile":
            mdfile = of
    else:
        opts[a] = True

assert ms2spectra, "No MS2 spectrum output file supplied on command-line"

version = None
for k in opts:
    if k.startswith("ReAdw4Mascot"):
	version = k
	break

if version:
    ReAdw4Mascot2bin = r"%s\%s\x64\ReAdw4Mascot2x64.exe"%(os.path.split(sys.argv[0])[0],version)
else:
    ReAdw4Mascot2bin = r"%s\ReAdw4Mascot2\x64\ReAdw4Mascot2x64.exe"%(os.path.split(sys.argv[0])[0],)

inputdir = os.path.split(inputfile)[0]

inputbase,inputextn = inputfilename.rsplit('.',1)
if '/' in inputbase:
    inputpath,inputbase = inputbase.rsplit('/',1)
inputbaseextn = inputbase+'.'+inputextn

inputfile1 = os.path.join(inputdir,inputbaseextn)
util.movefile(inputfile,inputfile1)

md5,sha1,size = util.gethash(inputfile1)
print
print "  md5(%s) = %s"%(inputbaseextn,md5)
print " sha1(%s) = %s"%(inputbaseextn,sha1)
print "bytes(%s) = %s"%(inputbaseextn,size)
print

outputdir = os.path.split(ms2spectra)[0]

if not opts.get('spsms3'):

    args = [ ReAdw4Mascot2bin,
             "-sep1", "-NoPeaks1", "-MaxPI",
             "-metadata", "-PIvsRT","-c",
             "-sepZC", 
             "-xpw", "10",
             "-xpm", "32",
             "-TmpInOutDir",
             ]
    if opts.get('ms1profile'):
        args.extend(["-XmlOrbiMs1Profile"])
    if opts.get('hiaccuracy'):
        args.extend(["-ChargeMgfOrbi","-MonoisoMgfOrbi","-FixPepmass"])
    for k in opts.keys():
        if opts.get(k) and (k.startswith('iTRAQ') or k.startswith('TMT')):
            args.append('-'+k)
	    opts['reporters'] = k
	    break
    args.append(inputfile1)
    args.append(outputdir)

    print "Execute:\n  ","\n       ".join(args)

    util.execute(args)
    util.printfilelist(os.path.join(outputdir,inputbase+'.'+inputextn+'.*'))

    mgffiles = glob.glob(os.path.join(outputdir,inputbase+'.'+inputextn+'.*.ch.MGF'))

    assert len(mgffiles) > 0, "Can't find MGF output file"
    assert len(mgffiles) == 1, "Multiple MGF output files"
    print "Move %s to %s"%(mgffiles[0],ms2spectra)
    shutil.move(mgffiles[0],ms2spectra)

    if reporters:
	if opts.get('reporters'):
            wh = open(reporters,"wb")
            for l in open(ms2spectra):
                if l.startswith("TITLE"):
                    print >>wh, util.extract_reporters_from_TITLE(l)
            wh.close()
	else:
            open(reporters,"wb").close()

    if ms1profile:

        if opts.get('ms1profile'):

            mzxmlfiles = glob.glob(os.path.join(outputdir,inputbase+'.'+inputextn+'.mzXML'))
            assert len(mzxmlfiles) > 0, "Can't find mzXML output file"
            assert len(mzxmlfiles) == 1, "Multiple mzXML output files"
            print "Move %s to %s"%(mzxmlfiles[0],ms1profile)
            shutil.move(mzxmlfiles[0],ms1profile)
            
            # Check for the mzXML closing tag in the mzXML file...
            h = open(ms1profile,'rb')
            # seek to the last 10 characters
            h.seek(-10, 2)
            # read the remainder of the file
            buf = h.read()
            # close the file
            h.close()
            # and fail loudly if the tag is not present
            assert '</mzXML>' in buf, "mzXML closing tag not present"

        else:
            
            # Touch this file in case it is needed...
            open(ms1profile,'wb').close()

else:

    # First, run to extract MS1 and MS3 high accuracy spectra, then
    # run to again to extract MS2 IT spectra.

    # First step to get the MS^3 spectra in a MGF file and MS1 spectra into mzXML file
    args = [ ReAdw4Mascot2bin,
             "-sep1", "-NoPeaks1", "-MaxPI", "-ms1", "-sep",
             "-metadata", "-PIvsRT","-c",
             "-xpw", "10",
             "-xpm", "32",
             "-msLevel","3","3",
             "-TmpInOutDir",
             ]

    # These should always be present for this workflow?
    # args.extend(["-ChargeMgfOrbi","-MonoisoMgfOrbi","-FixPepmass"])
    for k in opts.keys():
        if opts.get(k) and (k.startswith('iTRAQ') or k.startswith('TMT')):
            args.append('-'+k)
	    opts['reporters'] = k
	    break
    assert opts.get('reporters'), "Reporter ion flag expected for SPS-MS3 workflow"
    if opts.get('ms1profile'):
        args.extend(["-XmlOrbiMs1Profile"])
    args.append(inputfile1)
    args.append(outputdir)

    print "Execute:\n  ","\n       ".join(args)

    util.execute(args)
    util.printfilelist(os.path.join(outputdir,inputbase+'.'+inputextn+'.*'))

    mgffiles = glob.glob(os.path.join(outputdir,inputbase+'.'+inputextn+'.*.MGF'))

    util.printfilelist(os.path.join(outputdir,inputbase+'.'+inputextn+'.*.MGF'))

    assert len(mgffiles) > 0, "Can't find MS3 MGF output file"
    assert len(mgffiles) == 1, "Multiple MGF output files"

    ms3file = mgffiles[0]

    if ms3spectra:
        print "Move %s to %s"%(ms3file,ms3spectra)
        shutil.move(ms3file,ms3spectra)
	ms3file = ms3spectra

    if ms1profile:

        if opts.get('ms1profile'):

            mzxmlfiles = glob.glob(os.path.join(outputdir,inputbase+'.'+inputextn+'.mzXML'))

            assert len(mzxmlfiles) > 0, "Can't find mzXML output file"
            assert len(mzxmlfiles) == 1, "Multiple mzXML output files"

            print "Move %s to %s"%(mzxmlfiles[0],ms1profile)
            shutil.move(mzxmlfiles[0],ms1profile)
            
            # Check for the mzXML closing tag in the mzXML file...
            h = open(ms1profile,'rb')
            # seek to the last 10 characters
            h.seek(-10, 2)
            # read the remainder of the file
            buf = h.read()
            # close the file
            h.close()
            # and fail loudly if the tag is not present
            assert '</mzXML>' in buf, "mzXML closing tag not present"

        else:
            
            # Touch this file in case it is needed...
            open(ms1profile,'wb').close()

    # Second step to get the MS^2 spectra in a MGF file
    
    args = [ ReAdw4Mascot2bin,
             "-MaxPI", '-ms1', '-sep',
             "-metadata", "-PIvsRT","-c",
             "-xpw", "10",
             "-xpm", "32",
             "-msLevel","2","2",
             "-TmpInOutDir",
             ]

    args.extend(["-ChargeMgfOrbi","-MonoisoMgfOrbi","-FixPepmass"])
    args.append(inputfile1)
    args.append(outputdir)

    print "Execute:\n  ","\n       ".join(args)

    util.execute(args)
    util.printfilelist(os.path.join(outputdir,inputbase+'.'+inputextn+'.*'))

    mgffiles1= glob.glob(os.path.join(outputdir,inputbase+'.'+inputextn+'.*.MGF'))
    util.printfilelist(os.path.join(outputdir,inputbase+'.'+inputextn+'.*.MGF'))
    if ms3file in mgffiles1:
        mgffiles1.remove(ms3file)

    assert len(mgffiles1) > 0, "Can't find MS2 MGF output file"
    assert len(mgffiles1) == 1, "Extra MGF output files"

    mdfiles = glob.glob(os.path.join(outputdir,inputbase+'.'+inputextn+'.metadata'))
    util.printfilelist(os.path.join(outputdir,inputbase+'.'+inputextn+'.metadata'))

    assert len(mdfiles) > 0, "Can't find metadata output file"
    assert len(mdfiles) == 1, "Extra metadata output files"

    ms2file = mgffiles1[0]

    print "Move %s to %s"%(ms2file,ms2spectra)
    shutil.move(ms2file,ms2spectra)

    if reporters:
        if opts.get('reporters'):
	    try:
                ms3scan2ms2scan = util.ms3scan2ms2scan(mdfiles[0])
                wh = open(reporters,"wb")
                for l in open(ms3file):
                    if l.startswith("TITLE"):
                        print >>wh, util.extract_reporters_from_TITLE(l,ms3scan2ms2scan)
                wh.close()
	    except:
		print >>sys.stdout, traceback.format_exc()
                open(reporters,"wb").close()
	else:
            open(reporters,"wb").close()

    if mdfile:
        print "Move %s to %s"%(mdfiles[0],mdfile)
        shutil.move(mdfiles[0],mdfile)

util.removefile(inputfile1)
util.timestamp("ReAdw4Mascot2 Finish")

