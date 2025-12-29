from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from src.models import Service, TechnicCategory, Partner, City, PartnerService, Option
from src.services.partner.partner_orm import PartnerServiceRepository


class PartnerORMTestCase(APITestCase):
    def setUp(self):
        self.city = City.objects.create(title="test_city")
        self.service = Service.objects.create(title="test_service")
        self.service2 = Service.objects.create(title="test_service2")
        self.option = Option.objects.create(title="test_option", service=self.service)
        self.option2 = Option.objects.create(title="test_option2", service=self.service)
        self.option3 = Option.objects.create(
            title="test_option3", service=self.service2
        )
        self.technic_category = TechnicCategory.objects.create(title="test_category")
        self.partner = Partner.objects.create(
            first_name="test_first_name",
            last_name="test_last_name",
            city=self.city,
            legal_status=Partner.LegalStatuses.individual,
            verify=Partner.VerifyPartnerStatuses.confirmed,
        )
        self.partner_orm = PartnerServiceRepository(
            partner=self.partner,
            options_list=[self.option.id, self.option2.id],
            service_id=self.service.id,
            technic_category_id=self.technic_category.id,
        )
        self.partner_service = PartnerService.objects.create(
            verify_status=PartnerService.VerifyStatuses.confirmed,
            partner=self.partner,
            technic_category=self.technic_category,
        )

    def test_get_partner_service(self):
        partner_service = self.partner_orm.get_partner_service()
        self.assertEqual(partner_service, self.partner_service)

    def test_add_new_service_correct(self):
        technic_category2 = TechnicCategory.objects.create(title="test_category2")
        new_partner_service = PartnerServiceRepository(
            partner=self.partner,
            options_list=[self.option.id, self.option2.id],
            service_id=self.service.id,
            technic_category_id=technic_category2.id,
        ).add_new_service()
        self.assertIsInstance(new_partner_service, PartnerService)
        self.assertIsNotNone(new_partner_service)

    def test_add_new_service_incorrect(self):
        with self.assertRaises(ValidationError):
            PartnerServiceRepository(
                partner=self.partner,
                options_list=[self.option.id],
                service_id=self.service.id,
                technic_category_id=self.technic_category.id,
            ).add_new_service()
