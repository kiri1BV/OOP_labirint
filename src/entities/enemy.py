from abc import abstractmethod
from .character import Character
import random


class Enemy(Character):
    """
    Базовый класс врага.
    Не знает о конкретных способностях — только о поведении.
    """

    def __init__(
        self,
        name: str,
        max_health: int,
        max_mana: int,
        armor: int,
        base_damage: int,
        exp_reward: int,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            name=name,
            max_health=max_health,
            max_mana=max_mana,
            armor=armor,
            base_damage=base_damage,
            x=x,
            y=y
        )
        self._exp_reward = exp_reward

    @property
    def exp_reward(self) -> int:
        return self._exp_reward

    @abstractmethod
    def choose_action(self, player: Character) -> tuple:
        """
        Возвращает:
        ('attack', target)
        ('defend', None)
        ('ability', ability_index, target)
        """
        pass

    @abstractmethod
    def get_color(self) -> tuple:
        pass


class Warrior(Enemy):
    """
    Воин — агрессивный ближний боец.
    """

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(
            name="Warrior",
            max_health=60,
            max_mana=20,
            armor=8,
            base_damage=18,
            exp_reward=30,
            x=x,
            y=y
        )

    def choose_action(self, player: Character) -> tuple:
        if self.health < self.max_health * 0.3:
            return ('defend', None)
        return ('attack', player)

    def get_sprite_name(self) -> str:
        return "warrior.png"

    def get_color(self) -> tuple:
        return (200, 50, 50)


class Mage(Enemy):
    """
    Маг — полагается на способности.
    """

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(
            name="Mage",
            max_health=40,
            max_mana=80,
            armor=2,
            base_damage=8,
            exp_reward=40,
            x=x,
            y=y
        )

    def choose_action(self, player: Character) -> tuple:
        if self.abilities and self.mana >= 20 and random.random() > 0.3:
            ability_idx = random.randint(0, len(self.abilities) - 1)
            return ('ability', ability_idx, player)
        return ('attack', player)

    def get_sprite_name(self) -> str:
        return "mage.png"

    def get_color(self) -> tuple:
        return (100, 50, 200)


class Tank(Enemy):
    """
    Танк — живучий защитник.
    """

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(
            name="Tank",
            max_health=100,
            max_mana=30,
            armor=15,
            base_damage=12,
            exp_reward=50,
            x=x,
            y=y
        )

    def choose_action(self, player: Character) -> tuple:
        if self.health < self.max_health * 0.5 and self.abilities:
            return ('ability', 0, self)
        if random.random() > 0.7:
            return ('defend', None)
        return ('attack', player)

    def get_sprite_name(self) -> str:
        return "tank.png"

    def get_color(self) -> tuple:
        return (100, 100, 100)
