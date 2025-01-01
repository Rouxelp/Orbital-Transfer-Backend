import pytest
from app.schemas.orbits.orbit_base import OrbitBase, SunSynchronousOrbit
from astropy import units as u

@pytest.fixture
def valid_orbit() -> OrbitBase:
    """
    Fixture to provide a valid OrbitBase instance with RAAN, ARG, and NU.
    """
    return OrbitBase(
        altitude_perigee=500,
        altitude_apogee=40000,
        inclination=28.5,
        raan=50.0,
        argp=45.0,
        nu=10.0
    )


def test_orbit_to_poliastro_orbit(valid_orbit: OrbitBase) -> None:
    """
    Test the conversion of an OrbitBase instance to a Poliastro Orbit object.
    """
    poliastro_orbit = valid_orbit.to_poliastro_orbit()
    assert poliastro_orbit.a.to(u.km).value == pytest.approx(20250, rel=1e-3)
    assert poliastro_orbit.ecc == pytest.approx(0.971, rel=1e-3)
    assert poliastro_orbit.inc.to(u.deg).value == pytest.approx(28.5, rel=1e-3)
    assert poliastro_orbit.raan.to(u.deg).value == pytest.approx(50.0, rel=1e-3)
    assert poliastro_orbit.argp.to(u.deg).value == pytest.approx(45.0, rel=1e-3)
    assert poliastro_orbit.nu.to(u.deg).value == pytest.approx(10.0, rel=1e-3)


def test_orbit_log_info(valid_orbit: OrbitBase, caplog) -> None:
    """
    Test the log_info method of OrbitBase.
    """
    valid_orbit.log_info()
    assert "Orbit - Perigee Altitude" in caplog.text
    assert "Eccentricity" in caplog.text
    assert "Inclination" in caplog.text


def test_orbit_visualize(valid_orbit: OrbitBase) -> None:
    """
    Test the visualize method of OrbitBase.
    """
    # This test should verify that the method runs without error.
    # Use mocking or skip actual plotting in test environments.
    try:
        valid_orbit.visualize()
    except Exception as e:
        pytest.fail(f"Visualization failed with exception: {e}")


def test_orbit_json():
    orbit = OrbitBase(500, 20000, 28.5, raan=60.0, argp=30.0, nu=20.0)
    json_data = orbit.to_json()
    reconstructed_orbit = OrbitBase.from_json(json_data)
    assert orbit.altitude_perigee == reconstructed_orbit.altitude_perigee
    assert orbit.altitude_apogee == reconstructed_orbit.altitude_apogee
    assert orbit.inclination == reconstructed_orbit.inclination
    assert orbit.raan == reconstructed_orbit.raan
    assert orbit.argp == reconstructed_orbit.argp
    assert orbit.nu == reconstructed_orbit.nu


def test_orbit_xml():
    orbit = OrbitBase(500, 20000, 28.5, raan=60.0, argp=30.0, nu=20.0)
    xml_data = orbit.to_xml()
    reconstructed_orbit = OrbitBase.from_xml(xml_data)
    assert orbit.altitude_perigee == reconstructed_orbit.altitude_perigee
    assert orbit.altitude_apogee == reconstructed_orbit.altitude_apogee
    assert orbit.inclination == reconstructed_orbit.inclination
    assert orbit.raan == reconstructed_orbit.raan
    assert orbit.argp == reconstructed_orbit.argp
    assert orbit.nu == reconstructed_orbit.nu


def test_orbit_csv():
    """
    Test serialization and deserialization of OrbitBase with CSV.
    """
    orbit = OrbitBase(500, 20000, 28.5, raan=60.0, argp=30.0, nu=20.0)
    csv_data = orbit.to_csv()
    reconstructed_orbit = OrbitBase.from_csv(csv_data)
    assert orbit.altitude_perigee == reconstructed_orbit.altitude_perigee
    assert orbit.altitude_apogee == reconstructed_orbit.altitude_apogee
    assert orbit.inclination == reconstructed_orbit.inclination
    assert orbit.raan == reconstructed_orbit.raan
    assert orbit.argp == reconstructed_orbit.argp
    assert orbit.nu == reconstructed_orbit.nu
