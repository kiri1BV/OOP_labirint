from .ability import Ability
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.character import Character


class Heal(Ability):
    """
    Исцеление - восстанавливает здоровье цели (обычно себя).
    """
    
    def __init__(self):
        super().__init__(
            name="Heal",
            mana_cost=15,
            description="Восстанавливает 30 HP"
        )
        self._heal_amount = 30
    
    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        old_health = target.health
        target.heal(self._heal_amount)
        healed = target.health - old_health
        
        if caster == target:
            return f"{caster.name} исцеляет себя на {healed} HP!"
        return f"{caster.name} исцеляет {target.name} на {healed} HP!"
