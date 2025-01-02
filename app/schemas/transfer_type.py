from typing import Type
from pydantic import BaseModel
import inspect 

class TransferType(BaseModel):
    """
    Represents the type of orbital transfer being performed.
    Includes methods for identifying the type and calculating related parameters.
    """
    
    # Class-level registry for all subclasses
    _registry = {}

    def __init__(self, name: str, description: str, requires_inclination_change: bool = False, id: int = None) -> None:
        """
        Initialize a TransferType instance.

        Args:
            name (str): Name of the transfer (e.g., "Hohmann", "Bi-Elliptic").
            description (str): Description of the transfer.
            requires_inclination_change (bool): Whether the transfer includes an inclination change.
        """
        self.id = id
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
    
    @classmethod
    def _register_subclasses(cls):
        """
        Automatically registers all subclasses of TransferType in the registry.
        """
        for subclass in cls.__subclasses__():
            instance = subclass()
            if instance.id is not None:
                cls._registry[instance.id] = subclass

    @classmethod
    def get_transfer_by_id(cls, id: int) -> Type['TransferType']:
        """
        Retrieve a TransferType subclass by its ID.

        Args:
            id (int): The unique ID of the transfer type.

        Returns:
            TransferType: The corresponding TransferType subclass instance.
        """
        if not cls._registry:
            cls._register_subclasses()
        transfer_class = cls._registry.get(id)
        if not transfer_class:
            raise ValueError(f"No TransferType found with ID {id}")
        return transfer_class()
