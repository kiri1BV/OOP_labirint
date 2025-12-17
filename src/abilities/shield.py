from .ability import Ability
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.character import Character


class Shield(Ability):
    """
    Щит - временно увеличивает броню и восстанавливает немного HP.
    """
    
    def __init__(self):
        super().__init__(
            name="Shield",
            mana_cost=15,
            description="Активирует защиту и восстанавливает 10 HP"
        )
        self._heal_amount = 10
    
    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        target.defend()
        old_health = target.health
        target.heal(self._heal_amount)
        healed = target.health - old_health
        
        if caster == target:
            return f"{caster.name} поднимает щит и восстанавливает {healed} HP!"
        return f"{caster.name} защищает {target.name} и восстанавливает {healed} HP!"
