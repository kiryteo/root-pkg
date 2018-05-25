
import os
import sys
from os.path import expanduser

arg = sys.argv[1]

home = expanduser("~")

dir = []
dir2 = []

currpath = home+"/"+arg+"/math/CMakeLists.txt"

with open(home+"/"+arg+"/math/CMakeLists.txt", 'r') as f:
    for line in f:
        if 'add_root_subdirectory' in line:
            line.strip("\n")
            data = line[line.find("(")+1:line.find(")")]
            dir.append(data)

pkg = []
paths = []

x=0
for x in range(len(dir)):
    pkgs = dir[x].split(" ")
#    print(pkgs)
    pkg.append(pkgs)

#print(pkgs)


for i in range(len(dir)):
    if pkg[i][1] == 'ALL':
        paths.append(home+"/"+arg+"/math/"+pkg[i][0])

#print(paths)

for pt in paths:
    with open(pt+"/CMakeLists.txt", 'r') as t:
        for line in t:
            if 'ROOT_STANDARD_LIBRARY_PACKAGE' in line:
                line.strip("\n")
                data2 = line[line.find("(")+1:line.find(" ")]
                dir2.append(data2)

#print(dir2)

#with open('math.yml', 'w') as f:
#    print
fl = open('math.txt','w')
print(dir2, file=fl)
