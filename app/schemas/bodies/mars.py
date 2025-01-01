from app.schemas.bodies.body import Body
from poliastro.bodies import Mars as PoliastroMars

class Mars(Body):
    def __init__(self):
        super().__init__(PoliastroMars)
