import secrets
from astropy import units as u
from astropy.units import Quantity
from pydantic import BaseModel, Field, model_validator
from app.schemas.base_response_model import BaseResponseModel
from app.schemas.bodies.body import Body
from app.schemas.bodies.earth import Earth
from poliastro.twobody import Orbit
from poliastro.plotting.static import StaticOrbitPlotter # type: ignore
from poliastro.plotting import OrbitPlotter3D
from poliastro.czml.extract_czml import CZMLExtractor
from astropy.time import Time
from astropy.time import Time
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Any, List, Optional
from logger_handler import handle_logger
from utils.paginate import PaginatedResponse

logger = handle_logger()

class OrbitBase:
    """
    A base class to represent an orbital configuration.
    Includes methods for conversion to Poliastro Orbit objects,
    visualization, and logging key orbital information.
    """
    _id_generator = iter(int(secrets.token_hex(12), 16) for _ in range(1_000_000))

    def __init__(self, 
                 altitude_perigee: float, 
                 altitude_apogee: float, 
                 inclination: float, 
                 raan: float = 0.0, 
                 argp: float = 0.0, 
                 nu: float = 0.0, 
                 central_body: Body = Earth(), 
                 id: Optional[int] = None, 
                 name: Optional[str] = None
            ) -> None:
        """
        Args:
            altitude_perigee (float): Altitude of the perigee (in km).
            altitude_apogee (float): Altitude of the apogee (in km).
            inclination (float): Orbital inclination (in degrees).
            raan (float): Right ascension of the ascending node (in degrees).
            argp (float): Argument of perigee (in degrees).
            nu (float): True anomaly (in degrees).
            central_body (Body): Central body of the orbit (e.g., 'Earth'). Default Earth
            id (int, optional): ID of the orbit if exists.
            name (str, optional): Optional given name for the orbit.
        """
        if altitude_perigee > altitude_apogee:
            raise ValueError("The perigee must be strictly lower than the apogee.")
        
        self.id = next(self._id_generator) if not id else id
        self._altitude_perigee = altitude_perigee * u.km
        self._altitude_apogee = altitude_apogee * u.km
        self._inclination = inclination * u.deg
        self._raan = raan * u.deg
        self._argp = argp * u.deg
        self._nu = nu * u.deg
        self._central_body: Body = central_body
        self._poliastro_orbit: Orbit = None
        self.name: str = name

        # Add automatically calculated infos
        self._semi_major_axis = (
            (self.altitude_perigee + self.altitude_apogee) / 2 
        )
        self._eccentricity = ((self.altitude_apogee - self.altitude_perigee) / 
                             (self.altitude_apogee + self.altitude_perigee))

    @property
    def central_body(self) -> Body:
        return self._central_body

    @central_body.setter
    def central_body(self, new_central_body):
        self.central_body = new_central_body
        self.poliastro_orbit = self.to_poliastro_orbit()
    
    
    @property
    def altitude_apogee(self) -> Body:
        return self._altitude_apogee

    @altitude_apogee.setter
    def altitude_apogee(self, new_altitude_apogee):
        self._altitude_apogee = new_altitude_apogee
        self._poliastro_orbit = self.to_poliastro_orbit()
    
    @property
    def altitude_perigee(self) -> Body:
        return self._altitude_perigee

    @altitude_perigee.setter
    def altitude_perigee(self, new_altitude_perigee):
        self._altitude_perigee = new_altitude_perigee
        self._poliastro_orbit = self.to_poliastro_orbit()
    
    @property
    def inclination(self) -> Body:
        return self._inclination

    @inclination.setter
    def inclination(self, new_inclination):
        self._inclination = new_inclination
        self._poliastro_orbit = self.to_poliastro_orbit()

    @property
    def raan(self) -> Body:
        return self._raan

    @raan.setter
    def raan(self, new_raan):
        self._raan = new_raan
        self._poliastro_orbit = self.to_poliastro_orbit()
    
    @property
    def argp(self) -> Body:
        return self._argp

    @argp.setter
    def argp(self, new_argp):
        self._argp = new_argp
        self._poliastro_orbit = self.to_poliastro_orbit()
    
    @property
    def nu(self) -> Body:
        return self._nu

    @nu.setter
    def nu(self, new_nu):
        self._nu = new_nu
        self._poliastro_orbit = self.to_poliastro_orbit()
    
    @property
    def eccentricity(self) -> Body:
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, new_eccentricity):
        self._eccentricity = new_eccentricity
        self._poliastro_orbit = self.to_poliastro_orbit()

    @property
    def semi_major_axis(self) -> Body:
        return self._semi_major_axis

    @semi_major_axis.setter
    def semi_major_axis(self, new_semi_major_axis):
        self._semi_major_axis = new_semi_major_axis
        self._poliastro_orbit = self.to_poliastro_orbit()

    @property
    def poliastro_orbit(self) -> Orbit:
        return self._poliastro_orbit

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
            if self.poliastro_orbit is None:
                self.poliastro_orbit = poliastro_orbit
        return poliastro_orbit
    
    def log_info(self) -> None:
        """
        Logs key details about the orbit to the console.
        Includes eccentricity, period, and inclination.
        """
        poliastro_orbit = self.to_poliastro_orbit()
        logger.info(f"Orbit - ID: {self.id}")
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
            "id": self.id,
            "name": self.name if self.name else "",
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
        writer.writerow(["id", "name", "altitude_perigee", "altitude_apogee", "inclination", "raan", "argp", "nu"])
        writer.writerow([
            self.id, 
            self.name if self.name else "",
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
        ET.SubElement(root, "id").text = str(self.id)
        ET.SubElement(root, "name").text = str(self.name)
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
        data: dict = json.loads(json_str)
        if not data.get("id", None):
            raise ValueError("This Orbit has no id")
        
        return OrbitBase(
            id=int(data.get("id")),
            name=str(data.get("name", "")),
            altitude_perigee=float(data.get("altitude_perigee")) if data.get("altitude_perigee", None) is not None else None,
            altitude_apogee=float(data.get("altitude_apogee")) if data.get("altitude_apogee", None) is not None else None,
            inclination=float(data.get("inclination")) if data.get("inclination", None) is not None else None,
            raan=float(data.get("raan")) if data.get("raan", None) is not None else None,
            argp=float(data.get("argp")) if data.get("argp", None) is not None else None,
            nu=float(data.get("nu")) if data.get("nu", None) is not None else None
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
        if len(rows) < 2:
            raise ValueError("CSV data is invalid or missing header and data rows")
        
        header = rows[0]
        values = rows[1]

        data = {header[i]: values[i] for i in range(len(header))}
        if not data.get("id", None):
            raise ValueError("This Orbit has no id")
        
        return OrbitBase(
            id=int(data.get("id")),
            name=str(data.get("name", "")),
            altitude_perigee=float(data.get("altitude_perigee")) if data.get("altitude_perigee", None) is not None else None,
            altitude_apogee=float(data.get("altitude_apogee")) if data.get("altitude_apogee", None) is not None else None,
            inclination=float(data.get("inclination")) if data.get("inclination", None) is not None else None,
            raan=float(data.get("raan")) if data.get("raan", None) is not None else None,
            argp=float(data.get("argp")) if data.get("argp", None) is not None else None,
            nu=float(data.get("nu")) if data.get("nu", None) is not None else None
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

        id_text = root.find("id").text
        if not id_text:
            raise ValueError("This Orbit has no id")

        return OrbitBase(
            id=int(id_text),
            name=root.find("name").text if root.find("name") is not None and root.find("name").text else "",
            altitude_perigee=float(root.find("altitude_perigee").text) if root.find("altitude_perigee") is not None and root.find("altitude_perigee").text else None,
            altitude_apogee=float(root.find("altitude_apogee").text) if root.find("altitude_apogee") is not None and root.find("altitude_apogee").text else None,
            inclination=float(root.find("inclination").text) if root.find("inclination") is not None and root.find("inclination").text else None,
            raan=float(root.find("raan").text) if root.find("raan") is not None and root.find("raan").text else None,
            argp=float(root.find("argp").text) if root.find("argp") is not None and root.find("argp").text else None,
            nu=float(root.find("nu").text) if root.find("nu") is not None and root.find("nu").text else None
        )


class OrbitInput(BaseResponseModel):
    altitude_perigee: float = Field(
        ...,
        gt=0,
        description="Perigee altitude in kilometers. Must be a positive value."
    )
    altitude_apogee: float = Field(
        ...,
        gt=0,
        description="Apogee altitude in kilometers. Must be a positive value."
    )
    inclination: float = Field(
        ...,
        ge=0,
        le=180,
        description="Orbital inclination in degrees. Must be between 0 and 180."
    )
    raan: Optional[float] = Field(
        0.0,
        ge=0,
        le=360,
        description="Right Ascension of the Ascending Node (RAAN) in degrees. Must be between 0 and 360. Defaults to 0.0."
    )
    argp: Optional[float] = Field(
        0.0,
        ge=0,
        le=360,
        description="Argument of Perigee in degrees. Must be between 0 and 360. Defaults to 0.0."
    )
    nu: Optional[float] = Field(
        0.0,
        ge=0,
        le=360,
        description="True anomaly in degrees. Must be between 0 and 360. Defaults to 0.0."
    )
    file_type: str = Field(
        "json",
        pattern="^(json|csv|xml)$",
        description="File type to save the orbit. Must be one of: 'json', 'csv', or 'xml'. Defaults to 'json'."
    )

class OrbitResponse(BaseModel):
    id: int = Field(..., example=123)
    name: str = Field(..., example="Sample Orbit")
    altitude_perigee: float = Field(..., example=200.0)
    altitude_apogee: float = Field(..., example=400.0)
    inclination: float = Field(..., example=28.5)
    raan: Optional[float] = Field(0.0, example=0.0)
    argp: Optional[float] = Field(0.0, example=0.0)
    nu: Optional[float] = Field(0.0, example=0.0)

class OrbitResponseWrapper(BaseModel):
    message: str = Field(..., example="Orbit created successfully")
    orbit: OrbitResponse 

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Orbit created successfully",
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
        }

class PaginatedOrbitResponseWrapper(PaginatedResponse):
    data: List[OrbitResponse] = Field(
        ...,
        description="Paginated list of orbit responses.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 50,
                "total_items": 123,
                "total_pages": 3,
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
                        "nu": 0.0,
                    }
                ],
            }
        }
