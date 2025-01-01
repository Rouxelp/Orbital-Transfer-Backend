import pytest
from app.schemas.trajectory_base import Trajectory


@pytest.fixture
def valid_trajectory() -> Trajectory:
    """
    Fixture to provide a valid Trajectory instance.
    """
    points = [
        {"time": "2024-01-01T00:00:00Z", "position": [7000, 0, 0], "velocity": [0, 7.5, 0]},
        {"time": "2024-01-01T00:01:00Z", "position": [7020, 10, 5], "velocity": [0, 7.6, 0.1]},
    ]
    return Trajectory(delta_v1=2.5, delta_v2=3.0, time_of_flight=6.5, points=points)


def test_trajectory_to_json(valid_trajectory: Trajectory, tmp_path) -> None:
    """
    Test the to_json method of Trajectory.
    """
    json_file = tmp_path / "trajectory.json"
    valid_trajectory.to_json(filename=json_file)
    assert json_file.exists()
    with open(json_file, "r") as f:
        data = f.read()
    assert "delta_v1" in data


def test_trajectory_to_csv(valid_trajectory: Trajectory, tmp_path) -> None:
    """
    Test the to_csv method of Trajectory.
    """
    csv_file = tmp_path / "trajectory.csv"
    valid_trajectory.to_csv(filename=csv_file)
    assert csv_file.exists()
    with open(csv_file, "r") as f:
        data = f.read()
    assert "time,position,velocity" in data


def test_trajectory_visualize(valid_trajectory: Trajectory) -> None:
    """
    Test the visualize method of Trajectory.
    """
    try:
        valid_trajectory.visualize()
    except Exception as e:
        pytest.fail(f"Visualization failed with exception: {e}")

def test_trajectory_json():
    trajectory = Trajectory(2.5, 3.0, 6.5, points=[{"time": "T0", "position": [1, 2, 3], "velocity": [0, 1, 0]}])
    json_data = trajectory.to_json()
    reconstructed_trajectory = Trajectory.from_json(json_data)
    assert trajectory.delta_v1 == reconstructed_trajectory.delta_v1
    assert trajectory.delta_v2 == reconstructed_trajectory.delta_v2
    assert trajectory.time_of_flight == reconstructed_trajectory.time_of_flight
    assert trajectory.points == reconstructed_trajectory.points


def test_trajectory_xml():
    trajectory = Trajectory(2.5, 3.0, 6.5, points=[{"time": "T0", "position": [1, 2, 3], "velocity": [0, 1, 0]}])
    xml_data = trajectory.to_xml()
    reconstructed_trajectory = Trajectory.from_xml(xml_data)
    assert trajectory.delta_v1 == reconstructed_trajectory.delta_v1
    assert trajectory.delta_v2 == reconstructed_trajectory.delta_v2
    assert trajectory.time_of_flight == reconstructed_trajectory.time_of_flight
    assert trajectory.points == reconstructed_trajectory.points

def test_trajectory_csv():
    """
    Test serialization and deserialization of Trajectory with CSV.
    """
    trajectory = Trajectory(
        delta_v1=2.5,
        delta_v2=3.0,
        time_of_flight=6.5,
        points=[
            {"time": "T0", "position": [1, 2, 3], "velocity": [0, 1, 0]},
            {"time": "T1", "position": [2, 3, 4], "velocity": [1, 0, -1]}
        ],
    )
    csv_data = trajectory.to_csv()
    reconstructed_trajectory = Trajectory.from_csv(csv_data)

    assert trajectory.delta_v1 == reconstructed_trajectory.delta_v1
    assert trajectory.delta_v2 == reconstructed_trajectory.delta_v2
    assert trajectory.time_of_flight == reconstructed_trajectory.time_of_flight
    assert trajectory.points == reconstructed_trajectory.points
