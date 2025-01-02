import pytest
from astropy import units as u
from app.schemas.orbits.orbit_base import OrbitBase
from app.schemas.trajectory_base import Trajectory
from utils.hohmann.func.calculate_transfer import func_calculate_transfer
from logger_handler import handle_logger

logger = handle_logger()

@pytest.fixture
def valid_initial_orbit() -> OrbitBase:
    """
    Fixture to provide a valid low Earth orbit (LEO).
    """
    return OrbitBase(altitude_perigee=500 + 6378, altitude_apogee=500 + 6378, inclination=0)


@pytest.fixture
def valid_target_orbit() -> OrbitBase:
    """
    Fixture to provide a valid geostationary transfer orbit (GEO).
    """
    return OrbitBase(altitude_perigee=500 + 6378, altitude_apogee=35786 + 6378, inclination=0)


def test_func_calculate_transfer_typical_case(valid_initial_orbit: OrbitBase, valid_target_orbit: OrbitBase) -> None:
    """
    Test func_calculate_transfer with typical LEO to GEO transfer.
    """
    trajectory = func_calculate_transfer(valid_initial_orbit, valid_target_orbit)

    # Assert that the result is an instance of Trajectory
    assert isinstance(trajectory, Trajectory), "The result should be a Trajectory object"

    # Assert delta-v values are positive
    assert trajectory.delta_v1 > 0, "Delta-v1 should be greater than 0"
    assert trajectory.delta_v2 > 0, "Delta-v2 should be greater than 0"

    # Assert time of flight is positive
    assert trajectory.time_of_flight > 0, "Time of flight should be greater than 0"

    # Assert points contain the correct number of samples
    assert len(trajectory.points) == 101, "Trajectory points should contain 101 samples (including start and end)"


def test_func_calculate_transfer_edge_case_circular_orbits() -> None:
    """
    Test func_calculate_transfer with two circular orbits of the same altitude.
    """
    initial_orbit = OrbitBase(altitude_perigee=7000 + 6378, altitude_apogee=7000 + 6378, inclination=0)
    target_orbit = OrbitBase(altitude_perigee=7000 + 6378, altitude_apogee=7000 + 6378, inclination=0)

    trajectory = func_calculate_transfer(initial_orbit, target_orbit)

    # Assert that delta-v values are near zero for identical circular orbits
    assert pytest.approx(trajectory.delta_v1, abs=1e-3) == 0, "Delta-v1 should be near zero"
    assert pytest.approx(trajectory.delta_v2, abs=1e-3) == 0, "Delta-v2 should be near zero"

    # Assert time of flight is near zero
    logger.info(f"trajectory.time_of_flight: {trajectory.time_of_flight}")
    assert pytest.approx(trajectory.time_of_flight, abs=1e-3) == 0, "Time of flight should be near zero"

def test_func_calculate_transfer_invalid_input() -> None:
    """
    Test func_calculate_transfer with invalid orbit inputs.
    """
    with pytest.raises(ValueError):
        initial_orbit = OrbitBase(altitude_perigee=-500, altitude_apogee=40000, inclination=28.5)
        target_orbit = OrbitBase(altitude_perigee=500, altitude_apogee=-35786, inclination=0)
        func_calculate_transfer(initial_orbit, target_orbit)

def test_hohmann_reentry() -> None:
    """
    Test a Hohmann transfer simulating atmospheric reentry.
    This simulates lowering the orbit to intersect Earth's atmosphere.
    """
    # Define the initial LEO orbit and the target reentry orbit
    leo_orbit = OrbitBase(
        altitude_perigee=500,  # 500 km above Earth's surface
        altitude_apogee=500,  # Circular orbit at 500 km
        inclination=28.5  # Typical LEO inclination
    )

    reentry_orbit = OrbitBase(
        altitude_perigee=100,  # Perigee at 100 km (atmospheric reentry)
        altitude_apogee=500,  # Apogee remains the same
        inclination=28.5  # Same inclination
    )

    # Perform the Hohmann transfer
    trajectory = func_calculate_transfer(leo_orbit, reentry_orbit)

    # Assert the result is a Trajectory object
    assert isinstance(trajectory, Trajectory), "The result should be a Trajectory object."

    # Assert delta-v values are negative (indicating braking)
    assert trajectory.delta_v1 < 0, "Delta-v1 should be negative for deorbiting."
    assert trajectory.delta_v2 < 0, "Delta-v2 should be negative for deorbiting."

    # Assert time of flight is positive
    assert trajectory.time_of_flight > 0, "Time of flight should be greater than 0."

    # Verify trajectory points are not empty
    assert len(trajectory.points) > 0, "Trajectory points should not be empty."

    # Calculate the final altitude from the last trajectory point
    final_point_position = trajectory.points[-1].position
    final_point_position_magnitude = (
        (final_point_position[0])**2 + 
        (final_point_position[1])**2 + 
        (final_point_position[2])**2
    )**0.5

    final_altitude = final_point_position_magnitude

    # Assert the final altitude approximates the target perigee (100 km)
    assert pytest.approx(final_altitude.to(u.km).value, abs=10) == 100, \
        "Final altitude should approximate the reentry altitude (100 km)."
