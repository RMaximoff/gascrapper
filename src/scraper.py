import re
from math import ceil
from src.connector import Connector


class GAScraper:

    def __init__(self):
        self._navigation_url = 'https://goldapple.ru/front/api/catalog/navigation'
        self._redirect_url = 'https://goldapple.ru/front/api/catalog/redirect'
        self._url_catalog_plp = 'https://goldapple.ru/front/api/catalog/plp'

        self._city_id = '0c5b2444-70a0-4932-980c-b4dc0d3f02b5'

        self._product_categories = {}
        self._product_ids = {}
        self._products_info = []

        self._url_item = 'https://goldapple.ru/front/api/catalog/product-card?' \
                         'itemId=19000197391&cityId=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&customerGroupId=0'

        self._get_all_category_ids()

    @property
    def get_categories(self):
        return self._product_categories

    @property
    def get_product_info(self):
        return self._products_info

    def _get_all_category_ids(self):
        """Собираем все id категорий в словарь"""
        navigation = Connector.get_request(self._navigation_url).json()

        for item in navigation.get('data'):
            if item.get('name') == 'каталог':
                if len(item.get('children')) > 0:
                    names = []
                    for child in item.get('children'):
                        child_name = child.get('name')
                        names.append(child_name)
                        chapter_ids = []
                        for chapter in child.get('children'):
                            if chapter.get('name') != 'все товары категории':
                                chapter_ids.append(chapter.get('id'))
                                subchapter_ids = []
                                if len(chapter.get('children')) > 0:
                                    for subchapter in chapter.get('children'):
                                        chapter_ids.append(subchapter.get('id'))
                                    chapter_ids.extend(subchapter_ids)
                        self._product_categories[child_name] = chapter_ids

    def _get_item_ids(self, params, num_pages):
        """Получаем данные по всем продуктам выбранной категории"""
        params = params
        product_ids = {}
        for i in range(1, num_pages):
            response = Connector.post_request(url=self._url_catalog_plp, json=params).json()
            products = response.get('data').get('products').get('products')
            for product in products:
                product_id = product.get('itemId')
                url = product.get('url')
                product_ids[product_id] = url
                params["pageNumber"] = i + 1
        print(product_ids)
        return product_ids

    def get_products_list(self, key):
        """Получаем все страницы продуктов в каждой подкатегории"""
        category_ids = self._product_categories[key]

        for category_id in category_ids:
            params = {
                "categoryId": category_id,
                "cityId": self._city_id,
                "pageNumber": 1
            }
            response = Connector.post_request(url=self._url_catalog_plp, json=params).json()
            num_products = response.get('data').get('products').get('count')
            per_page = len(response.get('data').get('products').get('products'))
            num_pages = ceil(num_products / per_page)
            product_ids = self._get_item_ids(params=params, num_pages=num_pages)
            self._product_ids.update(product_ids)

        self._get_item_info()

    def _get_item_info(self):
        """Получаем информацию о продукте"""

        for item_id, url in self._product_ids.items():
            connect_link = f'https://goldapple.ru/front/api/catalog/product-card?' \
                  f'itemId={item_id}&cityId={self._city_id}&customerGroupId=0'
            response = Connector.get_request(connect_link).json().get('data')

            if not response:
                continue

            variant_count = len(response.get('variants'))
            for i in range(0, variant_count):
                url_part = url.split('-', 1)
                product_data = {
                    'ссылка на продукт': f'https://goldapple.ru/{response.get("variants")[i].get("itemId", "")}-{url_part[-1]}',
                    'наименование': f'{response.get("productType", "")} {response.get("brand", "")} '
                                    f'{response.get("name", "")} '
                                    f'{response.get("variants")[i].get("attributesValue", {}).get("units", "")}'
                                    f'{response.get("attributes", {}).get("units", {}).get("unit", "")}',
                    'цена': f'{response.get("variants")[i].get("price", {}).get("regular", {}).get("amount", "")}',
                    'рейтинг пользователей': '',
                    'описание продукта': '',
                    'инструкция по применению': '',
                    'страна-производитель': ''
                }

                for descript in response.get("productDescription", []):
                    text = descript.get('text')
                    content = re.sub(r'<p>|<br/>|<br>|[\n\r\t]+', ' ', descript.get('content')).strip()
                    subtitle = descript.get('subtitle')

                    if text == 'описание':
                        product_data['описание продукта'] = content
                    elif text == 'применение':
                        product_data['инструкция по применению'] = content
                    elif text == 'о бренде':
                        product_data['страна-производитель'] = subtitle

                print(product_data)

                self._products_info.append(product_data)
