from tkinter import *
from random import randint

ROWS = 15
COLUMNS = 10
SPACE_SIZE = 50
DELAY = 300
DOWN_DELAY = 40

DEBUG = False

class Tetris:
    def init(self):
        self.window = Tk()
        self.window.title("Tetris")
        self.window.resizable(False, False)
        self.window.configure(bg = "#000000")

        self.canvas = Canvas(self.window, bg = "#000000", width = COLUMNS * SPACE_SIZE, height = ROWS * SPACE_SIZE, bd = 0, relief = RAISED)
        self.canvas.pack()

        self.reset_block_types()
        self.placed_squares = []
        self.blocks = []
        self.delay = DELAY
        self.first_time = True
        self.score = 0
        self.label = Label(self.window, text = "Score: {}".format(self.score), font = ("Arial", 30), bg = "#000000", fg = "#ffffff")
        self.label.pack()
        self.paused = False

        self.window.bind("<Right>",             lambda e: self.move(right = True))
        self.window.bind("<Left>",              lambda e: self.move(right = False))
        self.window.bind("<Up>",                lambda e: self.turn())
        self.window.bind("<Down>",              lambda e: self.down_press(press = True))
        self.window.bind("<KeyRelease-Down>",   lambda e: self.down_press(press = False))
        self.window.bind("<Escape>",            lambda e: self.pause())

        self.new_block()
        self.draw_loop()

        self.window.mainloop()

    def increase_score(self, amount):
        self.score += amount
        self.label.configure(text = "Score: {}".format(self.score))

    def down_press(self, press):

        self.window.after_cancel(self.after)

        if press:
            self.delay = DOWN_DELAY
        else:
            self.delay = DELAY

        self.draw_loop()
            
    def move(self, right):
        if right:
            self.blocks[-1].move_right()
        else:
            self.blocks[-1].move_left()
        
        self.draw_single()

    def get_block_types(self):
        return self.block_types

    def reset_block_types(self):
        self.block_types = [    [   [[2, 1], [1, 2], [2, 2], [1, 3]], 
                                    [[1, 1], [2, 1], [2, 2], [3, 2]], "#3877FF", "Z"], 

                                [   [[1, 1], [1, 2], [2, 2], [2, 3]],
                                    [[2, 1], [3, 1], [1, 2], [2, 2]], "#FFE138", 'S'],

                                [   [[1, 1], [1, 2], [2, 2], [2, 1]], 
                                    [[1, 1], [1, 2], [2, 2], [2, 1]], "#0DC2FF", 'square'], 

                                [   [[1, 1], [2, 1], [3, 1], [4, 1]], 
                                    [[1, 0], [1, 1], [1, 2], [1, 3]], "#0DFF72", 'long'],

                                [   [[1, 2], [2, 2], [3, 2], [3, 1]], 
                                    [[1, 1], [1, 2], [1, 3], [2, 3]], 
                                    [[1, 1], [2, 1], [3, 1], [1, 2]], 
                                    [[1, 1], [2, 1], [2, 2], [2, 3]], "#F538FF", 'L'], 

                                [   [[2, 0], [2, 1], [2, 2], [1, 2]], 
                                    [[1, 1], [1, 2], [2, 2], [3, 2]], 
                                    [[1, 0], [1, 1], [1, 2], [2, 0]], 
                                    [[1, 1], [2, 1], [3, 1], [3, 2]], "#FF8E0D", 'J'], 

                                [   [[1, 1], [2, 1], [3, 1], [2, 2]], 
                                    [[2, 1], [1, 2], [2, 2], [2, 3]], 
                                    [[2, 1], [1, 2], [2, 2], [3, 2]], 
                                    [[1, 1], [1, 2], [1, 3], [2, 2]], "#FF0D72", 'T']
                            ]

    def new_block(self):
        if not self.first_time:
            game.increase_score(10)
        else:
            self.first_time = False
        self.reset_block_types()
        self.blocks.append(Block())

    def turn(self):
        if self.blocks[-1].block_type != 'square' and not self.blocks[-1].placed:
            self.blocks[-1].turn()

    def draw_loop(self):
        self.canvas.delete("all")
        num = 0
        if self.delay == DOWN_DELAY:
            self.increase_score(1)
        
        found_row = 0
        num = 0
        for a in range(ROWS):

            num = len([p for p in self.placed_squares if p[1] == a])
            if num == COLUMNS:
                found_row = a
                self.remove_row(found_row)


        if self.blocks[-1].placed:
            self.new_block()
        self.blocks[-1].move_down()
        for block in self.blocks:
            for square in block.squares:
                x = square[0] * SPACE_SIZE
                y = square[1] * SPACE_SIZE
                self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = block.color, outline = block.color)
        
        self.after = self.window.after(self.delay, self.draw_loop)
        print(self.score)

    def pause(self):
        if self.paused:
            self.paused = False
            self.draw_loop()
        else:
            self.paused = True
            self.window.after_cancel(self.after)
            self.draw_single()


    def draw_placed(self):
        if not DEBUG:
            return
        for square in self.placed_squares:
            x = square[0] * SPACE_SIZE
            y = square[1] * SPACE_SIZE
            self.canvas.create_rectangle(x + 5, y + 5, x + SPACE_SIZE - 5, y + SPACE_SIZE - 5, fill = "#FF0D72")

    def draw_single(self):
        self.canvas.delete("all")
        num = 0
        if self.blocks[-1].placed:
            self.new_block()
        for block in self.blocks:
            for square in block.squares:
                num += 1
                x = square[0] * SPACE_SIZE
                y = square[1] * SPACE_SIZE
                self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = block.color, outline = block.color)

        self.draw_placed()

    def remove_row(self,  row):

        for block in self.blocks:
            block.remove_row(row)

        self.placed_squares = [b for b in self.placed_squares if b[1] != row]

        for b in self.placed_squares:
            if b[1] < row:
                b[1] += 1

        self.draw_single()

game = Tetris()

class Block:
    
    def __init__(self):

        self.placed = False
        self.x_offset = 0
        self.y_offset = 0
        self.squares = []
        self.wait_place = False
        self.placed = False

        self.index = randint(0, len(game.block_types) - 1)
        self.block = game.get_block_types()[self.index]
        self.color = self.block[-2]
        self.block_type = self.block[-1]
        self.turn_configs = self.block[:-2]
        self.current_config = 0
        
        for square in self.turn_configs[0]:
            a = square
            self.squares.append([a[0], a[1] - 2])

    def turn(self):

        game.reset_block_types()
        self.block = game.get_block_types()[self.index]
        self.turn_configs = self.block[:-2]

        new_config_id = self.current_config
        if self.current_config == len(self.turn_configs) - 1:
            new_config_id = 0
        else:
            new_config_id += 1

        new_config = self.turn_configs[new_config_id]
        new_squares = []
        for square in new_config:
            new_squares.append([square[0] + self.x_offset, square[1] + self.y_offset - 2])

        for sq in new_squares:
            if sq in game.placed_squares or sq[0] not in range(0, COLUMNS) or sq[1] >= ROWS:
                return

        self.current_config = new_config_id
        self.squares = new_squares
        game.draw_single()

    def place(self):
        self.placed = True
        self.wait_place = False

    def move_down(self, check = True):
        if check:
            for sq in self.squares:
                if sq[1] + 1 == 15 or [sq[0], sq[1] + 1] in game.placed_squares:
                    self.wait_place = True
                    game.window.after(500, lambda: self.place())
            if self.placed or self.wait_place:
                for square in self.squares:
                    if [square[0], square[1]] not in game.placed_squares:
                        game.placed_squares.append([square[0], square[1]])
                return

        if not self.wait_place:
            self.y_offset += 1
            for squ in self.squares:
                squ[1] = squ[1] + 1

    def move_right(self):
        if self.placed:
            return
        for sq in self.squares:
            if sq[0] + 1 == 10 or [sq[0] + 1, sq[1]] in game.placed_squares:
                    return

        self.x_offset += 1
        for square in self.squares:
            square[0] += 1

    def move_left(self):
        if self.placed:
            return
        for sq in self.squares:
            if sq[0] - 1 == -1 or [sq[0] - 1, sq[1]] in game.placed_squares:
                    return

        self.x_offset -=1
        for square in self.squares:
            square[0] -= 1

    def remove_row(self, row):
        self.squares = [b for b in self.squares if b[1] != row]
        for sq in self.squares:
            if sq[1] < row:
                sq[1] += 1



game.init()