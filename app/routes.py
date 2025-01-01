from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.schemas.orbits.orbit_base import OrbitBase
from app.schemas.trajectory_base import Trajectory
from utils.hohmann.hohmann_transfer import HohmannTransfer
from logger_handler import handle_logger

logger = handle_logger()

# Initialize router
router = APIRouter()

# Simulated database
# For now, fetch data from the `data/` directory, and later connect to a database.
orbits_db: List[OrbitBase] = []
trajectories_db: List[Trajectory] = []


@router.post("/orbits", response_model=dict, status_code=201)
def create_orbit(altitude_perigee: float, altitude_apogee: float, inclination: float):
    """
    Create a new orbit and store it in the database.
    """
    try:
        orbit = OrbitBase(altitude_perigee, altitude_apogee, inclination)
        orbits_db.append(orbit)
        return {"message": "Orbit created successfully", "orbit": orbit.__dict__}
    except ValueError as e:
        logger.error(f"Error: str({e})")
        raise HTTPException(status_code=400, detail="Error")
    except Exception as e:
        logger.error(f"Error: str({e})")
        raise HTTPException(status_code=500)


@router.get("/orbits", response_model=List[dict])
def get_orbits():
    """
    Retrieve all stored orbits.
    """
    try:
        return [orbit.__dict__ for orbit in orbits_db]
    except Exception as e:
        logger.error(f"Error: str({e})")
        raise HTTPException(status_code=500)


@router.post("/transfers", response_model=dict, status_code=201)
def perform_transfer_calculation(
    orbit1_index: int,
    orbit2_index: int,
    transfer_type: str = Query("hohmann", description="Type of orbital transfer")
):
    """
    Calculate an orbital transfer between two orbits.

    Args:
        orbit1_index (int): Index of the initial orbit in the database.
        orbit2_index (int): Index of the target orbit in the database.
        transfer_type (str): Type of transfer (e.g., "hohmann").

    Returns:
        dict: The calculated trajectory "Error"  """
    try:
        # Validate indices
        if orbit1_index >= len(orbits_db) or orbit2_index >= len(orbits_db):
            logger.error(f"Error: str({e})")
            raise ValueError("Invalid orbit indices")

        orbit1 = orbits_db[orbit1_index]
        orbit2 = orbits_db[orbit2_index]

        # Handle transfer type
        if transfer_type == "hohmann":
            calculator = HohmannTransfer()
        else:
            logger.error(f"Error: str({e})")
            raise ValueError(f"Transfer type '{transfer_type}' not supported")

        # Calculate the transfer
        trajectory = calculator.calculate_transfer([orbit1, orbit2])
        trajectories_db.append(trajectory)

        return {"message": "Transfer calculated successfully", "trajectory": trajectory.__dict__}
    except ValueError as e:
        logger.error(f"Error: str({e})")
        raise HTTPException(status_code=400, detail="Error")
    except Exception as e:
        logger.error(f"Error: str({e})")
        raise HTTPException(status_code=500)


@router.get("/trajectories", response_model=List[dict])
def get_trajectories():
    """
    Retrieve all calculated trajectories.
    """
    try:
        return [trajectory.__dict__ for trajectory in trajectories_db]
    except Exception as e:
        logger.error(f"Error: str({e})")
        raise HTTPException(status_code=500)
