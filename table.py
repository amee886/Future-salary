import json
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

PER_PAGE = 100

TABLE_HEADER = [
    "Язык программирования",
    "Найдено вакансий",
    "Обработано вакансий",
    "Средняя зарплата",
]


HH_URL = "https://api.hh.ru/vacancies"


SJ_API_KEY = config("API_KEY")
SJ_URL = "https://api.superjob.ru/2.0/vacancies/"

SJ_HEADERS = {
    "X-Api-App-Id": SJ_API_KEY,
}

def calculate_average_salary(salaries: list) -> int:
    """Вычисляет среднюю зарплату по списку. Возвращает 0 для пустого списка."""
    return int(sum(salaries) / len(salaries)) if salaries else 0


def predict_salary(vacancy: dict):
    """Предсказывает зарплату по вакансии HeadHunter или SuperJob."""
    salary = vacancy.get("salary")

    if salary is not None:
        if not salary:
            return
        currency = salary.get("currency")
        salary_from = salary.get("from")
        salary_to = salary.get("to")
    else:
        currency = vacancy.get("currency")
        salary_from = vacancy.get("payment_from")
        salary_to = vacancy.get("payment_to")

    if currency and currency.upper() not in ("RUB", "RUR"):
        return

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    if salary_to:
        return salary_to * 0.8


def get_hh_language_stats(lang: str, area: int = 1) -> dict:
    salaries = []
    page = 0
    vacancies_found = 0

    while True:
        params = {
            "text": lang,
            "per_page": PER_PAGE,
            "page": page,
            "area": area,
        }
        response = requests.get(HH_URL, params=params)

        if not response.ok:
            try:
                error_body = response.json() if response.text else {}
            except json.JSONDecodeError:
                response.raise_for_status()
            bad_args = str(error_body.get("bad_arguments", "")) + str(error_body.get("bad_argument", ""))
            if "page" in bad_args.lower() or "per_page" in bad_args.lower():
                break
            response.raise_for_status()

        data = response.json()

        if page == 0:
            vacancies_found = data.get("found", 0)

        items = data.get("items", [])
        if not items:
            break

        for vacancy in items:
            salary = predict_salary(vacancy)
            if salary:
                salaries.append(salary)

        if len(items) < PER_PAGE:
            break
        page += 1

    return {
        "vacancies_found": vacancies_found,
        "vacancies_processed": len(salaries),
        "average_salary": calculate_average_salary(salaries),
    }


def collect_stats(get_stats_func, languages=LANGUAGES):
    """Собирает статистику по языкам, не строя таблицу."""
    stats_by_language = []
    for lang in languages:
        stats_by_language.append((lang, get_stats_func(lang)))
    return stats_by_language


def build_stats_table_rows(stats_by_language, title: str) -> AsciiTable:
    """Создаёт готовую AsciiTable по уже рассчитанной статистике."""
    table_data = [TABLE_HEADER]
    for lang, stats in stats_by_language:
        table_data.append(
            [
                lang,
                stats["vacancies_found"],
                stats["vacancies_processed"],
                stats["average_salary"],
            ]
        )

    return AsciiTable(table_data, title)


def get_sj_keyword_stats(keyword: str, town: int = 4) -> dict:
    salaries = []
    page = 0
    vacancies_found = 0

    while True:
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
            salary = predict_salary(vacancy)
            if salary:
                salaries.append(salary)

        if len(objects) < PER_PAGE:
            break
        page += 1

    return {
        "vacancies_found": vacancies_found,
        "vacancies_processed": len(salaries),
        "average_salary": calculate_average_salary(salaries),
    }


def main():
    hh_stats = collect_stats(get_hh_language_stats)
    hh_table = build_stats_table_rows(hh_stats, "HeadHunter Moscow")
    print(hh_table.table)

    print()

    sj_stats = collect_stats(get_sj_keyword_stats)
    sj_table = build_stats_table_rows(sj_stats, "SuperJob Moscow")
    print(sj_table.table)


if __name__ == "__main__":
    main()
