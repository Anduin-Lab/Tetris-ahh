import tkinter as tk
import random


ROW, COL = 20, 10
BLOCK_SIZE = 30
WIDTH, HEIGHT = COL * BLOCK_SIZE, ROW * BLOCK_SIZE

BG_COLOR = "#0D0D1A"       
GRID_COLOR = "#1A1A3A"     
SHADOW_COLOR = "#3A3A5A"   

NEON_COLORS = [
    None,
    "#00FFFF",
    "#0000FF",
    "#FF9900",
    "#FFFF00",
    "#00FF00",
    "#9900FF",
    "#FF0055"
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
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Tetris")
        self.root.configure(bg=BG_COLOR)

        self.grid = [[0 for _ in range(COL)] for _ in range(ROW)]
        self.score = 0
        self.game_over = False
        self.current_piece = Piece()

        self.setup_ui()
        self.bind_controls()
        self.game_loop()

    def setup_ui(self):
        self.title_label = tk.Label(self.root, text="NEON TETRIS", font=("Courier", 20, "bold"), fg="#00FFFF", bg=BG_COLOR)
        self.title_label.pack(pady=5)

        self.score_label = tk.Label(self.root, text="SCORE: 0", font=("Courier", 16, "bold"), fg="#FF0055", bg=BG_COLOR)
        self.score_label.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=BG_COLOR, highlightbackground=GRID_COLOR, highlightthickness=2)
        self.canvas.pack(padx=20, pady=10)

    def bind_controls(self):
        self.root.bind("<Left>", lambda e: self.move(-1, 0))
        self.root.bind("<Right>", lambda e: self.move(1, 0))
        self.root.bind("<Down>", lambda e: self.move(0, 1))
        self.root.bind("<Up>", lambda e: self.rotate())
        self.root.bind("<space>", lambda e: self.hard_drop())

    def check_collision(self, piece, x_off=0, y_off=0):
        for bx, by in piece.get_blocks(x_off, y_off):
            if bx < 0 or bx >= COL or by >= ROW:
                return True
            if by >= 0 and self.grid[by][bx]:
                return True
        return False

    def move(self, dx, dy):
        if self.game_over: return
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            self.draw()
            return True
        return False

    def rotate(self):
        if self.game_over: return
        self.current_piece.rotation += 1
        if self.check_collision(self.current_piece):
            self.current_piece.rotation -= 1
        self.draw()

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
        
        cleared = self.clear_lines()
        if cleared > 0:
            self.score += [0, 100, 300, 500, 800][cleared] 
            self.score_label.config(text=f"SCORE: {self.score}")

        self.current_piece = Piece()
        if self.check_collision(self.current_piece):
            self.game_over = True
            self.canvas.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER", fill="#FF0055", font=("Courier", 24, "bold"))
        self.draw()

    def clear_lines(self):
        cleared = 0
        for r in range(ROW - 1, -1, -1):
            if 0 not in self.grid[r]:
                del self.grid[r]
                self.grid.insert(0, [0 for _ in range(COL)])
                cleared += 1
        return cleared

    def draw(self):
        self.canvas.delete("all")

        for r in range(ROW):
            self.canvas.create_line(0, r*BLOCK_SIZE, WIDTH, r*BLOCK_SIZE, fill=GRID_COLOR)
        for c in range(COL):
            self.canvas.create_line(c*BLOCK_SIZE, 0, c*BLOCK_SIZE, HEIGHT, fill=GRID_COLOR)

        for r in range(ROW):
            for c in range(COL):
                if self.grid[r][c]:
                    color = NEON_COLORS[self.grid[r][c]]
                    self.canvas.create_rectangle(c*BLOCK_SIZE, r*BLOCK_SIZE, (c+1)*BLOCK_SIZE, (r+1)*BLOCK_SIZE, fill=color, outline="#FFFFFF", width=1)

        if not self.game_over:
            ghost_dy = self.get_ghost_y()
            for bx, by in self.current_piece.get_blocks(0, ghost_dy):
                if by >= 0:
                    self.canvas.create_rectangle(bx*BLOCK_SIZE+2, by*BLOCK_SIZE+2, (bx+1)*BLOCK_SIZE-2, (by+1)*BLOCK_SIZE-2, outline=SHADOW_COLOR, width=2, dash=(4, 2))

            for bx, by in self.current_piece.get_blocks():
                if by >= 0:
                    color = NEON_COLORS[self.current_piece.color]
                    self.canvas.create_rectangle(bx*BLOCK_SIZE, by*BLOCK_SIZE, (bx+1)*BLOCK_SIZE, (by+1)*BLOCK_SIZE, fill=color, outline="#FFFFFF", width=1)

    def game_loop(self):
        if not self.game_over:
            if not self.move(0, 1):
                self.lock_piece()
            self.root.after(500, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = TetrisGame(root)
    root.mainloop()
