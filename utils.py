from pclib.shcmd import syncexec_generater as run
from pclib.shcmd import syncexec
import os,urlparse, errno
from collections import namedtuple
import shutil
from os.path import isdir,exists


_g = None
GlobalConfig=namedtuple("GlobalConfig",["prefix", "dest", "cachedir"])

def getcfg():
    global _g
    if not _g:
        _g=GlobalConfig(os.getenv("PREFIX",'/opt/portable/build'),
               "/opt/portable/source",
               "/opt/portable/cache")
    return _g



def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise



def extractfilename(url):
    return urlparse.urlsplit(url).path.split('/')[-1]

def fetchfromurl(url,targetdir, targetfilename=None):
    # extract file name
    if targetfilename:
        filename = targetfilename
    else:
        filename = extractfilename(url)

    # build full target binary path
    targetpath = os.path.join(targetdir,filename)

    r = run("wget --no-check-certificate -c {0} -O {1}".format(url,targetpath))
    for i in r:print(i)

    # return path
    return targetpath

def fetchfromgit(url,targetdir):
    r = None
    if exists(targetdir) and isdir(targetdir):
        cmd = "(cd {0} && git pull)".format(targetdir)
        r = syncexec(cmd)
        print(r)

    if not r:
        try:shutil.rmtree(targetdir)
        except:pass
        cmd = "git clone {0} {1}".format(url, targetdir)
        r = run(cmd)
        for i in r:print(i)
    return targetdir

def extractsrc(binary, parentdir):
    cmdmap = {
        ".tar.gz":"tar -xzf {0} -C {1}",
        ".tar.bz2":"tar -xjf {0} -C {1}",
        ".tar.xz":"tar -xJf {0} -C {1}",
        ".tgz":"tar -xzf {0} -C {1}",
        ".zip":"unzip {0} -d {1}",
        ".jar":"cp -f {0} {1}"
    }

    # return src dir
    dirname = ""
    for i in cmdmap.keys():
        l = binary.rfind(i)
        if  l!= -1:
            cmd = cmdmap[i]
            dirname = binary[:l]
            break
    else:
        raise Exception("can't extract file {0}".format(binary))
    r = run(cmd.format(binary,parentdir))
    for i in r:print(i)
    # might be wrong
    if binary.rfind(".jar") != -1: # jar
        return parentdir
    else:
        return os.path.join(parentdir,os.path.basename(dirname))

# [{name=xx,aa=bb,cc=dd},{},{}]
def parsefile(conf):
    ret = []
    d = {}
    with open(conf) as c:
        for rawline in c.readlines():
            l = rawline.strip()
            if l.find("#") == 0: #skip comments
                continue
            if l.find("[") == 0: #new item
                if len(l) < 3: # bad title
                    #log error
                    continue
                if d: ret.append(d)
                d = {}
                d["name"] = l[1:-1]
                continue
            item = l.split("=",1)
            if len(item) < 2: # bad item string
                # logerror
                continue
            d[item[0].strip()] = item[1].strip()
    if d: ret.append(d)
    return ret

# create env.sh under folder, which specify PATH and LD_LIBRARY_PATH
def generaterc(folder):
    f = r"""CURDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export PATH=$CURDIR/bin:$CURDIR/sbin:$PATH
if [ ! -z $LD_LIBRARY_PATH ]; then
    export LD_LIBRARY_PATH=$CURDIR/lib:$LD_LIBRARY_PATH
else
    export LD_LIBRARY_PATH=$CURDIR/lib
fi
"""
    with open(os.path.join(folder,"env.sh"),"w") as e:
        e.write(f)

# create env.sh under folder, which specify PATH and LD_LIBRARY_PATH
def generaterc_lite(folder):
    f = r"""CURDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export PATH=$CURDIR/bin:$PATH
"""
    with open(os.path.join(folder,"env.sh"),"w") as e:
        e.write(f)
