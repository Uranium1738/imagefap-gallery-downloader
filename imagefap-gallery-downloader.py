#!/usr/bin/env python3

"""
TODO:
* Allow user to supply gallery URLs as an args. If args are present,
then skip prompting the user to enter a URL.
* Parse number of images from main gallery page
* Allow user to download multiple galleries.
** Refactor how the user is presented with information regarding
a given gallery. Notify them of the gallery's title and the number of images
the gallery contains.

NOTES:
* Important: Should we pause between requests in case
ImageFap times us out? This hasn't happened yet, though.

ImageFap INFO:
* Pages for individual images have a JSON file imbedded in a
<script type="application/ld+json"> tag. The "contentUrl" key
corresponds to the direct link to the full resolution image.
"""

from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urlparse
from html.parser import HTMLParser
from json import loads as json_loads
from os import mkdir

base_url = "http://www.imagefap.com"

class GalleryParser(HTMLParser):
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a' and attrs[-1][-1].startswith("/photo"):
            self.photo_url = base_url+attrs[-1][-1]
            self.photo_response = urlopen(self.photo_url).read().decode()
            photoParser.feed(self.photo_response)


class PhotoParser(HTMLParser):

    def get_filename(url):
        # this function gets a filename from a URL that points to a file
        return url.split("/")[-1]

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and len(attrs) > 0 and\
        attrs[0] == ("type","application/ld+json"):
            # we have to evaluate len(attrs) before checking attrs[0]
            # to avoid an index error.
            self.isJSON = True
        else:
            self.isJSON = False

    def handle_data(self, data):
        if self.isJSON:
            global files_downloaded
            self.photo_dict = json_loads(data)
            self.photo_raw_url = self.photo_dict["contentUrl"]
            self.save_name = PhotoParser.get_filename(self.photo_raw_url)
            print("Downloading: %s" % self.save_name)
            urlretrieve(self.photo_raw_url, save_folder + self.save_name)
            files_downloaded += 1
            self.isJSON = False


def get_save_folder(url):
    return urlparse(url)[2].split("/")[-1]

gallery = input("Enter the url of the gallery to download: ")

gallery = urlparse(gallery)
gallery = gallery[0] + "://" + ''.join(gallery[1:3]) + "?&view=2"
# We do all ^this^ to ensure that we're viewing
# the "One page" version of a gallery.
# Note: it's important that we add a question mark
# before &view=2 so that urlparse splits the url
# in the way we want when we name the save folder.

save_folder = get_save_folder(gallery)

try:
    mkdir(save_folder)
except FileExistsError:
    pass

save_folder += "/"

files_downloaded = 0

galleryParser = GalleryParser()
photoParser = PhotoParser()
gallery_response = urlopen(gallery).read().decode()
galleryParser.feed(gallery_response)

print("Gallery downloaded! Downloaded %d images." % files_downloaded)
