# &nbsp; 📚 Парсер данных о книгах с сайта [Books to Scrape](https://books.toscrape.com/)

 <hr>
 
## 📁 Структура проекта

```text
books_parser/
├── 📁 artifacts/                 # Результаты парсинга
│   └── 📄 books_data.txt
├── 📁 notebooks/                 # Jupyter блокнот с примерами работы кода
│   └── 📄 HW_03_python_ds_2025.ipynb
├── 📁 tests/                     # Тесты
│   └── 📄 test_scraper.py
├── 📄 scraper.py                # Основной скрипт парсера
├── 📄 requirements.txt          # Зависимости проекта
├── 📄 README.md                # Документация
└── 📄 .gitignore               # Игнорируемые файлы

```
 <hr>
 
## 🚀 Инструкция по запуску

### 1. Клонирование репозитория

```bash
git clone https://github.com/steishas/books_parser
cd books_parser
```
 
### 2. Создание виртуального окружения

**На Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```
**На Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```
 
### 4. Запуск парсера

<details>
<summary><b>Для всех страниц</b></summary>
  
```bash
python scraper.py
```
</details>

<details>
<summary><b>С сохранением результата</b></summary>

```bash
python -c "from scraper import scrape_books; scrape_books(save_flag=True)"
```
</details>
  
 <details>
<summary><b>С ограничением по страницам</b></summary>

```bash
python -c "from scraper import scrape_books; scrape_books(save_flag=True, pages_num=3)"
```
</details>

### 5. Запуск тестов

```bash
python -m pytest tests/ -v
```

### 6. Запуск Jupyter блокнота

```bash
jupyter notebook notebooks/Смирнова_А_М_HW_03.ipynb
```
<hr>

## 🚀 **Примеры работы функций**

```python
from scraper import scrape_books, get_book_data

# Парсинг одной книги
book_data = get_book_data("http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")

# Парсинг всех книг с сохранением
df = scrape_books(save_flag=True)

# Парсинг ограниченного количества страниц
df = scrape_books(save_flag=True, pages_num=5)
```
<hr>

## Зависимости проекта

- `requests` - HTTP-запросы;

- `beautifulsoup4` - парсинг HTML;

- `pandas` - работа с данными;

- `pytest` - тестирование;

- `jupyter` - интерактивные ноутбуки;

Полный список в requirements.txt
<hr>

## Тестирование
```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск с детальным выводом
python -m pytest tests/ -v

# Запуск конкретного теста
python -m pytest tests/test_scraper.py::test_get_book_data -v
```
## 🔧 Настройка

Параметры функции `scrape_books()`:
- `save_flag` (bool): Сохранять ли результаты в файл (по умолчанию `False`);

- `pages_num` (int): Ограничение количества страниц (по умолчанию `None` - все страницы)

## 📄 Результаты

Результаты парсинга сохраняются в:

- `artifacts/books_data.txt` - текстовый формат

- `DataFrame` с полной структурой данных

## 💻 Разработка

**Требования к окружению:**
Python 3.10+

Установленные зависимости из requirements.txt
  



