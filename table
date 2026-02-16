import requests
from decouple import config
from terminaltables import AsciiTable


LANGUAGES = [
    "Python",
    "Java",
    "JavaScript",
    "C#",
    "C++",
    "PHP",
    "Go",
    "Ruby",
]

MAX_VACANCIES_TO_PROCESS = 1000
PER_PAGE = 100

TABLE_HEADER = [
    "Язык программирования",
    "Найдено вакансий",
    "Обработано вакансий",
    "Средняя зарплата",
]


HH_URL = "https://api.hh.ru/vacancies"


def predict_hh_salary(vacancy: dict):
    salary = vacancy.get("salary")

    if not salary:
        return None

    if salary.get("currency") != "RUR":
        return None

    salary_from = salary.get("from")
    salary_to = salary.get("to")

    if salary_from is not None and salary_to is not None:
        return (salary_from + salary_to) / 2
    elif salary_from is not None:
        return salary_from * 1.2
    elif salary_to is not None:
        return salary_to * 0.8

    return None


def get_hh_language_stats(lang: str) -> dict:
    salaries = []
    vacancies_processed = 0
    page = 0
    vacancies_found = 0

    while vacancies_processed < MAX_VACANCIES_TO_PROCESS:
        params = {
            "text": lang,
            "per_page": PER_PAGE,
            "page": page,
            "area": 1,
        }
        response = requests.get(HH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if page == 0:
            vacancies_found = data.get("found", 0)

        items = data.get("items", [])
        if not items:
            break

        for vacancy in items:
            if vacancies_processed >= MAX_VACANCIES_TO_PROCESS:
                break
            salary = predict_hh_salary(vacancy)
            if salary is not None:
                salaries.append(salary)
            vacancies_processed += 1

        if len(items) < PER_PAGE:
            break
        page += 1

    average_salary = int(sum(salaries) / len(salaries)) if salaries else 0

    return {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }


def print_hh_table():
    table_data = [TABLE_HEADER]

    for lang in LANGUAGES:
        stats = get_hh_language_stats(lang)
        table_data.append(
            [
                lang,
                stats["vacancies_found"],
                stats["vacancies_processed"],
                stats["average_salary"],
            ]
        )

    table = AsciiTable(table_data, "HeadHunter Moscow")
    print(table.table)


SJ_API_KEY = config("API_KEY")
SJ_URL = "https://api.superjob.ru/2.0/vacancies/"

SJ_HEADERS = {
    "X-Api-App-Id": SJ_API_KEY,
}


def predict_sj_salary(vacancy: dict):
    currency = vacancy.get("currency")
    payment_from = vacancy.get("payment_from")
    payment_to = vacancy.get("payment_to")

    if currency and currency.upper() not in ("RUB", "RUR"):
        return None

    if payment_from and payment_to:
        return (payment_from + payment_to) / 2
    elif payment_from:
        return payment_from * 1.2
    elif payment_to:
        return payment_to * 0.8

    return None


def get_sj_keyword_stats(keyword: str, town: int = 4) -> dict:
    salaries = []
    vacancies_processed = 0
    page = 0
    vacancies_found = 0

    while vacancies_processed < MAX_VACANCIES_TO_PROCESS:
        params = {
            "count": PER_PAGE,
            "page": page,
            "keyword": keyword,
            "town": town,
        }
        response = requests.get(SJ_URL, headers=SJ_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if page == 0:
            vacancies_found = data.get("total", 0)

        objects = data.get("objects", [])
        if not objects:
            break

        for vacancy in objects:
            if vacancies_processed >= MAX_VACANCIES_TO_PROCESS:
                break
            salary = predict_sj_salary(vacancy)
            if salary is not None:
                salaries.append(salary)
            vacancies_processed += 1

        if len(objects) < PER_PAGE:
            break
        page += 1

    average_salary = int(sum(salaries) / len(salaries)) if salaries else 0

    return {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }


def print_superjob_table():
    table_data = [TABLE_HEADER]

    for lang in LANGUAGES:
        stats = get_sj_keyword_stats(lang)
        table_data.append(
            [
                lang,
                stats["vacancies_found"],
                stats["vacancies_processed"],
                stats["average_salary"],
            ]
        )

    table = AsciiTable(table_data, "SuperJob Moscow")
    print(table.table)


def main():
    print_hh_table()
    print() 
    print_superjob_table()


if __name__ == "__main__":
    main()

