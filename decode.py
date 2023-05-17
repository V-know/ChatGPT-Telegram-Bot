# -*- coding: utf-8 -*-
import json

with open("main.log") as f:
    i = 1
    for line in f.readlines():
        try:
            l = json.loads(line)
            result = l['choices'][0].get('text') if l['choices'][0].get('text') else l['choices'][0]['message']['content']
            print(f"{l['user']['name']} --- {l['user']['id']} --- {l['prompt']} --- {result}")
            print()
            print(i, "---------------------------------------------------------------------------------------------------")
            print()
            i+=1
        except (json.decoder.JSONDecodeError, KeyError):
            continue
