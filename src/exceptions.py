import logging
import re

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class ContactAPIException(HTTPException):
    """Базовий клас для помилок Contact API"""
    pass


class ContactNotFoundError(ContactAPIException):
    """Контакт не знайдено"""

    def __init__(self, contact_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт з ID {contact_id} не знайдено",
        )


class EmailAlreadyExistsError(ContactAPIException):
    """Email вже існує"""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Контакт з email '{email}' вже існує. Використайте інший email.",
        )


class InvalidDataError(ContactAPIException):
    """Некоректні дані"""

    def __init__(self, details: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некоректні дані: {details}",
        )


def handle_database_error(error: Exception, operation: str = "операції") -> HTTPException:
    """Централізована обробка помилок бази даних"""

    if isinstance(error, IntegrityError):
        # Обробляємо помилки унікальності
        error_msg = str(error.orig)

        if "duplicate key value violates unique constraint" in error_msg:
            if "ix_contacts_email" in error_msg or "email" in error_msg:
                # Витягуємо email з повідомлення про помилку
                email_match = re.search(r"\(email\)=\(([^)]+)\)", error_msg)
                email = email_match.group(1) if email_match else "невідомий"
                raise EmailAlreadyExistsError(email)
            else:
                raise InvalidDataError("Дублювання унікального значення")

        elif "violates foreign key constraint" in error_msg:
            raise InvalidDataError("Порушення зв'язку з іншими записами")

        elif "violates not-null constraint" in error_msg:
            # Витягуємо назву поля
            field_match = re.search(r'column "([^"]+)"', error_msg)
            field = field_match.group(1) if field_match else "невідоме поле"
            raise InvalidDataError(f"Обов'язкове поле '{field}' не може бути пустим")

        else:
            logger.error(f"Невідома помилка цілісності даних під час {operation}: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Помилка цілісності даних. Перевірте правильність введених даних.",
            )

    else:
        # Загальна помилка бази даних
        logger.error(f"Помилка бази даних під час {operation}: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутрішня помилка сервера. Спробуйте пізніше.",
        )


def handle_validation_error(error: ValidationError) -> HTTPException:
    """Обробка помилок валідації Pydantic"""

    errors = []
    for err in error.errors():
        field = " -> ".join([str(loc) for loc in err["loc"]])
        message = err["msg"]
        errors.append(f"{field}: {message}")

    detail = "Помилки валідації: " + "; ".join(errors)

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
    )


def safe_database_operation(operation_func, operation_name: str = "операції"):
    """Декоратор для безпечного виконання операцій з базою даних"""

    def decorator(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except (IntegrityError, Exception) as e:
            handle_database_error(e, operation_name)

    return decorator