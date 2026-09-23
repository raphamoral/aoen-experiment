from dataclasses import dataclass


@dataclass(frozen=True)
class ExamValue:
    """Value object representing a single measured lab value."""

    value: float
    unit: str

    def is_within_range(self, min_val: float | None, max_val: float | None) -> bool:
        if min_val is not None and self.value < min_val:
            return False
        if max_val is not None and self.value > max_val:
            return False
        return True

    def deviation_from_range(
        self, min_val: float, max_val: float
    ) -> float:
        """Returns signed deviation from range boundaries. 0 if within range."""
        if self.value < min_val:
            return self.value - min_val
        if self.value > max_val:
            return self.value - max_val
        return 0.0