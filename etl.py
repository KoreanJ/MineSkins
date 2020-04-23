# imports
import requests as r
from bs4 import BeautifulSoup
import time

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
    assert num_pages <= 50, 'Maximum number of pages to scrape is 50'
    assert url != '', 'URL cannot be empty'
    assert num_pages > 0, 'Cannot scrape negative or 0 pages'
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
    for i in range(1, num_pages+1):
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

###########################################################################################################

# Main method to gather data
def get_data(**kwargs):
    img_links = get_img_links(kwargs['n_pages'], kwargs['url'])
    print('{0} image links obtained.'.format(len(img_links)))


