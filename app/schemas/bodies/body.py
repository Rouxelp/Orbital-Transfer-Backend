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
        self._poliastro_body = poliastro_body
        self.name = poliastro_body.name
        self.mass = poliastro_body.mass
        self.radius = poliastro_body.R
        self.mu = poliastro_body.k  # Gravitational parameter (km^3/s^2)

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
