import pandas as pd
import json
import os
from datetime import  datetime
from src.utils import get_greeting
from src.utils import process_card_data
from src.utils import get_top_transactions
from src.utils import get_currency_rates
from src.utils import get_sp500_stock_prices



current_dir = os.path.dirname(__file__)
file = os.path.join(current_dir, "..", "data", "operations.xlsx")


# Главная функция
def main(transactions, current_date=None):
    """
    Главная функция обработки данных транзакций и получения сводной информации.
    Возвращает JSON-строку с результатами, включающими. В случае неверного формата даты возвращает JSON с ошибкой.
    """
    try:
        if current_date is None:
            current_time = datetime.now()
        else:
            current_time = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return json.dumps({"error": "Неверный формат даты и времени. Ожидается YYYY-MM-DD HH:MM:SS"})

        # Получаем приветствие

    greeting = get_greeting(current_time)

    # Обрабатываем данные карт
    result = process_card_data(transactions)

    # Получаем топ-5 транзакций
    top_transactions = get_top_transactions(transactions)

    # Получаем курсы валют
    currency_rates = get_currency_rates()

    # Получаем стоимость акций S&P 500
    sp500_prices = get_sp500_stock_prices()

    # Формируем JSON-ответ
    response = {
        "greeting": greeting,
        "card_data": {k: {**v, "transactions": v["transactions"][:5]} for k, v in result.items()},
        # Только первые 5 транзакций
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "sp500_prices": sp500_prices,
    }

    return json.dumps(response, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    excel_data = pd.read_excel(file)

    print(main(excel_data))