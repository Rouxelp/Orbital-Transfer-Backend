from app.schemas.transfer_type import TransferType
from utils.hohmann.hohmann_transfer import HohmannTransfer
from logger_handler import handle_logger

logger = handle_logger()
mock_instance = HohmannTransfer()

def test_transfer_type_initialization() -> None:
    """
    Test initialization of a TransferType instance.
    """
    transfer = TransferType(
        id=1,
        name="Hohmann",
        description="A simple transfer between two coplanar circular orbits.",
        requires_inclination_change=False
    )
    assert transfer.name == "Hohmann"
    assert transfer.description == "A simple transfer between two coplanar circular orbits."
    assert transfer.requires_inclination_change is False


def test_transfer_type_inclination_change_required() -> None:
    """
    Test the is_inclination_change_required method.
    """
    transfer = TransferType(
        id=2,
        name="Bi-Elliptic",
        description="Transfer involving two impulses and an inclination change.",
        requires_inclination_change=True
    )
    assert transfer.is_inclination_change_required() is True

def test_transfer_type_str_representation() -> None:
    """
    Test the string representation of a TransferType instance.
    """
    transfer = TransferType(
        id=1,
        name="Hohmann",
        description="A simple transfer between two coplanar circular orbits.",
        requires_inclination_change=False
    )
    assert str(transfer) == "TransferType: Hohmann, Requires Inclination Change: False"

def test_registry_structure() -> None:
    """
    Test to ensure the registry structure uses classes as keys and IDs as values.
    """
    TransferType._register_subclasses()

    # Check that keys are classes
    for key in TransferType._registry.keys():
        assert isinstance(key, type), f"Registry key is not a class: {key}"

    # Check that values are IDs (integers)
    for value in TransferType._registry.values():
        assert isinstance(value, int), f"Registry value is not an integer: {value}"

def test_get_transfer_by_id() -> None:
    """
    Test the retrieval of TransferType subclasses by their ID.
    """
    TransferType._register_subclasses()

    # Assume a class with ID 1 exists
    transfer = TransferType.get_transfer_by_id(1)
    assert isinstance(transfer, TransferType), "Retrieved object is not a TransferType instance."
    assert transfer.id == 1, f"Expected ID 1, got {transfer.id}"

def test_transfer_type_unique_ids() -> None:
    """
    #! This test isn't testing behavior or functionnalities but is a check on code structure and coherence
    Test to ensure all registered TransferType subclasses have unique IDs. 
    """
    # Force registration of subclasses
    TransferType._register_subclasses()

    # Extract IDs from the registry
    registered_ids = list(TransferType._registry.values())

    # Check for duplicate IDs
    duplicates = [id for id in set(registered_ids) if registered_ids.count(id) > 1]

    assert not duplicates, f"Duplicate TransferType IDs found: {duplicates}"

def test_transfer_type_duplicate_id_simulation() -> None:
    """
    #! This test isn't testing behavior or functionnalities but is a check on code structure and coherence
    Test to ensure all registered TransferType subclasses have unique IDs.
    """
    class DuplicatedIDTransfer(TransferType):
        def __init__(self) -> None:
            """
            Initialize the DuplicatedIDTransfer class with specific properties.
            """
            super().__init__(
                id=1,  # Duplicate ID
                name="DuplicatedIDTransfer",
                description="A transfer with a duplicated ID.",
                requires_inclination_change=False
            )

    # Register the duplicate class manually
    duplicated_instance = DuplicatedIDTransfer()
    TransferType._registry[DuplicatedIDTransfer] = duplicated_instance.id

    # Extract IDs from the registry
    registered_ids = list(TransferType._registry.values())

    # Check for duplicate IDs
    duplicates = [id for id in set(registered_ids) if registered_ids.count(id) > 1]

    assert duplicates, f"No duplicates found, but one was expected. Current IDs: {registered_ids}"
    assert 1 in duplicates, f"Duplicate ID 1 not detected in duplicates: {duplicates}"
