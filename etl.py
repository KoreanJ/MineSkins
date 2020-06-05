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

def get_skins(num_pages, url, search=''):
    """
    Purpose: Gather image links to all skins for a desired number of pages
    Params:
        num_pages - number of pages to scrape (will stop when max is reached)
        url - main website url
    Returns: list of image links
    """
    assert url != '', 'URL cannot be empty'
    assert int(num_pages) > 0, 'Cannot scrape negative or 0 pages'
    assert url[-1] == '/', 'URL must end with "/"'

    # clean data folder before downloading skins
    if os.path.exists('./data'):
        os.rename('./data', './data_del')
        shutil.rmtree('./data_del')
    os.mkdir('./data')

    # configure web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(executable_path=os.path.join('', 'drivers', 'chromedriver.exe'), options=options)
    
    # data to track
    img_links = []       # list of links already found
    tags = {}            # dictionary of image tags (img_num: [tags])
    img_num = 0          # image index
    
    # if search is enabled, perform search
    if search != '':
        driver_url = url + 'search/skin/' + search + '/'
    # else access homepage (top skins)
    else:
        driver_url = url

    # try to access main website and exit if error connecting
    try:
        req = r.get(driver_url)
    except:
        print('# Error connecting to', driver_url)
        exit()

    # grab profile links on each page
    cnt = 1
    for page_num in range(1, int(num_pages)+1):
        profile_soup = BeautifulSoup(r.get(driver_url+str(page_num)).text, 'html.parser')
        profile_links = [url[:-1]+x for x in get_profile_links(profile_soup)]
        
        # for each profile obtain image link
        
        for profile in profile_links:
            print('\nPage {0} Profile {1}: {2}'.format(page_num, cnt, profile))
            cnt += 1

            # get image tags
            try:
                driver.get(profile)
            except:
                print('>>> Error accessing profile (skipping this skin)')
                continue
            html = driver.page_source
            profile_soup = BeautifulSoup(html, 'html.parser')
            tags_div = profile_soup.find('div', {'class': 'se-tags hide-info'})
            if tags_div is None:
                print('\t# No tags division found')
                tags_found = []
            elif len(tags_div.find_all('a')) == 0:
                print('\t# No tags found')
                tags_found = []
            else:
                tags_found = [x.text for x in tags_div.find_all('a')]
            
            # get image link
            img_link_div = profile_soup.find('input', {'id': 'image-link-code'})
            if img_link_div is not None:
                img_link = img_link_div.get('value')
            else:
                print('\t# Unable to find image link')
                continue

            # add image link (with no duplicates)
            if img_link not in img_links:
                try:
                    req = Request(img_link, headers={'User-Agent': 'Mozilla/5.0'})
                    fname = str(img_num) + '.png'
                    new_img = open(fname, 'wb')
                    new_img.write(urlopen(req).read())
                    new_img.close()
                    shutil.move(fname, 'data/')
                except:
                    print('\t# Unable to download image from source: {0}'.format(img_link))
                    continue
                print('\tDownloaded Image {0}: SUCCESS!'.format(img_num+1))
                img_links.append(img_link)
                tags[img_num] = tags_found
                img_num += 1
            else:
                print('Image already in dataset')

    # dump tags into file and close web browser
    with open('tags.txt', 'w') as f:
        json.dump(tags, f)
    driver.close()

    print('Obtained {0} skins from {1}'.format(img_num, url))

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
    get_skins(kwargs['n_pages'], kwargs['url'], kwargs['search'])


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

def test_project():
    """
    Test the project using small subset of test data
    """
    print('Testing project')


