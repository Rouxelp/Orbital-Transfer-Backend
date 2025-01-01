from app.schemas.trajectory_base import Trajectory
from app.schemas.orbits.orbit_base import OrbitBase
from astropy import units as u
from logger_handler import handle_logger

logger = handle_logger()

def func_calculate_transfer(orbit1: OrbitBase, orbit2: OrbitBase, sample_value: int = 100):
    """
    Calculate the Hohmann transfer between two orbits and return the trajectory details.

    Parameters:
    - orbit1 (OrbitBase): The initial orbit.
    - orbit2 (OrbitBase): The target orbit.
    - sample_value (int, optional): The number of discrete points to sample along the transfer trajectory. Default is 100.

    Returns:
    - Trajectory: An object containing the delta-v values, time of flight, and discrete points along the trajectory.
    """
    try:
        # Convert orbits to poliastro Orbit objects
        poliastro_orbit1 = orbit1.to_poliastro_orbit()
        poliastro_orbit2 = orbit2.to_poliastro_orbit()

        # Calculate the Hohmann transfer
        transfer = poliastro_orbit1.hohmann_transfer_to(poliastro_orbit2)

        # Calculate the delta-v values
        dv1, dv2 = transfer.get_total_cost()

        # Discrete points for the trajectory
        time_steps = transfer.sample(sample_value)
        points = [
            {
                "time": str(step[0]),
                "position": step[1].tolist(),
                "velocity": step[2].tolist()
            }
            for step in time_steps
        ]

        # Return a Trajectory object
        return Trajectory(
            delta_v1=dv1.to(u.km / u.s).value,
            delta_v2=dv2.to(u.km / u.s).value,
            time_of_flight=transfer.time_of_flight.to(u.hour).value,
            points=points
        )

    except AttributeError as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Invalid orbit attributes")
    except ValueError as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Error during trajectory calculation")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise RuntimeError(f"Unexpected error during trajectory calculation")
