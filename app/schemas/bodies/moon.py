from app.schemas.bodies.body import Body
from poliastro.bodies import Moon as PoliastroMoon

class Moon(Body):
    def __init__(self):
        super().__init__(PoliastroMoon)
