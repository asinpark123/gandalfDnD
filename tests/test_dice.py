import pytest

from app.dice import DiceService


class FixedRandom:
    def __init__(self, results: list[int]) -> None:
        self._results = iter(results)

    def randint(self, start: int, end: int) -> int:
        value = next(self._results)
        assert start <= value <= end
        return value


def test_roll_uses_real_results_and_modifier() -> None:
    result = DiceService(FixedRandom([4, 6])).roll("2d6", modifier=3)

    assert result.rolls == [4, 6]
    assert result.total == 13


@pytest.mark.parametrize("notation", ["d20", "0d6", "1d1", "101d6", "1d1001", "2D6"])
def test_roll_rejects_unsafe_or_invalid_notation(notation: str) -> None:
    with pytest.raises(ValueError):
        DiceService().roll(notation)
