from abc import ABC, abstractmethod
from typing import List
from src.abilities.ability import Ability
from src.abilities.fireball import Fireball
from src.abilities.freeze import Freeze
from src.abilities.shield import Shield


class EnemyAbilityFactory(ABC):
    @abstractmethod
    def create(self) -> List[Ability]:
        pass


class MageAbilityFactory(EnemyAbilityFactory):
    def create(self) -> List[Ability]:
        return [Fireball(), Freeze()]


class TankAbilityFactory(EnemyAbilityFactory):
    def create(self) -> List[Ability]:
        return [Shield()]


class WarriorAbilityFactory(EnemyAbilityFactory):
    def create(self) -> List[Ability]:
        return []
