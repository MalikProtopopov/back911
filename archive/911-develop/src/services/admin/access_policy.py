from src.models import Partner, PartnerService
from src.models.administrator import Admin


class AdminAccessPolicy:
    @staticmethod
    def can_view_partners(admin: Admin) -> bool:
        return admin.role in {Admin.AdminRoles.super_admin, Admin.AdminRoles.operator}

    @staticmethod
    def can_view_or_edit_partner(admin: Admin, partner: Partner) -> bool:
        if admin.role == Admin.AdminRoles.super_admin:
            return True
        if admin.role == Admin.AdminRoles.operator:
            return partner.verify == Partner.VerifyPartnerStatuses.on_confirmation
        return False

    @staticmethod
    def can_approve_service(admin: Admin, service: PartnerService) -> bool:
        if admin.role == Admin.AdminRoles.super_admin:
            return True
        if admin.role == Admin.AdminRoles.operator:
            return (
                service.verify_status == PartnerService.VerifyStatuses.on_confirmation
            )
        return False

    @staticmethod
    def can_access_view(admin: Admin, action: str) -> bool:
        """Фолбек-доступ к определённым эндпоинтам"""
        if admin.role == Admin.AdminRoles.super_admin:
            return True
        if admin.role == Admin.AdminRoles.operator:
            return action in {
                "get_list_of_partners_on_confirmation_for_admin",
                "get_info_partner_for_admin",
                "update_partner",
                "get_list_of_services_on_confirmation_admin",
                "update_verify_status_for_service",
                "get_list_orders_for_admin",
                "get_list_of_order_conditions",
                "get_order_condition",
                "get_order_for_admin",
                "create_order_for_admin",
                "get_partner_list_for_order",
                "update_order_for_admin",
                "cancel_order_for_admin",
            }
        return False
