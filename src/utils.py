import json
import os
from collections import defaultdict

import requests
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
user_settings = os.path.join(current_dir, "..", "user_settings.json")

load_dotenv()
api_key = os.getenv("API_KEY")


def get_greeting(current_date):
    """
    Формирует приветствие в зависимости от времени суток.
    Возвращает словарь с ключом "greeting" и соответствующим приветствием
    """
    # Преобразуем строку даты и времени в объект datetime
    try:
        current_time = current_date.hour

        # Определяем приветствие в зависимости от времени
        if current_time < 6:
            greeting = "Доброй ночи"
        elif current_time < 12:
            greeting = "Доброе утро"
        elif current_time < 18:
            greeting = "Добрый день"
        else:
            greeting = "Добрый вечер"

        # Формируем JSON-ответ
        response = {"greeting": greeting}
        return response
    except ValueError:
        return json.dumps(
            {"error": "Неверный формат даты и времени. Ожидается YYYY-MM-DD HH:MM:SS"}
        )


# Функция для обработки данных карты
def process_card_data(transactions):
    """
    Обрабатывает данные по картам из транзакций, собирая информацию по каждой карте.
    Возвращает словарь, где ключ — номер карты.
    """
    card_info = defaultdict(
        lambda: {"last_digits": "", "total_spent": 0, "transactions": []}
    )

    for index, rows in transactions.iterrows():
        card_number = rows["Номер карты"]
        amount = rows["Сумма операции"]

        card_info[card_number]["last_digits"] = card_number
        card_info[card_number]["total_spent"] += amount
        card_info[card_number]["transactions"].append(amount)

    # Рассчитываем кешбэк
    for card in card_info.values():

        card["cashback"] = card["total_spent"] // 100  # 1 рубль на каждые 100 рублей

    return card_info


# Функция для получения топ-5 транзакций
def get_top_transactions(transactions):
    """
    Формирует список из топ-5 транзакций с наибольшей суммой платежа.
    Возвращает список из пяти словарей, каждый содержит информацию о транзакции.
    """
    transactions_info = []
    for index, rows in transactions.iterrows():
        date = rows["Дата платежа"]
        amount = rows["Сумма платежа"]
        category = rows["Категория"]
        description = rows["Описание"]

        transactions_info.append(
            {
                "date": date,
                "amount": amount,
                "category": category,
                "description": description,
            }
        )

    top_transactions = sorted(
        transactions_info, key=lambda x: x["amount"], reverse=True
    )[:5]

    return top_transactions


# Функция для получения курсов валют
def get_currency_rates():
    """
    Получает актуальные курсы валют, заданных пользователем.
    Читает список валют из файла настроек пользователя, запрашивает текущую цену каждой валюты через API twelvedata.
    Возвращает список словарей с текущими курсами валют.
    """
    result = []
    with open(user_settings, "r", encoding="utf-8") as file:
        data = json.load(file)
        currencies = data["user_currencies"]
    for currency in currencies:
        url = f"https://api.twelvedata.com/price?symbol={currency}&apikey={api_key}"
        response = requests.get(url).json()
        price = float(response.get("price", 0))
        result.append({"currency": currency, "price": round(price, 2)})
    return result


# Функция для получения стоимости акций S&P 500
def get_sp500_stock_prices():
    """
    Получает актуальные цены акций S&P 500 из списка пользователя.
    Читает список акций из файла настроек пользователя,
    запрашивает текущую цену каждой акции через API twelvedata.
    """
    result = []
    with open(user_settings, "r", encoding="utf-8") as file:
        data = json.load(file)
        stocks = data["user_stocks"]
    for stock in stocks:
        url = f"https://api.twelvedata.com/price?symbol={stock}&apikey={api_key}"
        response = requests.get(url).json()
        price = float(response.get("price", 0))
        result.append({"stock": stock, "price": round(price, 2)})
    return result
