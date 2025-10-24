# scraper.py

import os
import time

import pandas as pd
import requests
import schedule
from bs4 import BeautifulSoup


def get_book_data(book_url: str) -> pd.DataFrame:
    """
    Получает данные о книге со страницы и возвращает в виде DataFrame.

    Args:
        book_url (str): Ссылка на страницу с информацией о книге

    Returns:
        pd.DataFrame: DataFrame с одной строкой, содержащей информацию о книге.
                     Возвращает пустой DataFrame в случае ошибки.
    """
    try:
        # Отправляем запрос к странице и загружаем данные
        response = requests.get(book_url)

        if response.status_code != 200:
            error_log = (
                f"Ошибка при загрузке страницы {book_url}: {response.status_code}"
            )
            print(error_log)
            return pd.DataFrame()  # Возвращает пустой датафрейм в случае ошибки

        # Преобразуем HTML в объект BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Создаем словарь для записи данных
        book_info = {}

        # Извлекаем данные с проверкой на существование элементов
        title_elem = soup.find("li", class_="active")
        title = title_elem.text if title_elem else "No title"

        breadcrumb_elem = soup.find("ul", class_="breadcrumb")
        genre = breadcrumb_elem.text.split(
        )[2] if breadcrumb_elem else "No genre"

        rating_elem = soup.find('p', class_='star-rating')
        rating_text = rating_elem.get(
            "class")[1] if rating_elem else "No rating"

        # Извлекаем описание
        description_div = soup.find('div', id='product_description')
        if description_div:
            description_p = description_div.find_next_sibling('p')
            description = (description_p.text.strip()
                           if description_p else "No description")
        else:
            description = "No description"

        product_information = soup.find(
            "table", class_="table table-striped"
        ).text.split()

        upc = product_information[0] if len(product_information) > 0 else ""
        product_type = (
            product_information[2][4:] if len(product_information) > 2 else ""
        )
        price_excl_tax = (
            product_information[5][6:] if len(product_information) > 5 else ""
        )
        price_incl_tax = (
            product_information[8][6:] if len(product_information) > 8 else ""
        )
        tax = product_information[9][5:] if len(
            product_information) > 9 else ""
        in_stock = (product_information[13][1:] if len(
            product_information) > 13 else "")
        reviews_count = (
            product_information[18] if len(product_information) > 18 else ""
        )

        # Дополнительно преобразуем значения рейтинга в числовой формат
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        numeric_rating = rating_map.get(rating_text)

        # Записываем данные в словарь
        book_info["title"] = title
        book_info["genre"] = genre
        book_info["rating"] = numeric_rating
        book_info["upc"] = upc
        book_info["product_type"] = product_type
        book_info["price_excl_tax"] = price_excl_tax
        book_info["price_incl_tax"] = price_incl_tax
        book_info["tax"] = tax
        book_info["in_stock"] = in_stock
        book_info["reviews_count"] = reviews_count
        book_info["description"] = description
        book_info["url"] = book_url

        # Преобразуем словарь в DataFrame
        book_df = pd.DataFrame([book_info])

        return book_df

    except Exception as e:
        print(f"Неожиданная ошибка при обработке {book_url}: {e}")
        return pd.DataFrame()


def scrape_books(save_flag: bool = False,
                 pages_num: int = None) -> pd.DataFrame:
    """
    Собирает данные о книгах со страниц каталога.

    Args:
        save_flag (bool): True, если нужно сохранить результаты анализа
                         в текстовый файл (по умолчанию False)

        pages_num (int, optional): Количество страниц для парсинга.
                                  Если None - парсятся все страницы.

    Returns:
        pd.DataFrame: DataFrame с информацией о книгах
    """
    all_books = []
    page_num = 1

    while True:
        # Проверяем лимит страниц, если указан
        if pages_num is not None and page_num > pages_num:
            print(f"Достигнут установленный лимит в {pages_num} страниц(ы)")
            break

        # Формируем URL страницы
        if page_num == 1:
            page_url = "http://books.toscrape.com/catalogue/page-1.html"
        else:
            page_url = f"http://books.toscrape.com/catalogue/page-{page_num}.html"

        try:
            response = requests.get(page_url)

            # Проверяем, не достигнут ли конец каталога
            if response.status_code == 404:
                print("Достигнут конец каталога!")
                break

            if response.status_code != 200:
                print(
                    f"Возникла ошибка при обработке страницы №{page_num} "
                    f"(код: {response.status_code})"
                )
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # Находим все книги на странице
            book_elements = soup.find_all('article', class_='product_pod')

            if not book_elements:
                print("На странице нет книг, завершаем...")
                break

            # Обрабатываем каждую книгу на странице
            books_on_page = 0
            for book in book_elements:
                try:
                    # Получаем относительную ссылку и преобразуем в абсолютную
                    relative_link = book.h3.a['href']
                    # Исправляем путь - убираем лишние "catalogue/" если есть
                    if relative_link.startswith('catalogue/'):
                        # Убираем 'catalogue/'
                        relative_link = relative_link[10:]
                    book_url = f"http://books.toscrape.com/catalogue/{relative_link}"

                    # Получаем данные о книге
                    book_data = get_book_data(book_url)

                    if not book_data.empty:
                        all_books.append(book_data)
                        books_on_page += 1

                except Exception as e:
                    continue

            print(
                f"Страница {page_num}: успешно обработано "
                f"{books_on_page}/{len(book_elements)} книг"
            )

            # Переходим к следующей странице
            page_num += 1
            time.sleep(0.5)  # Делаем паузу между страницами

        except requests.RequestException as e:
            print(f"Ошибка сети на странице {page_num}: {e}")
            break
        except Exception as e:
            print(f"Неожиданная ошибка на странице {page_num}: {e}")
            break

    # Объединяем все данные
    if all_books:
        result_df = pd.concat(all_books, ignore_index=True)
        print(f"\nПарсинг завершен! Собрано данных о {len(result_df)} книгах")

        # Сохраняем данные в текстовый файл
        if save_flag:
            try:
                # Текущая директория
                current_dir = os.getcwd()

                # Корень проекта
                project_root = os.path.dirname(current_dir)

                # Путь к файлу
                file_path = os.path.join(
                    project_root, "artifacts", "books_data.txt")

                # Создаем папку artifacts в корне проекта
                artifacts_dir = os.path.join(project_root, "artifacts")
                os.makedirs(artifacts_dir, exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as file:
                    # Создаем шапку файла
                    file.write("-" * 70 + "\n")
                    file.write("Каталог книг с сайта Books to Scrape\n")
                    file.write("-" * 70 + "\n\n")
                    file.write(f"Всего книг в каталоге: {len(result_df)}\n")
                    file.write(f"Обработано страниц: {page_num - 1}\n")
                    if pages_num is not None:
                        file.write(f"Лимит страниц: {pages_num}\n")
                    file.write(
                        f"Дата создания отчета: "
                        f"{pd.Timestamp.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                    )

                    # Данные по каждой книге
                    for index, row in result_df.iterrows():
                        file.write(f"   Книга #{index + 1}\n")
                        file.write(f"   Название: {row.get('title', 'N/A')}\n")
                        file.write(f"   Жанр: {row.get('genre', 'N/A')}\n")
                        file.write(
                            f"   Рейтинг: {row.get('rating', 'N/A')}/5\n")
                        file.write(f"   UPC: {row.get('upc', 'N/A')}\n")
                        file.write(
                            f"   Цена (без налога): £{row.get('price_excl_tax', 'N/A')}\n"
                        )
                        file.write(
                            f"   Цена (с налогом): £{row.get('price_incl_tax', 'N/A')}\n"
                        )
                        file.write(f"   Налог: {row.get('tax', 'N/A')}\n")
                        file.write(
                            f"   В наличии: {row.get('in_stock', 'N/A')} шт.\n")
                        file.write(
                            f"   Отзывы: {row.get('reviews_count', 'N/A')}\n")
                        file.write(
                            f"   Описание: {row.get('description', 'N/A')}\n")
                        file.write(f"   Ссылка: {row.get('url', 'N/A')}\n")
                        file.write("-" * 70 + "\n\n")

                print("Данные успешно сохранены в файл 'artifacts/books_data.txt'")

            except Exception as e:
                print(f"Ошибка при сохранении файла: {e}")

        return result_df
    else:
        print("Не удалось собрать данные ни об одной книге")
        return pd.DataFrame()


def setup_parsing_schedule(start_time: str,
                           run_immediately: bool = False) -> None:
    """
    Настраивает и запускает ежедневный парсинг книг по расписанию.

    Args:
        start_time (str): Время запуска парсинга в формате 'HH:MM'
                         (например, '09:00')
        run_immediately (bool): Если True, запускает парсинг сразу при старте

    Returns:
        None
    """

    def parsing_task():
        """Внутренняя функция для выполнения парсинга"""
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Запуск парсинга с Books to Scrape в {current_time}")
        df = scrape_books(save_flag=True)

    # Настраиваем расписание
    schedule.every().day.at(start_time).do(parsing_task)
    print(f"Расписание настроено: ежедневный парсинг в {start_time}")

    # Запускаем сразу если нужно
    if run_immediately:
        print("Запуск немедленного парсинга...")
        parsing_task()

    # Бесконечный цикл проверки расписания
    print(f"Планировщик запущен. Начало парсинга в {start_time}")

    try:
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Проверяем каждый час
    except KeyboardInterrupt:
        print("\nПланировщик остановлен пользователем")