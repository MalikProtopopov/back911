import random

from src.models import Client, Partner
from src.models.administrator import Admin
from src.models.city import City
from users.models import CustomUser


class TestMockCreator:
    def create_random_text(self, letters_amount: int = 10) -> str:
        text = ""
        for _ in range(letters_amount):
            text += self.create_randletter()
        return text

    def create_randletter(self) -> str:
        return chr(random.randint(ord("a"), ord("z")))

    def create_randnumber(self, max_size: int = 9) -> int:
        rand_num = ""
        for _ in range(max_size):
            rand_num += str(random.randint(0, 9))
        return int(rand_num)

    def create_city(self):
        city = City.objects.create(title=self.create_random_text())
        return city

    def create_user(self):
        new_user = CustomUser.objects.create_user(phone=self.create_randnumber(10))
        return new_user

    def create_active_client(self):
        new_user = self.create_user()
        new_client = Client.objects.create(first_name=self.create_random_text(10))
        new_user.client = new_client
        new_user.save()
        return new_client

    def create_blocked_client(self):
        new_user = self.create_user()
        new_client = Client.objects.create(
            first_name=self.create_random_text(10), client_status=2
        )
        new_user.client = new_client
        new_user.save()
        return new_client

    def create_partner(self, legal_status="legal_entity"):
        new_user = self.create_user()
        new_partner = Partner.objects.create(
            first_name=self.create_random_text(10),
            last_name=self.create_random_text(10),
            legal_status=legal_status,
            city=self.create_city(),
        )
        new_user.partner = new_partner
        new_user.save()
        return new_partner

    def create_admin(self):
        new_user = self.create_user()
        new_admin = Admin.objects.create(
            first_name=self.create_random_text(10),
            user_login=self.create_random_text(10),
        )
        new_user.admin = new_admin
        new_user.save()
        return new_admin
