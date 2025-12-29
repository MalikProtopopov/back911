from typing import Optional

from src.elastic.search import get_all_partners_for_admin_es


def sort_partners_by_name(partners: list[dict]) -> list[dict]:
    return sorted(
        partners,
        key=lambda x: (
            (x.get("first_name") or "").strip().casefold(),
            (x.get("last_name") or "").strip().casefold(),
        ),
    )


def get_partners_for_admin(
    search_query: Optional[str] = None,
    filters: Optional[dict] = None,
) -> tuple[list[dict], int]:
    filters = filters or {}

    all_partners, total_count = get_all_partners_for_admin_es(
        search_query=search_query,
        filters=filters,
    )

    sorted_partners = sort_partners_by_name(all_partners)
    return sorted_partners, total_count
