import requests
import xml.etree.ElementTree as ET
import re


class Article:
    """ Article class that generates an article from Wikipedia, containing its title, image and views for 2023

        Typical use:

        article = Article()
        article.generate_article()
        article.high_res_url = article.get_image()
        article.get_views()

        Attributes:
        wikipedia_url: the URL to Wikipedia's API
        random_url: the extension of the URl with the necessary queries
        title: the title of the generated article
        page_id: the id of the generated article to check for images and retrieve title
        for_image: URL for retrieving the image of the article
        xml_response: the response from for_image in XML
        root: root in the XML response to read directly the data from a string retrieved
        namespace: namespace for the XML response
        items: items in the XML response
        image: image item in XML response
        image_url: the retrieved URL of the image of the article
        high_res_url: a modification of image_url for the bigger size of 500px
        total: the total of the article's views during 2023

      """
    def __init__(self):
        """ Inits Article with necessary variables to access APIs, handle XML parsing,
        and save title, image and views """
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
        """ Randomly generates a wikipedia article and retrieves the title of the article through Wikipedia API """
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
        """ Retrieves through XML an image of the generated article and converts it to 500px """
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
        """ Retrieves the total amount of Wikipedia views during 2023 of the generated article from Wikimedia API """
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
