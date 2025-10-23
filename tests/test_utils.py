import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd

import src.utils


class TestYourFunctions(unittest.TestCase):
    def test_get_greeting(self):
        dt = datetime(year=2024, month=6, day=1, hour=7)
        result = src.utils.get_greeting(dt)
        self.assertEqual(result, {"greeting": "Доброе утро"})

        dt = datetime(year=2024, month=6, day=1, hour=23)
        result = src.utils.get_greeting(dt)
        self.assertEqual(result, {"greeting": "Добрый вечер"})

    def test_process_card_data(self):
        # Мокаем DataFrame с транзакциями
        data = {
            "Номер карты": ["1111", "1111", "2222"],
            "Сумма операции": [150, 50, 200],
        }
        df_mock = pd.DataFrame(data)

        result = src.utils.process_card_data(df_mock)

        # Проверяем, что ключи равны номерам карт
        self.assertIn("1111", result)
        self.assertIn("2222", result)

        # Проверяем сумму трат по карте "1111" = 150 + 50
        self.assertEqual(result["1111"]["total_spent"], 200)
        self.assertEqual(result["1111"]["last_digits"], "1111")
        self.assertEqual(result["1111"]["transactions"], [150, 50])

        # Кешбэк 1 рубль за каждые 100 потраченных
        self.assertEqual(result["1111"]["cashback"], 2)  # 200 // 100 = 2
        self.assertEqual(result["2222"]["cashback"], 2)  # 200 // 100 = 2

    def test_get_top_transactions(self):
        data = {
            "Дата платежа": [
                "2024-06-01",
                "2024-06-02",
                "2024-06-03",
                "2024-06-04",
                "2024-06-05",
                "2024-06-06",
            ],
            "Сумма платежа": [300, 500, 200, 150, 170, 210],
            "Категория": ["food", "travel", "food", "shopping", "travel", "food"],
            "Описание": ["desc1", "desc2", "desc3", "desc4", "desc5", "desc6"],
        }
        df_mock = pd.DataFrame(data)

        result = src.utils.get_top_transactions(df_mock)

        # Проверяем, что вернулось ровно 5 топ транзакций
        self.assertEqual(len(result), 5)
        # Проверим, что самая дорогая транзакция на первом месте (500)
        self.assertEqual(result[0]["amount"], 500)
        # Проверим, что в списке нет транзакций с меньшей суммой, чем у 6-й (150)
        amounts = [item["amount"] for item in result]
        self.assertNotIn(150, amounts)  # Потому что топ-5 отсекает ту с 150

    @patch(
        "src.utils.open",
        new_callable=mock_open,
        read_data='{"user_currencies": ["USD", "EUR"]}',
    )
    @patch("src.utils.requests.get")
    def test_get_currency_rates(self, mock_get, mock_file):
        mock_get.side_effect = [
            unittest.mock.Mock(json=lambda: {"price": "75.4321"}),
            unittest.mock.Mock(json=lambda: {"price": "90.1234"}),
        ]

        result = src.utils.get_currency_rates()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"currency": "USD", "price": 75.43})
        self.assertEqual(result[1], {"currency": "EUR", "price": 90.12})
        mock_file.assert_called_once_with(
            src.utils.user_settings, "r", encoding="utf-8"
        )

    @patch(
        "src.utils.open",
        new_callable=mock_open,
        read_data='{"user_stocks": ["AAPL", "MSFT"]}',
    )
    @patch("src.utils.requests.get")
    def test_get_sp500_stock_prices(self, mock_get, mock_file):
        mock_get.side_effect = [
            unittest.mock.Mock(json=lambda: {"price": "150.56"}),
            unittest.mock.Mock(json=lambda: {"price": "250.78"}),
        ]

        result = src.utils.get_sp500_stock_prices()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"stock": "AAPL", "price": 150.56})
        self.assertEqual(result[1], {"stock": "MSFT", "price": 250.78})
        mock_file.assert_called_once_with(
            src.utils.user_settings, "r", encoding="utf-8"
        )


if __name__ == "__main__":
    unittest.main()
