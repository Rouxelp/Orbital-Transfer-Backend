import json
import secrets
from typing import List, Optional
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO
from pydantic import BaseModel, field_validator
from app.schemas.bodies.earth import Earth
from astropy.time import Time
from astropy import units as u
from poliastro.plotting.static import StaticOrbitPlotter
from poliastro.plotting import OrbitPlotter3D
from poliastro.twobody import Orbit
from poliastro.czml.extract_czml import CZMLExtractor
from app.schemas.transfer_type import TransferType
from logger_handler import handle_logger

logger = handle_logger()


class Trajectory:
    """
    A class to encapsulate the results of an orbital transfer or trajectory calculation.
    Includes methods for exporting results and visualizing trajectory points.
    """
    _id_generator = iter(int(secrets.token_hex(12), 16) for _ in range(1_000_000))
    
    def __init__(self, 
                 delta_v1: float, 
                 delta_v2: float, 
                 time_of_flight: float, 
                 points: List['Point'] = [], 
                 transfer_type: TransferType = None,
                 id: Optional[int] = None, 
                 initial_orbit_id: Optional[int] = None, 
                 target_orbit_id: Optional[int] = None,
                 name: Optional[str] = None
            ) -> None:
        """
        Initialize a trajectory object with delta-v values, time of flight, optional trajectory points, and orbit IDs.

        Args:
            delta_v1 (float): First impulse delta-v in km/s.
            delta_v2 (float): Second impulse delta-v in km/s.
            time_of_flight (float): Total time of flight in hours.
            points (list[Point], optional): Discretized trajectory points.
            transfer_type (TransferType): Type of transfer use to compute the trajectory
            id (int, optional): ID of the trajectory if exists. 
            initial_orbit_id (int, optional): ID of the initial orbit.
            target_orbit_id (int, optional): ID of the target orbit.
            name (str, optional): Name of the trajectory
        """
        self.id = next(self._id_generator) if not id else id
        self.delta_v1 = delta_v1 * u.km / u.s
        self.delta_v2 = delta_v2 * u.km / u.s
        self.time_of_flight = time_of_flight * u.hour
        self.points = points or []
        self.initial_orbit_id = initial_orbit_id
        self.target_orbit_id = target_orbit_id
        self.transfer_type: TransferType = transfer_type
        self.name = name

    def visualize_2d(self, title="2D Trajectory Visualization"):
        """
        Visualizes the trajectory in 2D using Poliastro's StaticOrbitPlotter.

        Args:
            title (str): Title of the plot.
        """
        if not self.points:
            logger.info("No trajectory points available for 2D visualization.")
            return

        # Extract position vectors from Point instances
        positions = [point.position for point in self.points]
        r = [pos * u.km for pos in positions]

        # Extract velocity vectors from Point instances
        velocities = [point.velocity for point in self.points]
        v = [vel * u.km / u.s for vel in velocities]

        # Create an Orbit object for plotting
        orbit = Orbit.from_vectors(Earth, r[0], v[0])

        plotter = StaticOrbitPlotter()
        plotter.plot(orbit, label="Trajectory")
        plotter.set_title(title)
        plotter.show()

    def visualize_3d(self, title="3D Trajectory Visualization"):
        """
        Visualizes the trajectory in 3D using Poliastro's OrbitPlotter3D.

        Args:
            title (str): Title of the plot.
        """
        if not self.points:
            logger.info("No trajectory points available for 3D visualization.")
            return

        # Extract position and velocity vectors from Point instances
        positions = [point.position for point in self.points]
        velocities = [point.velocity for point in self.points]

        # Convert to astropy quantities
        r = [pos * u.km for pos in positions]
        v = [vel * u.km / u.s for vel in velocities]

        # Create an Orbit object using the first position and velocity
        orbit = Orbit.from_vectors(Earth, r[0], v[0])

        # Initialize the 3D plotter and plot the trajectory
        plotter = OrbitPlotter3D(orbit.frame)
        fig = plotter.figure

        # Plot the entire trajectory
        plotter.plot_trajectory(orbit.sample(len(self.points)), label="Trajectory")

        # Customize title
        fig.update_layout(title=title)

        # Show the plot
        fig.show()

    def export_to_czml(self, filename="trajectory.czml", start_time=None, end_time=None, step_minutes=10):
        """
        Exports the trajectory to a CZML file for visualization in tools like Cesium.

        Args:
            filename (str): File name to save the CZML data.
            start_time (str, optional): Start time in ISO format. Defaults to current time.
            end_time (str, optional): End time in ISO format. Defaults to start_time + 1 day.
            step_minutes (int): Time step between frames in minutes.
        """
        if not self.points:
            logger.info("No trajectory points available for CZML export.")
            return

        # Define time range
        start_time = Time(start_time) if start_time else Time.now()
        end_time = Time(end_time) if end_time else start_time + 1 * u.day

        # Create the CZML extractor
        extractor = CZMLExtractor(start_time, end_time, step_minutes * u.minute)

        # Extract the first point's position and velocity for the initial orbit
        r = self.points[0].position * u.km
        v = self.points[0].velocity * (u.km / u.s)

        # Create a Poliastro Orbit object
        orbit = Orbit.from_vectors(Earth, r, v)

        # Add the orbit to the CZML extractor
        extractor.add_orbit(orbit, label="Trajectory")

        # Generate CZML data and save to file
        czml_data = extractor.get_czml()
        with open(filename, "w") as f:
            json.dump(czml_data, f, indent=2)
            logger.info(f"CZML file saved to {filename}")

    def log_info(self) -> None:
        """
        Logs key details about the trajectory.
        Includes delta-v, time of flight, orbits, transfer type, and point count.
        """
        logger.info(f"Trajectory - ID: {self.id}")
        logger.info(f"Trajectory - Name: {self.name if self.name else 'Unnamed'}")
        logger.info(f"Delta-v1: {self.delta_v1.to(u.km / u.s):.3f} km/s")
        logger.info(f"Delta-v2: {self.delta_v2.to(u.km / u.s):.3f} km/s")
        logger.info(f"Time of Flight: {self.time_of_flight.to(u.hour):.2f} hours")
        logger.info(f"Initial Orbit ID: {self.initial_orbit_id if self.initial_orbit_id else 'N/A'}")
        logger.info(f"Target Orbit ID: {self.target_orbit_id if self.target_orbit_id else 'N/A'}")
        logger.info(f"Transfer Type: {self.transfer_type.name if self.transfer_type else 'None'}")
        logger.info(f"Number of Points: {len(self.points)}")

    @staticmethod
    def from_json(json_str: str) -> 'Trajectory':
        """
        Create a Trajectory instance from JSON data.

        Args:
            json_str (str): JSON string.

        Returns:
            Trajectory: Reconstructed Trajectory instance.
        """
        data: dict = json.loads(json_str)
        if not data.get("id"):
            raise ValueError("This trajectory has no ID")

        transfer_type = None
        transfer_type_id = data.get("transfer_type_id")
        if transfer_type_id is not None:
            transfer_type = TransferType.get_transfer_by_id(transfer_type_id)

        points = [Point.from_json(point) for point in data.get("points", [])]

        return Trajectory(
            id=int(data.get("id")),
            delta_v1=float(data.get("delta_v1")) if data.get("delta_v1", None) is not None else None,
            delta_v2=float(data.get("delta_v2")) if data.get("delta_v2", None) is not None else None,
            time_of_flight=float(data.get("time_of_flight")) if data.get("time_of_flight", None) is not None else None,
            points=points,
            initial_orbit_id=int(data.get("initial_orbit_id")) if data.get("initial_orbit_id", None) is not None else None,
            target_orbit_id=int(data.get("target_orbit_id")) if data.get("target_orbit_id", None) is not None else None,
            transfer_type=transfer_type,
            name=data.get("name", "")
        )

    def to_json(self, filename: str = None) -> str:
        """
        Exports the trajectory to a JSON string or file.

        Args:
            filename (str, optional): Path to the JSON file to save. Defaults to None.

        Returns:
            str: JSON string of the trajectory data.
        """
        data = {
            "id": self.id,
            "delta_v1": self.delta_v1.value,
            "delta_v2": self.delta_v2.value,
            "time_of_flight": self.time_of_flight.value,
            "initial_orbit_id": self.initial_orbit_id,
            "target_orbit_id": self.target_orbit_id,
            "points": [point.to_json() for point in self.points],
            "transfer_type_id": self.transfer_type.id if self.transfer_type else None,
            "name": self.name,
        }
        json_data = json.dumps(data, indent=2)
        if filename:
            with open(filename, "w") as f:
                f.write(json_data)
                logger.info(f"Trajectory exported to {filename}")
        return json_data

    @staticmethod
    def from_xml(xml_str: str) -> 'Trajectory':
        """
        Create a Trajectory instance from XML data.

        Args:
            xml_str (str): XML string.

        Returns:
            Trajectory: Reconstructed Trajectory instance.
        """
        root = ET.fromstring(xml_str)
        id_text = root.find("id").text
        if not id_text:
            raise ValueError("This Orbit has no id")
        delta_v1 = float(root.find("delta_v1").text) if root.find("delta_v1").text is not None else None
        delta_v2 = float(root.find("delta_v2").text) if root.find("delta_v2").text is not None else None
        time_of_flight = float(root.find("time_of_flight").text) if root.find("time_of_flight").text is not None else None
        initial_orbit_id = int(root.find("initial_orbit_id").text) if root.find("initial_orbit_id").text is not None else None 
        target_orbit_id = int(root.find("target_orbit_id").text) if root.find("target_orbit_id").text is not None else None
        transfer_type_id = int(root.find("transfer_type_id").text) if root.find("transfer_type_id").text is not None else None
        transfer_type = TransferType.get_transfer_by_id(int(transfer_type_id)) if transfer_type_id else None
        name = root.find("name").text if root.find("name").text is not None else ""

        points = []
        points_elem = root.find("Points")

        if points_elem is not None:
            for point_elem in points_elem:
                # Log all child tags for this Point
                child_tags = [child.tag for child in point_elem]
                
                position_x = (
                    float(point_elem.find("position_x").text) * u.km
                    if point_elem.find("position_x") is not None and point_elem.find("position_x").text
                    else None
                )
                position_y = (
                    float(point_elem.find("position_y").text) * u.km
                    if point_elem.find("position_y") is not None and point_elem.find("position_y").text
                    else None
                )
                position_z = (
                    float(point_elem.find("position_z").text) * u.km
                    if point_elem.find("position_z") is not None and point_elem.find("position_z").text
                    else None
                )
                velocity_x = (
                    float(point_elem.find("velocity_x").text) * u.km / u.s
                    if point_elem.find("velocity_x") is not None and point_elem.find("velocity_x").text
                    else None
                )
                velocity_y = (
                    float(point_elem.find("velocity_y").text) * u.km / u.s
                    if point_elem.find("velocity_y") is not None and point_elem.find("velocity_y").text
                    else None
                )
                velocity_z = (
                    float(point_elem.find("velocity_z").text) * u.km / u.s
                    if point_elem.find("velocity_z") is not None and point_elem.find("velocity_z").text
                    else None
                )
    
                time = point_elem.find("time").text

                points.append(Point(
                    time=time,
                    position=[position_x, position_y, position_z],
                    velocity=[velocity_x, velocity_y, velocity_z]
                ))

        return Trajectory(
            id=int(id_text),
            delta_v1=delta_v1,
            delta_v2=delta_v2,
            time_of_flight=time_of_flight,
            points=points,
            initial_orbit_id=initial_orbit_id,
            target_orbit_id=target_orbit_id,
            transfer_type=transfer_type,
            name=name,
        )

    def to_xml(self, filename: str = None) -> str:
        """
        Exports the trajectory to an XML string or file.

        Args:
            filename (str, optional): File to save the XML data. Defaults to None.

        Returns:
            str: Serialized XML string.
        """
        root = ET.Element("Trajectory")
        ET.SubElement(root, "id").text = str(self.id)
        ET.SubElement(root, "delta_v1").text = str(self.delta_v1.to(u.km / u.s).value if self.delta_v1 is not None else "")
        ET.SubElement(root, "delta_v2").text = str(self.delta_v2.to(u.km / u.s).value if self.delta_v2 is not None else "")
        ET.SubElement(root, "time_of_flight").text = str(self.time_of_flight.to(u.hour).value if self.time_of_flight is not None else "")
        ET.SubElement(root, "initial_orbit_id").text = str(self.initial_orbit_id if self.initial_orbit_id is not None else "")
        ET.SubElement(root, "target_orbit_id").text = str(self.target_orbit_id if self.target_orbit_id is not None else "")
        ET.SubElement(root, "transfer_type_id").text = str(self.transfer_type.id if self.transfer_type is not None else "")
        ET.SubElement(root, "name").text = self.name if self.name else ""

        # Serialize points
        points_elem = ET.SubElement(root, "Points")
        for point in self.points:
            point_elem = ET.SubElement(points_elem, "Point")
            ET.SubElement(point_elem, "time").text = point.time
            ET.SubElement(point_elem, "position_x").text = str(point.position[0].to(u.km).value)
            ET.SubElement(point_elem, "position_y").text = str(point.position[1].to(u.km).value)
            ET.SubElement(point_elem, "position_z").text = str(point.position[2].to(u.km).value)
            ET.SubElement(point_elem, "velocity_x").text = str(point.velocity[0].to(u.km / u.s).value)
            ET.SubElement(point_elem, "velocity_y").text = str(point.velocity[1].to(u.km / u.s).value)
            ET.SubElement(point_elem, "velocity_z").text = str(point.velocity[2].to(u.km / u.s).value)

        # Serialize XML data
        xml_data = ET.tostring(root, encoding="unicode")
        if filename:
            with open(filename, "w") as f:
                f.write(xml_data)
                logger.info(f"Trajectory exported to {filename}")
        return xml_data

    @staticmethod
    def from_csv(csv_str: str) -> 'Trajectory':
        """
        Create a Trajectory instance from a CSV string with exploded metadata and new headers.

        Args:
            csv_str (str): CSV string.

        Returns:
            Trajectory: Reconstructed Trajectory instance.
        """
        df = pd.read_csv(StringIO(csv_str))

        # Extract metadata from the first row
        first_row = df.iloc[0]
        transfer_type_id = first_row.get("transfer_type_id", None)
        transfer_type = None
        if transfer_type_id and not pd.isna(transfer_type_id):
            transfer_type = TransferType.get_transfer_by_id(int(transfer_type_id))

        # Extract points
        points = []
        for _, row in df.iterrows():
            try:
                position = [
                    float(row.get("position_x", 0)),
                    float(row.get("position_y", 0)),
                    float(row.get("position_z", 0)),
                ]
                velocity = [
                    float(row.get("velocity_x", 0)),
                    float(row.get("velocity_y", 0)),
                    float(row.get("velocity_z", 0)),
                ]
                points.append(Point(
                    time=row.get("time", ""),
                    position=[coord * u.km for coord in position],
                    velocity=[coord * u.km / u.s for coord in velocity],
                ))
            except Exception as e:
                logger.error(f"Error parsing point data: {e}")
                raise ValueError(f"Invalid point data in row: {row}")

        return Trajectory(
            id=int(first_row.get("id", 0)),
            delta_v1=float(first_row.get("delta_v1", 0)) if first_row.get("delta_v1") is not None else None,
            delta_v2=float(first_row.get("delta_v2", 0)) if first_row.get("delta_v2") is not None else None,
            time_of_flight=float(first_row.get("time_of_flight", 0)) if first_row.get("time_of_flight") is not None else None,
            points=points,
            initial_orbit_id=int(first_row.get("initial_orbit_id", 0)) if first_row.get("initial_orbit_id") is not None else None,
            target_orbit_id=int(first_row.get("target_orbit_id", 0)) if first_row.get("target_orbit_id") is not None else None,
            transfer_type=transfer_type,
            name=first_row.get("name", ""),
        )

    def to_csv(self, filename: str = None) -> str:
        """
        Exports the trajectory to a CSV string or file, exploding metadata and splitting position/velocity into individual components.

        Args:
            filename (str, optional): Path to the CSV file to save. Defaults to None.

        Returns:
            str: CSV string of the trajectory data.
        """
        rows = []
        for point in self.points:
            position_values = [coord.to_value(u.km) for coord in point.position]
            velocity_values = [coord.to_value(u.km / u.s) for coord in point.velocity]

            rows.append({
                "id": self.id,
                "delta_v1": self.delta_v1.value if self.delta_v1 is not None else None,
                "delta_v2": self.delta_v2.value if self.delta_v2 is not None else None,
                "time_of_flight": self.time_of_flight.value if self.time_of_flight is not None else None,
                "initial_orbit_id": self.initial_orbit_id,
                "target_orbit_id": self.target_orbit_id,
                "transfer_type_id": self.transfer_type.id if self.transfer_type is not None else None,
                "name": self.name,
                "time": point.time,
                "position_x": position_values[0] if len(position_values) > 0 else None,
                "position_y": position_values[1] if len(position_values) > 1 else None,
                "position_z": position_values[2] if len(position_values) > 2 else None,
                "velocity_x": velocity_values[0] if len(velocity_values) > 0 else None,
                "velocity_y": velocity_values[1] if len(velocity_values) > 1 else None,
                "velocity_z": velocity_values[2] if len(velocity_values) > 2 else None,
            })

        # Convert rows to a DataFrame and save/export as CSV
        df = pd.DataFrame(rows)
        csv_data = df.to_csv(index=False)

        if filename:
            with open(filename, "w") as f:
                f.write(csv_data)
                logger.info(f"Trajectory exported to {filename}")

        return csv_data



class Point(BaseModel):
    """
    #! position does not include attractor body radius in its values, unlike the rest of the app, because they are defined relatively to the attractor and simplify calculation
    """
    time: str  # Timestamp or time string
    position: List[u.Quantity]  # Position as a list of Astropy Quantities
    velocity: List[u.Quantity]  # Velocity as a list of Astropy Quantities

    class Config:
        arbitrary_types_allowed = True

    @field_validator("position", mode="before")
    def validate_position(cls, value):
        """
        Ensure position is a list of valid Astropy Quantities or numerical values in kilometers.
        """
        if not isinstance(value, list) or not all(isinstance(coord, (u.Quantity, int, float)) for coord in value):
            raise ValueError("Position must be a list of numerical values or Astropy Quantities.")
        return [coord if isinstance(coord, u.Quantity) else coord * u.km for coord in value]

    @field_validator("velocity", mode="before")
    def validate_velocity(cls, value):
        """
        Ensure velocity is a list of valid Astropy Quantities or numerical values in kilometers per second.
        """
        if not isinstance(value, list) or not all(isinstance(coord, (u.Quantity, int, float)) for coord in value):
            raise ValueError("Velocity must be a list of numerical values or Astropy Quantities.")
        return [coord if isinstance(coord, u.Quantity) else coord * u.km / u.s for coord in value]

    def to_json(self) -> str:
        """
        Serialize the Point instance to a JSON string.

        Returns:
            str: Serialized JSON representation of the Point instance.
        """
        data = {
            "time": self.time,
            "position": [coord.to_value(u.km) for coord in self.position],  # Convert to plain floats
            "velocity": [coord.to_value(u.km / u.s) for coord in self.velocity]  # Convert to plain floats
        }
        return json.dumps(data, indent=2)
    
    @staticmethod
    def from_json(json_str: str) -> 'Point':
        """
        Deserialize a JSON string into a Point instance.

        Args:
            json_str (str): JSON string.

        Returns:
            Point: Reconstructed Point instance.
        """
        data = json.loads(json_str)
        
        # Validate and convert fields
        time = data.get("time", "")
        if not isinstance(time, str):
            raise ValueError(f"Invalid 'time' value: {time}")

        position = data.get("position", [])
        if not isinstance(position, list) or not all(isinstance(coord, (int, float)) for coord in position):
            raise ValueError(f"Invalid 'position' value: {position}")
        position = [coord * u.km for coord in position]

        velocity = data.get("velocity", [])
        if not isinstance(velocity, list) or not all(isinstance(coord, (int, float)) for coord in velocity):
            raise ValueError(f"Invalid 'velocity' value: {velocity}")
        velocity = [coord * u.km / u.s for coord in velocity]

        return Point(time=time, position=position, velocity=velocity)

