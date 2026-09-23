from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base Value Object — imutável, definido inteiramente pelos seus atributos."""
    pass