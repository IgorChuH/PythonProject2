import logging
from datetime import datetime
from typing import Optional

import pandas as pd


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    """
        Рассчитывает суммарные траты по заданной категории за последние 3 месяца от указанной даты.
        В процессе работы выводит отладочные сообщения с информацией о дате и промежутке фильтрации,
        а также итоговой сумме.
    """

    try:
        # Определяем текущую дату, если дата не передана
        if date is None:
            current_date = datetime.now()
        else:
            current_date = datetime.strptime(date, "%d.%m.%Y")
        logger.debug(f"Используемая дата: {current_date.strftime('%d.%m.%Y')}")

        # Дата 3 месяца назад (учтём, что 1 месяц = 30 дней примерно)
        three_months_ago = current_date - pd.DateOffset(months=3)
        logger.debug(f"Дата три месяца назад: {three_months_ago.strftime('%d.%m.%Y')}")

        # Убедимся, что дата транзакций в формате datetime
        if not pd.api.types.is_datetime64_any_dtype(transactions["Дата платежа"]):
            transactions["Дата платежа"] = pd.to_datetime(
                transactions["Дата платежа"], dayfirst=True
            )
            logger.debug("Преобразовали столбец 'Дата платежа' в datetime")

        # Отфильтруем транзакции по категории и дате
        mask = (
            (transactions["Категория"] == category)
            & (transactions["Дата платежа"] >= three_months_ago)
            & (transactions["Дата платежа"] <= current_date)
        )
        filtered = transactions.loc[mask]

        # Рассчитаем суммарные траты по категории за последние 3 месяца
        total_spending = filtered["Сумма операции"].sum()
        logger.debug(f"Общая сумма трат по категории '{category}': {total_spending}")

        result_df = pd.DataFrame(
            {"Категория": [category], "Сумма платежа": [total_spending]}
        )
        return result_df

    except Exception as e:
        logger.error(f"Ошибка при расчете трат по категории: {e}")
        return pd.DataFrame()  # возвращаем пустой датафрейм при ошибке


if __name__ == "__main__":
    excel_data = pd.read_excel(
        "C:\\Users\\ZIPHAI\\Decstop\\PythonProject2\\data\\operations.xlsx"
    )
    print(spending_by_category(excel_data, "Супермаркеты", "27.09.2021"))
