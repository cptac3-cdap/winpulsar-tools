
import sys, os, os.path, subprocess, shutil, zipfile
import util

def quote(s):
    return '"%s"'%(s,)

msconvertbin = r"%s\ProteoWizard\msconvert.exe"%(os.path.split(sys.argv[0])[0],)

util.timestamp("msconvertab Start")
print "Arguments:\n",
print "\n    ".join(sys.argv[1:])

inputfile = sys.argv[1]
inputscanfile = sys.argv[2]
outputfile = sys.argv[3]
inputfilename = sys.argv[4]
outputextn = sys.argv[5]

opts = dict()
for a in sys.argv[6:]:
    opts[a] = True

gzip = False
if outputextn.endswith('.gz'):
    gzip = True
    outputextn=outputextn.rsplit('.',1)[0]

inputdir = os.path.split(inputfile)[0]

inputbase,inputextn = inputfilename.rsplit('.',1)
if '/' in inputbase:
    inputpath,inputbase = inputbase.rsplit('/',1)

inputfile1 = os.path.join(inputdir,inputfilename)
util.movefile(inputfile,inputfile1)
util.movefile(inputscanfile,inputfile1+'.scan')

assert os.path.exists(inputfile1)
assert os.path.exists(inputfile1+'.scan')

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

util.timestamp("msconvertab Finish")

