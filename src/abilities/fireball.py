from .ability import Ability
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.character import Character


class Fireball(Ability):
    """
    Огненный шар - наносит магический урон, игнорируя часть брони.
    """
    
    def __init__(self):
        super().__init__(
            name="Fireball",
            mana_cost=20,
            description="Огненный шар наносит 25 урона, игнорируя 50% брони"
        )
        self._base_damage = 25
        self._armor_penetration = 0.5
    
    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        effective_armor = int(target.armor * (1 - self._armor_penetration))
        damage = max(1, self._base_damage - effective_armor)
        
        if target.is_defending:
            damage = damage // 2
        
        target.health -= damage
        
        return f"{caster.name} бросает Fireball в {target.name}! Нанесено {damage} урона!"
