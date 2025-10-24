# test_scraper.py

import os
import random
import sys
from unittest.mock import patch

import pandas as pd
import pytest
from tqdm import tqdm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scraper import get_book_data, scrape_books


class TestBookParser:
    """
    Класс для тестирования функций из модуля scraper.py
    """

    # Тестовые данные
    test_urls = [
        'https://books.toscrape.com/catalogue/soumission_998/index.html',
        'https://books.toscrape.com/catalogue/sharp-objects_997/index.html',
        'https://books.toscrape.com/catalogue/the-requiem-red_995/index.html'
    ]

    def test_data_type_gbd(self):
        """Проверяет возвращаемый тип данных для get_book_data"""
        url = random.choice(self.test_urls)
        result = get_book_data(url)
        assert isinstance(result, pd.DataFrame)

    def test_columns_exist_gbd(self):
        """Проверяет наличие нужных столбцов в созданном датафрейме для get_book_data"""
        url = random.choice(self.test_urls)
        result = get_book_data(url)
        expected_columns = [
            "title", "genre", "rating", "upc", "product_type",
            "price_excl_tax", "price_incl_tax", "tax", "in_stock",
            "reviews_count", "description", "url"
        ]
        for column in expected_columns:
            assert column in result.columns, f"Колонка {column} отсутствует"

    @pytest.mark.parametrize("url_index,expected_title", [
        (0, "Soumission"),
        (1, "Sharp Objects"),
        (2, "The Requiem Red")
    ])
    def test_contents_gbd(self, url_index, expected_title):
        """Проверяет корректность извлеченных заголовков для разных книг"""
        result = get_book_data(self.test_urls[url_index])
        assert result.iloc[0]['title'] == expected_title

    def test_total_price_sb(self):
        """Проверяет сумму стоимости с учетом налога для n-количества книг"""
        expected_prices = {
            1: 760.97,
            2: 1398.35,
            3: 2100.16,
            4: 2856.67,
            5: 3456.07
        }

        for pages, expected_price in tqdm(
                expected_prices.items(), desc="Страницы"):
            result = scrape_books(pages_num=pages)
            result["price_incl_tax"] = pd.to_numeric(
                result["price_incl_tax"], errors='coerce'
            )
            total_price = result["price_incl_tax"].sum()

            assert total_price == pytest.approx(expected_price, abs=0.01), (
                f"Итоговая стоимость для {pages} страниц не совпадает: "
                f"ожидалось {expected_price}, получено {total_price}"
            )
