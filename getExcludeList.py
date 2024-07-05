import subprocess

LIBS_TO_KEEP = set(['pyqt5-tools', 'numpy', 'gdal', 'rasterio', 'torch'])

def check_deps(dep_list, keep_list, stage, deep=False):
    for i in dep_list:
        lib = i['package_name'].lower()
        if lib not in LIBS_TO_KEEP:
            keep_list[stage].append(lib)
            LIBS_TO_KEEP.add(lib)
            if deep:
                check_deps(i['dependencies'], stage)

# run pipdeptree util and capture output as string
result_shallow = subprocess.run(['pipdeptree', '--json'], capture_output=True, text=True)

# deep tree only shows libs with deep dependencies, so I opted to use only the shallow tree above
# result_deep = subprocess.run(['pipdeptree', '--json-tree'], capture_output=True, text=True)

# convert string to list of dicts
deptree_shallow = eval(result_shallow.stdout)
# deptree_deep = eval(result_deep.stdout)

# get list of all installed libs
toExclude = [i['package']['package_name'].lower() for i in deptree_shallow]

# add deps to keep list
keep_list, stage = [list(LIBS_TO_KEEP)], 1
while len(keep_list) == stage:
    for i in deptree_shallow:
        lib = i['package']['package_name'].lower()
        if (lib in keep_list[stage-1]) and (len(i['dependencies']) > 0):
            if len(keep_list) == stage:
                keep_list.append([])
            check_deps(i['dependencies'], keep_list, stage)
    stage += 1

toExclude = set(toExclude) - LIBS_TO_KEEP
print(list(toExclude))
