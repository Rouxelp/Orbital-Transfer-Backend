import json
import pytest
import xml.etree.ElementTree as ET
from app.schemas.orbits.orbit_base import OrbitBase
from astropy import units as u

@pytest.fixture
def valid_orbit() -> OrbitBase:
    """
    Fixture to provide a valid OrbitBase instance with RAAN, ARG, and NU.
    """
    return OrbitBase(
        altitude_perigee=500 + 6378,
        altitude_apogee=40000 + 6378,
        inclination=28.5,
        raan=50.0,
        argp=45.0,
        nu=10.0
    )

def test_unique_orbit_ids():
    """
    Test to ensure that two OrbitBase objects have unique IDs.
    """
    orbit1 = OrbitBase(500, 40000, 28.5, raan=60.0, argp=30.0, nu=20.0)
    orbit2 = OrbitBase(600, 41000, 30.0, raan=70.0, argp=35.0, nu=25.0)

    assert orbit1.id != orbit2.id

def test_orbit_to_poliastro_orbit(valid_orbit: OrbitBase) -> None:
    """
    Test the conversion of an OrbitBase instance to a Poliastro Orbit object.
    """
    poliastro_orbit = valid_orbit.to_poliastro_orbit()
    assert poliastro_orbit.a.to(u.km).value == pytest.approx(26628.0, rel=1e-3)
    assert float(poliastro_orbit.ecc) == pytest.approx(0.7416, rel=1e-3)
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

def test_orbit_to_json(valid_orbit: OrbitBase, tmp_path) -> None:
    """
    Test the to_json method of OrbitBase.
    """
    json_file = tmp_path / "orbit.json"
    valid_orbit.to_json(filename=json_file)

    # Validate file existence
    assert json_file.exists(), "The JSON file was not created."

    # Validate JSON content
    with open(json_file, "r") as f:
        data: dict = json.load(f)

    assert "altitude_perigee" in data, "The 'altitude_perigee' field is missing in the JSON."
    assert "altitude_apogee" in data, "The 'altitude_apogee' field is missing in the JSON."
    assert "inclination" in data, "The 'inclination' field is missing in the JSON."
    assert data.get("altitude_perigee", None) == pytest.approx(6878.0), "The 'altitude_perigee' value is incorrect."
    assert data.get("altitude_apogee", None) == pytest.approx(46378.0), "The 'altitude_apogee' value is incorrect."
    assert data.get("inclination", None) == pytest.approx(28.5), "The 'inclination' value is incorrect."

def test_orbit_to_xml(valid_orbit: OrbitBase, tmp_path) -> None:
    """
    Test the to_xml method of OrbitBase.
    """
    xml_file = tmp_path / "orbit.xml"
    valid_orbit.to_xml(filename=xml_file)

    # Validate file existence
    assert xml_file.exists(), "The XML file was not created."

    # Validate XML content
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Check root tag
    assert root.tag == "Orbit", "The root tag should be 'Orbit'."

    # Check for key fields
    assert root.find("altitude_perigee") is not None, "The 'altitude_perigee' field is missing in the XML."
    assert root.find("altitude_apogee") is not None, "The 'altitude_apogee' field is missing in the XML."
    assert root.find("inclination") is not None, "The 'inclination' field is missing in the XML."

    # Validate field values
    assert float(root.find("altitude_perigee").text) == pytest.approx(6878.0), "The 'altitude_perigee' value is incorrect."
    assert float(root.find("altitude_apogee").text) == pytest.approx(46378.0), "The 'altitude_apogee' value is incorrect."
    assert float(root.find("inclination").text) == pytest.approx(28.5), "The 'inclination' value is incorrect."

def test_orbit_to_csv(valid_orbit: OrbitBase, tmp_path) -> None:
    """
    Test the to_csv method of OrbitBase.
    """
    csv_file = tmp_path / "orbit.csv"
    valid_orbit.to_csv(filename=csv_file)

    # Validate file existence
    assert csv_file.exists(), "The CSV file was not created."

    # Validate CSV content
    with open(csv_file, "r") as f:
        data = f.readlines()

    # Validate header and number of rows
    assert len(data) > 1, "The CSV file should have at least two rows (header + data)."
    header = data[0].strip().split(",")
    assert set(header) >= {
        "id", "altitude_perigee", "altitude_apogee", "inclination", "raan", "argp", "nu"
    }, "The CSV header is missing required fields."

    # Validate first data row
    first_row = data[1].strip().split(",")
    assert len(first_row) == len(header), "The first row data does not match the header structure."
    assert "6878.0" in first_row, "The 'altitude_perigee' is not serialized correctly."
    assert "46378.0" in first_row, "The 'altitude_apogee' is not serialized correctly."
    assert "28.5" in first_row, "The 'inclination' is not serialized correctly."

def test_orbit_from_json():
    orbit = OrbitBase(500, 20000, 28.5, raan=60.0, argp=30.0, nu=20.0)
    json_data = orbit.to_json()
    reconstructed_orbit = OrbitBase.from_json(json_data)
    assert orbit.altitude_perigee == reconstructed_orbit.altitude_perigee
    assert orbit.altitude_apogee == reconstructed_orbit.altitude_apogee
    assert orbit.inclination == reconstructed_orbit.inclination
    assert orbit.raan == reconstructed_orbit.raan
    assert orbit.argp == reconstructed_orbit.argp
    assert orbit.nu == reconstructed_orbit.nu

def test_orbit_from_xml():
    orbit = OrbitBase(500, 20000, 28.5, raan=60.0, argp=30.0, nu=20.0)
    xml_data = orbit.to_xml()
    reconstructed_orbit = OrbitBase.from_xml(xml_data)
    assert orbit.altitude_perigee == reconstructed_orbit.altitude_perigee
    assert orbit.altitude_apogee == reconstructed_orbit.altitude_apogee
    assert orbit.inclination == reconstructed_orbit.inclination
    assert orbit.raan == reconstructed_orbit.raan
    assert orbit.argp == reconstructed_orbit.argp
    assert orbit.nu == reconstructed_orbit.nu

def test_orbit_from_csv():
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

def test_orbit_poliastro_recalculation(valid_orbit: OrbitBase) -> None:
    """
    Test that the Poliastro Orbit is recalculated when an attribute is modified.
    """
    # Generate initial Poliastro Orbit
    initial_poliastro_orbit = valid_orbit.poliastro_orbit

    # Modify an attribute (e.g., altitude_apogee)
    new_altitude_apogee = 50000  # km
    valid_orbit.altitude_apogee = new_altitude_apogee

    # Generate updated Poliastro Orbit
    updated_poliastro_orbit = valid_orbit.poliastro_orbit

    # Ensure the orbit object has been recalculated
    assert initial_poliastro_orbit is not updated_poliastro_orbit, "Poliastro Orbit object was not recalculated."
    assert updated_poliastro_orbit.a.to(u.km).value == pytest.approx(
        (valid_orbit.altitude_perigee.to(u.km).value + new_altitude_apogee) / 2, rel=1e-3
    ), "Semi-major axis was not updated correctly."
    assert float(updated_poliastro_orbit.ecc) == pytest.approx(
        (new_altitude_apogee - valid_orbit.altitude_perigee.to(u.km).value) /
        (new_altitude_apogee + valid_orbit.altitude_perigee.to(u.km).value), rel=1e-3
    ), "Eccentricity was not updated correctly."

