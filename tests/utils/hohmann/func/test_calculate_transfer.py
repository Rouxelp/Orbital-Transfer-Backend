import pytest
from app.schemas import OrbitBase, Trajectory
from utils.hohmann.func.calculate_transfer import func_calculate_transfer


@pytest.fixture
def valid_orbit1() -> OrbitBase:
    """
    Fixture to provide a valid low Earth orbit (LEO).
    """
    return OrbitBase(altitude_perigee=500, altitude_apogee=500, inclination=28.5)


@pytest.fixture
def valid_orbit2() -> OrbitBase:
    """
    Fixture to provide a valid geostationary transfer orbit (GEO).
    """
    return OrbitBase(altitude_perigee=500, altitude_apogee=35786, inclination=0)


def test_func_calculate_transfer_typical_case(valid_orbit1: OrbitBase, valid_orbit2: OrbitBase) -> None:
    """
    Test func_calculate_transfer with typical LEO to GEO transfer.
    """
    trajectory = func_calculate_transfer(valid_orbit1, valid_orbit2)

    # Assert that the result is an instance of Trajectory
    assert isinstance(trajectory, Trajectory), "The result should be a Trajectory object"

    # Assert delta-v values are positive
    assert trajectory.delta_v1 > 0, "Delta-v1 should be greater than 0"
    assert trajectory.delta_v2 > 0, "Delta-v2 should be greater than 0"

    # Assert time of flight is positive
    assert trajectory.time_of_flight > 0, "Time of flight should be greater than 0"

    # Assert points are not empty
    assert len(trajectory.points) == 100, "Trajectory points should have 100 samples"


def test_func_calculate_transfer_edge_case_circular_orbits() -> None:
    """
    Test func_calculate_transfer with two circular orbits of the same altitude.
    """
    orbit1 = OrbitBase(altitude_perigee=7000, altitude_apogee=7000, inclination=0)
    orbit2 = OrbitBase(altitude_perigee=7000, altitude_apogee=7000, inclination=0)

    trajectory = func_calculate_transfer(orbit1, orbit2)

    # Assert that delta-v values are near zero for identical circular orbits
    assert pytest.approx(trajectory.delta_v1, abs=1e-3) == 0, "Delta-v1 should be near zero"
    assert pytest.approx(trajectory.delta_v2, abs=1e-3) == 0, "Delta-v2 should be near zero"

    # Assert time of flight is near zero
    assert pytest.approx(trajectory.time_of_flight, abs=1e-3) == 0, "Time of flight should be near zero"


def test_func_calculate_transfer_invalid_input() -> None:
    """
    Test func_calculate_transfer with invalid orbit inputs.
    """
    with pytest.raises(ValueError):
        orbit1 = OrbitBase(altitude_perigee=-500, altitude_apogee=40000, inclination=28.5)
        orbit2 = OrbitBase(altitude_perigee=500, altitude_apogee=-35786, inclination=0)
        func_calculate_transfer(orbit1, orbit2)


def test_func_calculate_transfer_inclination_change() -> None:
    """
    Test func_calculate_transfer with a transfer involving a change in inclination.
    """
    orbit1 = OrbitBase(altitude_perigee=500, altitude_apogee=500, inclination=0)
    orbit2 = OrbitBase(altitude_perigee=500, altitude_apogee=35786, inclination=45)

    trajectory = func_calculate_transfer(orbit1, orbit2)

    # Assert that the result is an instance of Trajectory
    assert isinstance(trajectory, Trajectory), "The result should be a Trajectory object"

    # Assert delta-v values are positive
    assert trajectory.delta_v1 > 0, "Delta-v1 should be greater than 0"
    assert trajectory.delta_v2 > 0, "Delta-v2 should be greater than 0"

    # Assert time of flight is positive
    assert trajectory.time_of_flight > 0, "Time of flight should be greater than 0"
