import arcade
from setup import SetupView
from battle import BattleView
from hotseat_other_screens import WaitingView, GameOverView
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, player1_board, player2_board, SQUARE_SIZE, blank_board


class HotseatGame(arcade.Window):
    """Main Hotseat class controlling the flow between setup and battle views.

    This class implements the Hotseat mode flow:
      - Manages player setup and battles
      - Tracks board and ship states for both players
      - Handles attack logic including hits, misses, and ship destruction
      - Implements turn switching and player waiting screens
      - Correctly detects game end states and displays the end screen
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Battleship Hotseat")

        # Player 1 and player 2 ship data (lists of ships with part coords and hit flags)
        self.player1_setup_data = None  
        self.player2_setup_data = None  

        # Player boards, copied to ensure game-specific mutable state per player
        self.player1_board = dict(player1_board)
        self.player2_board = dict(player2_board)

        # Current player who is either placing ships or attacking (1 or 2)
        self.current_player = 1

        # Begin game flow by launching player 1's ship setup view
        self.show_player_setup(self.current_player)

    # -------------------- View Management --------------------
    def show_player_setup(self, player_number):
        """Display the SetupView allowing the given player to place their ships.

        Args:
            player_number (int): The player (1 or 2) placing ships.
        """
        board = self.player1_board if player_number == 1 else self.player2_board
        setup_view = SetupView(player_number, self, board)
        self.show_view(setup_view)

    def show_player_battle(self, player_number):
        """Display the BattleView for the given player to conduct attacks.

        Args:
            player_number (int): The player attacking (1 or 2).
        """
        # Player's ships and board for personal view and opponent's board for attack view
        setup_data = self.player1_setup_data if player_number == 1 else self.player2_setup_data
        your_board = self.player1_board if player_number == 1 else self.player2_board
        opponents_board = self.player2_board if player_number == 1 else self.player1_board

        battle_view = BattleView(player_number, self, setup_data, your_board, opponents_board)
        self.show_view(battle_view)

    def show_waiting_screen(self, next_player=None):
        """Display the WaitingView to enforce turn switching for hotseat play.

        Args:
            next_player (int, optional): The player who will be next to play.
                Defaults to the current player (defender).
        """
        if next_player is None:
            next_player = self.current_player  # Default to defender's turn
        waiting_view = WaitingView(self, next_player)
        self.show_view(waiting_view)
    
    def show_end_screen(self, winning_player):
        """Display the GameOverView announcing the winner of the game.

        Args:
            winning_player (int): The player number who won the game.
        """
        gameover_view = GameOverView(self, winning_player)
        self.show_view(gameover_view)

    # -------------------- Setup Completion Callback --------------------
    def on_setup_finished(self, player_number, ship_data, board):
        """Called when a player finishes placing ships in SetupView.

        Converts ship data to mutable form and saves it along with the player's board.
        Advances game flow to the next player or to battle start if both players finished.

        Args:
            player_number (int): Player who completed setup.
            ship_data (list): Ship placement data, list of ships with parts.
            board (dict): Current player's board mapping showing ship positions.
        """
        converted = self._normalize_ship_data(ship_data)

        if player_number == 1:
            self.player1_setup_data = converted
            self.player1_board = dict(board)  # Copy current player 1 board state
            self.current_player = 2  # Switch to player 2 for their setup turn
            self.show_player_setup(self.current_player)
        else:
            self.player2_setup_data = converted
            self.player2_board = dict(board)  # Copy player 2 board
            # Both players done setup, start battle phase with player 1's turn
            self.current_player = 1
            self.show_waiting_screen(1)

    # -------------------- Attack & Game Logic --------------------
    def request_attack(self, player_number, key):
        """
        Process an attack from player_number at the specified board coordinate `key`.

        Determines if attack hits or misses, updates board and ship data accordingly.
        Checks for sunk ships and game end condition.
        Switches turn to the defender and shows waiting screen for player swap.

        Args:
            player_number (int): The attacking player (1 or 2).
            key (str): The target board coordinate (e.g., 'A1').

        Returns:
            str: One of 'hit', 'miss', 'invalid', 'already', or 'gameover' indicating result.
        """
        print(f"[TURN] Player {player_number} attacks {key}")
        
        attacker = player_number
        defender = 2 if attacker == 1 else 1

        # Determine defender board and ship data to apply attack on
        board = self.player2_board if attacker == 1 else self.player1_board
        ship_data = self.player2_setup_data if attacker == 1 else self.player1_setup_data

        # Handle case where ship data is not initialized
        if ship_data is None:
            ship_data = []

        current_val = board.get(key)
        # Invalid if key not on board
        if current_val is None:
            print(f"[TURN] Invalid attack key: {key}")
            return 'invalid'

        # Ignore if square was already attacked
        if current_val in (2, 3, 4):
            print(f"[TURN] Square {key} already attacked (value={current_val}).")
            return 'already'

        # ---------- Hit Case ----------
        if current_val == 1:
            board[key] = 2  # Mark hit on defender's board
            print(f"[TURN] HIT on {key}")

            # Mark hit flag on associated ship part in ship_data
            for ship in ship_data:
                for part in ship:
                    coords, hit_flag = part[0], part[1]
                    px, py = coords[0], coords[1]
                    part_key = self._coords_to_key(px, py)
                    if part_key == key:
                        part[1] = 1  # Mark part as hit
                        break

            # Check each ship if fully hit, mark all parts destroyed on board
            for ship in ship_data:
                if all(p[1] == 1 for p in ship):
                    for part in ship:
                        px, py = part[0][0], part[0][1]
                        destroyed_key = self._coords_to_key(px, py)
                        if destroyed_key in board:
                            board[destroyed_key] = 4  # Mark destroyed squares
                    print(f"[TURN] Ship sunk at {key}")

            result = 'hit'
        else:
            # ---------- Miss Case ----------
            board[key] = 3  # Mark miss on board
            print(f"[TURN] MISS on {key}")
            result = 'miss'

        # ---------- Game Over Check ----------
        if self.check_if_game_end(attacker):
            print(f"[TURN] GAME OVER! Player {attacker} wins!")
            self.show_end_screen(attacker)
            return 'gameover'

        # ---------- End Turn and Switch Player ----------
        old_player = self.current_player
        self.current_player = defender
        print(f"[TURN] Turn ends → switch from Player {old_player} to Player {self.current_player}")
        
        # Show waiting screen for smooth player swap in hotseat mode
        self.show_waiting_screen()
        return result
    

    def check_if_game_end(self, player_number):
        """
        Check if the opponent of player_number has any remaining unsunk ship parts.

        Args:
            player_number (int): Player who just attacked.

        Returns:
            bool: True if opponent has no ship parts left (game over), else False.
        """
        defender_board = self.player2_board if player_number == 1 else self.player1_board

        # Return False if any ship piece exists (marked as 1)
        for value in defender_board.values():
            if value == 1:
                return False
        return True

    # -------------------- Utility Helpers --------------------
    def _coords_to_key(self, x, y):
        """
        Convert pixel coordinates from SetupView to a Battleship board key (e.g., 'A1').

        Args:
            x (float): X pixel coordinate.
            y (float): Y pixel coordinate.

        Returns:
            str: Alphanumeric grid key corresponding to the coordinate.
        """
        col = int((x - (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
        row = int((y - (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
        col = max(0, min(9, col))  # Bound columns to 0-9
        row = max(0, min(9, row))  # Bound rows to 0-9
        return chr(ord('A') + row) + str(col + 1)

    def _normalize_ship_data(self, ship_data):
        """
        Normalize ship_data structure to ensure mutability and consistent data format.

        Converts tuples/lists of coordinates and hit flags to mutable lists with int flags.

        Args:
            ship_data (list or None): Raw ship data from SetupView or savefiles.

        Returns:
            list: Normalized list of ships with mutable parts [ [[x,y,angle], hit], ... ].
        """
        if ship_data is None:
            return []

        normalized = []
        for ship in ship_data:
            norm_ship = []
            for part in ship:
                # Handle standard formats: ((coords), hit_flag) or ([coords], hit_flag)
                if isinstance(part, (list, tuple)) and len(part) == 2:
                    coords, hit_flag = part[0], part[1]
                    coords_list = list(coords) if isinstance(coords, (list, tuple)) else [coords]
                    hit_flag = int(bool(hit_flag))
                    norm_ship.append([coords_list, hit_flag])
                else:
                    # Fallback for unexpected data: use zeros and unhit
                    norm_ship.append([[0, 0, 0], 0])
            normalized.append(norm_ship)
        return normalized
    
    def reset_game_state(self):
        """Reset game variables and restart Hotseat game with player 1's setup."""
        self.player1_setup_data = None
        self.player2_setup_data = None
        # Use copies of blank_board to avoid shared references
        self.player1_board = blank_board.copy()
        self.player2_board = blank_board.copy()
        self.current_player = 1
        self.game_role = None
        self.show_player_setup(self.current_player)


if __name__ == '__main__':
    # Start the Hotseat game window and enter the arcade run loop
    HotseatGame()
    arcade.run()