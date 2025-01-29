from fastapi import APIRouter, Path, Query, HTTPException
from typing import List
from pydantic import Field
from app.schemas.bodies.earth import Earth
from app.schemas.orbits.orbit_base import OrbitBase, OrbitInput, OrbitResponseWrapper, PaginatedOrbitResponseWrapper
from app.schemas.trajectory_base import PaginatedTrajectoryResponseWrapper, Trajectory, TrajectoryResponseWrapper
from app.schemas.transfer_type import TransferInput
from utils.hohmann.hohmann_transfer import HohmannTransfer
from logger_handler import handle_logger
from utils.loader import ORBIT_DIR, TRAJECTORY_DIR, load_orbit_by_id, load_orbits, load_trajectories, load_trajectory_by_id

logger = handle_logger()

# Initialize router
router = APIRouter()


@router.post("/orbit", response_model=OrbitResponseWrapper, status_code=200)
async def create_orbit(input: OrbitInput):
    #TODO: Remove the default Earth
    """
    Create a new orbit and store it in the specified format.

    **Request Parameters:**
    - `altitude_perigee` (float): Altitude of the perigee in km.
    - `altitude_apogee` (float): Altitude of the apogee in km.
    - `inclination`: (float): Orbital inclination in degrees.
    - `raan`: (float): Right Ascension of the Ascending Node (optional).
    - `argp`: (float): Argument of Perigee (optional).
    - `nu`: (float): True Anomaly (optional).
    - `file_type`: (str: File format to store the orbit (json, csv, xml). Defaults to "json".

    **Request Body:**
    ```json
    {
        "altitude_perigee": float, // Altitude of the perigee in km.
        "altitude_apogee": float, // Altitude of the apogee in km.
        "inclination": float, // Orbital inclination in degrees.
        "raan": float, // Right Ascension of the Ascending Node (optional).
        "argp": float, // Argument of Perigee (optional).
        "nu": float, // True Anomaly (optional).
        "file_type": str // File format to store the orbit (json, csv, xml). Defaults to "json".
    }
    ```

    **Response Schema:**
    ```json
    {
        "message": "Orbit created successfully",
        "orbit": {
            "id": int,
            "name": str,
            "altitude_perigee": float,
            "altitude_apogee": float,
            "inclination": float,
            "raan": float,
            "argp": float,
            "nu": float
        }
    }
    ```

    **Examples:**

    - **cURL:**
        ```bash
        curl -X POST "http://localhost:8000/orbit" \
            -H "Content-Type: application/json" \
            -d '{"altitude_perigee": 200, "altitude_apogee": 400, "inclination": 28.5}'
        ```

    - **Python:**
        ```python
        import requests

        response = requests.post(
            "http://localhost:8000/orbit",
            json={
                "altitude_perigee": 200,
                "altitude_apogee": 400,
                "inclination": 28.5
            }
        )
        print(response.json())
        ```

    - **JavaScript:**
        ```javascript
        fetch("http://localhost:8000/orbit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "altitude_perigee": 200,
                "altitude_apogee": 400,
                "inclination": 28.5
            })
        })
        .then(response => response.json())
        .then(data => console.log(data));
        ```
    """
    
    try:
        orbit = OrbitBase(input.altitude_perigee, input.altitude_apogee, input.inclination, input.raan, input.argp,input.nu, central_body=Earth()) # default Earth for now

        file_path = ORBIT_DIR / input.file_type / f"{orbit.id}.{input.file_type}"

        if input.file_type == "json":
            orbit.to_json(filename=str(file_path))
        elif input.file_type == "csv":
            orbit.to_csv(filename=str(file_path))
        elif input.file_type == "xml":
            orbit.to_xml(filename=str(file_path))
        else:
            raise ValueError("Invalid file type specified.")

        return {"message": "Orbit created successfully", "orbit": orbit.to_json()}
    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500)


@router.get("/orbit/{id}", response_model=OrbitResponseWrapper, status_code=200)
async def get_orbit(
    id: int = Path(
        ..., 
        description="Unique identifier of the orbit.",
        example=123, 
        ge=1
    ),
    file_type: str = Query(
        None,
        description="File format to search for (json, csv, xml). Defaults to None.",
        pattern="^(json|csv|xml)$"
    )
):
    """
    Retrieve an orbit by its ID and optional file type.

    **Request Parameters:**
    - `id` (int): Unique identifier of the orbit. Must be a positive integer.
    - `file_type` (str, optional): File format to search for (json, csv, xml).

    **Response Body:**
    ```json
    {
        "orbit": {
            "id": 123,
            "name": "Sample Orbit",
            "altitude_perigee": 200.0,
            "altitude_apogee": 400.0,
            "inclination": 28.5,
            "raan": 0.0,
            "argp": 0.0,
            "nu": 0.0
        }
    }
    ```

    **Examples:**

    - **cURL:**
        ```bash
        curl -X GET "http://localhost:8000/orbit/123?file_type=json" \
            -H "Content-Type: application/json"
        ```

    - **Python:**
        ```python
        import requests

        response = requests.get("http://localhost:8000/orbit/123", params={"file_type": "json"})
        print(response.json())
        ```

    - **JavaScript:**
        ```javascript
        fetch("http://localhost:8000/orbit/123?file_type=json")
        .then(response => response.json())
        .then(data => console.log(data));
        ```
    """
    
    try:
        orbit = await load_orbit_by_id(id, file_type)
        return {"orbit": orbit.to_json()}
    except FileNotFoundError as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500)


@router.get("/trajectory/{id}", response_model=TrajectoryResponseWrapper, status_code=200)
async def get_trajectory(
    id: int = Path(
        ...,  
        description="Unique identifier of the trajectory.",
        example=123, 
        ge=1
    ),
    file_type: str = Query(
        None,
        description="File format to search for (json, csv, xml). Defaults to None.",
        pattern="^(json|csv|xml)$"
    )
):
    """
    Retrieve a trajectory by its ID and optional file type.

    **Request Parameters:**
    - `id` (int): Unique identifier of the trajectory. Must be a positive integer.
    - `file_type` (str, optional): File format to search for (json, csv, xml).

    **Response Body:**
    ```json
    {
        "trajectory": {
            "id": 123,
            "delta_v1": 2.5,
            "delta_v2": 1.2,
            "time_of_flight": 7200.0,
            "initial_orbit_id": 1,
            "target_orbit_id": 2,
            "points": [
                {
                    "time": "2023-01-01T12:00:00Z",
                    "position": [7000.0, 0.0, 0.0],
                    "velocity": [0.0, 7.5, 0.0]
                }
            ],
            "transfer_type_id": 1,
            "name": "Hohmann Transfer"
        }
    }
    ```

    **Examples:**

    - **cURL:**
        ```bash
        curl -X GET "http://localhost:8000/trajectory/123?file_type=json" \
            -H "Content-Type: application/json"
        ```

    - **Python:**
        ```python
        import requests

        response = requests.get("http://localhost:8000/trajectory/123", params={"file_type": "json"})
        print(response.json())
        ```

    - **JavaScript:**
        ```javascript
        fetch("http://localhost:8000/trajectory/123?file_type=json")
        .then(response => response.json())
        .then(data => console.log(data));
        ```
    """
    
    try:
        trajectory = await load_trajectory_by_id(id, file_type)
        return {"trajectory": trajectory.to_json()}
    except FileNotFoundError as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500)


@router.post("/transfers", response_model=TrajectoryResponseWrapper, status_code=200)
async def perform_transfer_calculation(input: TransferInput):
    """
    Calculate an orbital transfer between two orbits and store the trajectory.
    **Request Parameters:**
    - `intial_orbit_id` (int): Unique identifier of the initial orbit. Must be a positive integer.
    - `target_orbit_id` (int): Unique identifier of the target orbit. Must be a positive integer.
    - `transfer_type` (str): Specify the type of transfer chosen.
    - `file_type` (str, optional): File format to search for (json, csv, xml).

    **Request Body:**
    ```json
    {
        "initial_orbit_id": 1,
        "target_orbit_id": 2,
        "transfer_type": "hohmann",
        "file_type": "json"
    }
    ```

    **Response Body:**
    ```json
    {
        "message": "Transfer calculated successfully",
        "trajectory": {
            "id": 123,
            "delta_v1": 2.5,
            "delta_v2": 1.2,
            "time_of_flight": 7200.0,
            "initial_orbit_id": 1,
            "target_orbit_id": 2,
            "points": [
                {
                    "time": "2023-01-01T12:00:00Z",
                    "position": [7000.0, 0.0, 0.0],
                    "velocity": [0.0, 7.5, 0.0]
                }
            ],
            "transfer_type_id": 1,
            "name": "Hohmann Transfer"
        }
    }
    ```

    **Examples:**

    - **cURL:**
        ```bash
        curl -X POST "http://localhost:8000/transfers" \
            -H "Content-Type: application/json" \
            -d '{"initial_orbit_id": 1, "target_orbit_id": 2, "transfer_type": "hohmann", "file_type": "json"}'
        ```

    - **Python:**
        ```python
        import requests

        response = requests.post(
            "http://localhost:8000/transfers",
            json={
                "initial_orbit_id": 1,
                "target_orbit_id": 2,
                "transfer_type": "hohmann",
                "file_type": "json"
            }
        )
        print(response.json())
        ```

    - **JavaScript:**
        ```javascript
        fetch("http://localhost:8000/transfers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "initial_orbit_id": 1,
                "target_orbit_id": 2,
                "transfer_type": "hohmann",
                "file_type": "json"
            })
        })
        .then(response => response.json())
        .then(data => console.log(data));
        ```
    """
    
    try:

        initial_orbit = await load_orbit_by_id(input.initial_orbit_id)
        target_orbit = await load_orbit_by_id(input.target_orbit_id)

        if input.transfer_type == "hohmann":
            calculator = HohmannTransfer()
        else:
            raise ValueError(f"Transfer type '{input.transfer_type}' not supported")

        trajectory = calculator.calculate_transfer(initial_orbit, target_orbit)
        file_path = TRAJECTORY_DIR / input.file_type / f"{trajectory.id}.{input.file_type}"

        if input.file_type == "json":
            trajectory.to_json(filename=str(file_path))
        elif input.file_type == "csv":
            trajectory.to_csv(filename=str(file_path))
        elif input.file_type == "xml":
            trajectory.to_xml(filename=str(file_path))
        else:
            raise ValueError("Invalid file type specified.")

        return {"message": "Transfer calculated successfully", "trajectory": trajectory.to_json()}
    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500)
    
@router.get("/orbits", response_model=PaginatedOrbitResponseWrapper, status_code=200)
async def get_orbits(
        file_type: str = Query(
            None,
            description="File format to search for (json, csv, xml). Defaults to None.",
        pattern="^(json|csv|xml)$"
        ),
        page: int = Query(
            1,
            ge=1,
            description="The current page number, starting from 1."
        ),
        page_size: int = Query(
            50,
            ge=1,
            le=100,
            description="The number of items per page. Must be between 1 and 100."
        )
    ):
    """
    Retrieve all stored orbits in the specified format with pagination.

    **Request Parameters:**
    - `file_type` (str, optional): File format to search for (json, csv, xml). Defaults to None.
    - `page` (int, optional): The current page number, starting from 1. Defaults to 1.
    - `page_size` (int, optional): The number of items per page. Must be between 1 and 100. Defaults to 50.

    **Response Body:**
    ```json
    {
        "page": 1,
        "page_size": 50,
        "total_items": 200,
        "total_pages": 4,
        "next": "/orbits?page=2&page_size=50",
        "data": [
            {
                "id": 123,
                "name": "Sample Orbit",
                "altitude_perigee": 200.0,
                "altitude_apogee": 400.0,
                "inclination": 28.5,
                "raan": 0.0,
                "argp": 0.0,
                "nu": 0.0
            },
            ...
        ]
    }
    ```

    **Examples:**

    - **cURL:**
        ```bash
        curl -X GET "http://localhost:8000/orbits?page=1&page_size=20" \
            -H "Content-Type: application/json"
        ```

    - **Python:**
        ```python
        import requests

        response = requests.get(
            "http://localhost:8000/orbits",
            params={"page": 1, "page_size": 20}
        )
        print(response.json())
        ```

    - **JavaScript:**
        ```javascript
        fetch("http://localhost:8000/orbits?page=1&page_size=20")
        .then(response => response.json())
        .then(data => console.log(data));
        ```
    """
    
    try:
        orbits: List[OrbitBase] = await load_orbits(file_type)
        base_url = "/orbits"
        return PaginatedTrajectoryResponseWrapper.paginate_items([orbit.to_json() for orbit in orbits], base_url, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500)


@router.get("/trajectories", response_model=PaginatedTrajectoryResponseWrapper, status_code=200)
async def get_trajectories(
        file_type: str = Query(
            None,
            description="File format to search for (json, csv, xml). Defaults to None.",
        pattern="^(json|csv|xml)$"
        ),
        page: int = Query(
            1,
            ge=1,
            description="The current page number, starting from 1."
        ),
        page_size: int = Query(
            50,
            ge=1,
            le=100,
            description="The number of items per page. Must be between 1 and 100."
        )
    ):
    """
    Retrieve all stored trajectories in the specified format with pagination.

    **Request Parameters:**
    - `file_type` (str, optional): File format to search for (json, csv, xml). Defaults to None.
    - `page` (int, optional): The current page number, starting from 1. Defaults to 1.
    - `page_size` (int, optional): The number of items per page. Must be between 1 and 100. Defaults to 50.

    **Response Body:**
    ```json
    {
        "page": 1,
        "page_size": 50,
        "total_items": 200,
        "total_pages": 4,
        "next": "/trajectories?page=2&page_size=50",
        "data": [
            {
                "id": 123,
                "delta_v1": 2.5,
                "delta_v2": 1.2,
                "time_of_flight": 7200.0,
                "initial_orbit_id": 1,
                "target_orbit_id": 2,
                "points": [
                    {
                        "time": "2023-01-01T12:00:00Z",
                        "position": [7000.0, 0.0, 0.0],
                        "velocity": [0.0, 7.5, 0.0]
                    }
                ],
                "transfer_type_id": 1,
                "name": "Hohmann Transfer"
            },
            ...
        ]
    }
    ```

    **Examples:**

    - **cURL:**
        ```bash
        curl -X GET "http://localhost:8000/trajectories?page=1&page_size=20" \
            -H "Content-Type: application/json"
        ```

    - **Python:**
        ```python
        import requests

        response = requests.get(
            "http://localhost:8000/trajectories",
            params={"page": 1, "page_size": 20}
        )
        print(response.json())
        ```

    - **JavaScript:**
        ```javascript
        fetch("http://localhost:8000/trajectories?page=1&page_size=20")
        .then(response => response.json())
        .then(data => console.log(data));
        ```
    """
    
    try:
        trajectories: List[Trajectory] = await load_trajectories(file_type)
        base_url = "/trajectories"
        return PaginatedTrajectoryResponseWrapper.paginate_items([trajectory.to_json() for trajectory in trajectories], base_url, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500)
