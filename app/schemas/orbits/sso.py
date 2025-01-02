import numpy as np
from astropy import units as u
from app.schemas.orbits.orbit_base import OrbitBase
from app.schemas.bodies.earth import Earth
from logger_handler import handle_logger

logger = handle_logger()

class SunSynchronousOrbit(OrbitBase):
    """
    A specialized subclass for Sun Synchronous Orbits.
    Calculates inclination based on altitude and ensures Earth as the central body.
    """

    def __init__(
        self,
        altitude_perigee: float,
        altitude_apogee: float,
        raan: float = 0.0,
        argp: float = 0.0,
        nu: float = 0.0,
        central_body: Earth = Earth(),
    ) -> None:
        """
        Initializes a Sun Synchronous Orbit instance.

        Args:
            altitude_perigee (float): Altitude of the perigee (in km).
            altitude_apogee (float): Altitude of the apogee (in km).
            raan (float): Right ascension of the ascending node (in degrees).
            argp (float): Argument of perigee (in degrees).
            nu (float): True anomaly (in degrees).
            central_body (Earth): Central body for the orbit (default is Earth).
        """
        if not isinstance(central_body, Earth):
            raise TypeError("SunSynchronousOrbit is only valid for Earth as the central body.")

        # Constants
        J2 = 1.08263e-3  # Earth's second zonal harmonic coefficient
        Re = central_body.radius.to(u.m)  # Earth's equatorial radius in meters
        mu = central_body.mu.to(u.m**3 / u.s**2)  # Gravitational parameter in m^3/s^2

        # Convert semi-major axis to meters
        semi_major_axis = ((altitude_perigee + altitude_apogee) / 2) * u.km.to(u.m) * u.m

        mean_motion = (1.991 * 10**-7) * (1 / u.s)  # Mean motion in rad/s

        # Calculate cos(inclination) for SSO
        cos_inclination = (
            -2
            / 3
            * mean_motion
            * np.sqrt(semi_major_axis**7)
            / (J2 * Re**2 * np.sqrt(mu))
        ).value
        if not -1 <= cos_inclination <= 1:
            logger.debug(f"cos_inclination: {cos_inclination}")  
            raise ValueError("The calculated inclination is out of valid bounds.")

        # Convert inclination to degrees
        inclination = float(np.arccos(cos_inclination) * (180 / np.pi))

        # Initialize the base class
        super().__init__(
            altitude_perigee=altitude_perigee,
            altitude_apogee=altitude_apogee,
            inclination=inclination,
            raan=raan,
            argp=argp,
            nu=nu,
            central_body=central_body,
        )
