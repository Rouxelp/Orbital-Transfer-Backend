from pydantic import BaseModel

class TransferType(BaseModel):
    """
    Represents the type of orbital transfer being performed.
    Includes methods for identifying the type and calculating related parameters.
    """
    def __init__(self, name: str, description: str, requires_inclination_change: bool = False) -> None:
        """
        Initialize a TransferType instance.

        Args:
            name (str): Name of the transfer (e.g., "Hohmann", "Bi-Elliptic").
            description (str): Description of the transfer.
            requires_inclination_change (bool): Whether the transfer includes an inclination change.
        """
        self.name = name
        self.description = description
        self.requires_inclination_change = requires_inclination_change

    def is_inclination_change_required(self) -> bool:
        """
        Checks if the transfer involves an inclination change.

        Returns:
            bool: True if inclination change is required, False otherwise.
        """
        return self.requires_inclination_change

    def __str__(self) -> str:
        """
        String representation of the TransferType.

        Returns:
            str: Formatted string with the transfer details.
        """
        return f"TransferType: {self.name}, Requires Inclination Change: {self.requires_inclination_change}"
