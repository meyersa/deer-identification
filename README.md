# Deer Identification 

Utilizing data from trail cameras to train a CNN that can identify if a deer is present in the picture or not. 

With the conditions of something like a trail camera that has poor quality and low light levels, using context clues like the time, wind, temperature, and moon should be usable to better identify deer in pictures. 

# Setup 

Utilize the requirements file to install dependencies

> pip3 install -r requirements.txt 

# image_collection.py

Gather images for training

# image_procesing.py

Pre-process images for training. Takes in the /images folder and crops out the bottom border, reduces to a standard size, ~~and removes duplicates~~.

# train.ipynb

Notebook for training models 

# Macos 

This is optimized for Mac since it is the platform this was developed on. When you install requirements, MacOS w/ apple silicon packages are installed - like tensorflow-metal and tensorflow-macos. 

You will also need to install TKinter since it is not installed by default 

```Shell
brew install python-tk
```
