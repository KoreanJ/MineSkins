def get_skin_links(page_html):
    img_links = [x.find('a').get('href') for x in page_html.find_all('div', {'class': 'skin-img'})]
    return img_links


# imports
import requests as r
from bs4 import BeautifulSoup
import time

# connect to website
url = 'https://www.minecraftskins.com/'
req = r.get(url)
if req.ok:
    print('Successfully connected to', url)
else:
    print('Error connecting to', url)

# create parser for website
links = []
soup = BeautifulSoup(req.text, 'lxml')

# determine total number of pages
page_cnt = int(soup.find('div', {'class': 'pagination'}).find_all('li')[-2].text.strip())

# grab skins on each page
for i in range(1, page_cnt+1):
    links += get_skin_links(BeautifulSoup(r.get(url+str(i)).text, 'lxml'))
    time.sleep(2)

# show that links were gathered
print(links)

