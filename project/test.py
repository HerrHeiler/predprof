import json, os, shutil

pp = {
    1 : [23, 4], 
    2 : [33, 0]}
pp1 = (json.dumps(pp, separators=(",", " ")))
# print(json.load(pp1)) 
# pp = {
#     1 :      [23, 4], 
#     2 : [33, 0    ]    }
# pp1 = (json.dumps(pp, separators=(",", " ")))
# print(json.load(pp1)) 
# pp = {
#     1 : [23, 4]}
# pp[2] = [33, 0]
# pp1 = (json.dumps(pp, separators=(",", " ")))
# print(json.load(pp1)) 
pp = {
    1 : [23, 4], 
    2 : [33, 0]}
pp1 = (json.dumps(pp, separators=(",", ":")))
print(dict(json.loads(pp1))) 
# pp1 = ("db" in os.listdir("./"))
# shutil.rmtree("./db")
