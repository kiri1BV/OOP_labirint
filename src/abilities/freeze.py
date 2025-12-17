from .ability import Ability
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.character import Character


class Freeze(Ability):
    """
    Заморозка - замораживает цель на 1-2 хода и наносит небольшой урон.
    """
    
    def __init__(self):
        super().__init__(
            name="Freeze",
            mana_cost=25,
            description="Замораживает врага на 2 хода и наносит 10 урона"
        )
        self._damage = 10
        self._freeze_turns = 2
    
    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        target.health -= self._damage
        target.freeze(self._freeze_turns)
        
        return f"{caster.name} замораживает {target.name}! {target.name} пропустит {self._freeze_turns} хода и получил {self._damage} урона!"
