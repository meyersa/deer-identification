# Deer Identification 

Utilizing data from trail cameras to train a CNN that can identify if a deer is present in the picture or not. 

# Setup 

Utilize the requirements file to install dependencies

> pip3 install -r requirements.txt 

# image_collection.py

Gather images for training

# image_procesing.py

Pre-process images for training. Takes in the /images folder and crops out the bottom border, reduces to a standard size, and removes duplicates.