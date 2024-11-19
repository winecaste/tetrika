import functools
import inspect


def strict(func):
    """
    Декоратор для строгой проверки типов аргументов и возвращаемого значения.

    Декоратор анализирует аннотации типов функции и выполняет следующие проверки:
    - Проверяет соответствие типов входящих аргументов
    - Проверяет соответствие типа возвращаемого значения

    Вызывает TypeError в случае несоответствия типов.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Получаем сигнатуру функции для связывания аргументов
        sig = inspect.signature(func)

        # Связываем переданные аргументы с параметрами функции
        # Применяем значения по умолчанию, если они есть
        bound_arguments = sig.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        # Проверяем типы каждого аргумента
        for param_name, param_value in bound_arguments.arguments.items():
            # Получаем ожидаемый тип из аннотации функции
            expected_type = func.__annotations__.get(param_name)

            # Если тип указан, проверяем соответствие
            if expected_type and not isinstance(param_value, expected_type):
                # Формируем информативное сообщение об ошибке
                raise TypeError(
                    f"Аргумент '{param_name}' должен быть типа {expected_type}, "
                    f"передан {type(param_value)}"
                )

        # Вызываем оригинальную функцию
        result = func(*args, **kwargs)

        # Проверяем тип возвращаемого значения
        return_type = func.__annotations__.get('return')

        # Если тип возврата указан, проверяем соответствие
        if return_type and not isinstance(result, return_type):
            raise TypeError(
                f"Возвращаемое значение должно быть типа {return_type}, "
                f"получено {type(result)}"
            )

        return result
    return wrapper


# Примеры использования декоратора
@strict
def sum_two(a: str, b: str) -> str:
    """
    Простой пример функции с проверкой типов.
    Складывает два целых числа.
    """
    return a + b

print(sum_two('a', 'b'))