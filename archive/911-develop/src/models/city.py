from general_layout.models.abs_city import CityAbs


class City(CityAbs):

    class Meta:
        db_table = "city_db"
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.title
