from celery import shared_task
from django.db.models import Avg

from src.documents import PartnerDocument
from src.models import Partner


@shared_task
def update_partner_rating(partner_id: int) -> None:
    """
    0. get partner
    1. get partner reviews
    2.
    """
    from src.models import Partner, Review

    partner = Partner.objects.get(id=partner_id)
    partner.rating = Review.objects.filter(partner=partner).aggregate(
        average=Avg("rating")
    )["average"]
    partner.save()


@shared_task
def update_partner_documents() -> None:
    for partner in Partner.objects.all():
        PartnerDocument().update(partner)
