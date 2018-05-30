import os
import sys
from os.path import expanduser

arg1 = sys.argv[1]
arg2 = sys.argv[2]

home = expanduser("~")

dir = []
dir2 = []
pkg = []
paths = []
pkg2 = []
pt2 = []


currpath = home+"/"+arg1+"/"+arg2+"/CMakeLists.txt"

with open(home+"/"+arg1+"/"+arg2+"/CMakeLists.txt", 'r') as f:
    for line in f:
        if 'add_root_subdirectory' in line:
            line.strip("\n")
            data = line[line.find("(")+1:line.find(")")]
            dir.append(data)

#print(dir[0])
x=0
for x in range(len(dir)):
    pkgs = dir[x].split(" ")
#    print(pkgs)
    pkg.append(pkgs)

#print(pkg[0][0])

for i in range(len(dir)):
    if pkg[i][1] == 'ALL':
        paths.append(home+"/"+arg1+"/"+arg2+"/"+pkg[i][0])
#'BASE' are already present

#print(paths[0])

for pt in paths:
    with open(pt+"/CMakeLists.txt", 'r') as t:
        for line in t:
            #print(line)
            if 'ROOT_STANDARD_LIBRARY_PACKAGE' in line:
    #            line.strip("\n")
    #            line.split("\t")
    #            line = line.replace('\n','')
    #            line = line.replace('\t','')
    #            line = line.replace('\t','')
    #            line = line.replace('\t','')
    #            line = line.replace('\t','')
    #            line = line.replace('\t','')
    #            line = line.replace('\t','')
    #            line = line.replace('\t','')
                #print(line)
                pt2.append(pt)
                data2 = line[line.find("(")+1:line.find(")")]
                dir2.append(data2)

for x in range(len(dir2)):
    pkgs2 = dir2[x].split(" ")
#    print(pkgs)
    pkg2.append(pkgs2)
#print(dir2[0][0])
pkgnames = []

for i in range(len(pkg2)):
    pkgnames.append(pkg2[i][0])
#print(pkg2[0][0])
#print(dir2)
#print(pt2)

#print(pkgnames)
for i in range (len(pkgnames)):
    print(pkgnames[i])
    print(" path: " + pt2[i] + "/")

dt3 = []

for pt in paths:
    with open(pt+"/CMakeLists.txt", 'r') as t:
        for line in t:
            line.lstrip()
            #print(line)
            if 'ROOT_STANDARD_LIBRARY_PACKAGE' in line:
            #    line.lstrip()
            #    print(line)
                if 'DEPENDENCIES' in line:
                    line.replace('\n','')
                    dt3.append(line)

#nt = []

#for i in range (len(dt3)):
#    k = dt3[i]
#    print(k)
#    op = k[k.find("DEPENDENCIES"):k.find(")")]# or k.find("DEPENDENCIES")+1:k.find("DICTIONARY_OPTIONS")]
#    nt.append(op)

#for i in range (len(nt)):
#    z = nt[i]
#    if 'DICTIONARY_OPTIONS' in z:


#print(dt3)
#print(nt)
