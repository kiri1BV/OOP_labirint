import random
from typing import List, Tuple, Optional


class Maze:
    """
    Класс для генерации и управления лабиринтом.
    Генерирует лабиринт с широкими коридорами и несколькими путями.
    """
    
    WALL = 1
    FLOOR = 0
    START = 2
    EXIT = 3
    
    def __init__(self, width: int = 41, height: int = 31, corridor_width: int = 2):
        self._corridor_width = corridor_width
        
        self._width = width
        self._height = height
        self._grid: List[List[int]] = []
        self._start_pos: Tuple[int, int] = (2, 2)
        self._exit_pos: Tuple[int, int] = (width - 3, height - 3)
        self._generate()
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def grid(self) -> List[List[int]]:
        return self._grid
    
    @property
    def start_pos(self) -> Tuple[int, int]:
        return self._start_pos
    
    @property
    def exit_pos(self) -> Tuple[int, int]:
        return self._exit_pos
    
    def _generate(self):
        """Генерация лабиринта с широкими коридорами"""
        self._grid = [[self.WALL for _ in range(self._width)] for _ in range(self._height)]
        
        cell_w = (self._width - 1) // 3
        cell_h = (self._height - 1) // 3
        
        if cell_w < 2:
            cell_w = 2
        if cell_h < 2:
            cell_h = 2
        
        visited = [[False for _ in range(cell_w)] for _ in range(cell_h)]
        
        def cell_to_grid(cx: int, cy: int) -> Tuple[int, int]:
            return (1 + cx * 3, 1 + cy * 3)
        
        def carve_cell(cx: int, cy: int):
            gx, gy = cell_to_grid(cx, cy)
            for dy in range(self._corridor_width):
                for dx in range(self._corridor_width):
                    nx, ny = gx + dx, gy + dy
                    if 0 < nx < self._width - 1 and 0 < ny < self._height - 1:
                        self._grid[ny][nx] = self.FLOOR
        
        def carve_passage(cx1: int, cy1: int, cx2: int, cy2: int):
            gx1, gy1 = cell_to_grid(cx1, cy1)
            gx2, gy2 = cell_to_grid(cx2, cy2)
            
            if cx1 == cx2:
                min_y = min(gy1, gy2)
                max_y = max(gy1, gy2) + self._corridor_width
                for y in range(min_y, max_y):
                    for dx in range(self._corridor_width):
                        nx = gx1 + dx
                        if 0 < nx < self._width - 1 and 0 < y < self._height - 1:
                            self._grid[y][nx] = self.FLOOR
            else:
                min_x = min(gx1, gx2)
                max_x = max(gx1, gx2) + self._corridor_width
                for x in range(min_x, max_x):
                    for dy in range(self._corridor_width):
                        ny = gy1 + dy
                        if 0 < x < self._width - 1 and 0 < ny < self._height - 1:
                            self._grid[ny][x] = self.FLOOR
        
        stack = [(0, 0)]
        visited[0][0] = True
        carve_cell(0, 0)
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while stack:
            cx, cy = stack[-1]
            
            random.shuffle(directions)
            found = False
            
            for dx, dy in directions:
                ncx, ncy = cx + dx, cy + dy
                
                if 0 <= ncx < cell_w and 0 <= ncy < cell_h:
                    if not visited[ncy][ncx]:
                        visited[ncy][ncx] = True
                        carve_passage(cx, cy, ncx, ncy)
                        carve_cell(ncx, ncy)
                        stack.append((ncx, ncy))
                        found = True
                        break
            
            if not found:
                stack.pop()
        
        self._add_extra_passages(cell_w, cell_h, cell_to_grid, carve_passage)
        
        sx, sy = self._start_pos
        for dy in range(self._corridor_width):
            for dx in range(self._corridor_width):
                if 0 < sx + dx < self._width - 1 and 0 < sy + dy < self._height - 1:
                    self._grid[sy + dy][sx + dx] = self.START
        
        ex, ey = self._exit_pos
        for dy in range(self._corridor_width):
            for dx in range(self._corridor_width):
                if 0 < ex + dx < self._width - 1 and 0 < ey + dy < self._height - 1:
                    self._grid[ey + dy][ex + dx] = self.EXIT
        
        self._ensure_exit_accessible()
    
    def _add_extra_passages(self, cell_w: int, cell_h: int, cell_to_grid, carve_passage):
        """Добавить дополнительные проходы для создания нескольких путей"""
        num_extra = (cell_w * cell_h) // 4
        
        for _ in range(num_extra):
            cx = random.randint(0, cell_w - 1)
            cy = random.randint(0, cell_h - 1)
            
            direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            ncx, ncy = cx + direction[0], cy + direction[1]
            
            if 0 <= ncx < cell_w and 0 <= ncy < cell_h:
                carve_passage(cx, cy, ncx, ncy)
    
    def _ensure_exit_accessible(self):
        """Убедиться, что выход доступен"""
        ex, ey = self._exit_pos
        
        for dx, dy in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
            for offset in range(self._corridor_width):
                if dx == 0:
                    nx, ny = ex + offset, ey + dy * self._corridor_width
                else:
                    nx, ny = ex + dx * self._corridor_width, ey + offset
                
                if 0 < nx < self._width - 1 and 0 < ny < self._height - 1:
                    if self._grid[ny][nx] == self.FLOOR:
                        return
        
        for dy in range(-self._corridor_width, self._corridor_width + 1):
            for dx in range(-self._corridor_width, 0):
                nx, ny = ex + dx, ey + dy
                if 0 < nx < self._width - 1 and 0 < ny < self._height - 1:
                    self._grid[ny][nx] = self.FLOOR
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Проверить, можно ли пройти по клетке"""
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._grid[y][x] != self.WALL
        return False
    
    def is_wall(self, x: int, y: int) -> bool:
        """Проверить, является ли клетка стеной"""
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._grid[y][x] == self.WALL
        return True
    
    def is_exit(self, x: int, y: int) -> bool:
        """Проверить, является ли клетка выходом"""
        ex, ey = self._exit_pos
        return ex <= x < ex + self._corridor_width and ey <= y < ey + self._corridor_width
    
    def get_random_floor_positions(self, count: int, exclude: Optional[List[Tuple[int, int]]] = None) -> List[Tuple[int, int]]:
        """Получить случайные позиции на полу для размещения врагов"""
        if exclude is None:
            exclude = []
        
        sx, sy = self._start_pos
        ex, ey = self._exit_pos
        
        expanded_exclude = list(exclude)
        for dy in range(self._corridor_width + 2):
            for dx in range(self._corridor_width + 2):
                expanded_exclude.append((sx + dx - 1, sy + dy - 1))
                expanded_exclude.append((ex + dx - 1, ey + dy - 1))
        
        floor_positions = []
        for y in range(self._height):
            for x in range(self._width):
                if self._grid[y][x] == self.FLOOR and (x, y) not in expanded_exclude:
                    floor_positions.append((x, y))
        
        if len(floor_positions) < count:
            count = len(floor_positions)
        
        if count == 0:
            return []
        
        return random.sample(floor_positions, count)
    
    def get_cell_type(self, x: int, y: int) -> int:
        """Получить тип клетки"""
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._grid[y][x]
        return self.WALL
