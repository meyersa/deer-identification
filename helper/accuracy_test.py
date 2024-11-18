import os 
import json 

IMAGE_JSON = os.path.join(os.getcwd(), "images.json")

with open(IMAGE_JSON, 'r') as f: 
    image_json = json.load(f)

num_correct = 0 
num_miss = 0 
num_deer = 0 

for image_dict in image_json.values(): 
    if not image_dict.get("newTags"): 
        continue

    deer = image_dict.get("newTags")[0]
    pred_deer = False

    for tag in image_dict.get("imageTags"): 
        if any(keyword in tag.get("name", "").lower() for keyword in ["deer", "buck", "doe"]):
            pred_deer = True 
            
    if deer == "deer": 
        num_deer += 1 

        if pred_deer: 
            num_correct += 1
            continue

        num_miss += 1
        continue

    if pred_deer: 
        num_miss += 1
        continue

    num_correct += 1

print(f'Num correct: {num_correct}')
print(f'Num miss: {num_miss}')
print(f'Accuracy: {num_correct / (num_correct + num_miss)}')
print(f'Num deer: {num_deer}')
