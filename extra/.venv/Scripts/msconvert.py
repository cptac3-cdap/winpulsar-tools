
import sys, os, os.path, subprocess, shutil
import util

def quote(s):
    return '"%s"'%(s,)

util.timestamp("msconvert Start")
print "Arguments:\n   ",
print "\n    ".join(sys.argv[1:])

inputfile = sys.argv[1]
outputfile = sys.argv[2]
inputfilename = sys.argv[3]
outputextn = sys.argv[4]

opts = dict()
for a in sys.argv[5:]:
    opts[a] = True

directory = 'ProteoWizard'
for dir in ('ProteoWizard','pwiz-vc141-release-3_0_18320_db8142ed4'):
  if opts.get(dir,False):
    directory = dir
msconvertbin = r"%s\%s\msconvert.exe"%(os.path.split(sys.argv[0])[0],directory)

gzip = False
if outputextn.endswith('.gz'):
    gzip = True
    outputextn=outputextn.rsplit('.',1)[0]

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

outputdir = os.path.split(outputfile)[0]

args = [ msconvertbin,
            "--outdir",outputdir,
            "--outfile",inputbase+'.'+outputextn,
            "--%s"%(outputextn,),
            "--verbose",
            ]
if opts.get('centroid'):
    args.extend(["--filter",quote("peakPicking true 1-")])
if opts.get('zlib'):
    args.append('--zlib')
if gzip:
    args.append('--gzip')
args.append(inputfile1)

print "Execute:"," ".join(args)
            
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

outputfile1 = os.path.join(outputdir,inputbase+'.'+outputextn+('.gz' if gzip else ''))
print "Move %s to %s"%(outputfile1,outputfile)
shutil.move(outputfile1,outputfile)

util.removefile(inputfile1)

util.timestamp("msconvert Finish")



