from astropy import units as u
from logger_handler import handle_logger

logger = handle_logger()

class Body:
    """
    Base class to represent a celestial body.
    Encapsulates a Poliastro body and provides an extended interface.
    """

    def __init__(self, poliastro_body):
        """
        Initialize the celestial body using a Poliastro body.

        Args:
            poliastro_body: Poliastro celestial body.
        """
        if not hasattr(poliastro_body, "name") or not hasattr(poliastro_body, "k"):
            raise ValueError("Invalid Poliastro body. It must have 'name' and 'k' attributes.")

        self._poliastro_body = poliastro_body
        self.name = poliastro_body.name

        # Mass (if available)
        self.mass = (
            poliastro_body.mass
            if hasattr(poliastro_body, "mass")
            else None
        )

        # Radius (convert to Astropy Quantity)
        self.radius = (
            poliastro_body.R.to(u.km)
            if hasattr(poliastro_body, "R")
            else None
        )

        # Gravitational parameter (mu)
        self.mu = poliastro_body.k.to(u.km**3 / u.s**2)

    def __repr__(self):
        return f"<Body(name={self.name}, mass={self.mass}, radius={self.radius}, mu={self.mu})>"

    @property
    def poliastro_body(self):
        """
        Returns the encapsulated Poliastro body.

        Returns:
            Poliastro body.
        """
        return self._poliastro_body
    
    def log_info(self):
        """
        Logs detailed information about the celestial body.
        """
        info = f"Body Name: {self.name}\n"
        info += f"Mass: {self.mass.to(u.kg) if self.mass else 'Unknown'}\n"
        info += f"Radius: {self.radius.to(u.km) if self.radius else 'Unknown'}\n"
        info += f"Gravitational Parameter (mu): {self.mu:.3e}\n"
        logger.info(info)
