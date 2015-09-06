import os
from utils import getcfg, mkdir_p,generaterc,generaterc_lite
from buildsrc import buildpkg


def cleanup():
    # rm -rf g.cachedir/*
    # rm -rf g.dest/*
    pass

def work() :
    g = getcfg()
    mkdir_p(g.dest)
    mkdir_p(g.cachedir)
    os.environ["LD_LIBRARY_PATH"]=os.path.join(g.prefix,"lib")
    try:
        oldcwd = os.getcwd()
        #buildpkg("util.install",False)
        buildpkg("simple_local.install")
        #generaterc(g.prefix)
        generaterc_lite(g.prefix)
    except:
        raise
    finally:
        os.chdir(oldcwd)

if __name__ == "__main__":
    work()
    cleanup()
