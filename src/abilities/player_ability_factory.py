from typing import List
from src.abilities.ability import Ability
from src.abilities.fireball import Fireball
from src.abilities.heal import Heal
from src.abilities.shield import Shield
from src.abilities.ability_factory import AbilityFactory


class PlayerAbilityFactory(AbilityFactory):

    def create_abilities(self) -> List[Ability]:
        return [
            Fireball(),
            Heal(),
            Shield()
        ]
