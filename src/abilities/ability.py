from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.character import Character


class Ability(ABC):
    """
    Абстрактный базовый класс для всех способностей.
    """
    
    def __init__(self, name: str, mana_cost: int, description: str):
        self._name = name
        self._mana_cost = mana_cost
        self._description = description
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def mana_cost(self) -> int:
        return self._mana_cost
    
    @property
    def description(self) -> str:
        return self._description
    
    def can_use(self, caster: 'Character') -> bool:
        """Проверить, может ли персонаж использовать способность"""
        return caster.mana >= self._mana_cost and caster.is_alive
    
    def use(self, caster: 'Character', target: 'Character') -> str:
        """
        Использовать способность.
        Возвращает строку с описанием результата.
        """
        if not self.can_use(caster):
            return f"{caster.name} не хватает маны для {self._name}!"
        
        caster.use_mana(self._mana_cost)
        return self._apply_effect(caster, target)
    
    @abstractmethod
    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        """Применить эффект способности. Реализуется в подклассах."""
        pass
    
    def get_info(self) -> str:
        """Получить информацию о способности"""
        return f"{self._name} (MP: {self._mana_cost}) - {self._description}"
