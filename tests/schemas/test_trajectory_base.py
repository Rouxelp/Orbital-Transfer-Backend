import json
from typing import List
from astropy import units as u
import numpy as np
import pytest
import xml.etree.ElementTree as ET
from app.schemas.trajectory_base import Point, Trajectory

@pytest.fixture
def valid_points() -> List[Point]:
   return [
        Point(time="2024-01-01T00:00:00Z", position=[7000 * u.km, 0 * u.km, 0 * u.km], velocity=[0 * u.km / u.s, 7.5 * u.km / u.s, 0 * u.km / u.s]),
        Point(time="2024-01-01T00:01:00Z", position=[7020 * u.km, 10 * u.km, 5 * u.km], velocity=[0 * u.km / u.s, 7.6 * u.km / u.s, 0.1 * u.km / u.s]),
    ] 

@pytest.fixture
def valid_trajectory(valid_points: List[Point]) -> Trajectory:
    """
    Fixture to provide a valid Trajectory instance.
    """
    return Trajectory(
        delta_v1=2.5, 
        delta_v2=3.0, 
        time_of_flight=6.5, 
        points=valid_points, 
        initial_orbit_id=1, 
        target_orbit_id=2
    )

def test_unique_trajectory_ids():
    """
    Test to ensure that two Trajectory objects have unique IDs.
    """
    trajectory1 = Trajectory(delta_v1=2.5, delta_v2=3.0, time_of_flight=6.5, initial_orbit_id=1, target_orbit_id=2)
    trajectory2 = Trajectory(delta_v1=1.5, delta_v2=2.0, time_of_flight=4.0, initial_orbit_id=3, target_orbit_id=4)

    assert trajectory1.id != trajectory2.id

def test_trajectory_to_json(valid_trajectory: Trajectory, tmp_path) -> None:
    """
    Test the to_json method of Trajectory.
    """
    json_file = tmp_path / "trajectory.json"
    valid_trajectory.to_json(filename=json_file)

    # Validate file existence
    assert json_file.exists(), "The JSON file was not created."

    # Validate JSON content
    with open(json_file, "r") as f:
        data = json.load(f)

    assert "delta_v1" in data, "The 'delta_v1' field is missing in the JSON."
    assert "points" in data, "The 'points' field is missing in the JSON."
    assert isinstance(data["points"], list), "The 'points' field is not a list."
    assert len(data["points"]) > 0, "The 'points' field is empty."
    assert "time" in data["points"][0], "The 'time' field is missing in a point."

def test_trajectory_to_csv(valid_trajectory: Trajectory, tmp_path) -> None:
    """
    Test the to_csv method of Trajectory.
    """
    csv_file = tmp_path / "trajectory.csv"
    valid_trajectory.to_csv(filename=csv_file)

    # Validate file existence
    assert csv_file.exists(), "The CSV file was not created."

    # Validate CSV content
    with open(csv_file, "r") as f:
        data = f.readlines()

    # Validate header and number of rows
    assert len(data) > 1, "The CSV file should have at least two rows (header + data)."
    header = data[0].strip().split(",")
    assert set(header) >= {
        "id", "delta_v1", "delta_v2", "time", "position_x", "position_y", "position_z",
        "velocity_x", "velocity_y", "velocity_z"
    }, "The CSV header is missing required fields."

    # Validate first data row
    first_row = data[1].strip().split(",")
    assert len(first_row) == len(header), "The first row data does not match the header structure."
    assert "2024-01-01T00:00:00Z" in first_row, "The first point's 'time' field is missing in the CSV."
    assert "7000.0" in first_row, "The first point's 'position_x' is not serialized correctly."
    assert "7.5" in first_row, "The first point's 'velocity_y' is not serialized correctly."

def test_trajectory_to_xml(valid_trajectory: Trajectory, tmp_path) -> None:
    """
    Test the to_xml method of Trajectory.
    """
    xml_file = tmp_path / "trajectory.xml"
    valid_trajectory.to_xml(filename=xml_file)

    # Validate file existence
    assert xml_file.exists(), "The XML file was not created."

    # Validate XML content
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Check root tag
    assert root.tag == "Trajectory", "The root tag should be 'Trajectory'."

    # Check for key fields
    assert root.find("delta_v1") is not None, "The 'delta_v1' field is missing in the XML."
    assert root.find("delta_v2") is not None, "The 'delta_v2' field is missing in the XML."
    assert root.find("time_of_flight") is not None, "The 'time_of_flight' field is missing in the XML."
    assert root.find("initial_orbit_id") is not None, "The 'initial_orbit_id' field is missing in the XML."
    assert root.find("target_orbit_id") is not None, "The 'target_orbit_id' field is missing in the XML."

    # Check points data
    points_elem = root.find("Points")
    assert points_elem is not None, "The 'Points' element is missing in the XML."
    assert len(points_elem) > 0, "The 'Points' element should contain at least one point."

    # Check first point data
    first_point = points_elem[0]
    assert first_point.find("time") is not None, "The 'time' field is missing in the first point."
    assert first_point.find("position_x") is not None, "The 'position_x' field is missing in the first point."
    assert first_point.find("position_y") is not None, "The 'position_y' field is missing in the first point."
    assert first_point.find("position_z") is not None, "The 'position_z' field is missing in the first point."
    assert first_point.find("velocity_x") is not None, "The 'velocity_x' field is missing in the first point."
    assert first_point.find("velocity_y") is not None, "The 'velocity_y' field is missing in the first point."
    assert first_point.find("velocity_z") is not None, "The 'velocity_z' field is missing in the first point."

    # Validate specific values for the first point
    assert first_point.find("time").text == "2024-01-01T00:00:00Z", "The 'time' value is incorrect in the first point."
    assert float(first_point.find("position_x").text) == pytest.approx(7000.0), "The 'position_x' value is incorrect in the first point."
    assert float(first_point.find("position_y").text) == pytest.approx(0.0), "The 'position_y' value is incorrect in the first point."
    assert float(first_point.find("velocity_y").text) == pytest.approx(7.5), "The 'velocity_y' value is incorrect in the first point."

def test_trajectory_from_json(valid_trajectory: Trajectory) -> None:
    """
    Test serialization and deserialization of Trajectory with JSON.
    """

    json_data = valid_trajectory.to_json()
    reconstructed_trajectory = Trajectory.from_json(json_data)
    assert valid_trajectory.delta_v1 == reconstructed_trajectory.delta_v1
    assert valid_trajectory.delta_v2 == reconstructed_trajectory.delta_v2
    assert valid_trajectory.time_of_flight == reconstructed_trajectory.time_of_flight
    assert valid_trajectory.points == reconstructed_trajectory.points

def test_trajectory_from_xml(valid_trajectory: Trajectory) -> None:
    """
    Test serialization and deserialization of Trajectory with XML.
    """

    xml_data = valid_trajectory.to_xml()
    reconstructed_trajectory = Trajectory.from_xml(xml_data)
    assert valid_trajectory.delta_v1 == reconstructed_trajectory.delta_v1
    assert valid_trajectory.delta_v2 == reconstructed_trajectory.delta_v2
    assert valid_trajectory.time_of_flight == reconstructed_trajectory.time_of_flight
    assert valid_trajectory.points == reconstructed_trajectory.points

def test_trajectory_from_csv(valid_trajectory: Trajectory) -> None:
    """
    Test serialization and deserialization of Trajectory with CSV.
    """
    # Serialize trajectory to CSV
    csv_data = valid_trajectory.to_csv()

    # Deserialize the CSV back into a Trajectory object
    reconstructed_trajectory = Trajectory.from_csv(csv_data)

    # Validate metadata
    assert valid_trajectory.id == reconstructed_trajectory.id, "Trajectory ID mismatch."
    assert valid_trajectory.delta_v1 == reconstructed_trajectory.delta_v1, "Delta-v1 mismatch."
    assert valid_trajectory.delta_v2 == reconstructed_trajectory.delta_v2, "Delta-v2 mismatch."
    assert valid_trajectory.time_of_flight == reconstructed_trajectory.time_of_flight, "Time of flight mismatch."
    assert valid_trajectory.initial_orbit_id == reconstructed_trajectory.initial_orbit_id, "initial_orbit ID mismatch."
    assert valid_trajectory.target_orbit_id == reconstructed_trajectory.target_orbit_id, "target_orbit ID mismatch."

    # Validate points
    for original, reconstructed in zip(valid_trajectory.points, reconstructed_trajectory.points):
        assert original.time == reconstructed.time, f"Point 'time' mismatch: {original.time} vs {reconstructed.time}"
        assert all(np.isclose(original.position[i].value, reconstructed.position[i].value) for i in range(3)), "Point 'position' mismatch."
        assert all(np.isclose(original.velocity[i].value, reconstructed.velocity[i].value) for i in range(3)), "Point 'velocity' mismatch."
