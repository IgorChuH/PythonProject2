import unittest
from unittest.mock import patch, MagicMock
from src.views import main  # импорт вашей функции main
import json

class TestMainFunction(unittest.TestCase):

    @patch('src.views.get_sp500_stock_prices')
    @patch('src.views.get_currency_rates')
    @patch('src.views.get_top_transactions')
    @patch('src.views.process_card_data')
    @patch('src.views.get_greeting')
    @patch('src.views.datetime')
    def test_main_with_fixed_date(
        self, mock_datetime,
        mock_get_greeting,
        mock_process_card_data,
        mock_get_top_transactions,
        mock_get_currency_rates,
        mock_get_sp500_stock_prices):

        # Мокируем datetime.strptime корректно
        from datetime import datetime as real_datetime
        mock_datetime.strptime.side_effect = lambda s, fmt: real_datetime.strptime(s, fmt)

        # Мокируем возвращаемые значения
        mock_get_greeting.return_value = "Добрый день"
        mock_process_card_data.return_value = {
            "card1": {"transactions": [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]}
        }
        mock_get_top_transactions.return_value = [{"id": 1}, {"id": 2}]
        mock_get_currency_rates.return_value = {"USD": 70}
        mock_get_sp500_stock_prices.return_value = {"AAPL": 150}

        date_str = "2024-06-01 12:00:00"
        transactions = MagicMock()  # Можно передать мок или реальные данные, если нужно

        result_json = main(transactions, current_date=date_str)
        result = json.loads(result_json)

        # Проверяем корректность вызовов
        mock_datetime.strptime.assert_called_once_with(date_str, '%Y-%m-%d %H:%M:%S')
        mock_get_greeting.assert_called_once()
        mock_process_card_data.assert_called_once_with(transactions)
        mock_get_top_transactions.assert_called_once_with(transactions)
        mock_get_currency_rates.assert_called_once()
        mock_get_sp500_stock_prices.assert_called_once()

        # Проверяем структуру результата
        self.assertEqual(result["greeting"], "Добрый день")

        # В card_data транзакций только 5
        self.assertEqual(len(result["card_data"]["card1"]["transactions"]), 5)

        self.assertEqual(result["top_transactions"], [{"id": 1}, {"id": 2}])
        self.assertEqual(result["currency_rates"], {"USD": 70})
        self.assertEqual(result["sp500_prices"], {"AAPL": 150})

    def test_main_with_invalid_date_format(self):
        invalid_date = "2024/06/01"
        result_json = main(transactions=None, current_date=invalid_date)
        result = json.loads(result_json)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Неверный формат даты и времени. Ожидается YYYY-MM-DD HH:MM:SS")

if __name__ == "__main__":
    unittest.main()