from .character import Character
from src.abilities.fireball import Fireball
from src.abilities.heal import Heal
from src.abilities.shield import Shield


class Player(Character):
    """
    Класс игрока. Наследуется от Character.
    Демонстрирует принцип наследования в ООП.
    """
    
    def __init__(self, name: str = "Hero", x: int = 0, y: int = 0):
        super().__init__(
            name=name,
            max_health=100,
            max_mana=50,
            armor=5,
            base_damage=15,
            x=x,
            y=y
        )
        self._init_abilities()
        self._experience = 0
        self._level = 1
    
    def _init_abilities(self):
        """Инициализировать способности игрока"""
        self.add_ability(Fireball())
        self.add_ability(Heal())
        self.add_ability(Shield())
    
    @property
    def experience(self) -> int:
        return self._experience
    
    @property
    def level(self) -> int:
        return self._level
    
    def gain_experience(self, amount: int):
        """Получить опыт"""
        self._experience += amount
        exp_needed = self._level * 100
        if self._experience >= exp_needed:
            self._level_up()
    
    def _level_up(self):
        """Повысить уровень"""
        self._level += 1
        self._max_health += 10
        self._health = self._max_health
        self._max_mana += 5
        self._mana = self._max_mana
        self._base_damage += 2
        self._armor += 1
    
    def get_sprite_name(self) -> str:
        return "player.png"
    
    def get_status_string(self) -> str:
        base = super().get_status_string()
        return f"{base} | LVL {self._level} | EXP {self._experience}"
