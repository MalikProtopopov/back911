from geojson import FeatureCollection

from src.models import WorkingZone


def update_working_zones(geo_json: FeatureCollection) -> None:
    new_zone_ids = []
    for feature in geo_json["features"]:
        try:
            area_coordinates = feature["geometry"]["coordinates"][0]
            title = feature["properties"]["description"]
            zone, created = WorkingZone.objects.get_or_create(
                title=title, defaults={"area_coordinates": area_coordinates}
            )
            if not created:
                zone.area_coordinates = area_coordinates
                zone.save()
            new_zone_ids.append(zone.id)
        except KeyError:
            pass
    WorkingZone.objects.exclude(id__in=new_zone_ids).delete()
