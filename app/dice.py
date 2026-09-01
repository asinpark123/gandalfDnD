import random
import re
from dataclasses import dataclass
from typing import Protocol

_DICE_PATTERN = re.compile(r"^(?P<count>[1-9]\d*)d(?P<sides>[2-9]|[1-9]\d{1,2})$")


class RandomSource(Protocol):
    def randint(self, start: int, end: int) -> int: ...


@dataclass(frozen=True)
class RollResult:
    notation: str
    rolls: list[int]
    modifier: int
    total: int


class DiceService:
    def __init__(self, random_source: RandomSource | None = None) -> None:
        self._random = random_source or random.SystemRandom()
        self.algorithm_version = (
            "system-random-1.0.0"
            if random_source is None
            else getattr(random_source, "algorithm_version", "injected-random-source-1.0.0")
        )

    def roll(self, notation: str, modifier: int = 0) -> RollResult:
        match = _DICE_PATTERN.fullmatch(notation)
        if not match:
            raise ValueError("Dice notation must look like 1d20")

        count = int(match.group("count"))
        sides = int(match.group("sides"))
        if count > 100 or sides > 1000:
            raise ValueError("Dice request exceeds Phase 0 safety limits")

        rolls = [self._random.randint(1, sides) for _ in range(count)]
        return RollResult(
            notation=notation,
            rolls=rolls,
            modifier=modifier,
            total=sum(rolls) + modifier,
        )


def get_dice_service() -> DiceService:
    return DiceService()
