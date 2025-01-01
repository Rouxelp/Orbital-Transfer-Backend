import pytest
from app.schemas import TransferType


def test_transfer_type_initialization() -> None:
    """
    Test initialization of a TransferType instance.
    """
    transfer = TransferType(
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
        name="Hohmann",
        description="A simple transfer between two coplanar circular orbits.",
        requires_inclination_change=False
    )
    assert str(transfer) == "TransferType: Hohmann, Requires Inclination Change: False"
