import pytest
from astropy import units as u
from app.schemas.orbits.sso import SunSynchronousOrbit


def test_sun_synchronous_orbit() -> None:
    """
    Test the creation and properties of a SunSynchronousOrbit.
    """
    sso_orbit = SunSynchronousOrbit(altitude_perigee=600 + 6378.137, altitude_apogee=600 + 6378.137)

    # Validate that the central body is Earth
    assert sso_orbit.central_body.name == "Earth"

    # Validate inclination is calculated (should be around 98° for this altitude)
    assert 97.0 <= sso_orbit.inclination.value <= 99.0

    # Validate semi-major axis
    expected_semi_major_axis = (600 + 6378.137 + 600 + 6378.137) / 2 # Perigee + Apogee
    assert sso_orbit.semi_major_axis.to(u.km).value == pytest.approx(expected_semi_major_axis, rel=1e-3)
