from dag4pkg import *
import re

dg = Dag4pkg()

def getdag(arg):
    rule_name = re.compile(".*name:.*")
    rule_deps = re.compile(".*deps:.*")

    bld = os.environ["ROOTSYS"]
    global count
    count = count + 1

    #Case when we are working with package modules
    if count == 1:
        with open(bld + "/" + arg + ".yml") as fl:
            fl_read = fl.read()
            name = rule_name.findall(fl_read)
            deps = rule_deps.findall(fl_read)
            fl.close()
    #Case when we are working with ouside module dependencies        
    else:
        path = PathChecker()
        directory = path.path4module(arg, ROOT_SOURCES)

        with open(directory + "/module.yml") as fl:
        	fl_read = fl.read()
            name = rule_name.findall(fl_read)
            deps = rule_deps.findall(fl_read)
            fl.close()

    parc_name = [x.lstrip(' name: ') for x in name]
    parc_dep = [x.lstrip(' deps: ') for x in deps]

    for i in range(len(parc_name)):
        if '"' in parc_name[i]:
            parc_name[i] = parc_name[i].replace('"','')

    #Create deplist once only,
    # we dont want to override it each time
    if count == 1:
        deplist = []

    #Adding multiple or single dependency to deplist
    for i in range(len(parc_dep)):
        if ";" in parc_dep[i]:
            z = parc_dep[i].split(";")
            deplist.append(z)
        else:
            deplist.append(parc_dep[i])
    
    #Remove default present deps
    for i in range(len(deplist)):
        if isinstance(deplist[i], str):
            if deplist[i] == "Core" or "RIO":
                if deplist[i] != "MathCore":
                    deplist[i] = deplist[i].replace("Core", "")
                    deplist[i] = deplist[i].replace("RIO", "")
        elif isinstance(deplist[i], list):
            for j in range(len(deplist[i])):
                if deplist[i][j] == "Core" or "RIO":
                    if deplist[i][j] != "MathCore":
                        deplist[i][j] = deplist[i][j].replace("Core", "")
                        deplist[i][j] = deplist[i][j].replace("RIO", "") 

    for item in deplist:
        if isinstance(item, list):
            for j in item:
                if '' in item:
                    item.remove('')
    
    #For package module names start at index 3 in parc_name list
    if count == 1:
        namelist = []
        for i in range(3, len(parc_name)):
            if parc_name[i] not in namelist:
                namelist.append(parc_name[i])
    #For modules just add the name
    else:
        for i in range(len(parc_name)):
            if parc_name[i] not in namelist:
                namelist.append(parc_name[i])
    
    #Create set once only, no overriding
    if count == 1:
        s = set()
    
    #Add namelist to set
    for i in range(len(namelist)):
        s.add(namelist[i])

    #Add deplist entities to set
    for item in deplist:
        if isinstance(item, str):
            s.add(item)
        elif isinstance(item, list):
            for val in item:
                s.add(val)
    
    #remove null values from set
    if '' in s:
        s.remove('')

# check if "name" or name is to be checked now and 
# proceed accordingly
    
    with open(bld + "/" + arg + ".yml") as ml:
    	mread = ml.read()
    for i in s:
        k = i
            #check if entity is present as module name 
            # that is with "" around the name.
        k = '"' + k + '"'
            #if not -> its a module outside the package,
            # get its path 
        if k not in mread:
            path = PathChecker()
            directory = path.path4module(str(i), ROOT_SOURCES)
        with open(directory + "/module.yml") as md:
            md_read = md.read()
            name = rule_name.findall(md_read)
            parc_name = [x.lstrip(' name: ') for x in name]
        #getdag(parc_name[0])
        getdag(parc_name[0])


    dt = {}

    for i in range(len(namelist)):
        dt[namelist[i]] = deplist[i]

    for item in s:
        dg.add_node_if_not_exists(item)

    for key, value in dt.items():
        if isinstance(value, list):
            for val in value:
                if val != '':
                    dg.add_edge(str(key), str(val))
        elif isinstance(value, str):
            if value != '':
                dg.add_edge(str(key), str(value))


    #print(dg.topological_sort())
