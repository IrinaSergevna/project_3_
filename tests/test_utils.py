import pytest
from src.utils import format_salary


def test_format_salary_both_values():
    """Тест форматирования зарплаты с обоими значениями."""
    result = format_salary(100000, 150000)
    assert result == "от 100000 до 150000"

def test_format_salary_only_from():
    """Тест форматирования зарплаты только с начальным значением."""
    result = format_salary(100000, None)
    assert result == "от 100000"

def test_format_salary_only_to():
    """Тест форматирования зарплаты только с конечным значением."""
    result = format_salary(None, 150000)
    assert result == "до 150000"

def test_format_salary_no_values():
    """Тест форматирования зарплаты без значений."""
    result = format_salary(None, None)
    assert result == "не указана"

def test_format_salary_zero_both():
    """Тест форматирования с нулевыми значениями."""
    result = format_salary(0, 0)
    assert result == "от 0 до 0"

def test_format_salary_zero_from():
    """Тест форматирования с нулевым начальным значением."""
    result = format_salary(0, 150000)
    assert result == "от 0 до 150000"

def test_format_salary_zero_to():
    """Тест форматирования с нулевым конечным значением."""
    result = format_salary(100000, 0)
    assert result == "от 100000 до 0"