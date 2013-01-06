appname = 'mutagion'
mac_files = ['main.app']
win_files = ['main.exe','library.zip','python26.dll','w9xpopen.exe']
ignore = ['logfile.txt','lastlog.txt','loghistory.txt','.DS_Store','.hg','.hgignore','.git','.svn','build','build.py']

import os
import shutil
import zipfile

def copy_file(a,b,type="mac"):
    print "copying file",a
    f = open(a,"rb")
    f2 = open(b,"wb")
    f2.write(f.read())
    f.close()
    f2.close()

def copy_folder(a,b,type="mac"):
    if not os.path.exists(b):
        os.mkdir(b)
    for f in os.listdir(a):
        next = a+"/"+f
        if next.startswith("./"):
            next = next[2:]
        if type=="mac" and next in mac_files and ".app" in next:
            shutil.copytree(next,b+"/"+f)
            continue
        if next in ignore:
            continue
        if next in [appname+"_mac.zip",appname+"_src.zip",appname+"_win.zip"]:
            continue
        if next in mac_files and type!='mac':
            continue
        if next in win_files and type!='win':
            continue
        if os.path.isdir(next):
            copy_folder(next,b+"/"+f,type)
        else:
            copy_file(next,b+"/"+f,type)

def remdir(d):
    for f in os.listdir(d):
        next = d+"/"+f
        if os.path.isdir(next):
            remdir(next)
        else:
            os.remove(next)
    try:
        os.rmdir(d)
    except:
        os.remove(d)
        
def makezip(z,path,start):
    zf = zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED)
    d = [path+"/"+start]
    while d:
        zf.write(d[0],d[0].replace(path,""))
        for f in os.listdir(d[0]):
            if os.path.isdir(d[0]+"/"+f):
                d.append(d[0]+"/"+f)
            else:
                zf.write(d[0]+"/"+f,(d[0]+"/"+f).replace(path,""))
        del d[0]

if os.path.exists("build"):
    remdir("build")
if not os.path.exists("build"):
    os.mkdir("build")
    os.mkdir("build/mac")
    os.mkdir("build/win")
    os.mkdir("build/src")
copy_folder(".","build/mac/"+appname,"mac")
makezip(appname+"_mac.zip","build/mac",appname)
copy_folder(".","build/win/"+appname,"win")
makezip(appname+"_win.zip","build/win",appname)
copy_folder(".","build/src/"+appname,"src")
makezip(appname+"_src.zip","build/src",appname)
