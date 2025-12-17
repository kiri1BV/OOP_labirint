from typing import List, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.abilities.ability import Ability


class Character(ABC):
    """
    Базовый абстрактный класс для всех персонажей игры.
    """

    def __init__(
        self,
        name: str,
        max_health: int,
        max_mana: int,
        armor: int,
        base_damage: int,
        x: int = 0,
        y: int = 0
    ):
        self._name = name
        self._max_health = max_health
        self._health = max_health
        self._max_mana = max_mana
        self._mana = max_mana
        self._armor = armor
        self._base_damage = base_damage
        self._x = x
        self._y = y
        self._abilities: List['Ability'] = []
        self._is_defending = False
        self._frozen_turns = 0
        self._status_effects: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int):
        self._health = max(0, min(value, self._max_health))

    @property
    def max_health(self) -> int:
        return self._max_health

    @property
    def mana(self) -> int:
        return self._mana

    @mana.setter
    def mana(self, value: int):
        self._mana = max(0, min(value, self._max_mana))

    @property
    def max_mana(self) -> int:
        return self._max_mana

    @property
    def armor(self) -> int:
        return self._armor

    @property
    def base_damage(self) -> int:
        return self._base_damage

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    @property
    def position(self) -> tuple:
        return self._x, self._y

    @position.setter
    def position(self, pos: tuple):
        self._x, self._y = pos

    @property
    def is_alive(self) -> bool:
        return self._health > 0

    @property
    def is_frozen(self) -> bool:
        return self._frozen_turns > 0

    @property
    def is_defending(self) -> bool:
        return self._is_defending

    @property
    def abilities(self) -> List['Ability']:
        return self._abilities

    def add_ability(self, ability: 'Ability'):
        self._abilities.append(ability)

    def move(self, dx: int, dy: int) -> bool:
        if self.is_frozen:
            return False
        self._x += dx
        self._y += dy
        return True

    def attack(self, target: 'Character') -> int:
        if self.is_frozen:
            return 0
        return target.take_damage(self._base_damage)

    def take_damage(self, damage: int) -> int:
        armor = self._armor * 2 if self._is_defending else self._armor
        actual_damage = max(1, damage - armor)
        self._health = max(0, self._health - actual_damage)
        return actual_damage

    def defend(self):
        self._is_defending = True

    def end_turn(self):
        self._is_defending = False
        if self._frozen_turns > 0:
            self._frozen_turns -= 1
        self._mana = min(self._max_mana, self._mana + 5)

    def freeze(self, turns: int = 1):
        self._frozen_turns = turns
        if "frozen" not in self._status_effects:
            self._status_effects.append("frozen")

    def heal(self, amount: int):
        self._health = min(self._max_health, self._health + amount)

    def use_mana(self, amount: int) -> bool:
        if self._mana >= amount:
            self._mana -= amount
            return True
        return False

    def use_ability(self, ability_index: int, target: 'Character') -> Optional[str]:
        if self.is_frozen:
            return f"{self._name} заморожен и не может действовать!"
        if 0 <= ability_index < len(self._abilities):
            return self._abilities[ability_index].use(self, target)
        return None

    @abstractmethod
    def get_sprite_name(self) -> str:
        pass

    def get_status_string(self) -> str:
        status = (
            f"{self._name}: "
            f"HP {self._health}/{self._max_health} | "
            f"MP {self._mana}/{self._max_mana} | "
            f"ARM {self._armor}"
        )
        if self._is_defending:
            status += " [DEF]"
        if self._frozen_turns > 0:
            status += f" [FROZEN:{self._frozen_turns}]"
        return status



