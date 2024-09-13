import requests
import xml.etree.ElementTree as ET
import re


class Article:
    def __init__(self):
        # Access to Wikipedia API
        self.wikipedia_url = "https://en.wikipedia.org/w/api.php?format=json"

        # Access info of randomly generated article
        self.random_url = ("&action=query&generator=random&grnnamespace=0&prop=revisions|images&"
                           "rvprop=content&grnlimit=1&piprop=original")

        # Initialized variables
        self.title = None
        self.page_id = None

        # Initialized variables for XML response
        self.for_image = None
        self.xml_response = None
        self.root = None
        self.namespace = {'ns': 'http://opensearch.org/searchsuggest2'}
        self.items = None
        self.image = None
        self.image_url = None
        self.high_res_url = None

        # Initialized variable to store total views
        self.total = 0

    def generate_article(self):
        # Retrieve the info
        response = requests.get(self.wikipedia_url + self.random_url).json()

        # Get the page id
        for key in response['query']['pages']:
            self.page_id = key

        # Generate new article if it does not have any images
        while 'images' not in response['query']['pages'][self.page_id]:
            response = requests.get(self.wikipedia_url + self.random_url).json()
            for key in response['query']['pages']:
                self.page_id = key
            print(response)

        # Retrieve the article's title
        self.title = response['query']['pages'][self.page_id]['title']

    # Retrieve the article's image
    def get_image(self):
        # URL for retrieving image from Wikipedia API
        self.for_image = (f"http://en.wikipedia.org/w/api.php?action=opensearch"
                          f"&limit=5&format=xml&search={self.title}&namespace=0")

        # Retrieving and parsing XML response
        self.xml_response = requests.get(self.for_image)
        self.root = ET.fromstring(self.xml_response.content)
        self.items = self.root.findall(".//ns:Item", namespaces=self.namespace)

        # Retrieving first image among the items
        for item in self.items:
            # Find image item
            self.image = item.find("ns:Image", namespaces=self.namespace)
            # Set high_res_url to the first image that is not None
            if self.image is not None:
                self.image_url = self.image.attrib['source']
                self.high_res_url = re.sub(r'/\d+px-', '/500px-', self.image_url)
                break
        # After looping through all items, if no image item is found, generate new article and find image again
        if self.high_res_url is None:
            self.generate_article()
            self.get_image()
        return self.high_res_url

    def get_views(self):
        # Headers to access the API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        # Retrieve views for a year from Wikimedia of 2023
        resp = requests.get(f'https://wikimedia.org/api/rest_v1/metrics/pageviews'
                            f'/per-article/en.wikipedia/all-access/all-agents/{self.title}/daily/2023010100/2023123000',
                            headers=headers).json()
        # If views can not be found for that year, generate a new article and find image and views again
        if 'items' not in resp:
            self.generate_article()
            self.get_image()
            self.get_views()
        # Add together views of all months
        else:
            for item in resp["items"]:
                self.total += item["views"]
