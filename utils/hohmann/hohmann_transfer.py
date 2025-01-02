from app.schemas.trajectory_base import Trajectory
from app.schemas.orbits.orbit_base import OrbitBase
from app.schemas.transfer_type import TransferType, TypeTransferType
from utils.hohmann.func.calculate_transfer import func_calculate_transfer
import numpy as np
import plotly.graph_objects as go
from app.schemas.trajectory_base import Trajectory
from app.schemas.orbits.orbit_base import OrbitBase
from logger_handler import handle_logger

logger = handle_logger()

class HohmannTransferType(TypeTransferType):
    """
    A descriptive subclass of TransferType for Hohmann Transfers.

    This class is used to represent the Hohmann transfer type in a lightweight manner.
    Unlike the HohmannTransfer class, it avoids additional memory usage by excluding
    computational methods, making it more suitable for embedding within trajectory objects.
    """
    pass

class HohmannTransfer(TransferType):
    """
    Class to handle Hohmann transfer calculation.
    Extends TransferType and provides additional logic specific to Hohmann transfers.
    """

    def __init__(self) -> None:
        """
        Initialize the HohmannTransfer class with specific properties.
        """
        super().__init__(
            id=1,
            name="Hohmann",
            description="A simple transfer between two coplanar circular orbits.",
            requires_inclination_change=False
        )

    @staticmethod
    def calculate_transfer(
        initial_orbit: OrbitBase, target_orbit: OrbitBase, sample_value: int = 100
    ) -> Trajectory:
        """
        Calculate the Hohmann transfer between two orbits.

        Args:
            initial_orbit (OrbitBase): The initial orbit.
            target_orbit (OrbitBase): The target orbit.
            sample_value (int): Number of discrete points for trajectory sampling.

        Returns:
            Trajectory: The calculated trajectory including delta-v, time of flight, and points.
        """
        try:
            # Validate that orbits are coplanar
            if initial_orbit.inclination != target_orbit.inclination:
                raise ValueError(
                    "Hohmann transfer is only valid for coplanar orbits with the same inclination."
                )

            # Delegate calculation to func_calculate_transfer
            trajectory = func_calculate_transfer(initial_orbit, target_orbit, sample_value)

            # Add the transfer type to the trajectory
            trajectory.transfer_type = HohmannTransferType(
                name="Hohmann",
                description="A simple transfer between two coplanar circular orbits.",
                requires_inclination_change=False
            )
            return trajectory

        except ValueError as e:
            raise ValueError(f"Error during Hohmann transfer calculation: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during transfer calculation: {e}")

    @staticmethod
    def visualize_transfer(
        initial_orbit: OrbitBase,
        target_orbit: OrbitBase,
        trajectory: Trajectory,
        steps: int = 100
    ):
        """
        Visualizes the Hohmann transfer between two orbits.

        Args:
            initial_orbit (OrbitBase): Initial orbit.
            target_orbit (OrbitBase): Target orbit.
            trajectory (Trajectory): The calculated trajectory for the transfer.
            steps (int): Number of steps for the trajectory animation.
        """
        try:
            # Sample points from initial_orbit
            initial_orbit_points = initial_orbit.to_poliastro_orbit().sample(steps).get_xyz()
            x1, y1, z1 = initial_orbit_points.to_value()

            # Sample points from target_orbit
            target_orbit_points = target_orbit.to_poliastro_orbit().sample(steps).get_xyz()
            x2, y2, z2 = target_orbit_points.to_value()

            # Extract trajectory points
            trajectory_positions = np.array([point["position"] for point in trajectory.points])
            tx, ty, tz = trajectory_positions.T

            # Create the 3D animation
            fig = go.Figure()

            # Add initial_orbit
            fig.add_trace(
                go.Scatter3d(
                    x=x1,
                    y=y1,
                    z=z1,
                    mode="lines",
                    name="Orbit 1",
                    line=dict(color="blue", width=2),
                )
            )

            # Add target_orbit
            fig.add_trace(
                go.Scatter3d(
                    x=x2,
                    y=y2,
                    z=z2,
                    mode="lines",
                    name="Orbit 2",
                    line=dict(color="green", width=2),
                )
            )

            # Add trajectory
            fig.add_trace(
                go.Scatter3d(
                    x=tx,
                    y=ty,
                    z=tz,
                    mode="lines",
                    name="Trajectory",
                    line=dict(color="red", width=2),
                )
            )

            # Add animation of points along the trajectory
            fig.add_trace(
                go.Scatter3d(
                    x=[tx[0]],
                    y=[ty[0]],
                    z=[tz[0]],
                    mode="markers",
                    name="Transfer Object",
                    marker=dict(size=5, color="yellow"),
                )
            )

            # Update layout
            fig.update_layout(
                title="Hohmann Transfer Visualization",
                scene=dict(
                    xaxis_title="X (km)",
                    yaxis_title="Y (km)",
                    zaxis_title="Z (km)",
                ),
            )

            # Show the plot
            logger.info("Displaying the Hohmann transfer visualization.")
            fig.show()

        except Exception as e:
            logger.error(f"Error during Hohmann transfer visualization: {e}")
            raise
