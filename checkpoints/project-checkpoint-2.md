# Project Checkpoint #2

<b>Project Name</b>: MineSkins <br>
<b>Author</b>: Nicholas Smith <br>
<b>Date</b>: April 26, 2020

### Project Update
Since the last submitted checkpoint, I have primarily focused on polishing my method of gathering Minecraft skins from the internet source and performing a basic analysis of the gathered data set. In checkpoint 1 I didn't have a solidified way to both gather links and download the images, but my project is now capable of running the data target as follows: `python run.py data`. This will gather links to all of the images on a desired number of pages from the source and then download each one into its own PNG file in the data folder. I'm currently working on a solution that includes sending this directory to the DataHub server so that I don't overwhelm the size of my project directory. <br>

In addition to the data target, I've also included a target for cleaning the project directory of all output files using the command `python run.py clean`. There are also a few new checks for correct targets so that if the user tries to run a random target, none of the included targets will be ran and the usage string will be printed out.

Finally, I have put more effort into studying this data set now that my method for obtaining the skins is more solid. Included in the repository are a few visualization that clearly display the distribution of skins in the obtained data set. This method of analysis was my first approach to understanding what sort of features I could use in the (soon to be implemented GANs).<br>

### Completed Tasks
* Moved Jupyter Notebook code into actual .py files
* Structured project directory based on template we studied in class
* Re-wrote method for gathering links and downloading images to be more organized and fluid
* Completed a few housekeeping items such as adding a `clean` target, automatically moving downloaded images to the proper folder, and creating a requirements.txt file inside my virtual environment
* Created configuration files


### Issues to Address
* Based on the template skin and sample skin layout, it seems that I won't be able to utilize a consistant method for gathering the skin data. For example, most of the limbs in my sample skin were comprised of the same pixel layout which meant that certain areas of the 64 x 64 skin were left white. Based on my crude method of randomly sampling other skins, it seems that the blank areas on a skin are intended for adding an overlay to any part of the body. Long hair or other clothing such as coats tend to be common overlays which can be seen in the right most parts of this example skin below.

<img src="https://www.minecraftskins.com/uploads/skins/2020/04/12/diamondtop111-14108874.png?v172" width="100" height="100" class="center">


