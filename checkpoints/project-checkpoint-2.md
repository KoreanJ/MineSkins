# Project Checkpoint #2

<b>Project Name</b>: MineSkins <br>
<b>Author</b>: Nicholas Smith <br>
<b>Date</b>: April 26, 2020

### Tasks for Week 4 (from backlog)
* Perform basic statistics on images and implement into functions
    - DONE
* Start cleaning the skins (i.e. removing bad data and filtering out poor quality skins)
    - IN PROGRESS
* If time allows, setup first instance of GAN and start playing around with it
    - NOT STARTED

### Completed tasks for Week 4 (not from backlog)
* Created new target, `data`
* Created new target, `clean`
* Created several helper functions in `etl.py` for gathering data and performing statistics
* Included requirements.txt for working in a virtual environment (had issues with packages after moving from Mac to Windows)
* Re-structured method of gathering skins. Now runs completely using `data` target
* Added configuration file for gathering data 

### Update since checkpoint 1
Since the last submitted checkpoint, I have primarily focused on 2 areas: data acquisition and EDA. By the first checkpoint I was able to gather a handful of Minecraft skins from the internet, but there was no solidified way of doing this via a command line. Everything was manually being moved around and renamed. To improve this, I implemented the `data` target which does the following: gathers a list of links to Minecraft skins (based on number of desired web pages configured in data-config.json), read those images into local files, renames them, and moves them to the appropriate directory. <br>

In addition to the new data target, I've also implemented a `clean` target for removing output files. No incorrect targets are allowed to be called as my program checks for that and outputs the usage if needed.

### Quality of data
Each skin has a shape of (64, 64, 4) where the 4 dimensions of each pixel represent R, G, B, and an indicator variable. This was determined empirically since it wasn't clear from the beginning. Minecraft does not provide a thorough explanation of why these use 4 dimensions for each pixel, so I was tasked with figuring this out myself. At first glance I noticed that all of the important pixels (ones that were not empty space and actually pertained to the unwrapped skin) had a 4th dimension value of 255. Since each skin contains a bit of empty space between unwrapped limbs, I checked and confirmed that those empty pixels had a 4th dimension value of 0. This led me to believe that pixels with a 4th dimension value of 255 were truly part of the skin whereas those with 0 were the filler space in between limbs. <br>

### Data cleaning for GAN
After thinking about the image features that may hinder my results, I developed a very simple method of filtering out "bad" skins. Since I want to make sure that the skins have actual features and are not simply comprised of a single color, I've empirically determined a variance cutoff and use that in filtering down the dataset.

### Completed Tasks
* Moved Jupyter Notebook code into actual .py files
* Structured project directory based on template we studied in class
* Re-wrote method for gathering links and downloading images to be more organized and fluid
* Completed a few housekeeping items such as adding a `clean` target, automatically moving downloaded images to the proper folder, and creating a requirements.txt file inside my virtual environment
* Created configuration files
* Tested images with and without the 4th dimension in order to understand its purpose


### Issues to Address
* 

<img src="https://www.minecraftskins.com/uploads/skins/2020/04/12/diamondtop111-14108874.png?v172" width="100" height="100" class="center">


