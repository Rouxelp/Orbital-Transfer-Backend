from typing import Type
from logger_handler import handle_logger

logger = handle_logger()

class TypeTransferType: 
    """
    A descriptive class TransferType.

    This class is used to represent the type of transfer type in a lightweight manner.
    Unlike the TransferType class, it avoids additional memory usage by excluding
    computational methods, making it more suitable for embedding within trajectory objects.
    """
    pass

class TransferType():
    """
    Represents the type of orbital transfer being performed.
    Includes methods for identifying the type and calculating related parameters.
    """
    
    # Class-level registry for all subclasses
    _registry = {}

    def __init__(self, id: int, name: str, description: str, requires_inclination_change: bool = False) -> None:
        """
        Initialize a TransferType instance.

        Args:
            id (int): ID of the transfer
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
        Automatically registers all subclasses of TransferType in the registry,
        associating class names with their IDs.
        """
        logger.info(f"Registering subclasses: {cls.__subclasses__()}")
        for subclass in cls.__subclasses__():
            instance = subclass()
            if instance.id is not None:
                cls._registry[subclass] = instance.id

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

        # Search for the class with the matching ID
        for transfer_class, transfer_id in cls._registry.items():
            if transfer_id == id:
                return transfer_class()  # Instantiate the class

        raise ValueError(f"No TransferType found with ID {id}")

