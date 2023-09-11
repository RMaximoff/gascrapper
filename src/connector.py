import requests
import time


class Connector:

    @staticmethod
    def _handle_exceptions(url, method, exception, retry_count):
        """Обработчик ошибок"""
        sleep_time = retry_count * 3

        print(f'Произошла ошибка при отправке {method} запроса к {url}: {exception}. '
              f'Повторная попытка через {sleep_time} сек')
        time.sleep(sleep_time)

        return sleep_time

    @staticmethod
    def get_request(url: str):
        """Создание GET запроса"""
        retry_count = 0
        while True:
            try:
                r = requests.get(url=url)
                if r.status_code == 200:
                    return r

            except Exception as e:
                retry_count += 1

                sleep_time = Connector._handle_exceptions(
                    url=url,
                    method='GET',
                    exception=repr(e),
                    retry_count=retry_count
                )
                time.sleep(sleep_time)

    @staticmethod
    def post_request(url: str, json: dict):
        """Создание POST запроса"""
        retry_count = 0
        while True:
            try:
                r = requests.post(url=url, json=json)

                if r.status_code == 200:
                    return r

            except Exception as e:
                retry_count += 1
                sleep_time = Connector._handle_exceptions(
                    url=url,
                    method='POST',
                    exception=repr(e),
                    retry_count=retry_count
                )
                time.sleep(sleep_time)


