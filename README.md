# Orbital Transfer Backend

## Overview

This project is a backend system for managing and calculating orbital transfers, built using Python and the **Poliastro** library as a foundation. The system enables:

- Modeling orbital configurations (e.g., perigee, apogee, inclination).
- Computing orbital transfers (e.g., Hohmann transfers).
- Managing and exporting trajectory data.
- Storing orbital and trajectory data in a cold storage directory (`/data`).

While the project leverages **Poliastro** for its orbital mechanics capabilities, some calculations (e.g., Hohmann transfer) have been reimplemented manually. This approach aims to deepen understanding of core orbital mechanics and explore custom implementations for specific use cases.

Visualization functionalities are included primarily for debugging purposes.

---

## Features

### Core Objects

1. **OrbitBase**:
   - Represents an orbital configuration with perigee, apogee, and inclination.
   - Converts parameters into Poliastro-compatible `Orbit` objects.
   - Supports serialization to and deserialization from JSON, CSV, and XML formats.

2. **Trajectory**:
   - Encapsulates the results of an orbital transfer (delta-v values, time of flight, discrete trajectory points).
   - Includes methods for serialization and deserialization across multiple formats.
   - Visualizes trajectory data for debugging purposes.

3. **TransferType and HohmannTransfer**:
   - `TransferType`: A base class for implementing various orbital transfer methods.
   - `HohmannTransfer`: Implements the Hohmann transfer calculation using custom logic, independent of Poliastro’s built-in methods.

### Storage and Persistence

Data is stored in a local cold storage folder (`/data`), simulating bucket-based storage. The folder structure supports:

- **Orbital data** (e.g., JSON, CSV, XML).
- **Trajectory data** for calculated transfers.

This design allows for easy access and portability of the data.

### API Backend

The backend is implemented with **FastAPI**, exposing the following functionalities:

- **Orbit Management**:
  - Create, retrieve, and serialize orbital configurations.

- **Transfer Calculations**:
  - Compute orbital transfers (currently Hohmann transfers) by specifying the initial and target orbits.
  - Extendable to support additional transfer types (e.g., bi-elliptic transfers).

- **Trajectory Management**:
  - Retrieve and export calculated trajectory data.

### Testing

Comprehensive tests are written using **Pytest** to validate:

- Serialization/deserialization for JSON, CSV, and XML.
- Core functionalities of each object (e.g., OrbitBase, Trajectory).
- Correctness of custom implementations like Hohmann transfer calculations.

---

## Project Structure

```
project/
├── app/
│   ├── main.py          # Entry point for the FastAPI application
│   ├── routes.py        # API route definitions
│   ├── schemas/          # Core classes and logic
│   │   ├── bodies/  # Body class
│   │   ├── orbits/  # Orbit class
│   │   ├── trajectory.py  # Trajectory class
│   │   ├── transfer_type.py  # TransferType
│   │   └── __init__.py
│   ├──utils/           # Utility functions (e.g., custom calculations)
│       └── hohmann/
├──── data/        # Simulated local storage
│       ├── trajectories/        # JSON, CSV, XML files
│       ├── orbits/        # JSON, CSV, XML files
│       └── __init__.py
└── tests/               # Unit tests for all functionalities
    ├── test_orbit_base.py
    ├── test_trajectory.py
    ├── test_routes.py
    └── __init__.py
```
