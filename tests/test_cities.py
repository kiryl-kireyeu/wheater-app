from app.core.cities import CITIES


def test_required_cities_are_configured_in_stable_order() -> None:
    city_names = [city.name for city in CITIES]

    assert city_names == ["Warsaw", "Gdansk", "Berlin", "Krakow", "Nurnberg", "Munich"]


def test_city_coordinates_are_present() -> None:
    for city in CITIES:
        assert city.country
        assert -90 <= city.latitude <= 90
        assert -180 <= city.longitude <= 180
