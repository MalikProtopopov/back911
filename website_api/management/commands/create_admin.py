"""
Management command to create a superuser for Django Admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Создает суперпользователя для доступа к Django Admin'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя (по умолчанию: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@911.ru',
            help='Email пользователя (по умолчанию: admin@911.ru)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Пароль (если не указан, будет использован "admin123")'
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Не запрашивать подтверждение, использовать значения по умолчанию'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password'] or 'admin123'
        noinput = options['noinput']

        # Проверяем, существует ли уже пользователь
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Пользователь "{username}" уже существует!'
                )
            )
            if not noinput:
                update = input('Обновить пароль? (y/n): ')
                if update.lower() == 'y':
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Пароль для пользователя "{username}" обновлен!'
                        )
                    )
                else:
                    self.stdout.write('Отменено.')
            return

        # Создаем нового суперпользователя
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Суперпользователь "{username}" успешно создан!'
                )
            )
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Пароль: {password}')
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  ВНИМАНИЕ: Измените пароль после первого входа!'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании пользователя: {e}')
            )


