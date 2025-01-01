import numpy as np
from astropy import units as u
from app.schemas.orbits.orbit_base import OrbitBase
from app.schemas.bodies.earth import Earth


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

        # Calculate semi-major axis
        semi_major_axis = (altitude_perigee + altitude_apogee) / 2 + central_body.radius.to(u.km).value

        # Calculate orbital period (Kepler's Third Law)
        mu = central_body.mu.to(u.km**3 / u.s**2).value
        orbital_period = 2 * np.pi * np.sqrt((semi_major_axis ** 3) / mu)

        # Calculate inclination for SSO
        J2 = 1.08263e-3  # Earth's second zonal harmonic coefficient
        Re = central_body.radius.to(u.km).value
        inclination = np.arccos(-2 / 3 * np.sqrt(mu) / (J2 * Re**2 * semi_major_axis**3.5 * orbital_period)) * (180 / np.pi)

        # Initialize the base class
        super().__init__(
            altitude_perigee=altitude_perigee,
            altitude_apogee=altitude_apogee,
            inclination=inclination,
            raan=raan,
            argp=argp,
            nu=nu,
            central_body=central_body
        )
