#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, random, re, requests
from django.conf import settings
from flickrapi import FlickrAPI
from pk.utils import rget

USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'  # noqa


class PhotosFromFlickr:
    """ Get photos from Flickr. """
    RPP = 100           # Results per page
    GROUPIDS = [        # Vetted flickr groupids
        '830711@N25'    # Best Landscape Photographers
    ]
    
    def __init__(self):
        self.flickr = FlickrAPI(**settings.FLICKR)

    def get_photo(self, groupid=None, rpp=RPP):
        groupid = groupid or self.GROUPIDS[0]
        # Find number of pages in photo gallery
        response = self.flickr.groups.pools.getPhotos(group_id=groupid, per_page=rpp)
        pages = json.loads(response.decode('utf8'))['photos']['pages']
        # Choose a random photo from the gallery
        page = random.randrange(pages) + 1
        response = self.flickr.groups.pools.getPhotos(extras='description,owner_name,url_h,geo',
            get_user_info=1, group_id=groupid, page=page, per_page=rpp)
        photos = json.loads(response.decode('utf8'))['photos']['photo']
        photos = list(filter(_filter, photos))
        photo = random.choice(photos)
        return _photo(photo, 'url_h', 'ownername', 'title', 'description._content')


class PhotosFrom500px:
    """ Get photos from 500px. """
    RPP = 100           # Results per page
    HOME = 'https://500px.com'  # 500px homepage (to grab csrf-token)
    FEED = 'https://api.500px.com/v1/photos?feature=user&stream=photos&user_id={userid}&include_states=true&image_size%5B%5D=1600&page={page}&rpp={rpp}'  # noqa
    USERIDS = [         # Vetted 500px userids
        14026643,       # Tobias Hägg (airpixels); 500 landscape photos, no watermark
    ]

    def __init__(self):
        self.session = self.get_session()

    def get_session(self):
        """ Get an authenticated 500px session. """
        session = requests.Session()
        response = session.get(self.HOME)
        for line in response.content.split('\n'):
            if 'csrf-token' in line.lower():
                token = re.findall('content=\"(.+?)\"', line)
                session.headers.update({'X-CSRF-Token': token[0]})
        return session

    def get_photo(self, userid=None, rpp=RPP):
        """ Return a random photo for the specified userid. """
        userid = userid or self.USERIDS[0]
        # Inital request just to get the number of pages
        url = self.FEED.format(userid=userid, page=1, rpp=rpp)
        response = self.session.get(url)
        data = response.json()
        # Second request to a random page number
        page = random.randrange(data['total_pages'] + 1)
        url = self.FEED.format(userid=userid, page=page, rpp=rpp)
        response = self.session.get(url)
        data = response.json()
        import pprint; pprint.pprint(data)


def _filter(photo, wkey='width', hkey='height', **kwargs):
    """ Filter list of photos to only landscape mode. """
    width, height = photo.get(wkey,0), photo.get(hkey,0)
    if not width or not height: return False
    if int(width) < int(height): return False
    for key, value in kwargs.items():
        if photo.get(key) != value:
            return False
    return True


def _photo(photo, urlkey, userkey, titlekey, desckey):
    """ Create common dict of photo details. """
    return {
        'url': rget(photo, urlkey, ''),
        'user': rget(photo, userkey, ''),
        'title': rget(photo, titlekey, ''),
        'description': rget(photo, desckey, ''),
    }


if __name__ == '__main__':
    api = PhotosFrom500px()
    api.get_photo()
