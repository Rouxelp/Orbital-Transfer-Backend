import json
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
    def __init__(self, delta_v1: float, delta_v2: float, time_of_flight: float, points=None):
        """
        Initialize a trajectory object with delta-v values, time of flight, and optional trajectory points.

        Args:
            delta_v1 (float): First impulse delta-v in km/s.
            delta_v2 (float): Second impulse delta-v in km/s.
            time_of_flight (float): Total time of flight in hours.
            points (list, optional): Discretized trajectory points.
        """
        self.delta_v1 = delta_v1
        self.delta_v2 = delta_v2
        self.time_of_flight = time_of_flight
        self.points = points or []
        self.transfer_type: TransferType = None

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

        # Assuming self.points is a list of dictionaries with 'position' keys
        positions = [point["position"] for point in self.points]
        r = [pos[0] * u.km for pos in positions]
        v = [pos[1] * u.km / u.s for pos in positions]

        # Create an Orbit object for plotting
        orbit = Orbit.from_vectors(Earth, r[0], v[0])

        plotter = OrbitPlotter3D()
        plotter.plot(orbit, label="Trajectory")
        plotter.set_title(title)
        pio.show(plotter.figure)

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

    def to_xml(self, filename: str = "trajectory.xml") -> None:
        """
        Exports the trajectory to an XML file.

        Args:
            filename (str): Path to the XML file to save.
        """
        root = ET.Element("Trajectory")
        ET.SubElement(root, "delta_v1").text = str(self.delta_v1)
        ET.SubElement(root, "delta_v2").text = str(self.delta_v2)
        ET.SubElement(root, "time_of_flight").text = str(self.time_of_flight)

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
    def from_json(json_str: str) -> 'Trajectory':
        """
        Create a Trajectory instance from JSON data.

        Args:
            json_str (str): JSON string.

        Returns:
            Trajectory: Reconstructed Trajectory instance.
        """
        data = json.loads(json_str)
        return Trajectory(
            delta_v1=data["delta_v1"],
            delta_v2=data["delta_v2"],
            time_of_flight=data["time_of_flight"],
            points=data.get("points", []),
        )

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
        points = df.to_dict(orient="records")
        return Trajectory(delta_v1=0, delta_v2=0, time_of_flight=0, points=points)

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
        delta_v1 = float(root.find("delta_v1").text)
        delta_v2 = float(root.find("delta_v2").text)
        time_of_flight = float(root.find("time_of_flight").text)

        points = []
        for point_elem in root.find("Points"):
            point = {
                "time": point_elem.find("time").text,
                "position": eval(point_elem.find("position").text),
                "velocity": eval(point_elem.find("velocity").text),
            }
            points.append(point)

        return Trajectory(delta_v1, delta_v2, time_of_flight, points)