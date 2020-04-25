# imports
import requests as r
import shutil
import time
import os
import numpy as np
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from skimage import io
from matplotlib import pyplot as plt
import constants as C

### Helper Functions ###
def get_profile_links(page_html):
    """
    Purpose: Get links to each skin's profile on a single page
    Params:
        page_html - the raw html page
    Returns: list of profile links for that page
    """
    profile_links = [x.find('a').get('href') for x in page_html.find_all('div', {'class': 'skin-img'})]
    return profile_links

def get_img_links(num_pages, url):
    """
    Purpose: Gather image links to all skins for a desired number of pages
    Params:
        num_pages - number of pages to scrape (will stop when max is reached)
        url - main website url
    Returns: list of image links
    """
    assert int(num_pages) <= 50, 'Maximum number of pages to scrape is 50'
    assert url != '', 'URL cannot be empty'
    assert int(num_pages) > 0, 'Cannot scrape negative or 0 pages'
    assert url[-1] == '/', 'URL must end with "/"'
    
    # data structure for skin images
    img_links = []
    
    # connect to website
    req = r.get(url)
    if req.ok == False:
        print('# Error connecting to', url)
        return
    soup = BeautifulSoup(req.text, 'lxml')

    # grab profile links on each page
    for i in range(1, int(num_pages)+1):
        profile_links = [url[:-1]+x for x in get_profile_links(BeautifulSoup(r.get(url+str(i)).text, 'lxml'))]
        
        # for each profile obtain image link
        for profile in profile_links:
            req = r.get(profile)
            if req.ok == False:
                print('# Error accessing the following url:', profile)
                continue
            
            # parse out image link
            soup = BeautifulSoup(req.text, 'lxml')
            img_link = soup.find('input', {'id': 'image-link-code'}).get('value')
            if img_link is None:
                print('# Error obtaining image from profile')
                continue
            img_links.append(img_link)
            time.sleep(1)
        
    return img_links

def download_images(img_links):
    """
    Purpose: Download images from website into binary files (rendered as images)
    Params:
        img_links - list of links to skins
    Returns: None
    """

    # clean data folder before downloading skins
    if os.path.exists('./data'):
        os.rename('./data', './data_del')
        shutil.rmtree('./data_del')
    os.mkdir('./data')

    # write data from image into new files
    i = 0
    for l in img_links:
        req = Request(l, headers={'User-Agent': 'Mozilla/5.0'})
        fname = str(i) + '.png'
        new_img = open(fname, 'wb')
        new_img.write(urlopen(req).read())
        new_img.close()
        shutil.move(fname, 'data/')
        i += 1
        time.sleep(1)

def get_face(fname):
    img = io.imread('data/'+fname)
    FR = C.FACE_RANGE
    return img[FR[0][0]:FR[0][1], FR[1][0]:FR[1][1], :]

def get_torso(fname):
    img = io.imread('data/'+fname)
    TR = C.TORSO_RANGE
    return img[TR[0][0]:TR[0][1], TR[1][0]:TR[1][1], :]

def get_stats_brightness(body_part):
    """
    Purpose: Compute the mean brightness of each image or piece of image
    Params:
        body_part - the skin's body part to analyze (face, torso, full, etc.)
    Returns: List of mean brightness across all images in data
    """
    assert body_part in C.SUPPORTED_BODY_PARTS, 'Unrecognized body part'


    fnames = os.listdir('./data')
    brightness = []
    for f in fnames:
        if body_part == 'face':
            brightness.append(np.mean(get_face(f)))
        elif body_part == 'torso':
            brightness.append(np.mean(get_torso(f)))

    return brightness




###################################################################################################


### Main Functions ###
def get_data(**kwargs):
    """
    Purpose: Scrape skin image links from configured URL and download images into data folder
    Params:
        **kwargs - parameters passed from data-config.json
    """
    print('Gathering image links...', end='')
    img_links = get_img_links(kwargs['n_pages'], kwargs['url'])
    print('Done')
    print('Downloading images...', end='')
    download_images(img_links)
    print('Done')
    print('{0} skins downloaded from {1}'.format(len(img_links), kwargs['url']))


def get_stats():
    """
    Purpose: Gather statistics for the image dataset
    """
    if os.path.exists('./data') == False or len(os.listdir('data')) == 0:
        print('Error - Data directory cannot be empty')
        return

    stats = {}
    # get brightness for each image
    stats['brightness'] = get_stats_brightness('face')

    # get saturation for each image
    #stats['saturation'] = get_stats_saturation()

    print('Brightness Distribution\n', '-'*80, '\n', stats['brightness'])

    plt.hist(stats['brightness'])
    plt.show()


