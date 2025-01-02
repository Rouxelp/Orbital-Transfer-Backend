import pytest
from astropy import units as u
from app.schemas.orbits.geostationary import GeostationaryOrbit

def test_geostationary_orbit():
    """
    Test the initialization of a GeostationaryOrbit.
    """
    # Initialize a Geostationary Orbit
    geo_orbit = GeostationaryOrbit()

    # Validate key parameters
    assert geo_orbit.central_body.name == "Earth", "Central body should be Earth"
    assert geo_orbit.altitude_perigee.to(u.km).value == pytest.approx(42164, rel=1e-3), "Altitude perigee should be ~35,786 km"
    assert geo_orbit.altitude_apogee.to(u.km).value == pytest.approx(42164, rel=1e-3), "Altitude apogee should be ~35,786 km"
    assert geo_orbit.inclination.to(u.deg).value == pytest.approx(0.0, rel=1e-3), "Inclination should be 0°"
    assert geo_orbit.semi_major_axis.to(u.km).value == pytest.approx(42164, rel=1e-3), "Semi-major axis should be ~42,164 km"
    assert float(geo_orbit.eccentricity) == pytest.approx(0.0, rel=1e-3), "Eccentricity should be 0 (circular orbit)"