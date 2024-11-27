import requests
import gspread
import pandas as pd

from datetime import datetime
from typing import List, Dict, Any
from config import *

class WildberriesAPI:
    def __init__(self, WB_API_TOKEN: str) -> None:
        self.WB_API_TOKEN = WB_API_TOKEN

    def get_products(self,offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        '''
        Делает запрос к API Wildberries и возвращает список товаров.
        :param offset: Смещение (количество пропущенных карточек) для пагинации.
        :param limit: Количество товаров для запроса (максимум — 100).
        :return: Список товаров, каждый товар представлен словарем.
        '''
        base_url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
        headers = {'Authorization': self.WB_API_TOKEN}
        payload = {
            'offset': offset,  # Смещение для пагинации
            'limit': limit
        }
        response = requests.post(base_url, headers=headers, json=payload)
        assert response.status_code == 200, f'Ошибка при запросе: {response.status_code}, {response.text}'
        return response.json().get('cards', [])


class ProductProcessor:
    @staticmethod
    def process(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        '''
        Обрабатывает список товаров и добавляет дату выгрузки.
        :param products: Список товаров из API.
        :return: Список обработанных товаров с добавленной датой.
        '''
        processed_products = []
        
        for product in products:
            processed_products.append({
                'Артикул WB': product.get('nmID'),
                'Наименование товара': product.get('title'),
                'Бренд': product.get('brand'),
                'Артикул продавца': product.get('imtID'),
                'Дата создания': product.get('createdAt'),
                'Дата обновления': product.get('updatedAt')
            })
        processed_products.append({
            'Дата создания':'Дата и время выгрузки:',
            'Дата обновления': datetime.now().strftime('%d.%m.%Y %H:%M:%S')})

        return processed_products


class GoogleSheetsExporter:
    def __init__(self, credentials_file: str, spreadsheet_name: str) -> None:
        '''
        Инициализирует класс для записи данных в Google Таблицу.

        :param credentials_file: Путь к JSON-файлу с учетными данными Google.
        :param spreadsheet_name: Название таблицы в Google Sheets.
        '''
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = gspread.service_account(filename=self.credentials_file)
        self.sheet = self._get_or_create_spreadsheet()

    def _get_or_create_spreadsheet(self):
        '''
        Проверяет существование таблицы и возвращает её, либо создает новую.

        :return: Объект таблицы.
        '''
        try:
            return self.client.open(self.spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            return self.client.create(self.spreadsheet_name)

    def export(self, data: List[Dict[str, Any]]) -> None:
        '''
        Записывает данные в Google Таблицу. Заменяет все данные на новые.

        :param data: Список словарей с данными для записи.
        '''
        # Открыть первый лист (или создать его)
        worksheet = self.sheet.get_worksheet(0) or self.sheet.add_worksheet(title='Sheet1', rows='100', cols='20')

        # Подготовка данных для записи (включая заголовки)
        if data:
            headers = list(data[0].keys())
            values = [headers] + [list(item.values()) for item in data]
        else:
            values = []

        # Очистить существующие данные и записать новые
        worksheet.clear()
        if values:
            worksheet.update(values)



def main() -> None:
    '''
    Загружает товары, обрабатывает их и сохраняет в Google Таблицу.
    '''
    # Проверка наличия необходимых переменных окружения
    assert all([WB_API_TOKEN, credentials_file, spreadsheet_name]), 'Не установлены все необходимые переменные окружения.'

    # Инициализация
    api = WildberriesAPI(WB_API_TOKEN)
    exporter = GoogleSheetsExporter(credentials_file, spreadsheet_name)

    offset: int = 0
    limit: int = 100
    min_target: int = 100
    all_products: List[Dict[str, Any]] = []

    try:
        while offset < min_target:
            # Получение следующей страницы товаров
            print(f'Загрузка с {offset} по {offset+limit} товар...')
            products = api.get_products(offset=offset, limit=100) # Следующей страница товаров
            if not products: break # Список товаров пуст
            all_products.extend(products)
            offset += limit # Увеличиваем смещение для следующей страницы
        exporter.export(ProductProcessor.process(all_products))
    except Exception as e: print(f'Ошибка: {e}')
    else: print('Успех!')


if __name__ == '__main__':
    main()
