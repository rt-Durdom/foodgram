from django.core.validators import RegexValidator

validate_username = RegexValidator(
    r'^[\w.@+-]+$',
    message='Имя пользователя содержит недопустимые символы',
    code='invalid_username'
)
