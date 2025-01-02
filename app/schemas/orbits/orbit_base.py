from astropy import units as u
from app.schemas.bodies.body import Body
from app.schemas.bodies.earth import Earth
from poliastro.twobody import Orbit
from poliastro.plotting.static import StaticOrbitPlotter
from poliastro.plotting.plotly import OrbitPlotter3D
from poliastro.czml.extract_czml import CZMLExtractor
from astropy.time import Time
from astropy.time import Time
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Optional
from logger_handler import handle_logger

logger = handle_logger()

class OrbitBase:
    """
    A base class to represent an orbital configuration.
    Includes methods for conversion to Poliastro Orbit objects,
    visualization, and logging key orbital information.
    """
    def __init__(self, altitude_perigee: float, altitude_apogee: float, inclination: float, 
                 raan: float = 0.0, argp: float = 0.0, nu: float = 0.0, central_body: Optional[object] = Earth()) -> None:
        """
        Args:
            altitude_perigee (float): Altitude of the perigee (in km).
            altitude_apogee (float): Altitude of the apogee (in km).
            inclination (float): Orbital inclination (in degrees).
            raan (float): Right ascension of the ascending node (in degrees).
            argp (float): Argument of perigee (in degrees).
            nu (float): True anomaly (in degrees).
            central_body (str): Central body of the orbit (e.g., 'Earth').
        """
        if altitude_perigee >= altitude_apogee:
            raise ValueError("The perigee must be lower than the apogee.")
        
        self.altitude_perigee = altitude_perigee * u.km
        self.altitude_apogee = altitude_apogee * u.km
        self.inclination = inclination * u.deg
        self.raan = raan * u.deg
        self.argp = argp * u.deg
        self.nu = nu * u.deg
        self.central_body: Body = central_body
        self.poliastro_orbit: Orbit = None

        # Example: μ for Earth
        self.mu = 398600.4418 * (u.km**3 / u.s**2) if isinstance(central_body, Earth) else None

        # Add automatically calculated infos
        self.semi_major_axis = (self.altitude_perigee + self.altitude_apogee) / 2
        self.eccentricity = ((self.altitude_apogee - self.altitude_perigee) / 
                             (self.altitude_apogee + self.altitude_perigee))

    def to_poliastro_orbit(self, store_poliastro: bool = False) -> Orbit:
        """
        Converts the current orbit parameters into a Poliastro Orbit object.

        Returns:
            Orbit: Poliastro Orbit object representing the current orbit.
        """
        poliastro_orbit = Orbit.from_classical(
            self.central_body.poliastro_body,
            a=self.semi_major_axis,
            ecc=self.eccentricity,
            inc=self.inclination,
            raan=self.raan,
            argp=self.argp,
            nu=self.nu
        )
        if store_poliastro:
            if not self.poliastro_orbit:
                self.poliastro_orbit = poliastro_orbit
        return poliastro_orbit
    
    def log_info(self) -> None:
        """
        Logs key details about the orbit to the console.
        Includes eccentricity, period, and inclination.
        """
        poliastro_orbit = self.to_poliastro_orbit()
        logger.info(f"Orbit - Perigee Altitude: {self.altitude_perigee}")
        logger.info(f"Orbit - Apogee Altitude: {self.altitude_apogee}")
        logger.info(f"Orbit - Inclination: {self.inclination}")
        logger.info(f"Eccentricity: {poliastro_orbit.ecc:.3f}")
        logger.info(f"Orbital Period: {poliastro_orbit.period.to(u.minute):.2f}")

    def visualize_2d(self, title: str = "2D Orbit Visualization") -> None:
        """
        Visualizes the orbit in 2D using Poliastro's static plotter.

        Args:
            title (str): Title of the plot.
        """
        poliastro_orbit = self.to_poliastro_orbit()
        plotter = StaticOrbitPlotter()
        plotter.plot(poliastro_orbit, label="Orbit")
        plotter.set_title(title)
        plotter.show()

    def visualize_3d(self, title: str = "3D Orbit Visualization") -> None:
        """
        Visualizes the orbit in 3D using Poliastro's Plotly-based plotter.

        Args:
            title (str): Title of the plot.
        """
        poliastro_orbit = self.to_poliastro_orbit()
        frame = poliastro_orbit.frame
        plotter = OrbitPlotter3D(frame)
        plotter.plot(poliastro_orbit, label=f"Orbit around {self.central_body.name}")
        plotter.set_title(title)
        plotter.show()

    def visualize_czml(
        self,
        filename: str = "orbit.czml",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        step_minutes: int = 10,
    ) -> None:
        """
        Generates a CZML animation file for visualization in tools like Cesium.

        Args:
            filename (str): File name to save the CZML animation.
            start_time (str, optional): Start time of the animation in ISO format (default is now).
            end_time (str, optional): End time of the animation in ISO format (default is one day after start_time).
            step_minutes (int): Time step between frames in minutes.
        """
        # Set default times if not provided
        start_time = Time(start_time) if start_time else Time.now()
        end_time = Time(end_time) if end_time else start_time + 1 * u.day

        # Create the CZML extractor
        extractor = CZMLExtractor(start_time, end_time, step_minutes * u.minute)

        # Add the orbit
        poliastro_orbit = self.to_poliastro_orbit()
        extractor.add_orbit(poliastro_orbit, label=f"Orbit around {self.central_body.name}")

        # Save CZML file
        czml_data = extractor.get_czml()
        with open(filename, "w") as f:
            json.dump(czml_data, f, indent=2)
            logger.info(f"CZML file saved to {filename}")

    # Serialization Methods
    def to_json(self, filename: str = None) -> str:
        """
        Serialize the orbit data to JSON.

        Args:
            filename (str, optional): File to save the JSON data. Defaults to None.

        Returns:
            str: Serialized JSON string.
        """
        data = {
            "altitude_perigee": self.altitude_perigee.to(u.km).value,
            "altitude_apogee": self.altitude_apogee.to(u.km).value,
            "inclination": self.inclination.to(u.deg).value,
            "raan": self.raan.to(u.deg).value,
            "argp": self.argp.to(u.deg).value,
            "nu": self.nu.to(u.deg).value
        }
        json_data = json.dumps(data, indent=2)
        if filename:
            with open(filename, "w") as f:
                f.write(json_data)
        return json_data

    def to_csv(self, filename: str = None) -> str:
        """
        Serialize the orbit data to CSV.

        Args:
            filename (str, optional): File to save the CSV data. Defaults to None.

        Returns:
            str: Serialized CSV string.
        """
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["altitude_perigee", "altitude_apogee", "inclination", "raan", "argp", "nu"])
        writer.writerow([
            self.altitude_perigee.to(u.km).value,
            self.altitude_apogee.to(u.km).value,
            self.inclination.to(u.deg).value,
            self.raan.to(u.deg).value,
            self.argp.to(u.deg).value,
            self.nu.to(u.deg).value
        ])
        csv_data = output.getvalue()
        if filename:
            with open(filename, "w") as f:
                f.write(csv_data)
        return csv_data

    def to_xml(self, filename: str = None) -> str:
        """
        Serialize the orbit data to XML.

        Args:
            filename (str, optional): File to save the XML data. Defaults to None.

        Returns:
            str: Serialized XML string.
        """
        root = ET.Element("Orbit")
        ET.SubElement(root, "altitude_perigee").text = str(self.altitude_perigee.to(u.km).value)
        ET.SubElement(root, "altitude_apogee").text = str(self.altitude_apogee.to(u.km).value)
        ET.SubElement(root, "inclination").text = str(self.inclination.to(u.deg).value)
        ET.SubElement(root, "raan").text = str(self.raan.to(u.deg).value)
        ET.SubElement(root, "argp").text = str(self.argp.to(u.deg).value)
        ET.SubElement(root, "nu").text = str(self.nu.to(u.deg).value)
        xml_data = ET.tostring(root, encoding="unicode")
        if filename:
            with open(filename, "w") as f:
                f.write(xml_data)
        return xml_data

    # Deserialization Methods
    @staticmethod
    def from_json(json_str: str) -> 'OrbitBase':
        """
        Create an OrbitBase instance from JSON data.

        Args:
            json_str (str): JSON string.

        Returns:
            OrbitBase: Reconstructed OrbitBase instance.
        """
        data = json.loads(json_str)
        return OrbitBase(
            data["altitude_perigee"],
            data["altitude_apogee"],
            data["inclination"],
            data["raan"],
            data["argp"],
            data["nu"]
        )

    @staticmethod
    def from_csv(csv_str: str) -> 'OrbitBase':
        """
        Create an OrbitBase instance from CSV data.

        Args:
            csv_str (str): CSV string.

        Returns:
            OrbitBase: Reconstructed OrbitBase instance.
        """
        reader = csv.reader(StringIO(csv_str))
        rows = list(reader)
        values = rows[1]
        return OrbitBase(
            float(values[0]),
            float(values[1]),
            float(values[2]),
            float(values[3]),
            float(values[4]),
            float(values[5])
        )

    @staticmethod
    def from_xml(xml_str: str) -> 'OrbitBase':
        """
        Create an OrbitBase instance from XML data.

        Args:
            xml_str (str): XML string.

        Returns:
            OrbitBase: Reconstructed OrbitBase instance.
        """
        root = ET.fromstring(xml_str)
        return OrbitBase(
            float(root.find("altitude_perigee").text),
            float(root.find("altitude_apogee").text),
            float(root.find("inclination").text),
            float(root.find("raan").text),
            float(root.find("argp").text),
            float(root.find("nu").text)
        )
