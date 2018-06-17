import os
import re

cwd = os.getcwd()

rootdir = cwd

rule1 = re.compile('.*name:.*')
rule2 = re.compile('.*deps:.*')
rule3 = re.compile('.*path:.*')


for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        if file.endswith(".yaml"):
            fp = os.path.join(subdir, file)
#           print(fp)
            with open(fp) as t:
                fl = t.read()
                r1 = rule1.findall(fl)
                r1 = [x.strip(' name: ') for x in r1 ]
                r2 = rule2.findall(fl)
                r3 = rule3.findall(fl)
                if r1:
                    fl2 = open("new.yml", 'a')
                    fl2.write(",".join(r1))
                    fl2.write(":")
                    fl2.write("\n")
                if r1:
                    fl2 = open("new.yml", 'a')
                    fl2.write(",".join(r2))
                    fl2.write("\n")
                if r1:
                    fl2 = open("new.yml", 'a')
                    fl2.write(",".join(r3))
                    fl2.write("\n")
