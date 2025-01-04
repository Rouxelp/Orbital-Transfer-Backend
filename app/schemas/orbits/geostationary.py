from typing import Optional
from app.schemas.bodies.earth import Earth
from app.schemas.orbits.orbit_base import OrbitBase

class GeostationaryOrbit(OrbitBase):
    """
    Represents a geostationary orbit, which is circular, equatorial, and has a specific altitude
    allowing a satellite to remain fixed relative to a point on Earth's surface.
    """
    def __init__(self, central_body: Earth = Earth(), name: Optional[str] = "Geostationary Orbit") -> None:
        """
        Initialize a GeostationaryOrbit instance.

        Args:
            central_body (Earth, optional): The central body for the orbit (default is Earth).
            id (int, optional): Unique identifier for the orbit.
            name (str, optional): Name of the orbit (default is "Geostationary Orbit").
        """
        # Geostationary orbit parameters
        altitude = 42164  # km
        inclination = 0.0  # Equatorial
        raan = 0.0        # Right Ascension of Ascending Node
        argp = 0.0        # Argument of Perigee
        nu = 0.0          # True Anomaly

        # Call the base class constructor with the geostationary parameters
        super().__init__(
            altitude_perigee=altitude,
            altitude_apogee=altitude, 
            inclination=inclination,
            raan=raan,
            argp=argp,
            nu=nu,
            central_body=central_body,
            name=name
        )
