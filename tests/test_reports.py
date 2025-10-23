import datetime as real_datetime
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.reports import \
    spending_by_category  # замените your_module на имя файла с функцией


class TestSpendingByCategory(unittest.TestCase):

    def setUp(self):
        # Исходный тестовый DataFrame
        data = {
            "Дата платежа": ["01.04.2024", "15.01.2024", "10.02.2024", "20.12.2023"],
            "Категория": ["Еда", "Еда", "Транспорт", "Еда"],
            "Сумма операции": [100, 200, 300, 400],
        }
        self.df = pd.DataFrame(data)

    @patch("src.reports.datetime")
    @patch("src.reports.logging.getLogger")
    def test_spending_with_fixed_date(self, mock_getLogger, mock_datetime):
        # Задаём фиксированную текущую дату
        mock_datetime.now.return_value = pd.Timestamp("2024-04-10 00:00:00")
        mock_datetime.strptime.side_effect = (
            lambda s, f: real_datetime.datetime.strptime(s, f)
        )

        # Мокаем логгер
        mock_logger = MagicMock()
        mock_getLogger.return_value = mock_logger

        result = spending_by_category(self.df, category="Еда", date="10.04.2024")

        # Проверяем результат — суммы с учётом 3 месяцев назад
        # Транзакция от 20.12.2023 выходит за период (10.01.2024 - 10.04.2024)
        # Оставляем оплаты 01.04. и 15.01.
        expected_sum = 100 + 200

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.at[0, "Категория"], "Еда")
        self.assertAlmostEqual(result.at[0, "Сумма платежа"], expected_sum)

        # Проверяем вызовы логгера debug
        mock_logger.debug.assert_any_call("Используемая дата: 10.04.2024")
        mock_logger.debug.assert_any_call("Дата три месяца назад: 10.01.2024")
        mock_logger.debug.assert_any_call(
            "Преобразовали столбец 'Дата платежа' в datetime"
        )

    @patch("src.reports.logging.getLogger")
    def test_spending_with_invalid_date_logs_error(self, mock_getLogger):
        mock_logger = MagicMock()
        mock_getLogger.return_value = mock_logger

        # Передаем некорректный формат даты
        result = spending_by_category(self.df, category="Еда", date="invalid-date")

        self.assertTrue(result.empty)
        mock_logger.error.assert_called_once()
        self.assertIn(
            "Ошибка при расчете трат по категории", mock_logger.error.call_args[0][0]
        )


if __name__ == "__main__":
    unittest.main()
