
import os
from os.path import expanduser

home = expanduser("~")

#with open(home+"/root/CMakeLists.txt", newline='') as f:
    #for line in f:
        #line = str(line)
#    content = f.readlines()
#    content = [x.strip('\n') for x in content]
#    print (content)
    #    """if line == "add_root_subdirectory(core BASE)":
    #        print ("ab")
        #print (line)"""

dir = []

with open(home+"/root/CMakeLists.txt", 'r') as f:
    for line in f:
        if 'add_root_subdirectory' in line:
            line.strip("\n")
            data = line[line.find("(")+1:line.find(")")]
            dir.append(data)

#print(dir)
pkg = []
paths = []

x=0
for x in range(len(dir)):
    pkgs = dir[x].split(" ")
    #print(pkgs)
    pkg.append(pkgs)


for i in range(len(dir)):
    if pkg[i][1] == 'BASE' or 'ALL':
        paths.append(home+"/root/"+pkg[i][0])

print(paths)

#for root, dirs, files in os.walk(home+"/root"):
    #print (root)#root, dirs#, files
#    if
