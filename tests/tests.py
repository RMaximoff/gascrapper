import json
import unittest
import requests
from unittest.mock import patch, MagicMock, Mock
from src.connector import Connector
from src.scraper import GAScraper


class TestConnector(unittest.TestCase):

    @patch('requests.get')
    def test_get_request_success(self, mock_get):
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = 'https://yandex.ru'
        response = Connector.get_request(url)

        mock_get.assert_called_once_with(url=url)
        self.assertEqual(response, mock_response)

    @patch('requests.get')
    def test_get_request_retry_on_exception(self, mock_get):
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_get.side_effect = [
            requests.exceptions.RequestException,
            requests.exceptions.RequestException,
            mock_response
        ]
        url = 'https://yandex.ru'
        response = Connector.get_request(url)

        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(response.status_code, 200)

    @patch('requests.post')
    def test_post_request_success(self, mock_post):

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        url = 'https://yandex.ru'
        json_data = {'key': 'value'}
        response = Connector.post_request(url, json_data)

        mock_post.assert_called_once_with(url=url, json=json_data)
        self.assertEqual(response, mock_response)

    @patch('requests.post')
    def test_post_request_retry_on_exception(self, mock_post):
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_post.side_effect = [
            requests.exceptions.RequestException,
            requests.exceptions.RequestException,
            mock_response
        ]

        url = 'https://yandex.ru'
        json_data = {'key': 'value'}
        response = Connector.post_request(url, json_data)

        self.assertEqual(mock_post.call_count, 3)
        self.assertEqual(response.status_code, 200)


class TestGAScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = GAScraper()
        self.connector_mock = Mock()

    @patch('src.connector.Connector.get_request')
    def test_get_all_category_ids(self, mock_get_request):
        self.scraper._product_ids = [1]
        mock_response = MagicMock()
        with open('catalog.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        mock_response.json.return_value = data
        mock_get_request.return_value = mock_response

        self.scraper._get_all_category_ids()

        with open('catalog_out.json', 'r', encoding='utf-8') as file:
            data_out = json.load(file)

        self.assertEqual(self.scraper.get_categories, data_out)

    @patch('src.connector.Connector.post_request')
    def test_get_item_ids(self, mock_post_request):
        self.scraper._product_categories = {'key': [1]}
        self.connector_mock.json.return_value = {
            'data': {
                'products': {
                    'count': 1,
                    'products': [{'itemId': 1}]
                }
            }
        }
        mock_post_request.return_value = self.connector_mock

        product_ids = self.scraper._get_item_ids(
            params={"categoryId": 1, "cityId": self.scraper._city_id, "pageNumber": 1}, num_pages=2
        )

        self.assertEqual(product_ids, [1])

    @patch('src.connector.Connector.get_request')
    def test_get_item_info(self, mock_get_request):
        self.scraper._product_ids = [1]
        self.scraper._city_id = 123
        self.connector_mock.json.return_value = {
            'data': {
                'itemId': 1,
                'name': 'Продукт 1',
                'productType': 'Тип 1',
                'brand': 'Бренд 1',
                'attributesValue': {'units': 'Единицы 1'},
                'price': {
                    'regular': {'amount': '100'}
                },
                'productDescription': [
                    {'text': 'описание', 'content': 'Описание продукта'},
                    {'text': 'применение', 'content': 'Инструкция по применению'},
                    {'text': 'о бренде', 'subtitle': 'Страна-производитель', 'content': 'Описание бренда'}
                ],
                'variants': [
                    {
                        'itemId': 1,
                        'attributesValue': {'units': 'Единицы 1'},
                        'price': {'regular': {'amount': '100'}}
                    }
                ]
            }
        }
        mock_get_request.return_value = self.connector_mock

        self.scraper._get_item_info()

        expected_product_data = {
            'ссылка на продукт': 'https://goldapple.ru/1-продукт-1',
            'наименование': 'Тип 1 Бренд 1 Продукт 1 Единицы 1',
            'цена': '100',
            'рейтинг пользователей': '',
            'описание продукта': 'Описание продукта',
            'инструкция по применению': 'Инструкция по применению',
            'страна-производитель': 'Страна-производитель'
        }

        self.assertEqual(len(self.scraper._products_info), 1)
        self.assertEqual(self.scraper._products_info[0], expected_product_data)

    def test_get_item_info_with_empty_response(self):
        with patch('src.connector.Connector.get_request', return_value=self.connector_mock):
            self.connector_mock.json.return_value = None

            self.scraper._get_item_info()

            self.assertEqual(self.scraper._products_info, [])

    def test_get_categories(self):
        self.scraper._product_categories = {'key': [1]}
        self.assertEqual(self.scraper.get_categories, {'key': [1]})

    def test_get_product_info(self):
        self.scraper._products_info = [{'product': 'info'}]
        self.assertEqual(self.scraper.get_product_info, [{'product': 'info'}])

    @patch('src.connector.Connector.post_request')
    @patch.object(GAScraper, '_get_item_ids', return_value=[1])
    @patch.object(GAScraper, '_get_item_info')
    def test_get_products_list(self, mock_get_item_info, mock_get_item_ids, mock_post_request):
        self.scraper._product_categories = {'key': [1]}
        self.connector_mock.json.return_value = {
            'data': {
                'products': {
                    'count': 1,
                    'products': [{}]
                }
            }
        }
        mock_post_request.return_value = self.connector_mock

        self.scraper.get_products_list('key')

        mock_get_item_ids.assert_called_once()
        mock_get_item_info.assert_called_once()
        self.assertEqual(list(self.scraper._product_ids), [1])


if __name__ == '__main__':
    unittest.main()
