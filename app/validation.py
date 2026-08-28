from dataclasses import dataclass

from app.schemas import HPDelta, InventoryChange, MoveLocation, StateChange


class InvalidStateChange(ValueError):
    pass


@dataclass(frozen=True)
class CharacterSnapshot:
    hp: int
    max_hp: int
    inventory: dict[str, int]


class StateChangeValidator:
    def validate(
        self, snapshot: CharacterSnapshot | None, changes: list[StateChange]
    ) -> CharacterSnapshot | None:
        current = snapshot
        for change in changes:
            if isinstance(change, MoveLocation):
                continue
            if current is None:
                raise InvalidStateChange("Character state cannot change before a character exists")
            if isinstance(change, HPDelta):
                new_hp = current.hp + change.amount
                if not 0 <= new_hp <= current.max_hp:
                    raise InvalidStateChange(
                        f"HP change would leave allowed range 0..{current.max_hp}"
                    )
                current = CharacterSnapshot(new_hp, current.max_hp, current.inventory.copy())
            elif isinstance(change, InventoryChange):
                inventory = current.inventory.copy()
                item_key = change.item_name.strip()
                new_quantity = inventory.get(item_key, 0) + change.quantity_delta
                if new_quantity < 0:
                    raise InvalidStateChange(
                        f"Cannot remove more {item_key} than the character has"
                    )
                if new_quantity == 0:
                    inventory.pop(item_key, None)
                else:
                    inventory[item_key] = new_quantity
                current = CharacterSnapshot(current.hp, current.max_hp, inventory)
        return current
