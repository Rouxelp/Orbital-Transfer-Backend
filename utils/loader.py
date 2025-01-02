from pathlib import Path
from typing import List, Optional
from app.schemas.orbits.orbit_base import OrbitBase
from app.schemas.trajectory_base import Trajectory

# Base directories for data storage
DATA_DIR = Path("data")
ORBIT_DIR = DATA_DIR / "orbits"
TRAJECTORY_DIR = DATA_DIR / "trajectories"

# Ensure directory structure exists
for folder in [ORBIT_DIR / "json", ORBIT_DIR / "csv", ORBIT_DIR / "xml",
               TRAJECTORY_DIR / "json", TRAJECTORY_DIR / "csv", TRAJECTORY_DIR / "xml"]:
    folder.mkdir(parents=True, exist_ok=True)

# Base directories for data storage
DATA_DIR = Path("data")
ORBIT_DIR = DATA_DIR / "orbits"
TRAJECTORY_DIR = DATA_DIR / "trajectories"

def find_file_by_id(base_dir: Path, obj_id: str) -> Optional[Path]:
    """
    Search for a file by its ID across all subdirectories and file types.

    Args:
        base_dir (Path): The base directory to search within.
        obj_id (str): The ID to search for.

    Returns:
        Optional[Path]: The first matching file path, or None if not found.
    """
    for file in base_dir.rglob("*"):
        if file.is_file() and obj_id in file.stem:
            return file
    return None

async def load_orbit_by_id(obj_id: str, file_type: Optional[str] = None) -> OrbitBase:
    """
    Load an OrbitBase object by its ID and optional file type.

    Args:
        obj_id (str): The ID of the orbit.
        file_type (Optional[str]): The file extension (json, csv, xml).

    Returns:
        OrbitBase: The loaded OrbitBase object.
    """
    # Determine the search directory based on file type
    search_dir = ORBIT_DIR / file_type if file_type else ORBIT_DIR

    # Locate the file
    file = (
        find_file_by_id(search_dir, obj_id)
        if not file_type
        else (search_dir / f"{obj_id}.{file_type}")
    )

    if file and file.exists():
        with open(file, "r") as f:
            if file.suffix == ".json":
                return OrbitBase.from_json(f.read())
            elif file.suffix == ".csv":
                return OrbitBase.from_csv(f.read())
            elif file.suffix == ".xml":
                return OrbitBase.from_xml(f.read())
    raise FileNotFoundError(f"No file found for orbit with ID '{obj_id}'.")

async def load_trajectory_by_id(obj_id: str, file_type: Optional[str] = None) -> Trajectory:
    """
    Load a Trajectory object by its ID and optional file type.

    Args:
        obj_id (str): The ID of the trajectory.
        file_type (Optional[str]): The file extension (json, csv, xml).

    Returns:
        Trajectory: The loaded Trajectory object.
    """
    # Determine the search directory based on file type
    search_dir = TRAJECTORY_DIR / file_type if file_type else TRAJECTORY_DIR

    # Locate the file
    file = (
        find_file_by_id(search_dir, obj_id)
        if not file_type
        else (search_dir / f"{obj_id}.{file_type}")
    )

    if file and file.exists():
        with open(file, "r") as f:
            if file.suffix == ".json":
                return Trajectory.from_json(f.read())
            elif file.suffix == ".csv":
                return Trajectory.from_csv(f.read())
            elif file.suffix == ".xml":
                return Trajectory.from_xml(f.read())
    raise FileNotFoundError(f"No file found for trajectory with ID '{obj_id}'.")


async def load_orbits(file_type: str = "json") -> List[OrbitBase]:
    """
    Load all orbits from the specified file type directory.
    """
    orbits = []
    for file in (ORBIT_DIR / file_type).glob(f"*.{file_type}"):
        if file_type == "json":
            with open(file, "r") as f:
                orbits.append(OrbitBase.from_json(f.read()))
        elif file_type == "csv":
            with open(file, "r") as f:
                orbits.append(OrbitBase.from_csv(f.read()))
        elif file_type == "xml":
            with open(file, "r") as f:
                orbits.append(OrbitBase.from_xml(f.read()))
    return orbits


async def load_trajectories(file_type: str = "json") -> List[Trajectory]:
    """
    Load all trajectories from the specified file type directory.
    """
    trajectories = []
    for file in (TRAJECTORY_DIR / file_type).glob(f"*.{file_type}"):
        if file_type == "json":
            with open(file, "r") as f:
                trajectories.append(Trajectory.from_json(f.read()))
        elif file_type == "csv":
            with open(file, "r") as f:
                trajectories.append(Trajectory.from_csv(f.read()))
        elif file_type == "xml":
            with open(file, "r") as f:
                trajectories.append(Trajectory.from_xml(f.read()))
    return trajectories