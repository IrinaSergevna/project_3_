from dotenv import load_dotenv
import os
import traceback
from src.hh_api import HhApi
from src.db_setup import create_database, create_tables, drop_tables
from src.db_manager import DBManager
from src.data_processor import save_to_json, load_to_db
from src.config import Config
from src.utils import format_salary

load_dotenv()


def main():
    try:
        config = Config()
        db_params = config.get_db_params()
        print("Подключено", flush=True)
        create_database(db_params)
        drop_tables(db_params)
        create_tables(db_params)

        # Получение данных
        hh_api = HhApi()
        employer_ids = ["1740", "80", "15478", "3529", "78638", "2180", "39305", "4219", "676", "1455"]  # Пример компаний
        employers = hh_api.get_employers(employer_ids)
        vacancies = []
        employer_vacancy_counts = {}

        for emp_id in employer_ids:
            total_vacancies, emp_vacancies = hh_api.get_vacancies(emp_id)
            employer_vacancy_counts[emp_id] = total_vacancies
            vacancies.extend(emp_vacancies)  # Загружаем только первую страницу для БД

        # Сохранение в JSON
        save_to_json(employers, "data/companies.json")
        save_to_json(vacancies, "data/vacancies.json")

        # Загрузка в БД
        load_to_db(db_params, employers, vacancies)

        # Интерфейс пользователя
        db_manager = DBManager(db_params)
        while True:
            print("\n1. Список компаний и количество вакансий")
            print("2. Список всех вакансий")
            print("3. Средняя зарплата")
            print("4. Вакансии с зарплатой выше средней")
            print("5. Вакансии по ключевому слову")
            print("0. Выход")

            choice = input("Выберите действие: ")
            if choice == "1":
                for emp in employers:
                    emp_id = emp["id"]
                    total = employer_vacancy_counts.get(emp_id, 0)
                    print(f"Компания: {emp['name']}, Вакансий: {total}")
            elif choice == "2":
                for vac in db_manager.get_all_vacancies():
                    salary = format_salary(vac["salary_from"], vac["salary_to"])
                    print(
                        f"Компания: {vac['company']}, Вакансия: {vac['vacancy']}, Зарплата: {salary}, Ссылка: {vac['url']}")
                # Подсчёт и вывод общего количества вакансий
                total_all_vacancies = sum(employer_vacancy_counts.values())
                print(f"\nОбщее количество вакансий всех компаний: {total_all_vacancies}", flush=True)
            elif choice == "3":
                avg_salary = db_manager.get_avg_salary()
                print(f"Средняя зарплата: {avg_salary:.2f}")
            elif choice == "4":
                for vac in db_manager.get_vacancies_with_higher_salary():
                    salary = format_salary(vac["salary_from"], vac["salary_to"])
                    print(
                        f"Компания: {vac['company']}, Вакансия: {vac['vacancy']}, Зарплата: {salary}, Ссылка: {vac['url']}")
            elif choice == "5":
                keyword = input("Введите ключевое слово: ")
                for vac in db_manager.get_vacancies_with_keyword(keyword):
                    salary = format_salary(vac["salary_from"], vac["salary_to"])
                    print(
                        f"Компания: {vac['company']}, Вакансия: {vac['vacancy']}, Зарплата: {salary}, Ссылка: {vac['url']}")
            elif choice == "0":
                break
    except Exception as e:
        print("Произошла ошибка:")
        traceback.print_exc()


if __name__ == "__main__":
    main()