from abc import ABC, abstractmethod
from typing import List
from src.abilities.ability import Ability


class AbilityFactory(ABC):
    """
    Абстрактная фабрика способностей
    """

    @abstractmethod
    def create_abilities(self) -> List[Ability]:
        pass
