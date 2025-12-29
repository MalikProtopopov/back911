from string import ascii_lowercase, ascii_uppercase

from rest_framework.exceptions import ValidationError


def validate_for_phone_number(value: str) -> None:
    acceptable_chars = "+1234567890"
    for char in value:
        if char not in acceptable_chars:
            raise ValidationError("Недопустимое значение!")


def validate_charfield_for_letters(
    validate_data: str, error_type: str = "serializer"
) -> None:
    """
    Проверяет данные на наличие букв (русский и английский алфавиты).
    """
    eng_alphabet = list(ascii_uppercase + ascii_lowercase)
    rus_alphabet = [chr(i) for i in range(ord("А"), ord("а") + 32)]

    if error_type == "serializer":
        for symbol in validate_data:
            if symbol in rus_alphabet + eng_alphabet:
                raise ValidationError("Никаких букв!")
    elif error_type == "validator":
        for symbol in validate_data:
            if symbol in rus_alphabet + eng_alphabet:
                raise ValidationError("Номер телефона должен состоять из цифр")
    else:
        pass
