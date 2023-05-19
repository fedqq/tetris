from tkinter import *
from random import randint
from tkextrafont import Font
from copy import copy, deepcopy

ROWS = 15
COLUMNS = 10
SPACE_SIZE = 50
DELAY = 300
DOWN_DELAY = 40

DEBUG = False

class Tetris:
    def init(self):
        
        #Starts the game for the first time, creating the window, the variables and the canvas

        self.window = Tk()
        self.window.title("Tetris")
        self.window.resizable(False, False)
        self.window.configure(bg = "#000000")

        self.canvas = Canvas(self.window, bg = "#000000", width = COLUMNS * SPACE_SIZE, height = ROWS * SPACE_SIZE, bd = 0, relief = RAISED)
        self.canvas.pack()

        self.reset_block_types()
        self.placed_squares = []
        self.blocks         = []
        self.keys = {'right': False, 'left': False}
        self.delay = DELAY
        self.first_time     = True
        self.space_clicked  = False
        self.lost           = False
        self.paused         = False
        self.record         = 0
        self.score          = 0
        self.label = Label(self.window, text = "Score: {}".format(self.score), font = ("Arial", 30), bg = "#000000", fg = "#ffffff")
        self.label.pack()
        self.best_label = Label(self.window, text = "Record: {}".format(self.record), font = ("Arial", 30), bg = "#000000", fg = "#ffffff")
        self.best_label.pack()

        self.window.bind("<Right>",             lambda e: self.press_key(right = True))
        self.window.bind("<KeyRelease-Right>",  lambda e: self.press_key(right = True, release = True))
        self.window.bind("<Left>",              lambda e: self.press_key(right = False))
        self.window.bind("<KeyRelease-Left>",   lambda e: self.press_key(right = False, release = True))
        self.window.bind("<Up>",                lambda e: self.turn())
        self.window.bind("<Down>",              lambda e: self.down_press(press = True))
        self.window.bind("<KeyRelease-Down>",   lambda e: self.down_press(press = False))
        self.window.bind("<Escape>",            lambda e: self.pause())
        self.window.bind("<space>",             lambda e: self.hard_drop())
        self.window.bind("<KeyRelease-space>",  lambda e: self.space_release())
        self.window.bind("<Button-1>",          lambda e: self.click())

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        best_file = open("score.txt", 'r')
        high_score = best_file.read()
        if high_score != '':
            self.record = int(high_score)
        best_file.close()
        self.best_label.configure(text = "Record: {}".format(self.record))

        self.new_block()
        self.draw_loop()
        self.check_move()

        self.window.mainloop()
        
    def press_key(self, right = False, release = False):
        if right:
            self.keys['right'] = not release
        else:
            self.keys['left'] = not release
    
    def check_move(self):
        if self.keys['right']:
            self.move(right = True)
        if self.keys['left']:
            self.move(right = False)
        self.window.after(50, self.check_move)
        
    def space_release(self):
        self.space_clicked = False

    def click(self):
        if self.lost:
            self.restart()

    def lose(self):
        self.lost = True
        self.window.after_cancel(self.after)
        self.canvas.delete("all")
        self.label.destroy()
        self.best_label.destroy()

        middle = (COLUMNS * SPACE_SIZE) / 2
        self.canvas.create_text(    
                                    (COLUMNS * SPACE_SIZE) / 2, 
                                    (ROWS * SPACE_SIZE) / 2, 
                                    text = 'Score: {}\nRecord: {}\nClick To Restart'.format(self.score, self.record), 
                                    fill = 'white', 
                                    font = ('Rockwell Nova Extra Bold', 30), 
                                    justify = CENTER
                                )
    
    def restart(self):

        self.reset_block_types()
        self.placed_squares = []
        self.blocks = []
        self.delay = DELAY
        self.first_time = True
        self.lost = False
        self.record = 0
        self.score = 0
        self.label = Label(self.window, text = "Score: {}".format(self.score), font = ("Arial", 30), bg = "#000000", fg = "#ffffff")
        self.label.pack()
        self.best_label = Label(self.window, text = "Record: {}".format(self.record), font = ("Arial", 30), bg = "#000000", fg = "#ffffff")
        self.best_label.pack()
        self.paused = False

        self.new_block()
        self.draw_loop()

    def increase_score(self, amount):
        self.score += amount
        if self.score > self.record:
            self.record = self.score
            self.best_label.configure(text = "Record: {}".format(self.record))
        self.label.configure(text = "Score: {}".format(self.score))

    def down_press(self, press):
        if self.lost:
            return

        self.window.after_cancel(self.after)

        if press:
            self.delay = DOWN_DELAY
        else:
            self.delay = DELAY

        self.draw_loop()
            
    def move(self, right):
        if self.lost:
            return
        if right:
            self.blocks[-1].move_right()
        else:
            self.blocks[-1].move_left()
        
        self.draw()

    def on_close(self):
        open('score.txt', 'w').close()
        file = open("score.txt", 'w')
        file.write(str(self.record))
        file.close()
        self.lose()
        self.window.destroy()

    def get_block_types(self):
        return self.block_types

    def hard_drop(self):
        if self.space_clicked:
            return
        self.space_clicked = True
        if self.lost:
            return
        while self.blocks[-1].placed == False:
            self.increase_score(2)
            self.blocks[-1].move_down(self, delay = False)
            self.blocks[-1].check_placeable()
            if self.blocks[-1].placeable:
                self.blocks[-1].place()
                
        self.check_rows()
        self.draw()
        
        
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

        if not self.lost:
            self.canvas.delete("all")
        if self.delay == DOWN_DELAY:
            self.increase_score(1)

        if self.blocks[-1].placed:
            if not self.lost:
                self.new_block()
        self.blocks[-1].move_down(self)
        for block in self.blocks:
            for square in block.squares:
                x = square[0] * SPACE_SIZE
                y = square[1] * SPACE_SIZE
                if not self.lost:
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = block.color, outline = block.color)
            
        game.check_rows()
        if not self.lost:
            self.after = self.window.after(self.delay, self.draw_loop)

    def check_rows(self):
        found_row = 0
        found_rows = 0
        num = 0
        for a in range(0, ROWS):
            failed = False
            for column in range(0, COLUMNS):
                if [column, a] not in self.placed_squares:
                    failed = True

            if not failed:
                self.remove_row(a)
                found_rows += 1

        if found_rows == 1:
            self.increase_score(40)
        elif found_rows == 2:
            self.increase_score(100)
        elif found_rows == 3:
            self.increase_score(300)
        elif found_rows == 4:
            self.increase_score(1200)

    def remove_row(self, row):

        self.placed_squares = [square for square in self.placed_squares if square[1] != row]

        for block in self.blocks:
            block.remove_row(row)
            
        for square in self.placed_squares:
            if square[1] < row:
                square[1] += 1

        self.draw()

    def pause(self):
        if self.paused:
            self.paused = False
            self.draw_loop()
        else:
            self.paused = True
            self.window.after_cancel(self.after)
            self.draw()

    def draw(self):
        if self.lost:
            return
        self.canvas.delete("all")
        num = 0
        if self.blocks[-1].placed:
            self.new_block()
        for block in self.blocks:
            for square in block.squares:
                num += 1
                x = square[0] * SPACE_SIZE
                y = square[1] * SPACE_SIZE
                if not self.lost:
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = block.color, outline = block.color)

game = Tetris()

class Block:
    
    def __init__(self):

        self.placed = False
        self.x_offset = 3
        self.y_offset = -2
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
            if [a[0] + 3, a[1] - 2] in game.placed_squares:
                game.lose()
            self.squares.append([a[0] + 3, a[1] - 2])

        self.check_placeable()

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
        new_squares = [[square[0] + self.x_offset, square[1] + self.y_offset] for square in new_config]

        first_squares = new_squares
        second_squares = [[a[0] - 1, a[1]] for a in new_squares]
        third_squares = [[a[0] + 1, a[1]] for a in new_squares]

        #0 means passed, 1 means failed
        tests = [0, 0, 0]

        for c in first_squares:
            if c in game.placed_squares or c[0] not in range(0, COLUMNS) or c[1] >= ROWS:
                tests[0] = 1
                break

        if tests[0] == 1:
            for d in second_squares:
                if d in game.placed_squares or d[0] not in range(0, COLUMNS) or d[1] >= ROWS:
                    tests[1] = 1
                    break
        
        if tests[1] == 1:
            for e in third_squares:
                if e in game.placed_squares or e[0] not in range(0, COLUMNS) or e[1] >= ROWS:
                    tests[2] = 1
                    break

        if tests[0] == 0:
            self.squares = new_squares
        elif tests[1] == 0:
            self.squares = second_squares
        elif tests[2] == 0:
            self.squares = third_squares
        
        self.current_config = new_config_id
        game.draw()

    def check_placeable(self):
        self.placeable = False
        for square in self.squares:
            if square[1] + 1 == ROWS or [square[0], square[1] + 1] in game.placed_squares:
                self.placeable = True
                return

    def place(self):
        self.check_placeable()
        if self.placeable:
            game.placed_squares += deepcopy(self.squares)
            self.placed = True

    def move_down(self, game: Tetris, delay = True):

        self.check_placeable()

        if self.placeable:
            if delay:
                game.window.after(500, self.place)
            else:
                self.placed = True
                self.place()
        else:
            self.y_offset += 1
            self.squares = [[square[0], square[1] + 1] for square in self.squares]

    def move_right(self):
        if self.placed:
            return
        for sq in self.squares:
            if sq[0] + 1 == 10 or [sq[0] + 1, sq[1]] in game.placed_squares:
                    return

        self.x_offset += 1
        self.squares = [[square[0] + 1, square[1]] for square in self.squares]
        self.check_placeable()

    def move_left(self):
        if self.placed:
            return
        for sq in self.squares:
            if sq[0] - 1 == -1 or [sq[0] - 1, sq[1]] in game.placed_squares:
                    return

        self.x_offset -=1
        for square in self.squares:
            square[0] -= 1
        self.check_placeable()
        
    def remove_row(self, row):
        self.squares = [b for b in self.squares if b[1] != row]
        for sq in self.squares:
            if sq[1] < row:
                sq[1] += 1

game.init()