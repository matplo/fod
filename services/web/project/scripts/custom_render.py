# custom_render.py

from bs4 import BeautifulSoup

def add_img_classes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for img_tag in soup.find_all('img'):
        img_tag['class'] = img_tag.get('class', []) + ['img-fluid']
    return str(soup)

def custom_render(html_content):
	h0 = add_img_classes(html_content)
	# ... can do more
	return h0
