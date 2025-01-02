import numpy as np
from app.schemas.trajectory_base import Point, Trajectory
from app.schemas.orbits.orbit_base import OrbitBase
from astropy import units as u
from logger_handler import handle_logger

logger = handle_logger()

def func_calculate_transfer(initial_orbit: OrbitBase, target_orbit: OrbitBase, sample_value: int = 100) -> Trajectory:
    """
    Calculate the Hohmann transfer between two orbits using explicit equations.

    Parameters:
    - initial_orbit (OrbitBase): The initial orbit.
    - target_orbit (OrbitBase): The target orbit.
    - sample_value (int, optional): Number of discrete points to sample along the transfer trajectory. Default is 100.

    Returns:
    - Trajectory: An object containing the delta-v values, time of flight, and discrete points along the trajectory.
    """
    try:
        # Constants
        mu = initial_orbit.central_body.mu  # Gravitational parameter of the central body
        # Dynamically determine r1 and r2 based on transfer type
        if initial_orbit.altitude_perigee <= target_orbit.altitude_perigee:  # Transfer to a higher orbit
            r1 = initial_orbit.altitude_perigee
            r2 = target_orbit.altitude_apogee
        else:  # Transfer to a lower orbit
            r1 = initial_orbit.altitude_perigee
            r2 = target_orbit.altitude_perigee


        # If the two orbits are the same
        if np.isclose(initial_orbit.altitude_perigee, target_orbit.altitude_perigee, atol=1e-3) and np.isclose(initial_orbit.altitude_apogee, target_orbit.altitude_apogee, atol=1e-3):  
            logger.info("No transfer required: Orbits are identical.")
            return Trajectory(
                delta_v1=0.0,
                delta_v2=0.0,
                time_of_flight=0.0,
                points=[],
                initial_orbit_id=initial_orbit.id,
                target_orbit_id=target_orbit.id,
            )
        
        # Semi-major axis of the transfer ellipse
        a_transfer = (r1 + r2) / 2

        # Velocities at the initial orbit, transfer orbit (periapsis and apoapsis), and target orbit
        v1_initial = (mu / r1)**(1/2) # Circular velocity at initial_orbit
        v1_transfer = ((2 * mu / r1) - (mu / a_transfer))**(1/2) # Velocity at periapsis of transfer orbit
        v2_transfer = ((2 * mu / r2) - (mu / a_transfer))**(1/2) # Velocity at apoapsis of transfer orbit
        v2_final = (mu / r2)**(1/2) # Circular velocity at target_orbit

        # Delta-v calculations
        delta_v1 = (v1_transfer - v1_initial).to(u.km / u.s)  # First impulse
        delta_v2 = (v2_final - v2_transfer).to(u.km / u.s)  # Second impulse

        # Time of flight for the transfer
        time_of_flight = (np.pi * (a_transfer**3 / mu)**(1/2)).to(u.hour)

        # Generate trajectory points for visualization
        points = []
        for i in range(sample_value + 1):
            # Interpolation along the transfer ellipse
            theta = np.pi * i / sample_value  # True anomaly from 0 to π
            r = (a_transfer * (1 - ((r2 - r1) / (r1 + r2))**2)) / (1 + ((r2 - r1) / (r1 + r2)) * np.cos(theta))

            x = r * np.cos(theta)
            y = r * np.sin(theta)

            # Orbital velocity at this position
            v = ((2 * mu / r) - (mu / a_transfer))**(1/2)

            points.append(Point(
                time=f"T+{(time_of_flight.value * i / sample_value):.2f}h",
                position=[x.to(u.km).value, y.to(u.km).value, 0.0],
                velocity=[-v * np.sin(theta), v * np.cos(theta), 0.0] 
            ))

        # Create and return the Trajectory object
        return Trajectory(
            delta_v1=delta_v1.value,
            delta_v2=delta_v2.value,
            time_of_flight=time_of_flight.value,
            points=points,
            initial_orbit_id=initial_orbit.id,
            target_orbit_id=target_orbit.id
        )
    except AttributeError as e:
        logger.error(f"Attribute error: {e}")
        raise ValueError("Invalid orbit attributes.")
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise ValueError("Error during trajectory calculation.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError("Unexpected error during trajectory calculation.")

