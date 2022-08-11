# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.files import FilesPipeline

import hashlib
from scrapy.utils.python import to_bytes
import mimetypes

import os


class SberParsPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.sber_market

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class SberFilesPipeline(FilesPipeline):
    @staticmethod
    def is_valid_type_img(_url):
        type_img = _url.split('/')[-2]
        return True if type_img in ('normal', 'small', 'preview') else False

    def get_media_requests(self, item, info):
        category_img_url = item['category_img_url']
        if self.is_valid_type_img(category_img_url):
            if 'sbermarket.ru' in category_img_url:
                yield scrapy.Request(category_img_url)
            else:
                yield scrapy.Request(category_img_url, headers={'Host': 'storage.yandexcloud.net'})

        main_category_img_url = item['main_category_img_url']
        if self.is_valid_type_img(main_category_img_url):
            if 'sbermarket.ru' in main_category_img_url:
                yield scrapy.Request(main_category_img_url)
            else:
                yield scrapy.Request(main_category_img_url, headers={'Host': 'storage.yandexcloud.net'})

        for val in item['product_img_link']:
            link_img_preview = val['preview_url']
            link_img_small = val['small_url']
            if self.is_valid_type_img(link_img_preview):
                yield scrapy.Request(link_img_preview)
            if self.is_valid_type_img(link_img_small):
                yield scrapy.Request(link_img_small)

    def file_path(self, request, response=None, info=None, *, item=None):
        name_ext = request.url.split('/')[-1]
        type_img = request.url.split('/')[-2]
        media_guid = hashlib.sha1(to_bytes(name_ext)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]
        if media_ext not in mimetypes.types_map:
            url_no_params = request.url.split('?')[0]
            media_ext = os.path.splitext(url_no_params)[1]
            if media_ext not in mimetypes.types_map:
                media_ext = ''
                media_type = mimetypes.guess_type(request.url)[0]
                if media_type:
                    media_ext = mimetypes.guess_extension(media_type)
        return f'{type_img}/{media_guid}{media_ext}'

    def item_completed(self, results, item, info):
        item['category_img_url'] = results[0][1]
        item['main_category_img_url'] = results[1][1]
        item['product_img_link'] = \
            {'preview': [itm[1] for itm in results[2:] if itm[0] and itm[1]['path'].split('/')[0] == 'preview'],
             'small': [itm[1] for itm in results[2:] if itm[0] and itm[1]['path'].split('/')[0] == 'small']}
        return item
