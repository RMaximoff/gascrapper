import time
import requests


class GAScraper:

    def __init__(self):
        self._main_url = 'https://goldapple.ru/'
        self._redirect_url = 'https://goldapple.ru/front/api/catalog/redirect'
        self._url_catalog_plp = 'https://goldapple.ru/front/api/catalog/plp'

        self._city_id = '1000000007'  # id категории парфюмерии, взято из запроса отправляемого сайтом
        self._category_id = "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"

        self._subcategory_ids_list = []
        self._item_ids_list = []
        self._url_item = 'https://goldapple.ru/front/api/catalog/product-card?' \
                         'itemId=19000197391&cityId=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&customerGroupId=0'

    @staticmethod
    def _post_request(url, json):

        sleep_time = 3

        while True:
            try:
                r = requests.post(url=url, json=json)
                print(r.status_code)
                print(r.json())
                if r.status_code == 200:
                    return r

            except requests.exceptions.RequestException as e:
                print(f'Произошла ошибка при отправке запроса: {e}. Повторная попытка через {sleep_time} сек')
                time.sleep(sleep_time)
                sleep_time += 3

    def _get_sub_categories(self):
        """Собираем id всех подкатегорий"""
        params_category_json = {
            'categoryId': self._category_id,
            'cityId': self._city_id
        }

        categories_list = self._post_request(self._url_catalog_plp,
                                             params_category_json).json().get('data').get('category').get('bubbles')

        for category in categories_list:
            link = category.get('link')
            print(link)
            params = {
                'url': link
            }

            subcategory_id = self._post_request(self._redirect_url,
                                                params).json().get('data').get('category').get('id')
            self._subcategory_ids_list.append(subcategory_id)

        print(self._subcategory_ids_list)


a = GAScraper()
a._get_sub_categories()

