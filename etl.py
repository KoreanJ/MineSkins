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
from skimage.color import *
from matplotlib import pyplot as plt
from selenium import webdriver
import pandas as pd
import time

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

def process_tags(N=10):
    """
    Purpose: Process raw tags to select only the most popular one based on total count and assign new single tag
    Params:
        N - use top N popular tags to assign class label for each image (default to 10)
    Returns:
        Dataframe of each image name with most popular tag and assigned class
        Dataframe of each tag and its count
    """
    
    # read tag data
    fp = os.path.join('.', 'tags.txt')
    with open(fp) as f:
        tags_dict = json.load(f)

    # raw list of tags
    tags = []
    for key, item in tags_dict.items():
        if len(item) > 0:
            tags += item

    # get counts of each tag
    tag_counts_full = {
        'tag': []
        , 'cnt': []
    }
    for t1 in tags:
        if t1 in tag_counts_full['tag']:
            continue
        cnt = 0
        for t2 in tags:
            if t1.lower() == t2.lower():
                cnt += 1
        tag_counts_full['tag'].append(t1)
        tag_counts_full['cnt'].append(cnt)
        
    # create dataframe and sort by most popular
    tags_df = pd.DataFrame(tag_counts_full)
    tags_df = tags_df.sort_values(by='cnt', ascending=False).reset_index(drop=True)
    
    # select only the most popular tag for each image
    single_tags = {
    'img_num': [],
    'popular_tag': []
    }
    for fname, tags in tags_dict.items():
        if len(tags) == 0:
            single_tags['img_num'].append(fname)
            single_tags['popular_tag'].append('no_tags')
            continue

        # find most popular tag and use that
        max_tag = tags[0]
        max_val = tags_df[tags_df['tag'] == max_tag]['cnt'].values[0]
        for t in tags:
            val = tags_df[tags_df['tag'] == t]['cnt'].values[0] 
            if val > max_val:
                max_tag = t
                max_val = val
        single_tags['img_num'].append(fname)
        single_tags['popular_tag'].append(max_tag)
        
    # use top N popular tags to assign class label for each image
    class_labels = pd.DataFrame(single_tags)
    top_classes = list(tags_df.loc[:N-1, 'tag'].values)
    def get_class(x):
        if x in top_classes or x == 'no_tags':
            return x
        return 'other'
    class_labels['class'] = class_labels['popular_tag'].apply(get_class)

    # map each class to target number (for cluster colors). no_tags = 10 and other = 11
    target_mapping = {}
    labels = list(class_labels[~class_labels['class'].isin(['no_tags', 'other'])].groupby('class').count().index)
    for i in range(len(labels)):
        target_mapping[labels[i]] = i
    target_mapping['no_tags'] = i+1
    target_mapping['other'] = i+2
    class_labels['target'] = class_labels['class'].apply(lambda x: target_mapping[x])

    
    # return tag counts and assigned class labels
    return tags_df, class_labels


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

def save_previews(read_path):
    """
    Purpose: For each skin saved in the data directory, parse out the front facing view (face, torso, arms, and legs) and save
    as a new PNG file.
    Params:
        read_path - string represententing the path where data is to be read from
    Returns: None
    """
    write_path = read_path + '_previews'

    # create directory for storing previews
    if os.path.exists(write_path):
        os.rename(write_path, write_path + '_del')
        shutil.rmtree(write_path + '_del')
    os.mkdir(write_path)

    # create spacers
    template = io.imread('./front-view-template.png')
    spacer = template[:8, 20:23, :]
    spacer_big = template[:12, 20:23, :]
    
    read_path += '/'
    write_path += '/'
    for i in range(len(os.listdir(read_path))):
        img = io.imread(read_path+str(i)+'.png')
        
        # parse out body parts
        head = img[8:16,8:16,:]
        torso = img[20:32, 20:28,:]
        left_leg = img[52:, 20:24, :]
        right_leg = img[20:32, 4:8, :]
        left_arm = img[52:, 36:39, :]
        right_arm = img[20:32, 44:47, :]
        
        # creat front view and save
        left = np.vstack((np.vstack((spacer, right_arm)), spacer_big))
        middle = np.vstack((np.vstack((head, torso)), np.hstack((right_leg, left_leg))))
        right = np.vstack((np.vstack((spacer, left_arm)), spacer_big))
        full = np.hstack((np.hstack((left, middle)), right))
        io.imsave(write_path+str(i)+'-preview.png', full)

def test_project():
    """
    Using the small test dataset, perform some basic tag analysis and produce a few visuals.
    """
    print('Testing project')

    # process tags and save to csv files
    counts, class_labels = process_tags()
    counts.to_csv('./out/tag-counts.csv', index=False)
    class_labels.to_csv('./out/tag-data.csv', index=False)

    # create bar charts of top 20 tags
    plt.figure(figsize=(20,8))
    plt.bar(counts.iloc[:20, 0], counts.iloc[:20, 1], color='teal')
    plt.title('Top 20 Most Common Tags on Minecraft Skins')
    plt.xlabel('Tag')
    plt.ylabel('Count')
    plt.savefig('./out/top-20-tags-barchart.png')

    # histogram of mean hue
    hue = []
    for i in range(len(os.listdir('./test_data'))):
        img = io.imread('./test_data/'+str(i)+'.png')
        hsv = rgb2hsv(img[:, :, :-1])
        mean_hue = np.mean(hsv[:, :, 0])
        hue.append(mean_hue)
    plt.figure(figsize=(14, 10))
    plt.hist(hue, bins=30, color='teal', density=False)
    plt.title('Distribution of All Skin\'s Mean Hue')
    plt.xlabel('Mean Hue')
    plt.savefig('./out/hue-histogram.png')

    # create front view images for each skin in test dataset
    save_previews('./test_data')

