# imports
import requests as r
import shutil
import time
import os
import numpy as np
import json
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from skimage import io
from matplotlib import pyplot as plt
from selenium import webdriver
import time
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

    # configure web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(executable_path="C:\\Windows\\chromedriver.exe", options=options)
    
    # data
    img_links = []
    tags = {}

    # index for tracking meta data
    i = 0
    
    # connect to website
    req = r.get(url)
    if req.ok == False:
        print('# Error connecting to', url)
        return
    soup = BeautifulSoup(req.text, 'lxml')

    # grab profile links on each page
    for i in range(1, int(num_pages)+1):
        profile_links = [url[:-1]+x for x in get_profile_links(BeautifulSoup(r.get(url+str(i)).text, 'html.parser'))]
        
        # for each profile obtain image link
        for profile in profile_links:

            # get image tags
            print(profile)
            driver.get(profile)
            html = driver.page_source
            time.sleep(2)
            tag_soup = BeautifulSoup(html, 'html.parser')
            tags_div = tag_soup.find('div', {'class': 'se-tags hide-info'})
            if tags_div is None:
                print('Unable to locate tags division')
                tags[i] = []
            elif tags_div.find_all('a') is None:
                print('Unable to find any tags')
                tags[i] = []
            else:
                tags[i] = [x.text for x in tags_div.find_all('a')]
            i += 1

            # get image link
            req = r.get(profile)
            if req.ok == False:
                print('# Error accessing the following url:', profile)
                continue
            
            # parse out image link
            soup = BeautifulSoup(req.text, 'html.parser')
            img_link = soup.find('input', {'id': 'image-link-code'}).get('value')
            if img_link is None:
                print('# Error obtaining image from profile')
                continue
            img_links.append(img_link)
            time.sleep(1)
        
    # dump tags into file and close web browser
    with open('tags.txt', 'w') as f:
        json.dump(tags, f)
    driver.close()

    return img_links, tags

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

def get_stats_variance(body_part):
    """
    Purpose: Compute the variance of each image or piece of image
    Params:
        body_part - the skin's body part to analyze (face, torso, full, etc.)
    Returns: List of variances values across all images in data
    """
    assert body_part in C.SUPPORTED_BODY_PARTS, 'Unrecognized body part'

    fnames = os.listdir('./data')
    variance = []
    for f in fnames:
        if body_part == 'face':
            variance.append(np.var(get_face(f)))
        elif body_part == 'torso':
            variance.append(np.var(get_torso(f)))

    return variance


###################################################################################################


### Main Functions ###
def get_data(**kwargs):
    """
    Purpose: Scrape skin image links from configured URL and download images into data folder
    Params:
        **kwargs - parameters passed from data-config.json
    """
    print('Gathering image links...', end='')
    img_links, tags = get_img_links(kwargs['n_pages'], kwargs['url'])
    print(tags)
    print('Done')
    print('Downloading images...', end='')
    #download_images(img_links)
    print('Done')
    print('{0} skins downloaded from {1}'.format(len(img_links), kwargs['url']))


def get_stats():
    """
    Purpose: Gather statistics for the image dataset
    """
    if os.path.exists('./data') == False or len(os.listdir('data')) == 0:
        print('Error - Data directory cannot be empty')
        return

    # get states across all images
    stats = {}
    stats['brightness'] = get_stats_brightness('face')
    stats['variance'] = get_stats_variance('face')

    # get saturation for each image
    #stats['saturation'] = get_stats_saturation()

    # print('Brightness Distribution')
    # print('-'*100, '\n', stats['brightness'])

    plt.hist(stats['variance'], color='green', density=True)
    plt.title('Variance Distribution')
    plt.xlabel('Variance')
    plt.ylabel('Density')
    plt.show()


