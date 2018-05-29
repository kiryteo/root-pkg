import os
import sys
from os.path import expanduser

arg = sys.argv[1]

home = expanduser("~")

dir = []
dir2 = []
pkg = []
paths = []
pkg2 = []
pt2 = []


currpath = home+"/"+arg+"/math/CMakeLists.txt"

with open(home+"/"+arg+"/math/CMakeLists.txt", 'r') as f:
    for line in f:
        if 'add_root_subdirectory' in line:
            line.strip("\n")
            data = line[line.find("(")+1:line.find(")")]
            dir.append(data)

x=0
for x in range(len(dir)):
    pkgs = dir[x].split(" ")
    pkg.append(pkgs)


for i in range(len(dir)):
    if pkg[i][1] == 'ALL':
        paths.append(home+"/"+arg+"/math/"+pkg[i][0])

for pt in paths:
    with open(pt+"/CMakeLists.txt", 'r') as t:
        for line in t:
            if 'ROOT_STANDARD_LIBRARY_PACKAGE' in line:
                pt2.append(pt)
                data2 = line[line.find("(")+1:line.find(")")]
                dir2.append(data2)

for x in range(len(dir2)):
    pkgs2 = dir2[x].split(" ")
    pkg2.append(pkgs2)

pkgnames = []

for i in range(len(pkg2)):
    pkgnames.append(pkg2[i][0])

for i in range (len(pkgnames)):
    print(pkgnames[i])
    print(" path: " + pt2[i] + "/")
