import scrapy
import json

from scrapy import Request
from scrapy.http import HtmlResponse
from w3lib.url import add_or_replace_parameters
from Sber_pars.items import SberParsItem
from Sber_pars.json_files.parse_cat import get_one_line_cat


class SberSpider(scrapy.Spider):
    name = 'sber'
    allowed_domains = ['sbermarket.ru']
    stores = [
        {'store_name': 'metro', 'store_id': 2},
        {'store_name': 'lenta', 'store_id': 57},
        {'store_name': 'auchan', 'store_id': 70},
        {'store_name': 'magnit_express', 'store_id': 2242},
        {'store_name': 'victoria', 'store_id': 1088},
        {'store_name': 'vkusvill', 'store_id': 3424},
    ]
    headers = {
        "client-token": "7ba97b6f4049436dab90c789f946ee2f",
        "api-version": "3.0",
    }

    def start_requests(self):
        for store in self.stores:
            yield Request(
                f'https://sbermarket.ru/api/categories?store_id={store["store_id"]}',
                dont_filter=True,
                cb_kwargs=store
            )

    def parse(self, response: HtmlResponse, **kwargs):
        js_dict = self.convert_to_json(response)
        dict_list = get_one_line_cat(js_dict["categories"])

        for _dict in dict_list:
            _dict.update(kwargs)
            url = self.get_link_block_products(_dict['permalink'], _dict['store_id'])
            yield response.follow(
                url,
                callback=self.parse_products_roll,
                headers=self.headers,
                cb_kwargs=_dict,
            )

    @staticmethod
    def get_link_block_products(permalink, store_id, page=1):
        params = {
            "tid": permalink,
            "page": page,
            "per_page": 20,
            "sort": "popularity"
        }
        link = add_or_replace_parameters(f'/api/stores/{store_id}/products', params)
        return link

    @staticmethod
    def get_link_products(slug, store_id):
        return f'/api/stores/{store_id}/products/' + slug

    @staticmethod
    def convert_to_json(response: HtmlResponse):
        return json.loads(response.text)

    def parse_products_roll(self, response: HtmlResponse, **kwargs):
        data = self.convert_to_json(response)
        total_pages = data['meta']['total_pages']
        for page in range(1, total_pages + 1):
            url = self.get_link_block_products(kwargs['permalink'], kwargs['store_id'], page=page)
            yield response.follow(
                url,
                callback=self.parse_product_block,
                headers=self.headers,
                cb_kwargs=kwargs,
                dont_filter=True,
            )

    def parse_product_block(self, response: HtmlResponse, **kwargs):
        data = self.convert_to_json(response)
        for product in data['products']:
            slug = product['slug']
            url = self.get_link_products(slug, kwargs['store_id'])
            yield response.follow(
                url,
                callback=self.parse_product,
                cb_kwargs=kwargs,
            )

    def parse_product(self, response: HtmlResponse, **kwargs):
        data = self.convert_to_json(response)

        if data['product']['manufacturer']:
            manufacturer = data['product']['manufacturer']['name']
        else:
            manufacturer = None

        if data['product']['brand']:
            brand = data['product']['brand']['name']
        else:
            brand = None

        if data['product']['manufacturing_country']:
            manufacturing_country = data['product']['manufacturing_country']['name']
        else:
            manufacturing_country = None

        product_properties = {
            'product_ingredients': {},
            'product_nutrition': {},
            'product_information': {
                'brand': brand,
                'manufacturer': manufacturer,
                'manufacturing_country': manufacturing_country,
            },
        }
        for _property in data['productProperties']:
            if _property['name'] == 'ingredients':
                product_properties['product_ingredients'][_property['presentation']] = _property['value']
            elif _property['name'] in {'protein', 'fat', 'carbohydrate', 'energy_value'}:
                product_properties['product_nutrition'][_property['presentation']] = _property['value']
            else:
                product_properties['product_information'][_property['presentation']] = _property['value']
        yield SberParsItem(
            name_store=kwargs['store_name'],
            main_category_name=kwargs['main_category_name'],
            main_category_img_url=kwargs['img_main_category_url'],
            category_name=kwargs['category_name'],
            category_img_url=kwargs['img_category_url'],
            category_permalink=kwargs["permalink"],
            product_name=data['product']['name'],
            product_img_link=data['product']['images'],
            product_instamart_price=data['product']['offer']['instamart_price'],
            product_original_unit_price=data['product']['offer']['original_unit_price'],
            product_price=data['product']['offer']['price'],
            product_human_volume=data['product']['human_volume'],
            product_items_per_pack=data['product']['items_per_pack'],
            product_price_type=data['product']['offer']['price_type'],
            product_stock=data['product']['offer']['stock'],
            product_stock_rate=data['product']['offer']['stock_rate'],
            product_max_stock_rate=data['product']['offer']['max_stock_rate'],
            product_discounted=data['product']['offer']['discounted'],
            product_discount=data['product']['offer']['discount'],
            product_unit_price=data['product']['offer']['unit_price'],
            product_description=data['product']['description'],
            product_description_original=data['product']['description_original'],
            product_properties=product_properties,
        )
