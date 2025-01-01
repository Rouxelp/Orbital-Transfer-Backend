from app.schemas.bodies.body import Body
from poliastro.bodies import Jupiter as PoliastroJupiter

class Jupiter(Body):
    def __init__(self):
        super().__init__(PoliastroJupiter)


