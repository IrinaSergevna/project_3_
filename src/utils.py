from typing import Optional


def format_salary(salary_from: Optional[int], salary_to: Optional[int]) -> str:
    """Форматирует зарплату для вывода."""
    if salary_from is not None and salary_to is not None:
        return f"от {salary_from} до {salary_to}"
    elif salary_from is not None:
        return f"от {salary_from}"
    elif salary_to is not None:
        return f"до {salary_to}"
    return "не указана"