from typing import List, Optional, Tuple
from src.entities.character import Character
from src.entities.player import Player
from src.entities.enemy import Enemy


class BattleSystem:
    """
    Пошаговая боевая система.
    Управляет боем между игроком и врагом.
    """
    
    def __init__(self, player: Player, enemy: Enemy):
        self._player = player
        self._enemy = enemy
        self._turn = 0
        self._is_player_turn = True
        self._battle_log: List[str] = []
        self._is_battle_over = False
        self._winner: Optional[Character] = None
    
    @property
    def player(self) -> Player:
        return self._player
    
    @property
    def enemy(self) -> Enemy:
        return self._enemy
    
    @property
    def is_player_turn(self) -> bool:
        return self._is_player_turn
    
    @property
    def battle_log(self) -> List[str]:
        return self._battle_log
    
    @property
    def is_battle_over(self) -> bool:
        return self._is_battle_over
    
    @property
    def winner(self) -> Optional[Character]:
        return self._winner
    
    def _log(self, message: str):
        """Добавить сообщение в лог боя"""
        self._battle_log.append(message)
        if len(self._battle_log) > 10:
            self._battle_log.pop(0)
    
    def player_attack(self) -> str:
        """Игрок атакует врага"""
        if not self._is_player_turn or self._is_battle_over:
            return ""
        
        if self._player.is_frozen:
            msg = f"{self._player.name} заморожен и пропускает ход!"
            self._log(msg)
            self._end_player_turn()
            return msg
        
        damage = self._player.attack(self._enemy)
        msg = f"{self._player.name} атакует {self._enemy.name}! Нанесено {damage} урона!"
        self._log(msg)
        self._check_battle_end()
        self._end_player_turn()
        return msg
    
    def player_defend(self) -> str:
        """Игрок защищается"""
        if not self._is_player_turn or self._is_battle_over:
            return ""
        
        if self._player.is_frozen:
            msg = f"{self._player.name} заморожен и не может защищаться!"
            self._log(msg)
            self._end_player_turn()
            return msg
        
        self._player.defend()
        msg = f"{self._player.name} принимает защитную стойку!"
        self._log(msg)
        self._end_player_turn()
        return msg
    
    def player_use_ability(self, ability_index: int, target_self: bool = False) -> str:
        """Игрок использует способность"""
        if not self._is_player_turn or self._is_battle_over:
            return ""
        
        if self._player.is_frozen:
            msg = f"{self._player.name} заморожен и не может использовать способности!"
            self._log(msg)
            self._end_player_turn()
            return msg
        
        target = self._player if target_self else self._enemy
        result = self._player.use_ability(ability_index, target)
        
        if result:
            self._log(result)
            self._check_battle_end()
            self._end_player_turn()
            return result
        
        return "Не удалось использовать способность!"
    
    def _end_player_turn(self):
        """Завершить ход игрока"""
        self._player.end_turn()
        if not self._is_battle_over:
            self._is_player_turn = False
            self._turn += 1
    
    def process_enemy_turn(self) -> str:
        """Обработать ход врага (ИИ)"""
        if self._is_player_turn or self._is_battle_over:
            return ""
        
        if self._enemy.is_frozen:
            msg = f"{self._enemy.name} заморожен и пропускает ход!"
            self._log(msg)
            self._enemy.end_turn()
            self._is_player_turn = True
            return msg
        
        action = self._enemy.choose_action(self._player)
        msg = ""
        
        if action[0] == 'attack':
            damage = self._enemy.attack(self._player)
            msg = f"{self._enemy.name} атакует {self._player.name}! Нанесено {damage} урона!"
        
        elif action[0] == 'defend':
            self._enemy.defend()
            msg = f"{self._enemy.name} принимает защитную стойку!"
        
        elif action[0] == 'ability':
            ability_idx = action[1]
            target = action[2]
            result = self._enemy.use_ability(ability_idx, target)
            msg = result if result else f"{self._enemy.name} пытается использовать способность!"
        
        self._log(msg)
        self._enemy.end_turn()
        self._check_battle_end()
        self._is_player_turn = True
        
        return msg
    
    def _check_battle_end(self):
        """Проверить, закончился ли бой"""
        if not self._enemy.is_alive:
            self._is_battle_over = True
            self._winner = self._player
            self._player.gain_experience(self._enemy.exp_reward)
            self._log(f"{self._enemy.name} повержен! +{self._enemy.exp_reward} EXP!")
        
        elif not self._player.is_alive:
            self._is_battle_over = True
            self._winner = self._enemy
            self._log(f"{self._player.name} погиб...")
    
    def get_player_abilities_info(self) -> List[str]:
        """Получить информацию о способностях игрока"""
        return [ability.get_info() for ability in self._player.abilities]
