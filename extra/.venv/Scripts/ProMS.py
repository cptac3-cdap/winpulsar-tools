
import sys, os, os.path, subprocess, shutil, glob
import util
def quote(s):
    return '"%s"'%(s,)

basedir = os.path.split(sys.argv[0])[0]
# ProMSbin = r"%s\ProMS\ProMS_old2.exe"%(os.path.split(sys.argv[0])[0],)

util.timestamp("ProMS Start")
print "Arguments:\n   ",
print "\n    ".join(sys.argv[1:])

inputfile = sys.argv[1]
psmfile = sys.argv[2]
outputfile = sys.argv[3]
inputfilename = sys.argv[4]
psmfilename = sys.argv[5]
opts = dict()
for a in sys.argv[5:]:
    opts[a] = True

ProMSdir = r"%s\ProMS"%(basedir,)
for d in glob.glob(r"%s\ProMS*"%(basedir,)):
    if opts.get(os.path.split(d)[1],False) and os.path.isdir(d):
	ProMSdir = d
	break

ProMSbin = "ProMS.exe"
for f in glob.glob(r"%s\ProMS*.exe"%(ProMSdir,)):
    if opts.get(os.path.split(f)[1],False):
	ProMSbin = f
	break

ParamFile = "ParametersForProMS.txt"
for f in glob.glob(r"%s\ParametersForProMS*.txt"%(ProMSdir,)):
    if opts.get(os.path.split(f)[1],False):
	ParamFile = f
	break

cwd = os.getcwd()

inputfilename = util.gettail(inputfilename)
inputbase = util.getbase(inputfilename)
inputfile1 = os.path.join(cwd,inputfilename)
util.movefile(inputfile,inputfile1)

psmfilename = util.gettail(psmfilename)
psmfile1 = os.path.join(cwd,psmfilename)
util.movefile(psmfile,psmfile1)

outputdir = os.path.split(outputfile)[0]

args = [ProMSbin]
tocopy = args + [ ParamFile, 'zlib1.dll'  ]
for f in tocopy:
    util.copyfile(os.path.join(ProMSdir,f),os.path.join(cwd,f))

wh = open('proms.ini','wb')
print >>wh, inputfilename
print >>wh, psmfilename
print >>wh, inputbase+'.proms.txt'
if opts.get("iTRAQ",False):
  print >>wh, "MSGF+ iTRAQ"
elif opts.get("TMT",False):
  print >>wh, "MSGF+ TMT"
else:
  print >>wh, "MSGF+"
for k in ("ORBI_HCD","ORBI","LTQ","QTOF"):
    if opts.get(k,False):
        print >>wh, k
print >>wh, "Peptide"
wh.close()

print "proms.ini:\n ","\n  ".join(open('proms.ini').read().splitlines())

print "Execute:"," ".join(args)
            
process = subprocess.Popen(args,
                           stdin=None,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           bufsize=1024)

while True:
    buf = process.stdout.read(1024)
    if not buf and process.poll() != None:
        break
    sys.stdout.write(buf)

print "\nStatus:",process.poll()

for f in glob.glob("*.txt"):
    if f.endswith('.proms.txt'):
	continue
    print "\nFile: %s"%f
    sys.stdout.write(open(f).read())

outputfile1 = os.path.join(cwd,inputbase+'.proms.txt')
print "Move %s to %s"%(outputfile1,outputfile)
util.movefile(outputfile1,outputfile)

util.removefile(inputfile1)
util.removefile(psmfile1)

util.timestamp("ProMS Finish")

