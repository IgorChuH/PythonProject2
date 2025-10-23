import json
import unittest
from unittest.mock import patch

import pandas as pd

from src.services import search_by_phone, search_transactions

# Импортируем функции (предположим, что они в файле search_module.py)
# from search_module import search_transactions, search_by_phone


class TestSearchFunctions(unittest.TestCase):

    def setUp(self):
        # Пример тестового DataFrame
        data = {
            "Описание": [
                "Оплата +7 123 456-78-90",
                "Покупка в магазине",
                "встреча +7 987 65-43-21",
            ],
            "Категория": ["Услуги", "Продукты", "Развлечения"],
        }
        self.df = pd.DataFrame(data)

    @patch("src.services.logging.info")
    def test_search_transactions(self, mock_log_info):
        query = "услуги"

        result_json = search_transactions(self.df, query)
        result = json.loads(result_json)

        self.assertEqual(len(result), 1)
        self.assertIn("Оплата +7 123 456-78-90", result[0]["Описание"])
        mock_log_info.assert_any_call(f"Search query: {query}")
        mock_log_info.assert_any_call(f"Found {len(result)} matches")

    @patch("src.services.logging.info")
    def test_search_by_phone(self, mock_log_info):
        phone_query = "+7 987 65-43-21"

        result_json = search_by_phone(self.df, phone_query)
        result = json.loads(result_json)

        self.assertEqual(len(result), 1)
        self.assertIn("+7 987 65-43-21", result[0]["Описание"])
        mock_log_info.assert_any_call(f"Phone search query: {phone_query}")
        mock_log_info.assert_any_call(f"Found {len(result)} phone matches")


if __name__ == "__main__":
    unittest.main()
