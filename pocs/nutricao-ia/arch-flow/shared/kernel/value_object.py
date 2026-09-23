from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Objeto de Valor — sem identidade, definido pelos seus atributos.

    Imutável por design: qualquer alteração produz um novo objeto.
    Encapsula regras de validação e comportamento do conceito que representa.
    Dois VOs são iguais se todos os seus atributos são iguais.
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))