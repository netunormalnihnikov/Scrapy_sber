# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class SberParsPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.sber_market

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class SberImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request('https://sbermarket.ru' + item['category_img_url'])
        yield scrapy.Request('https://sbermarket.ru' + item['main_category_img_url'])

        for val in item['product_img_link']:
            link_img = val['original_url']
            yield scrapy.Request(link_img)

    def item_completed(self, results, item, info):
        item['category_img_url'] = results[0][1]
        item['main_category_img_url'] = results[1][1]
        item['product_img_link'] = [itm[1] for itm in results[2:] if itm[0]]
        return item
