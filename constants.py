import arcade
from pyglet.graphics import Batch

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Battleship Setup" 
SQUARE_SIZE = 50
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
player1_board = {}
player2_board = {}
blank_board = {}
for letter in letters:
    for number in range(1, 11):
        player1_board[letter+str(number)] = 0
        player2_board[letter+str(number)] = 0
        blank_board[letter+str(number)] = 0


def createShip(number_of_parts, start_x, start_y, horizontal=True):
    sprites_list = arcade.SpriteList()
    for i in range(number_of_parts):
        if i == 0:
            sprite = arcade.Sprite('Pictures/End.png', angle=0 if horizontal else 90)
        elif i == number_of_parts - 1:
            sprite = arcade.Sprite('Pictures/End.png', angle=180 if horizontal else 90)
        else:
            sprite = arcade.Sprite('Pictures/Middle.png', angle=0 if horizontal else 90)

        sprite.width = SQUARE_SIZE
        sprite.height = 30 

        if horizontal:
            sprite.center_x = start_x + i * SQUARE_SIZE + SQUARE_SIZE / 2
            sprite.center_y = start_y + SQUARE_SIZE / 2
        else:
            sprite.center_x = start_x + SQUARE_SIZE / 2
            sprite.center_y = start_y + i * SQUARE_SIZE + SQUARE_SIZE / 2

        sprites_list.append(sprite)
    return sprites_list

def on_draw(current_view, player_board):
    grid_x_offset = current_view.grid_x_offset
    grid_y_offset = current_view.grid_y_offset

    # Choose which board to draw based on current_view.player
    board = player_board

    # Draw grid squares
    for key, value in board.items():
        row = ord(key[0]) - ord('A')
        col = int(key[1:]) - 1
        state = value

        left = grid_x_offset + col * SQUARE_SIZE
        bottom = grid_y_offset + row * SQUARE_SIZE

        if state == 0 or state == 1:
            color = arcade.color.WHITE
        elif state == 2:
            color = arcade.color.RED
        elif state == 3:
            color = arcade.color.GREEN
        elif state == 4:
            color = arcade.color.PURPLE
        arcade.draw_lrbt_rectangle_outline(left, left + SQUARE_SIZE, bottom, bottom+SQUARE_SIZE, arcade.color.BLACK, 2)
        arcade.draw_lrbt_rectangle_filled(left, left + SQUARE_SIZE, bottom, bottom + SQUARE_SIZE, color)
    # Draw labels
    for i in range(10):
        arcade.draw_text(
            letters[i],
            grid_x_offset + SQUARE_SIZE * i + SQUARE_SIZE / 2,
            grid_y_offset - 20,
            arcade.color.BLACK,
            12,
            anchor_x="center"
        )
        arcade.draw_text(
            str(i + 1),
            grid_x_offset - 20,
            grid_y_offset + SQUARE_SIZE * i + SQUARE_SIZE / 2,
            arcade.color.BLACK,
            12,
            anchor_y="center"
        )

    current_view.all_sprites.draw()
