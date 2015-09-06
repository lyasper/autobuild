from utils import fetchfromurl,extractsrc,getcfg,parsefile,fetchfromgit
from pclib.shcmd import syncexec_generater as run
import os
from urlparse import urlparse
from os.path import basename


def getdefaults():
    return {
            "config":"./configure --prefix={PREFIX}",
            "build":"make && make install",
            "clean":"make clean"
        }

g = getcfg()

def buildpkg(conf, fake=False):
    pkglist = parsefile(conf)
    defaultcmds = getdefaults()
    # get default method from file
    for i in pkglist:
        if i.get("name","") == 'DEFAULT':
            for c in i.keys():
                defaultcmds[c] = i[c]
            pkglist.remove(i)
            break
    def getcmd(i, s):
        return i.get(s,defaultcmds.get(s,""))

    for i in pkglist:
        rawurl = getcmd(i,"url")
        cfg = getcmd(i,"config")
        bld = getcmd(i,"build")
        title = getcmd(i,"name")

        print "== build {0} ==".format(title)
        print rawurl
        print cfg.format(PREFIX=g.prefix)
        print bld.format(PREFIX=g.prefix)
        if fake:continue
        # incase downloaded compressed file has different name
        # as its content
        url_parts = rawurl.split(" ")
        if len(url_parts) > 1:
            url = url_parts[0]
            target = url_parts[1]
        else:
            url = rawurl
            target = None

        o = urlparse(url)
        if o.scheme == "git":
            gitsrcdir = basename(o.path) # xxx.git
            srcdir = fetchfromgit(url, os.path.join(g.dest, gitsrcdir))
        else:
            localfile = fetchfromurl(url, g.cachedir, target)
            srcdir = extractsrc(localfile, g.dest)



        os.chdir(srcdir)
        r = run(cfg.format(PREFIX=g.prefix))
        for i in r:print(i)
        r = run(bld.format(PREFIX=g.prefix))
        for i in r:print(i)


