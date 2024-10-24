import xml.etree.ElementTree as ET
import sqlite3
import re
from datetime import datetime


# Функция для валидации данных.
def is_valid_company(company):
    ogrn = company.get('ogrn')
    inn = company.get('inn')
    date = company.get('date')

    # Проверка ОГРН (должно состоять из 13 цифр)
    if not re.match(r'^\d{13}$', ogrn):
        print(f'Ошибка: Некорректный ОГРН {ogrn}')
        return False

    # Проверка ИНН (должно состоять из 10 цифр)
    if not re.match(r'^\d{10}$', inn):
        print(f'Ошибка: Некорректный ИНН {inn}')
        return False

    # Проверка корректности даты.
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print(f'Ошибка: Некорректная дата {date}')
        return False

    return True


# Функция для добавления или обновления компании в базе данных.
def insert_or_update_company(company):
    ogrn = company['ogrn']
    inn = company['inn']
    name = company['name']
    date = company['date']

    # Проверяем, есть ли уже компания с таким ОГРН.
    cursor.execute('SELECT * FROM companies WHERE ogrn = ?', (ogrn,))
    existing_company = cursor.fetchone()

    if existing_company:
        existing_date = existing_company[2]
        if date < existing_date:
            # Обновляем запись, если дата новее.
            cursor.execute('''
                UPDATE companies
                SET inn = ?, date = ?, name = ?
                WHERE ogrn = ?
            ''', (inn, date, name, ogrn))
            insert_phones_company(company)
            print(f'Компания с ОГРН {ogrn} обновлена.')
        else:
            print(f'Компания с ОГРН {ogrn} не обновлена, так как дата старше.')
    else:
        # Добавляем новую компанию.
        cursor.execute('''
            INSERT INTO companies (ogrn, inn, date, name)
            VALUES (?, ?, ?, ?)
        ''', (ogrn, inn, date, name))
        insert_phones_company(company)
        print(f'Компания с ОГРН {ogrn} добавлена в базу.')


# Функция для добавления телефонов в базу данных.
def insert_phones_company(company):
    for phone in company['phones']:
        cursor.execute('''
            INSERT OR IGNORE INTO company_phones (ogrn, phone)
            VALUES (?, ?)
        ''', (company['ogrn'], phone.text))
    print(f'Телефоны для компании с ОГРН {company["ogrn"]} добавлены в базу.')


# Парсинг XML файла.
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for company_elem in root.findall('КОМПАНИЯ'):
        company = {
            'ogrn': company_elem.find('ОГРН').text,
            'inn': company_elem.find('ИНН').text,
            'name': company_elem.find('НазваниеКомпании').text if company_elem.find('НазваниеКомпании') is not None else None,
            'date': company_elem.find('ДатаОбн').text,
            'phones': company_elem.findall('Телефон') if company_elem.findall('Телефон') is not None else None
        }

        # Валидация компании.
        if is_valid_company(company):
            insert_or_update_company(company)  # Добавляем компанию.
        else:
            print(f'Компания с ОГРН {company["ogrn"]} не прошла валидацию и не будет добавлена.')


if __name__ == '__main__':
    # Подключение к базе данных SQLite.
    conn = sqlite3.connect('companies.db')
    cursor = conn.cursor()

    # Создаем таблицу для компаний.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        ogrn TEXT PRIMARY KEY,
        inn TEXT NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL
        )
    ''')

    # Создаем таблицу для телефонов компании.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company_phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ogrn TEXT NOT NULL,
        phone TEXT,
        FOREIGN KEY (ogrn) REFERENCES companies (ogrn) ON DELETE CASCADE,
        UNIQUE (ogrn, phone)
        );
    ''')

    # Запускаем обработку XML файла.
    parse_xml('companies.xml')

    # Сохраняем изменения и закрываем соединение с базой данных.
    conn.commit()
    conn.close()
