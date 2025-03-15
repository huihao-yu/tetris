import pygame
import random
pygame.init()
GAME_WIDTH = 300
PREVIEW_WIDTH = 100
SCREEN_WIDTH = GAME_WIDTH + PREVIEW_WIDTH
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = GAME_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (128, 0, 128)
]
SHAPES = [
    [[(0, 1), (1, 1), (2, 1), (3, 1)],  # I型水平
     [(1, 0), (1, 1), (1, 2), (1, 3)]],  # I型垂直
    [[(0, 0), (0, 1), (1, 0), (1, 1)]],  # O型
    [[(1, 0), (0, 1), (1, 1), (2, 1)],  # T型
     [(1, 0), (1, 1), (1, 2), (2, 1)],
     [(0, 1), (1, 1), (2, 1), (1, 2)],
     [(1, 0), (1, 1), (1, 2), (0, 1)]],
    [[(0, 0), (0, 1), (0, 2), (1, 2)],  # L型
     [(0, 1), (1, 1), (2, 1), (2, 0)],
     [(1, 0), (1, 1), (1, 2), (0, 0)],
     [(0, 0), (0, 1), (1, 0), (2, 0)]],
    [[(0, 2), (0, 1), (0, 0), (1, 0)],  # J型
     [(0, 0), (1, 0), (2, 0), (2, 1)],
     [(1, 2), (1, 1), (1, 0), (0, 2)],
     [(2, 1), (1, 1), (0, 1), (0, 0)]],
    [[(1, 0), (2, 0), (0, 1), (1, 1)],  # S型
     [(0, 0), (0, 1), (1, 1), (1, 2)]],
    [[(0, 0), (1, 0), (1, 1), (2, 1)],  # Z型
     [(1, 0), (0, 1), (1, 1), (0, 2)]]
]

# 新增踢墙数据（不同形状的旋转修正）
KICK_DATA = {
    # L, J, T, S, Z 的踢墙数据
    3: [[(0,0), (-1,0), (1,0), (0,1), (-1,1)]],  # L型
    4: [[(0,0), (-1,0), (1,0), (0,1), (-1,1)]],  # J型
    2: [[(0,0), (-1,0), (1,0), (0,1), (-1,1)]],  # T型
    5: [[(0,0), (0,1), (1,1), (-1,0), (0,-1)]],  # S型
    6: [[(0,0), (0,1), (1,1), (-1,0), (0,-1)]],  # Z型
    # I型的特殊踢墙数据
    0: [
        [(0,0), (-2,0), (1,0), (-2,1), (1,-2)],  # 0->1
        [(0,0), (2,0), (-1,0), (2,-1), (-1,2)]   # 1->0
    ]
}

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块V4.0")
        self.clock = pygame.time.Clock()
        self.grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.speed_levels = [0.2, 0.25, 0.35, 0.45, 0.5]
        self.current_speed_index = 2
        self.fall_speed = self.speed_levels[self.current_speed_index]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.fall_time = 0
        self.clear_delay = 0

    def new_piece(self):
        shape_index = random.randint(0, 6)
        rotation = 0
        color = random.choice(COLORS)
        shape = SHAPES[shape_index][rotation]
        x = GRID_WIDTH // 2 - 2
        y = 0
        return {'shape': shape, 'shape_index': shape_index,
                'rotation': rotation, 'color': color, 'x': x, 'y': y}

    def check_collision(self, shape, x, y):
        for (dx, dy) in shape:
            px = x + dx
            py = y + dy
            if px < 0 or px >= GRID_WIDTH or py >= GRID_HEIGHT:
                return True
            if py >= 0 and self.grid[py][px] is not None:
                return True
        return False

    def rotate_piece(self):
        piece = self.current_piece
        shape_index = piece['shape_index']
        old_rotation = piece['rotation']
        new_rotation = (old_rotation + 1) % len(SHAPES[shape_index])
        new_shape = SHAPES[shape_index][new_rotation]

        # 获取踢墙数据
        if shape_index in KICK_DATA:
            if shape_index == 0:  # I型特殊处理
                kick_cases = KICK_DATA[0][old_rotation]
            else:
                kick_cases = KICK_DATA[shape_index][0]
        else:  # O型没有踢墙
            kick_cases = [(0,0)]

        # 尝试所有踢墙偏移
        original_x = piece['x']
        original_y = piece['y']
        for (dx, dy) in kick_cases:
            piece['x'] = original_x + dx
            piece['y'] = original_y + dy
            if not self.check_collision(new_shape, piece['x'], piece['y']):
                piece['rotation'] = new_rotation
                piece['shape'] = new_shape
                return
        # 所有尝试失败则恢复原状
        piece['x'] = original_x
        piece['y'] = original_y

    def lock_piece(self):
        piece = self.current_piece
        for (dx, dy) in piece['shape']:
            px = piece['x'] + dx
            py = piece['y'] + dy
            if py >= 0:
                self.grid[py][px] = piece['color']
        self.clear_delay = 5

    def clear_lines(self):
        lines_to_clear = [y for y in range(GRID_HEIGHT) if all(self.grid[y])]
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [None] * GRID_WIDTH)
        return len(lines_to_clear)

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x],
                                     (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                      BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_piece(self, piece):
        for (dx, dy) in piece['shape']:
            x = (piece['x'] + dx) * BLOCK_SIZE
            y = (piece['y'] + dy) * BLOCK_SIZE
            pygame.draw.rect(self.screen, piece['color'],
                             (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def draw_preview(self):
        piece = self.next_piece
        if piece['shape_index'] == 0:
            preview_shape = SHAPES[0][1]
        else:
            preview_shape = piece['shape']
        min_dx = min(dx for dx, dy in preview_shape)
        max_dx = max(dx for dx, dy in preview_shape)
        min_dy = min(dy for dx, dy in preview_shape)
        max_dy = max(dy for dx, dy in preview_shape)
        width = (max_dx - min_dx + 1) * BLOCK_SIZE
        height = (max_dy - min_dy + 1) * BLOCK_SIZE
        start_x = GAME_WIDTH + (PREVIEW_WIDTH - width) // 2
        start_y = 150
        for (dx, dy) in preview_shape:
            x = start_x + (dx - min_dx) * BLOCK_SIZE
            y = start_y + (dy - min_dy) * BLOCK_SIZE
            pygame.draw.rect(self.screen, piece['color'],
                             (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def reset(self):
        self.grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.current_speed_index = 2
        self.fall_speed = self.speed_levels[self.current_speed_index]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.clear_delay = 0

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(FPS) / 1000.0
            self.fall_time += delta_time
            self.screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    if event.key == pygame.K_s:
                        self.reset()
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.current_piece['x'] -= 1
                            if self.check_collision(self.current_piece['shape'],
                                                    self.current_piece['x'],
                                                    self.current_piece['y']):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece['x'] += 1
                            if self.check_collision(self.current_piece['shape'],
                                                    self.current_piece['x'],
                                                    self.current_piece['y']):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_DOWN:
                            self.current_piece['y'] += 1
                            if self.check_collision(self.current_piece['shape'],
                                                    self.current_piece['x'],
                                                    self.current_piece['y']):
                                self.current_piece['y'] -= 1
                                self.lock_piece()
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                            self.current_speed_index = (self.current_speed_index - 1) % 5
                            self.fall_speed = self.speed_levels[self.current_speed_index]
                        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                            self.current_speed_index = (self.current_speed_index + 1) % 5
                            self.fall_speed = self.speed_levels[self.current_speed_index]

            if self.clear_delay > 0:
                self.clear_delay -= 1
                if self.clear_delay == 0:
                    lines_cleared = self.clear_lines()
                    self.score += lines_cleared
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    if self.check_collision(self.current_piece['shape'],
                                            self.current_piece['x'],
                                            self.current_piece['y']):
                        self.game_over = True

            if not self.game_over and self.clear_delay == 0:
                if self.fall_time >= self.fall_speed:
                    self.current_piece['y'] += 1
                    if self.check_collision(self.current_piece['shape'],
                                            self.current_piece['x'],
                                            self.current_piece['y']):
                        self.current_piece['y'] -= 1
                        self.lock_piece()
                    self.fall_time = 0

            self.draw_grid()
            pygame.draw.line(self.screen, WHITE, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)
            self.draw_text(f'Score: {self.score}', 30, WHITE, GAME_WIDTH // 2, 20)
            self.draw_text(f'Speed: {self.fall_speed}s', 30, WHITE, GAME_WIDTH // 2, 50)
            if not self.game_over:
                self.draw_piece(self.current_piece)
                self.draw_text('Next:', 30, WHITE, GAME_WIDTH + PREVIEW_WIDTH // 2, 100)
                self.draw_preview()
            if self.game_over:
                self.draw_text('Game Over! Press S to restart', 40, WHITE,
                               SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Tetris()
    game.run()