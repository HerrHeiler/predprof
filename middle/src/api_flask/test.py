import json
set1 = {1: [[False], [True], [False, True, False, True], [False, False]],
        2: [[True], [True], [False, False, False, False], [False, False]],
        3: [[False], [False], [True, False, True, True], [True, True]],
        4: [[True], [True], [False, True, False, False], [False, False]]
        }
set1_string = json.dumps(set1, separators=(",",":"))
print(json.loads(set1_string))
