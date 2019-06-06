# -*- coding: utf-8 -*-
import json, re, requests
from django.conf import settings
from flickrapi import FlickrAPI
from pk import log
from pk.utils import rget, threaded
from pk.utils.decorators import DAYS, softcache

USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'  # noqa


class PhotosFromFlickr:
    """ Get photos from Flickr.
        https://www.flickr.com/services/api/flickr.galleries.getPhotos.html
        https://stuvel.eu/flickrapi-doc/
    """
    RPP = 500           # Results per page
    EXTRAS = 'description,owner_name,url_h,geo'
    GROUPIDS = [        # Vetted flickr groupids
        '830711@N25'    # Best Landscape Photographers
    ]
    
    def __init__(self):
        self.flickr = FlickrAPI(**settings.FLICKR)

    def get_photos(self):
        photos = []
        for groupid in self.GROUPIDS:
            response = self.flickr.groups.pools.getPhotos(group_id=groupid, per_page=self.RPP)
            pages = response.json()['photos']['pages']
            kwargs = {str(p):[self._get_page,groupid,p] for p in range(1, pages+1)}
            results = threaded(numthreads=20, **kwargs)
            for page, result in results.items():
                photos += result
        log.info('Finished processing %s photos from Flickr' % len(photos))
        return photos

    def _get_page(self, groupid, page):
        photos = []
        log.info('Fetching Flickr photos: %s page %s' % (groupid, page))
        response = self.flickr.groups.pools.getPhotos(extras=self.EXTRAS,
            get_user_info=1, group_id=groupid, page=page, per_page=self.RPP)
        for photo in response.json()['photos']['photo']:
            if _filter(photo, 'width_h', 'height_h'):
                photos.append(_photo(photo, 'url_h', 'ownername', 'title', 'description._content'))
        return photos


class PhotosFrom500px:
    """ Get photos from 500px. """
    RPP = 100           # Results per page
    HOME = 'https://500px.com/popular'  # 500px homepage (to grab csrf-token)
    FEED = 'https://api.500px.com/v1/photos?feature=user&stream=photos&user_id={userid}&include_states=true&image_size%5B%5D=1600&page={page}&rpp={rpp}'  # noqa
    USERIDS = [         # Vetted 500px userids
        14026643,       # Tobias Hägg (airpixels); 500 landscapes, no watermark
        72777941,       # Simon W Xu; Landscapes
    ]

    def __init__(self):
        self.session = self.get_session()

    def get_session(self):
        """ Get an authenticated 500px session. """
        session = requests.Session()
        response = session.get(self.HOME)
        for line in response.content.decode('utf8').split('\n'):
            if 'csrf-token' in line.lower():
                token = re.findall('content=\"(.+?)\"', line)
                session.headers.update({'X-CSRF-Token': token[0]})
        return session

    def get_photos(self, rpp=RPP):
        photos = []
        for userid in self.USERIDS:
            url = self.FEED.format(userid=userid, page=1, rpp=rpp)
            response = self.session.get(url)
            pages = response.json()['total_pages']
            # kwargs = {str(p):[self._get_page,userid,p] for p in range(1, 2)}
            kwargs = {str(p):[self._get_page,userid,p] for p in range(1, pages+1)}
            results = threaded(numthreads=10, **kwargs)
            for page, result in results.items():
                photos += result
        log.info('Finished processing %s photos from 500px' % len(photos))
        return photos

    def _get_page(self, userid, page):
        photos = []
        log.info('Fetching 500px photos: %s page %s' % (userid, page))
        url = self.FEED.format(userid=userid, page=page, rpp=self.RPP)
        response = self.session.get(url)
        for photo in response.json()['photos']:
            if _filter(photo, 'width', 'height'):
                photos.append(_photo(photo, 'images.0.url', 'user.fullname', 'name', 'description'))
        return photos


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


@softcache(timeout=30*DAYS, expires=60*DAYS, key='album')
def get_album(request, cls):
    try:
        return cls().get_photos()
    except Exception as err:
        log.exception(err)


if __name__ == '__main__':
    api = PhotosFrom500px()
    photos = api.get_photos()
    print(photos)
