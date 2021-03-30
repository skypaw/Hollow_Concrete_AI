import subprocess

subprocess.call("abaqus cae noGUI=src\\readOdb.py", shell=True)


"""For creating dataset 

a = CreateModel(param)

for f in range(0,10,1):
    a.editParam(f)
    a.calculate

"""