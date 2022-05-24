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
    def get_media_requests(self, item, info):
        category_img_url = 'https://sbermarket.ru' + item['category_img_url']
        yield scrapy.Request(category_img_url)

        main_category_img_url = 'https://sbermarket.ru' + item['main_category_img_url']
        yield scrapy.Request(main_category_img_url)

        for val in item['product_img_link']:
            link_img = val['original_url']
            yield scrapy.Request(link_img)

    def file_path(self, request, response=None, info=None, *, item=None):
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]
        if media_ext not in mimetypes.types_map:
            url_no_params = request.url.split('?')[0]
            media_ext = os.path.splitext(url_no_params)[1]
            if media_ext not in mimetypes.types_map:
                media_ext = ''
                media_type = mimetypes.guess_type(request.url)[0]
                if media_type:
                    media_ext = mimetypes.guess_extension(media_type)
        return f'full/{media_guid}{media_ext}'

    def item_completed(self, results, item, info):
        item['category_img_url'] = results[0][1]
        item['main_category_img_url'] = results[1][1]
        item['product_img_link'] = [itm[1] for itm in results[2:] if itm[0]]
        return item
