import pygame
import random

pygame.init()
pygame.font.init()

# Layout Dimensions
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10 * BLOCK_SIZE, 20 * BLOCK_SIZE
SIDEBAR_WIDTH = 180
WINDOW_WIDTH = GRID_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Neon Tetris")

# Palettes
BG_COLOR = (13, 13, 26)
GRID_COLOR = (26, 26, 58)
GHOST_ALPHA_COLOR = (58, 58, 90, 80) # RGBA: The 4th value is 80/255 transparency

NEON_COLORS = [
    (0, 0, 0),        
    (0, 255, 255),    
    (0, 0, 255),      
    (255, 165, 0),    
    (255, 255, 0),    
    (0, 255, 0),      
    (128, 0, 128),    
    (255, 0, 85)       
]

SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]], 
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 8, 9], [4, 5, 6, 10]], 
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]], 
    [[1, 2, 5, 6]], 
    [[2, 3, 5, 6], [1, 5, 6, 10]], 
    [[1, 4, 5, 6], [1, 5, 6, 9], [4, 5, 6, 9], [1, 4, 5, 9]], 
    [[1, 2, 6, 7], [2, 5, 6, 9]]  
]

class Piece:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.rotation = 0
        self.color = self.shape_idx + 1
        self.x = 3
        self.y = 0

    def get_blocks(self, x_offset=0, y_offset=0):
        shape = SHAPES[self.shape_idx][self.rotation % len(SHAPES[self.shape_idx])]
        return [(self.x + b % 4 + x_offset, self.y + b // 4 + y_offset) for b in shape]

class TetrisGame:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Courier", 24, bold=True)
        self.font_ui = pygame.font.SysFont("Courier", 18, bold=True)
        self.font_go = pygame.font.SysFont("Courier", 28, bold=True)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(10)] for _ in range(20)]
        self.score = 0
        self.game_over = False
        self.current_piece = Piece()
        self.next_piece = Piece()
        self.fall_time = 0
        self.fall_speed = 500 

    def check_collision(self, piece, x_off=0, y_off=0):
        for bx, by in piece.get_blocks(x_off, y_off):
            if bx < 0 or bx >= 10 or by >= 20:
                return True
            if by >= 0 and self.grid[by][bx]:
                return True
        return False

    def move(self, dx, dy):
        if self.game_over: return False
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate(self):
        if self.game_over: return
        self.current_piece.rotation += 1
        if self.check_collision(self.current_piece):
            self.current_piece.rotation -= 1

    def get_ghost_y(self):
        dy = 0
        while not self.check_collision(self.current_piece, 0, dy + 1):
            dy += 1
        return dy

    def hard_drop(self):
        if self.game_over: return
        dy = self.get_ghost_y()
        self.current_piece.y += dy
        self.lock_piece()

    def lock_piece(self):
        for bx, by in self.current_piece.get_blocks():
            if by >= 0:
                self.grid[by][bx] = self.current_piece.color
        
        cleared = 0
        for r in range(20 - 1, -1, -1):
            if 0 not in self.grid[r]:
                del self.grid[r]
                self.grid.insert(0, [0 for _ in range(10)])
                cleared += 1
        
        if cleared > 0:
            self.score += [0, 100, 300, 500, 800][cleared]

        self.current_piece = self.next_piece
        self.next_piece = Piece()

        if self.check_collision(self.current_piece):
            self.game_over = True

    def draw(self):
        screen.fill(BG_COLOR)

        # Draw main grid layout
        for r in range(20):
            pygame.draw.line(screen, GRID_COLOR, (0, r * BLOCK_SIZE), (GRID_WIDTH, r * BLOCK_SIZE))
        for c in range(10):
            pygame.draw.line(screen, GRID_COLOR, (c * BLOCK_SIZE, 0), (c * BLOCK_SIZE, GRID_HEIGHT))

        # Draw locked blocks
        for r in range(20):
            for c in range(10):
                if self.grid[r][c]:
                    pygame.draw.rect(screen, NEON_COLORS[self.grid[r][c]], (c*BLOCK_SIZE, r*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
                    pygame.draw.rect(screen, (255, 255, 255), (c*BLOCK_SIZE, r*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1), 1)

        if not self.game_over:
            # Ghost piece rendering utilizing an alpha surface layer
            ghost_dy = self.get_ghost_y()
            ghost_surface = pygame.Surface((BLOCK_SIZE-1, BLOCK_SIZE-1), pygame.SRCALPHA)
            ghost_surface.fill(GHOST_ALPHA_COLOR)
            
            for bx, by in self.current_piece.get_blocks(0, ghost_dy):
                if by >= 0:
                    screen.blit(ghost_surface, (bx * BLOCK_SIZE, by * BLOCK_SIZE))
                    pygame.draw.rect(screen, (58, 58, 90), (bx*BLOCK_SIZE, by*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1), 1)

            # Draw active falling piece
            for bx, by in self.current_piece.get_blocks():
                if by >= 0:
                    pygame.draw.rect(screen, NEON_COLORS[self.current_piece.color], (bx*BLOCK_SIZE, by*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
                    pygame.draw.rect(screen, (255, 255, 255), (bx*BLOCK_SIZE, by*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1), 1)

        # Draw Sidebar UI text partitions
        sb_x = GRID_WIDTH + 15
        
        title_surf = self.font_title.render("NEON", True, (0, 255, 255))
        title_surf2 = self.font_title.render("TETRIS", True, (0, 255, 255))
        screen.blit(title_surf, (sb_x + 20, 20))
        screen.blit(title_surf2, (sb_x + 10, 50))

        score_title = self.font_ui.render("SCORE", True, (58, 58, 90))
        score_val = self.font_ui.render(str(self.score), True, (255, 0, 85))
        screen.blit(score_title, (sb_x + 25, 120))
        screen.blit(score_val, (sb_x + 25, 145))

        next_title = self.font_ui.render("NEXT", True, (58, 58, 90))
        screen.blit(next_title, (sb_x + 30, 210))

        # Box outline container for the preview
        pygame.draw.rect(screen, GRID_COLOR, (GRID_WIDTH + 25, 240, 130, 130), 2)
        
        # Render the previewed piece centered inside the box
        next_shape = SHAPES[self.next_piece.shape_idx][0]
        p_box_size = 22
        for b in next_shape:
            bx, by = b % 4, b // 4
            x_offset = (130 - (4 * p_box_size)) // 2 if self.next_piece.shape_idx == 0 else (130 - (3 * p_box_size)) // 2
            y_offset = (130 - (2 * p_box_size)) // 2 if self.next_piece.shape_idx == 0 else (130 - (3 * p_box_size)) // 2
            
            px = GRID_WIDTH + 25 + x_offset + (bx * p_box_size)
            py = 240 + y_offset + (by * p_box_size)
            pygame.draw.rect(screen, NEON_COLORS[self.next_piece.color], (px, py, p_box_size - 1, p_box_size - 1))
            pygame.draw.rect(screen, (255, 255, 255), (px, py, p_box_size - 1, p_box_size - 1), 1)

        # Game Over Screen Layer
        if self.game_over:
            # Fills full surface with dim filter overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 220)) 
            screen.blit(overlay, (0, 0))

            go_text1 = self.font_go.render("GAME OVER", True, (255, 0, 85))
            go_text2 = self.font_ui.render("Press 'Y' to Restart", True, (0, 255, 255))
            
            screen.blit(go_text1, (WINDOW_WIDTH // 2 - go_text1.get_width() // 2, WINDOW_HEIGHT // 2 - 40))
            screen.blit(go_text2, (WINDOW_WIDTH // 2 - go_text2.get_width() // 2, WINDOW_HEIGHT // 2 + 10))

        pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.fall_time += clock.get_rawtime()
            clock.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.reset_game()
                    
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()

            if not self.game_over:
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    if not self.move(0, 1):
                        self.lock_piece()

            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
