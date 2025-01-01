from app.schemas.bodies.body import Body
from poliastro.bodies import Sun as PoliastroSun

class Sun(Body):
    def __init__(self):
        super().__init__(PoliastroSun)
