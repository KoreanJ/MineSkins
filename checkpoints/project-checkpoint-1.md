# Project Checkpoint #1

<b>Group Name</b>:  MineSkins <br>
<b>Author</b>:      Nicholas Smith <br>
<b>Date</b>:        April 12, 2020

### About the Data
After searching across several publicly available websites for easily scrapable Minecraft skins, I settled on https://www.minecraftskins.com (The Skindex). This site provides an easy link to find using traditional HTML parsing methods in addition to thousands of downloadable skins. At first, I experienced a bit of trouble as all of my requests were being blocked despite robots.txt not explicitly saying that requests are prohibited. With a bit of help from the internet, the solution was to create a request object that include meta data for making my request look like a user agent - specifically Mozilla Firefox. This way I was able to quickly scrape and download skins from the website for analysis.

Using a single sample skin, I found the image to be of the following dimensions: 64 x 64 x 4 meaning that each pixels has four color channels. Using a quick call to <b>imshow</b> allowed me to confirm that all of the skin's data had been perfectly copied over. 

### Completed Tasks
* Solve issue with being forbidden from downloading skins via requests
* Print out skin to make sure all of the data had been copied over correctly
* Understand the data's dimensions


### Issues to Address
* Based on the template skin and sample skin layout, it seems that I won't be able to utilize a consistant method for gathering the skin data. For example, most of the limbs in my sample skin were comprised of the same pixel layout which meant that certain areas of the 64 x 64 skin were left white. Based on my crude method of randomly sampling other skins, it seems that the blank areas on a skin are intended for adding an overlay to any part of the body. Long hair or other clothing such as coats tend to be common overlays which can be seen in the right most parts of this example skin below.

<img src="https://www.minecraftskins.com/uploads/skins/2020/04/12/diamondtop111-14108874.png?v172" width="100" height="100" class="center">


