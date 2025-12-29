from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from src.models.administrator import Admin
from src.services.admin.admin_orm import AdminORM, UserAdminORM, AdminCreator
from users.models import CustomUser


class AdminORMTestCase(APITestCase):
    def setUp(self):
        self.user_login = "test_login"
        self.first_name = "test_first_name"
        self.admin1 = Admin.objects.create(
            first_name=self.first_name, user_login=self.user_login
        )

    def test_get_admin_correct(self):
        admin = AdminORM(
            first_name=self.first_name, user_login=self.user_login
        ).get_admin()
        self.assertEqual(admin, self.admin1)

    def test_get_admin_non_existing(self):
        admin = AdminORM(first_name="test", user_login="test").get_admin()
        self.assertEqual(admin, None)

    def test_create_admin_correct(self):
        admin = AdminORM(first_name="test", user_login="test").create_admin()
        self.assertIsNotNone(admin)
        self.assertIsInstance(admin, Admin)

    def test_create_admin_incorrect(self):
        with self.assertRaises(ValidationError):
            AdminORM(
                first_name=self.first_name, user_login=self.user_login
            ).create_admin()


class UserAdminORMTestCase(APITestCase):
    def setUp(self):
        self.phone1 = "1234"
        self.phone2 = "1111"
        self.password = "test_password"
        self.admin1 = AdminORM(first_name="test", user_login="test").create_admin()
        self.user1 = CustomUser.objects.create_user(self.phone2)
        self.superuser1 = CustomUser.objects.create_superuser(
            phone=self.phone1, password=self.password
        )
        self.user_admin_orm = UserAdminORM(phone=self.phone2, password=self.password)

    def test_create_new_superuser_correct(self):
        user = UserAdminORM(
            phone="1235", password="test_password"
        ).create_new_superuser(self.admin1)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, CustomUser)

    def test_create_new_superuser_incorrect(self):
        UserAdminORM(phone=self.phone1, password=self.password)
        self.assertRaises(ValidationError)

    def test_change_user_to_superuser_correct(self):
        self.assertFalse(self.user1.is_superuser)
        self.assertFalse(self.user1.is_staff)
        self.assertFalse(self.user1.is_admin)

        self.user_admin_orm.change_user_to_superuser(self.user1, self.admin1)

        self.user1.refresh_from_db()

        self.assertTrue(self.user1.is_superuser)
        self.assertTrue(self.user1.is_staff)
        self.assertTrue(self.user1.is_admin)
        self.assertEqual(self.user1.admin, self.admin1)

    def test_change_user_to_superuser_existing_admin(self):
        self.user1.admin = self.admin1
        self.user1.save()

        with self.assertRaises(ValidationError):
            self.user_admin_orm.change_user_to_superuser(self.user1, self.admin1)


class AdminCreatorTestCase(APITestCase):
    def setUp(self):
        self.user_login = "test_user_login"
        self.first_name = "test_first_name"
        self.phone = "1234"
        self.password = "test_password"
        self.admin_creator = AdminCreator(
            user_login=self.user_login,
            first_name=self.first_name,
            phone=self.phone,
            password=self.password,
        )

    def test_create_admin_with_user_new_admin_new_user(self):
        self.assertIsNone(Admin.objects.filter(user_login=self.user_login).first())
        self.assertIsNone(CustomUser.objects.filter(phone=self.phone).first())
        admin = self.admin_creator.create_admin_with_user()
        self.assertIsNotNone(admin)
        self.assertEqual(admin.user_login, self.user_login)
        self.assertEqual(admin.first_name, self.first_name)

        user = CustomUser.objects.filter(phone=self.phone).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.admin, admin)
        self.assertEqual(admin.current_user.phone, self.phone)

    def test_create_admin_with_existing_non_admin_user(self):
        user = CustomUser.objects.create_user(phone=self.phone)
        self.assertIsNone(user.admin)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)

        admin = self.admin_creator.create_admin_with_user()

        self.assertIsNotNone(admin)
        self.assertEqual(admin.user_login, self.user_login)
        self.assertEqual(admin.first_name, self.first_name)

        user.refresh_from_db()

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.admin, admin)

    def test_create_admin_with_existing_admin_user(self):
        CustomUser.objects.create_superuser(phone=self.phone, password=self.password)
        with self.assertRaises(ValidationError):
            self.admin_creator.create_admin_with_user()

    def test_create_admin_with_user_no_phone(self):
        admin_creator = AdminCreator(
            user_login=self.user_login,
            first_name=self.first_name,
            phone=None,
            password=self.password,
        )

        admin = admin_creator.create_admin_with_user()

        self.assertIsNotNone(admin)
        self.assertEqual(admin.user_login, self.user_login)
        self.assertEqual(admin.first_name, self.first_name)

        user = CustomUser.objects.filter(phone=None).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.admin, admin)
