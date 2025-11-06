import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Battleship Setup"
SQUARE_SIZE = 50
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']


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


class BattleshipSetup(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)

        self.grid_x_offset = (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2
        self.grid_y_offset = (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2

        self.all_sprites = arcade.SpriteList()
        self.carrier = createShip(5, 20, 20)
        self.battleship = createShip(4, 20, 100)
        self.submarine = createShip(3, 20, 180)
        self.cruiser = createShip(3, 20, 260)
        self.destroyer = createShip(2, 20, 340)

        for ship in [self.carrier, self.battleship, self.submarine, self.cruiser, self.destroyer]:
            self.all_sprites.extend(ship)

        self.selected_ship = None
        self.horizontal = True
        self.anchor = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def on_draw(self):
        self.clear()

        for row in range(10):
            for col in range(10):
                left = self.grid_x_offset + SQUARE_SIZE * col
                bottom = self.grid_y_offset + SQUARE_SIZE * row
                arcade.draw_lbwh_rectangle_outline(left, bottom, SQUARE_SIZE, SQUARE_SIZE, arcade.color.BLACK, 2)

        self.all_sprites.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for ship in [self.carrier, self.battleship, self.submarine, self.cruiser, self.destroyer]:
            for part in ship:
                if part.collides_with_point((x, y)):
                    self.selected_ship = ship
                    self.anchor = ship[0]

                    if self.horizontal:
                        ship_left_edge = min(p.center_x - p.width / 2 for p in ship)
                        self.drag_offset_x = ship_left_edge - x
                        self.drag_offset_y = self.anchor.center_y - y
                    else:
                        ship_top_edge = max(p.center_y + p.height / 2 for p in ship)
                        self.drag_offset_x = self.anchor.center_x - x
                        self.drag_offset_y = ship_top_edge - y
                    return

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.selected_ship:
            return

        if self.horizontal:
            start_x = x + self.drag_offset_x + self.selected_ship[0].width / 2
            start_y = y + self.drag_offset_y
            for i, part in enumerate(self.selected_ship):
                part.center_x = start_x + i * SQUARE_SIZE
                part.center_y = start_y
        else:
            start_x = x + self.drag_offset_x
            start_y = y + self.drag_offset_y - self.selected_ship[0].height / 2
            for i, part in enumerate(self.selected_ship):
                part.center_x = start_x
                part.center_y = start_y - i * SQUARE_SIZE

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.selected_ship:
            return

        if self.horizontal:
            left_edge = min(p.center_x - p.width / 2 for p in self.selected_ship)
            col = round((left_edge - self.grid_x_offset) / SQUARE_SIZE)
            row = round((self.selected_ship[0].center_y - self.grid_y_offset) / SQUARE_SIZE)
        else:
            top_edge = max(p.center_y + p.height / 2 for p in self.selected_ship)
            col = round((self.selected_ship[0].center_x - self.grid_x_offset) / SQUARE_SIZE)
            row = round((top_edge - self.grid_y_offset) / SQUARE_SIZE)

        col = max(0, min(9, col))
        row = max(0, min(9, row))

        start_x = self.grid_x_offset + col * SQUARE_SIZE + SQUARE_SIZE / 2
        start_y = self.grid_y_offset + row * SQUARE_SIZE + SQUARE_SIZE / 2

        for i, part in enumerate(self.selected_ship):
            if self.horizontal:
                part.center_x = start_x + i * SQUARE_SIZE
                part.center_y = start_y
            else:
                part.center_x = start_x
                part.center_y = start_y - i * SQUARE_SIZE

        self.selected_ship = None

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and self.selected_ship:
            self.horizontal = not self.horizontal
            anchor_x = self.anchor.center_x
            anchor_y = self.anchor.center_y

            for i, part in enumerate(self.selected_ship):
                if i == 0:
                    part.angle = 0 if self.horizontal else 90
                elif i == len(self.selected_ship) - 1:
                    part.angle = 180 if self.horizontal else 270
                else:
                    part.angle = 0 if self.horizontal else 90

                if self.horizontal:
                    part.center_x = anchor_x + i * SQUARE_SIZE
                    part.center_y = anchor_y
                else:
                    part.center_x = anchor_x
                    part.center_y = anchor_y - i * SQUARE_SIZE


def main():
    window = BattleshipSetup()
    arcade.run()


if __name__ == "__main__":
    main()
