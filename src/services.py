import logging
import json
import re
import pandas as pd

pattern = re.compile(r'^\+7\s(\d{3})\s(\d{3}-\d{2}-\d{2}|\d{2}-\d{2}-\d{2})$')

logging.basicConfig(level=logging.INFO)

def search_transactions(transactions, query):
    logging.info(f"Search query: {query}")
    result = []
    q = query.lower()
    for index, rows in transactions.iterrows():
        description = rows['Описание'].lower()
        category = str(rows['Категория']).lower()
        if q in description or q in category:
            result.append(rows.to_dict())

    logging.info(f"Found {len(result)} matches")

    return json.dumps(result, ensure_ascii=False, indent=4)

def search_by_phone(transactions, phone_query):
    logging.info(f"Phone search query: {phone_query}")
    result = []

    def normalize_phone(phone):
        return re.sub(r'\D', '', phone)

    phone_query_norm = normalize_phone(phone_query)

    for _, row in transactions.iterrows():
        phones_text = row['Описание']
        phones_text_norm = normalize_phone(phones_text)

        if phone_query_norm in phones_text_norm:
            result.append(row.to_dict())  # Преобразуем Series в dict

    logging.info(f"Found {len(result)} phone matches")
    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    excel_data = pd.read_excel("C:\\Users\\ZIPHAI\\Decstop\\PythonProject2\\data\\operations.xlsx")

    print(search_transactions(excel_data, "Аптеки"))
    print(search_by_phone(excel_data, "+7 921 111-22-33"))