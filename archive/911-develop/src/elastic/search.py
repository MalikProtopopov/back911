from typing import Any

from elasticsearch_dsl import Q, Search
from rest_framework.exceptions import ValidationError

from src.documents import ClientDocument, WorkingZoneDocument
from src.documents.partner_document import PartnerDocument


def get_hit_departure_price(hit: Any):
    return hit.departure_price


def search_coordinates_contains_point(point: list[float]) -> tuple | str:
    search = WorkingZoneDocument.search().query(
        Q(
            "geo_shape",
            area_coordinates={
                "relation": "intersects",
                "shape": {"type": "point", "coordinates": point},
            },
        )
    )
    response = search.execute()
    if response.hits.total.value > 0:
        hit = min(response.hits, key=get_hit_departure_price)
        document_id = hit.meta.id
        departure_price = hit.departure_price
        fuel_delivery_price = hit.fuel_delivery_price
        return document_id, departure_price, fuel_delivery_price
    raise ValidationError({"error_message": "Указанный адрес не обслуживается"})


def search_for_partner(partner_data: str):
    query_value = partner_data.lower()
    search = PartnerDocument.search().query(
        Q(
            "bool",
            should=[
                Q("term", first_name__raw=query_value),
                Q("term", last_name__raw=query_value),
            ],
            minimum_should_match=1,
        )
    )
    response = search.execute()
    partner_id_list = [hit.meta.id for hit in response]
    return partner_id_list


def search_for_client(client_data: str):
    search = ClientDocument.search().query(
        Q(
            "bool",
            should=[
                Q("term", first_name__raw={"value": client_data.lower()}),
                Q("term", last_name__raw={"value": client_data.lower()}),
            ],
            minimum_should_match=1,
        )
    )
    response = search.execute()
    partner_id_list = [hit.meta.id for hit in response]
    return partner_id_list


def get_list_of_clients_for_admin_es(
    search_query: str = None,
    status_filter: str = None,
    per_page: int = 10,
    page: int = 1,
):
    s = Search(index="client")
    if search_query:
        query_value = search_query.lower()
        s = s.query(
            "bool",
            should=[
                {"term": {"first_name.raw": query_value}},
                {"term": {"phone.raw": query_value}},
            ],
            minimum_should_match=1,
        )
    else:
        s = s.sort("-datetime_created")

    if status_filter:
        s = s.filter("term", client_status=status_filter)

    start = (page - 1) * per_page
    s = s[start : start + per_page]
    response = s.execute()

    results = [
        {
            "id": hit.id,
            "first_name": hit.first_name,
            "phone": getattr(hit, "phone", None),
            "client_status": getattr(hit, "client_status", None),
            "datetime_created": getattr(hit, "datetime_created", None),
        }
        for hit in response
    ]
    return results, response.hits.total.value


def get_list_of_partners_for_admin_es(
    search_query: str = None,
    page: int = 1,
    per_page: int = 10,
    filters: dict = None,
):
    filters = filters or {}
    s = Search(index="partner")

    if search_query:
        q_val = search_query.lower()
        s = s.query(
            "bool",
            should=[
                {"term": {"first_name.raw": q_val}},
                {"term": {"last_name.raw": q_val}},
                {"term": {"phone.raw": q_val}},
            ],
            minimum_should_match=1,
        )
    else:
        s = s.sort("-datetime_created")

    q_filters = []

    if filters.get("verify"):
        q_filters.append(Q("term", verify=filters["verify"]))

    if filters.get("city"):
        q_filters.append(Q("term", city__id=filters["city"]))

    if filters.get("is_working") is not None:
        q_filters.append(Q("term", is_working=filters["is_working"]))

    if filters.get("services"):
        q_filters.append(
            Q(
                "nested",
                path="services",
                query=Q("term", services__service_id=filters["services"]),
            )
        )

    if q_filters:
        s = s.query(
            "bool", must=s.query if s.query else Q("match_all"), filter=q_filters
        )

    start = (page - 1) * per_page
    s = s[start : start + per_page]
    response = s.execute()
    results = [
        {
            "id": hit.id,
            "first_name": hit.first_name,
            "last_name": hit.last_name,
            "verify": hit.verify,
            "rating": hit.rating,
            "photo": hit.photo,
            "city": hit.city,
            "phone": getattr(hit, "phone", None),
            "datetime_created": getattr(hit, "datetime_created", None),
            "is_working": hit.is_working,
            "accepted_orders": hit.accepted_orders,
            "cancelled_orders": hit.cancelled_orders,
            "profit": hit.profit,
        }
        for hit in response
    ]
    return results, response.hits.total.value


def get_all_partners_for_admin_es(
    search_query: str = None,
    filters: dict = None,
):
    filters = filters or {}
    s = Search(index="partner")

    if search_query:
        q_val = search_query.lower()
        s = s.query(
            "bool",
            should=[
                {"term": {"first_name.raw": q_val}},
                {"term": {"last_name.raw": q_val}},
                {"term": {"phone.raw": q_val}},
            ],
            minimum_should_match=1,
        )
    else:
        s = s.sort("-datetime_created")

    q_filters = []

    if filters.get("verify"):
        q_filters.append(Q("term", verify=filters["verify"]))

    if filters.get("city"):
        q_filters.append(Q("term", city__id=filters["city"]))

    if filters.get("is_working") is not None:
        q_filters.append(Q("term", is_working=filters["is_working"]))

    if filters.get("services"):
        q_filters.append(
            Q(
                "nested",
                path="services",
                query=Q("term", services__service_id=filters["services"]),
            )
        )

    if q_filters:
        s = s.query(
            "bool", must=s.query if s.query else Q("match_all"), filter=q_filters
        )

    count_response = s.params(size=0).execute()
    total = count_response.hits.total.value

    if total > 0:
        s = s[0:total]

    response = s.execute()
    results = [
        {
            "id": hit.id,
            "first_name": hit.first_name,
            "last_name": hit.last_name,
            "verify": hit.verify,
            "rating": hit.rating,
            "photo": hit.photo,
            "city": hit.city,
            "phone": getattr(hit, "phone", None),
            "datetime_created": getattr(hit, "datetime_created", None),
            "is_working": hit.is_working,
            "accepted_orders": hit.accepted_orders,
            "cancelled_orders": hit.cancelled_orders,
            "profit": hit.profit,
        }
        for hit in response
    ]
    return results, total
