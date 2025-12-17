from src.entities.enemy import Warrior, Mage, Tank
from src.abilities.enemy_ability_factories import (
    MageAbilityFactory,
    TankAbilityFactory,
    WarriorAbilityFactory
)
import random


class EnemyFactory:

    @staticmethod
    def create_random(x: int, y: int):
        enemy_class = random.choice([Warrior, Mage, Tank])

        enemy = enemy_class(x=x, y=y)

        if isinstance(enemy, Mage):
            abilities = MageAbilityFactory().create()
        elif isinstance(enemy, Tank):
            abilities = TankAbilityFactory().create()
        else:
            abilities = WarriorAbilityFactory().create()

        for ability in abilities:
            enemy.add_ability(ability)

        return enemy
