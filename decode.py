# -*- coding: utf-8 -*-
import json
with open("main.log") as f:
    for line in f.readlines():
       #print(repr(line))
       l = json.loads(line)
       print(f"{l['user']['name']} --- {l['user']['id']} --- {l['prompt']} --- {l['choices'][0]['text']}")
       print()
       print("---------------------------------------------------------------------------------------------------")
       print()
#print(f"'{' '.join(sys.argv)}'")
#res = repr(f"'{' '.join(sys.argv)}'")
#print(res)
