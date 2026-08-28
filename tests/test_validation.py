import pytest

from app.schemas import HPDelta, InventoryChange, MoveLocation
from app.validation import CharacterSnapshot, InvalidStateChange, StateChangeValidator


def test_validator_applies_valid_changes_in_order() -> None:
    snapshot = CharacterSnapshot(hp=10, max_hp=10, inventory={"Torch": 1})
    changes = [
        HPDelta(type="hp_delta", amount=-2, reason="Fell from the loft"),
        InventoryChange(
            type="inventory_change", item_name="Torch", quantity_delta=-1, reason="Used it"
        ),
        MoveLocation(type="move_location", location_name="Stable Loft"),
    ]

    result = StateChangeValidator().validate(snapshot, changes)

    assert result == CharacterSnapshot(hp=8, max_hp=10, inventory={})


def test_validator_rejects_impossible_hp() -> None:
    snapshot = CharacterSnapshot(hp=10, max_hp=10, inventory={})
    with pytest.raises(InvalidStateChange, match="allowed range"):
        StateChangeValidator().validate(
            snapshot,
            [HPDelta(type="hp_delta", amount=1, reason="Impossible overheal")],
        )


def test_validator_rejects_missing_inventory() -> None:
    snapshot = CharacterSnapshot(hp=10, max_hp=10, inventory={})
    with pytest.raises(InvalidStateChange, match="Cannot remove"):
        StateChangeValidator().validate(
            snapshot,
            [
                InventoryChange(
                    type="inventory_change",
                    item_name="Torch",
                    quantity_delta=-1,
                    reason="Not owned",
                )
            ],
        )
