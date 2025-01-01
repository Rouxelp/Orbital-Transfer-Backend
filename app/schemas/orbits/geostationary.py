from app.schemas.bodies.earth import Earth
from app.schemas.orbits.orbit_base import OrbitBase


class GeostationaryOrbit(OrbitBase):
    def __init__(self, central_body: Earth = Earth()) -> None:
        altitude = 35786  # km
        inclination = 0.0  # Équatorial
        super().__init__(altitude, altitude, inclination, central_body=central_body)