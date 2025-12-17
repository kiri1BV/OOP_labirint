import pygame
import random
import os
from typing import List, Optional, Tuple

from src.core.maze import Maze
from src.core.battle import BattleSystem
from src.entities.player import Player
from src.entities.enemy_factory import EnemyFactory
from src.entities.enemy import Enemy
class Game:
    """
    Главный класс игры. Управляет игровым циклом и состояниями.
    Включает систему камеры для следования за игроком.
    """
    
    TILE_SIZE = 64
    VIEWPORT_TILES_X = 11
    VIEWPORT_TILES_Y = 9
    
    STATE_EXPLORATION = 'exploration'
    STATE_BATTLE = 'battle'
    STATE_GAME_OVER = 'game_over'
    STATE_VICTORY = 'victory'
    
    COLORS = {
        'wall': (40, 40, 60),
        'floor': (100, 100, 120),
        'start': (50, 150, 50),
        'exit': (200, 200, 50),
        'player': (50, 150, 255),
        'ui_bg': (30, 30, 40),
        'ui_text': (255, 255, 255),
        'hp_bar': (200, 50, 50),
        'mp_bar': (50, 50, 200),
        'armor': (150, 150, 150),
    }
    
    def __init__(self, maze_width: int = 41, maze_height: int = 31):
        pygame.init()
        pygame.display.set_caption("Dungeon Crawler RPG")
        
        self._maze = Maze(maze_width, maze_height, corridor_width=2)
        
        self._ui_height = 180
        self._viewport_width = self.VIEWPORT_TILES_X * self.TILE_SIZE
        self._viewport_height = self.VIEWPORT_TILES_Y * self.TILE_SIZE
        self._screen_width = self._viewport_width
        self._screen_height = self._viewport_height + self._ui_height
        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
        
        self._camera_x = 0
        self._camera_y = 0
        
        self._clock = pygame.time.Clock()
        self._font = pygame.font.Font(None, 28)
        self._font_small = pygame.font.Font(None, 22)
        self._font_large = pygame.font.Font(None, 42)
        
        start_x, start_y = self._maze.start_pos
        self._player = Player("Hero", start_x, start_y)
        
        self._enemies: List[Enemy] = []
        self._spawn_enemies(7)
        
        self._state = self.STATE_EXPLORATION
        self._battle: Optional[BattleSystem] = None
        self._current_enemy: Optional[Enemy] = None
        
        self._sprites = {}
        self._load_sprites()
        
        self._messages: List[str] = []
        self._running = True
        
        self._update_camera()
    
    def _load_sprites(self):
        """Загрузить спрайты или создать placeholder'ы"""
        sprite_dir = "assets/sprites"
        
        sprite_names = ["player.png", "warrior.png", "mage.png", "tank.png", 
                        "wall.png", "floor.png"]
        
        for name in sprite_names:
            path = os.path.join(sprite_dir, name)
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    self._sprites[name] = pygame.transform.scale(sprite, (self.TILE_SIZE, self.TILE_SIZE))
                except:
                    self._sprites[name] = None
            else:
                self._sprites[name] = None

    def _spawn_enemies(self, count: int):
        exclude = [self._maze.start_pos, self._maze.exit_pos]
        positions = self._maze.get_random_floor_positions(count, exclude)

        for x, y in positions:
            enemy = EnemyFactory.create_random(x=x, y=y)
            self._enemies.append(enemy)

    def _update_camera(self):
        """Обновить позицию камеры, центрируя на игроке"""
        target_x = self._player.x - self.VIEWPORT_TILES_X // 2
        target_y = self._player.y - self.VIEWPORT_TILES_Y // 2
        
        self._camera_x = max(0, min(target_x, self._maze.width - self.VIEWPORT_TILES_X))
        self._camera_y = max(0, min(target_y, self._maze.height - self.VIEWPORT_TILES_Y))
    
    def _world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Преобразовать мировые координаты в экранные"""
        screen_x = (world_x - self._camera_x) * self.TILE_SIZE
        screen_y = (world_y - self._camera_y) * self.TILE_SIZE
        return (screen_x, screen_y)
    
    def _is_visible(self, world_x: int, world_y: int) -> bool:
        """Проверить, видна ли клетка на экране"""
        return (self._camera_x <= world_x < self._camera_x + self.VIEWPORT_TILES_X and
                self._camera_y <= world_y < self._camera_y + self.VIEWPORT_TILES_Y)
    
    def _draw_placeholder_sprite(self, surface: pygame.Surface, world_x: int, world_y: int, 
                                  color: tuple, label: str = ""):
        """Нарисовать placeholder спрайт (цветной квадрат)"""
        if not self._is_visible(world_x, world_y):
            return
        
        screen_x, screen_y = self._world_to_screen(world_x, world_y)
        rect = pygame.Rect(screen_x + 4, screen_y + 4,
                          self.TILE_SIZE - 8, self.TILE_SIZE - 8)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        
        if label:
            text = self._font.render(label[0], True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x + self.TILE_SIZE // 2,
                                               screen_y + self.TILE_SIZE // 2))
            surface.blit(text, text_rect)
    
    def _draw_maze(self):
        """Отрисовать видимую часть лабиринта"""
        for vy in range(self.VIEWPORT_TILES_Y + 1):
            for vx in range(self.VIEWPORT_TILES_X + 1):
                world_x = self._camera_x + vx
                world_y = self._camera_y + vy
                
                if world_x >= self._maze.width or world_y >= self._maze.height:
                    continue
                
                cell = self._maze.get_cell_type(world_x, world_y)
                screen_x, screen_y = self._world_to_screen(world_x, world_y)
                rect = pygame.Rect(screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE)
                
                if cell == Maze.WALL:
                    if self._sprites.get("wall.png"):
                        self._screen.blit(self._sprites["wall.png"], rect)
                    else:
                        pygame.draw.rect(self._screen, self.COLORS['wall'], rect)
                        pygame.draw.rect(self._screen, (60, 60, 80), rect, 1)
                elif cell == Maze.START:
                    pygame.draw.rect(self._screen, self.COLORS['start'], rect)
                elif cell == Maze.EXIT:
                    pygame.draw.rect(self._screen, self.COLORS['exit'], rect)
                    exit_text = self._font_small.render("EXIT", True, (0, 0, 0))
                    text_rect = exit_text.get_rect(center=(screen_x + self.TILE_SIZE // 2,
                                                           screen_y + self.TILE_SIZE // 2))
                    self._screen.blit(exit_text, text_rect)
                else:
                    if self._sprites.get("floor.png"):
                        self._screen.blit(self._sprites["floor.png"], rect)
                    else:
                        pygame.draw.rect(self._screen, self.COLORS['floor'], rect)
    
    def _draw_entities(self):
        """Отрисовать персонажей"""
        if self._is_visible(self._player.x, self._player.y):
            sprite_name = self._player.get_sprite_name()
            screen_x, screen_y = self._world_to_screen(self._player.x, self._player.y)
            
            if self._sprites.get(sprite_name):
                rect = pygame.Rect(screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE)
                self._screen.blit(self._sprites[sprite_name], rect)
            else:
                self._draw_placeholder_sprite(self._screen, self._player.x, self._player.y,
                                             self.COLORS['player'], "P")
        
        for enemy in self._enemies:
            if enemy.is_alive and self._is_visible(enemy.x, enemy.y):
                sprite_name = enemy.get_sprite_name()
                screen_x, screen_y = self._world_to_screen(enemy.x, enemy.y)
                
                if self._sprites.get(sprite_name):
                    rect = pygame.Rect(screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE)
                    self._screen.blit(self._sprites[sprite_name], rect)
                else:
                    self._draw_placeholder_sprite(self._screen, enemy.x, enemy.y,
                                                 enemy.get_color(), enemy.name)
    
    def _draw_bar(self, x: int, y: int, width: int, height: int, 
                  current: int, maximum: int, color: tuple):
        """Нарисовать полоску (HP/MP)"""
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self._screen, (50, 50, 50), bg_rect)
        
        if maximum > 0:
            fill_width = int((current / maximum) * width)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(self._screen, color, fill_rect)
        
        pygame.draw.rect(self._screen, (255, 255, 255), bg_rect, 1)
    
    def _draw_ui_exploration(self):
        """Отрисовать UI в режиме исследования"""
        ui_y = self._viewport_height
        ui_rect = pygame.Rect(0, ui_y, self._screen_width, self._ui_height)
        pygame.draw.rect(self._screen, self.COLORS['ui_bg'], ui_rect)
        
        name_text = self._font_large.render(self._player.name, True, self.COLORS['ui_text'])
        self._screen.blit(name_text, (10, ui_y + 8))
        
        hp_label = self._font_small.render(f"HP: {self._player.health}/{self._player.max_health}", 
                                           True, self.COLORS['ui_text'])
        self._screen.blit(hp_label, (10, ui_y + 45))
        self._draw_bar(90, ui_y + 45, 160, 18, self._player.health, 
                      self._player.max_health, self.COLORS['hp_bar'])
        
        mp_label = self._font_small.render(f"MP: {self._player.mana}/{self._player.max_mana}", 
                                           True, self.COLORS['ui_text'])
        self._screen.blit(mp_label, (10, ui_y + 68))
        self._draw_bar(90, ui_y + 68, 160, 18, self._player.mana, 
                      self._player.max_mana, self.COLORS['mp_bar'])
        
        stats_text = self._font_small.render(f"Armor: {self._player.armor} | LVL: {self._player.level}", 
                                              True, self.COLORS['armor'])
        self._screen.blit(stats_text, (10, ui_y + 95))
        
        controls = [
            "WASD - Move | Find EXIT"
        ]
        for i, line in enumerate(controls):
            text = self._font_small.render(line, True, self.COLORS['ui_text'])
            self._screen.blit(text, (280, ui_y + 10 + i * 22))
        
        for i, msg in enumerate(self._messages[-3:]):
            text = self._font_small.render(msg, True, (200, 200, 100))
            self._screen.blit(text, (10, ui_y + 120 + i * 20))
    
    def _draw_ui_battle(self):
        """Отрисовать UI в режиме боя"""
        ui_y = self._viewport_height
        ui_rect = pygame.Rect(0, ui_y, self._screen_width, self._ui_height)
        pygame.draw.rect(self._screen, self.COLORS['ui_bg'], ui_rect)
        
        battle_text = self._font_large.render("BATTLE!", True, (255, 100, 100))
        self._screen.blit(battle_text, (self._screen_width // 2 - 60, ui_y + 5))
        
        player_text = self._font_small.render(f"{self._player.name}: HP {self._player.health}/{self._player.max_health} MP {self._player.mana}/{self._player.max_mana}", 
                                              True, self.COLORS['ui_text'])
        self._screen.blit(player_text, (10, ui_y + 38))
        self._draw_bar(10, ui_y + 56, 180, 14, self._player.health, 
                      self._player.max_health, self.COLORS['hp_bar'])
        
        if self._current_enemy:
            enemy_text = self._font_small.render(f"{self._current_enemy.name}: HP {self._current_enemy.health}/{self._current_enemy.max_health}", 
                                                True, self.COLORS['ui_text'])
            self._screen.blit(enemy_text, (10, ui_y + 75))
            self._draw_bar(10, ui_y + 93, 180, 14, self._current_enemy.health, 
                          self._current_enemy.max_health, self.COLORS['hp_bar'])
        
        if self._battle and self._battle.is_player_turn:
            actions = ["[A]Attack", "[D]Defend", "[1]Fire", "[2]Heal", "[3]Shield"]
            for i, action in enumerate(actions):
                color = (150, 255, 150) if i < 2 else (150, 150, 255)
                text = self._font_small.render(action, True, color)
                self._screen.blit(text, (200 + i * 95, ui_y + 45))
        else:
            wait_text = self._font.render("Enemy turn...", True, (255, 150, 150))
            self._screen.blit(wait_text, (200, ui_y + 45))
        
        if self._battle:
            for i, log in enumerate(self._battle.battle_log[-2:]):
                text = self._font_small.render(log[:60], True, (200, 200, 100))
                self._screen.blit(text, (10, ui_y + 115 + i * 20))
    
    def _draw_game_over(self):
        """Отрисовать экран Game Over"""
        overlay = pygame.Surface((self._screen_width, self._screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self._screen.blit(overlay, (0, 0))
        
        go_text = self._font_large.render("GAME OVER", True, (255, 50, 50))
        go_rect = go_text.get_rect(center=(self._screen_width // 2, self._screen_height // 2 - 20))
        self._screen.blit(go_text, go_rect)
        
        restart_text = self._font.render("Press R to restart or Q to quit", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self._screen_width // 2, self._screen_height // 2 + 20))
        self._screen.blit(restart_text, restart_rect)
    
    def _draw_victory(self):
        """Отрисовать экран победы"""
        overlay = pygame.Surface((self._screen_width, self._screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self._screen.blit(overlay, (0, 0))
        
        win_text = self._font_large.render("VICTORY!", True, (50, 255, 50))
        win_rect = win_text.get_rect(center=(self._screen_width // 2, self._screen_height // 2 - 20))
        self._screen.blit(win_text, win_rect)
        
        info_text = self._font.render(f"Level: {self._player.level} | EXP: {self._player.experience}", 
                                      True, (200, 200, 200))
        info_rect = info_text.get_rect(center=(self._screen_width // 2, self._screen_height // 2 + 10))
        self._screen.blit(info_text, info_rect)
        
        restart_text = self._font.render("Press R to play again or Q to quit", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self._screen_width // 2, self._screen_height // 2 + 40))
        self._screen.blit(restart_text, restart_rect)
    
    def _handle_exploration_input(self, event: pygame.event.Event):
        """Обработать ввод в режиме исследования"""
        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            
            if event.key in (pygame.K_w, pygame.K_UP):
                dy = -1
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                dy = 1
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                dx = -1
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                dx = 1
            
            if dx != 0 or dy != 0:
                new_x = self._player.x + dx
                new_y = self._player.y + dy
                
                if self._maze.is_walkable(new_x, new_y):
                    for enemy in self._enemies:
                        if enemy.is_alive and enemy.x == new_x and enemy.y == new_y:
                            self._start_battle(enemy)
                            return
                    
                    self._player.x = new_x
                    self._player.y = new_y
                    self._update_camera()
                    
                    if self._maze.is_exit(new_x, new_y):
                        self._state = self.STATE_VICTORY
    
    def _handle_battle_input(self, event: pygame.event.Event):
        """Обработать ввод в режиме боя"""
        if not self._battle or not self._battle.is_player_turn:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self._battle.player_attack()
            elif event.key == pygame.K_d:
                self._battle.player_defend()
            elif event.key == pygame.K_1:
                self._battle.player_use_ability(0, target_self=False)
            elif event.key == pygame.K_2:
                self._battle.player_use_ability(1, target_self=True)
            elif event.key == pygame.K_3:
                self._battle.player_use_ability(2, target_self=True)
    
    def _handle_game_over_input(self, event: pygame.event.Event):
        """Обработать ввод на экране Game Over"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._restart_game()
            elif event.key == pygame.K_q:
                self._running = False
    
    def _start_battle(self, enemy: Enemy):
        """Начать бой с врагом"""
        self._current_enemy = enemy
        self._battle = BattleSystem(self._player, enemy)
        self._state = self.STATE_BATTLE
        self._messages.append(f"Battle with {enemy.name}!")
    
    def _end_battle(self):
        """Завершить бой"""
        if self._battle and self._battle.winner:
            if self._battle.winner == self._player and self._current_enemy:
                self._enemies.remove(self._current_enemy)
                self._messages.append(f"Defeated {self._current_enemy.name}!")
            else:
                self._state = self.STATE_GAME_OVER
                return
        
        self._battle = None
        self._current_enemy = None
        self._state = self.STATE_EXPLORATION
    
    def _restart_game(self):
        """Перезапустить игру"""
        self._maze = Maze(self._maze.width, self._maze.height, corridor_width=2)
        start_x, start_y = self._maze.start_pos
        self._player = Player("Hero", start_x, start_y)
        self._enemies.clear()
        self._spawn_enemies(7)
        self._state = self.STATE_EXPLORATION
        self._battle = None
        self._current_enemy = None
        self._messages.clear()
        self._update_camera()
    
    def _update(self):
        """Обновить состояние игры"""
        if self._state == self.STATE_BATTLE and self._battle:
            if self._battle.is_battle_over:
                self._end_battle()
            elif not self._battle.is_player_turn:
                pygame.time.delay(500)
                self._battle.process_enemy_turn()
    
    def _draw(self):
        """Отрисовать все"""
        self._screen.fill((0, 0, 0))
        
        self._draw_maze()
        self._draw_entities()
        
        if self._state == self.STATE_EXPLORATION:
            self._draw_ui_exploration()
        elif self._state == self.STATE_BATTLE:
            self._draw_ui_battle()
        elif self._state == self.STATE_GAME_OVER:
            self._draw_ui_exploration()
            self._draw_game_over()
        elif self._state == self.STATE_VICTORY:
            self._draw_ui_exploration()
            self._draw_victory()
        
        pygame.display.flip()
    
    def run(self):
        """Главный игровой цикл"""
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                
                if self._state == self.STATE_EXPLORATION:
                    self._handle_exploration_input(event)
                elif self._state == self.STATE_BATTLE:
                    self._handle_battle_input(event)
                elif self._state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    self._handle_game_over_input(event)
            
            self._update()
            self._draw()
            self._clock.tick(60)
        
        pygame.quit()
