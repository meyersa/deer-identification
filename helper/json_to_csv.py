import json 
import os 

IMAGE_JSON = os.path.join(os.getcwd(), "images.json")
IMAGE_CSV = os.path.join(os.getcwd(), 'images.csv')
IMAGE_PROCESSED_DIR = os.getenv("IMAGE_PROCESSED_DIR", "processed-images")

with open(IMAGE_JSON, 'r') as i, open(IMAGE_CSV, 'w') as o:
    i = json.load(i)

    for line in i.values(): 
        deer_tag = line.get("newTags")

        # Skip if bad
        if not deer_tag or deer_tag == "bad": 
            continue
        
        else: 
            deer_tag = deer_tag[0]
            
        o_line = list() 
        o_line.append(os.path.join(IMAGE_PROCESSED_DIR, line.get("fullFilename")))
        o_line.append(deer_tag)
        o_line.append(line.get("createdDateTime"))
        o_line.append(line.get("moonPhase"))
        o_line.append(line.get("pressure"))
        o_line.append(line.get("pressureTendency"))
        o_line.append(line.get("temperature"))
        o_line.append(line.get("wind"))
        o_line.append(line.get("windDirection"))

        o_line = [str(l) for l in o_line]

        o.writelines(",".join(o_line) + "\n")
