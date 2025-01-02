import json
import secrets
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO
from app.schemas.bodies.earth import Earth
from astropy.time import Time
from astropy import units as u
from poliastro.plotting.static import StaticOrbitPlotter
from poliastro.plotting.plotly import OrbitPlotter3D
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
                 points=None, id: int = None, 
                 orbit1_id: int = None, 
                 orbit2_id: int = None,
                 transfer_type = None,
                 name: str = None
                 ):
        """
        Initialize a trajectory object with delta-v values, time of flight, optional trajectory points, and orbit IDs.

        Args:
            delta_v1 (float): First impulse delta-v in km/s.
            delta_v2 (float): Second impulse delta-v in km/s.
            time_of_flight (float): Total time of flight in hours.
            points (list, optional): Discretized trajectory points.
            orbit1_id (int, optional): ID of the initial orbit.
            orbit2_id (int, optional): ID of the target orbit.
        """
        self.id = next(self._id_generator) if not id else id
        self.delta_v1 = delta_v1
        self.delta_v2 = delta_v2
        self.time_of_flight = time_of_flight
        self.points = points or []
        self.orbit1_id = orbit1_id
        self.orbit2_id = orbit2_id
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

        # Assuming self.points is a list of dictionaries with 'position' keys
        positions = [point["position"] for point in self.points]
        r = [pos[0] * u.km for pos in positions]
        v = [pos[1] * u.km / u.s for pos in positions]

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

        # Extract position and velocity vectors from trajectory points
        positions = [point["position"] for point in self.points]
        velocities = [point["velocity"] for point in self.points]

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

        start_time = Time(start_time) if start_time else Time.now()
        end_time = Time(end_time) if end_time else start_time + 1 * u.day

        extractor = CZMLExtractor(start_time, end_time, step_minutes * u.minute)

        # Assuming self.points can be used to create an Orbit object
        r = self.points[0]["position"][0] * u.km
        v = self.points[0]["velocity"][0] * u.km / u.s
        orbit = Orbit.from_vectors(Earth, r, v)

        extractor.add_orbit(orbit, label="Trajectory")
        czml_data = extractor.get_czml()

        with open(filename, "w") as f:
            json.dump(czml_data, f, indent=2)
            logger.info(f"CZML file saved to {filename}")

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
        if not data.get("id", None):
            raise ValueError("This trajectory has no id")
        
        # Retrieve the transfer type from the registry
        transfer_type_id = data.get("transfer_type_id", None)
        transfer_type = None
        if transfer_type_id is not None:
            transfer_type = TransferType.get_transfer_by_id(transfer_type_id)
        
        return Trajectory(
            id=data.get("id"),
            delta_v1=data.get("delta_v1", None),
            delta_v2=data.get("delta_v2", None),
            time_of_flight=data.get("time_of_flight", None),
            points=data.get("points", []),
            orbit1_id=data.get("orbit1_id", None),
            orbit2_id=data.get("orbit2_id", None),
            transfer_type=transfer_type,  
            name=data.get("name", None)
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
            "delta_v1": self.delta_v1,
            "delta_v2": self.delta_v2,
            "time_of_flight": self.time_of_flight,
            "orbit1_id": self.orbit1_id,
            "orbit2_id": self.orbit2_id,
            "points": self.points,
            "transfer_type_id": self.transfer_type.id if self.transfer_type else None,  # Add the transfer type ID
            "name": self.name if self.name else "",
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
        id = int(root.find("id").text)
        delta_v1 = float(root.find("delta_v1").text)
        delta_v2 = float(root.find("delta_v2").text)
        time_of_flight = float(root.find("time_of_flight").text)
        orbit1_id = int(root.find("orbit1_id").text)
        orbit2_id = int(root.find("orbit2_id").text)
        transfer_type_id = int(root.find("transfer_type_id").text)
        name = str(root.find("name").text)

        transfer_type = None
        if transfer_type_id:
            transfer_type = TransferType.get_transfer_by_id(transfer_type_id)

        points = []
        for point_elem in root.find("Points"):
            point = {
                "time": point_elem.find("time").text,
                "position": eval(point_elem.find("position").text),
                "velocity": eval(point_elem.find("velocity").text),
            }
            points.append(point)

        return Trajectory(delta_v1, delta_v2, time_of_flight, points, id, orbit1_id, orbit2_id, transfer_type, name)

    
    def to_xml(self, filename: str = "trajectory.xml") -> None:
        """
        Exports the trajectory to an XML file.

        Args:
            filename (str): Path to the XML file to save.
        """
        root = ET.Element("Trajectory")
        ET.SubElement(root, "id").text = str(self.id)
        ET.SubElement(root, "delta_v1").text = str(self.delta_v1)
        ET.SubElement(root, "delta_v2").text = str(self.delta_v2)
        ET.SubElement(root, "time_of_flight").text = str(self.time_of_flight)
        ET.SubElement(root, "orbit1_id").text = str(self.orbit1_id)
        ET.SubElement(root, "orbit2_id").text = str(self.orbit2_id)
        ET.SubElement(root, "transfer_type_id").text = str(self.transfer_type.id if self.transfer_type else None)
        ET.SubElement(root, "name").text = str(self.name if self.name else "")

        points_elem = ET.SubElement(root, "Points")
        for point in self.points:
            point_elem = ET.SubElement(points_elem, "Point")
            ET.SubElement(point_elem, "time").text = point["time"]
            ET.SubElement(point_elem, "position").text = str(point["position"])
            ET.SubElement(point_elem, "velocity").text = str(point["velocity"])

        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        logger.info(f"Trajectory exported to {filename}")

    @staticmethod
    def from_csv(csv_str: str) -> 'Trajectory':
        """
        Create a Trajectory instance from CSV data.

        Args:
            csv_str (str): CSV string.

        Returns:
            Trajectory: Reconstructed Trajectory instance.
        """
        df = pd.read_csv(StringIO(csv_str))

        # Extract metadata from the first row
        metadata = df.iloc[0]
        transfer_type = None
        transfer_type_id = metadata.get("transfer_type_id", None)
        if transfer_type_id is not None:
            transfer_type = TransferType.get_transfer_by_id(int(transfer_type_id))
        if not metadata.get("id", None):
            raise ValueError("This trajectory has no ID")
        
        trajectory = Trajectory(
            id=int(metadata.get("id")),
            delta_v1=float(metadata.get("delta_v1", None)),
            delta_v2=float(metadata.get("delta_v2", None)),
            time_of_flight=float(metadata.get("time_of_flight", None)),
            orbit1_id=int(metadata.get("orbit1_id", None)),
            orbit2_id=int(metadata.get("orbit2_id", None)),
            transfer_type=transfer_type,  # Attach transfer type
            name=metadata.get("name", None),
        )

        # Extract points from the subsequent rows
        points_df = df.iloc[1:]
        trajectory.points = points_df.to_dict(orient="records")

        return trajectory


    def to_csv(self, filename: str = None) -> str:
        """
        Exports the trajectory to a CSV string or file.

        Args:
            filename (str, optional): Path to the CSV file to save. Defaults to None.

        Returns:
            str: CSV string of the trajectory data.
        """
        metadata = {
            "id": self.id,
            "delta_v1": self.delta_v1,
            "delta_v2": self.delta_v2,
            "time_of_flight": self.time_of_flight,
            "orbit1_id": self.orbit1_id,
            "orbit2_id": self.orbit2_id,
            "transfer_type_id": self.transfer_type.id if self.transfer_type else None,  # Add transfer type ID
            "name": self.name if self.name else "",
        }

        metadata_row = pd.DataFrame([metadata])
        points_df = pd.DataFrame(self.points)
        combined_df = pd.concat([metadata_row, points_df], ignore_index=True, sort=False)

        csv_data = combined_df.to_csv(index=False)
        if filename:
            with open(filename, "w") as f:
                f.write(csv_data)
                logger.info(f"Trajectory exported to {filename}")
        return csv_data
