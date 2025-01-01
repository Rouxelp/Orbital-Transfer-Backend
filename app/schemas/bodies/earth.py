from app.schemas.bodies.body import Body
from poliastro.bodies import Earth as PoliastroEarth

class Earth(Body):
    def __init__(self):
        super().__init__(PoliastroEarth)



