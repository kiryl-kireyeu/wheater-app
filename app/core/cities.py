from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class City:
    name: str
    country: str
    latitude: float
    longitude: float


# The task defines a fixed city list, and Open-Meteo weather endpoints require coordinates.
# Keeping coordinates static avoids unnecessary geocoding calls and makes scoring deterministic.
CITIES: tuple[City, ...] = (
    City(name="Warsaw", country="Poland", latitude=52.2297, longitude=21.0122),
    City(name="Gdansk", country="Poland", latitude=54.3520, longitude=18.6466),
    City(name="Berlin", country="Germany", latitude=52.5200, longitude=13.4050),
    City(name="Krakow", country="Poland", latitude=50.0647, longitude=19.9450),
    City(name="Nurnberg", country="Germany", latitude=49.4521, longitude=11.0767),
    City(name="Munich", country="Germany", latitude=48.1351, longitude=11.5820),
)
