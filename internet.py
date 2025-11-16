import arcade
import threading
import socket
import json
import sys
import time

# NOTE: You must ensure these imports point to your correctly defined files
from setup import SetupView 
from battle import BattleView
from connect import ConnectView 
from internet_other_screens import GameOverView, WaitingView 
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, player1_board, player2_board, SQUARE_SIZE, blank_board 

# ----------------- Utility for showing local IP ------------------

def get_local_ip():
    """Get the non-loopback local IP address.

    Attempts to create a UDP connection to a public server to discover the local IP.
    Falls back to hostname resolution if the above fails.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())


# ----------------- InternetGame Class (Main Window) -----------------

class InternetGame(arcade.Window):
    """Main Internet Game class controlling the flow between setup and battle views."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Battleship Internet")
        
        # Player setup data and game boards (copy blank boards)
        self.player1_setup_data = None
        self.player2_setup_data = None
        
        self.player1_board = blank_board.copy()
        self.player2_board = blank_board.copy()

        # Current player (1 or 2), host is player 1 and always starts first
        self.current_player = 1 
        
        # Networking attributes
        self.port = 5555
        self.host_ip = None 
        self.server_socket = None
        self.client_socket = None 
        self.game_role = None # 'host' or 'client'
        
        # Start connection screen
        self.show_connection_screen()

    # =========================================================================
    # 1. NETWORKING UTILITIES (Send/Receive/Listen)
    # =========================================================================

    def send_data(self, data):
        """JSON serialize and send data over the client socket with length prefix."""
        if not self.client_socket:
            print("Error: Client socket not available for sending.")
            return

        try:
            message = json.dumps(data).encode('utf-8')
            length_prefix = f"{len(message):<10}"
            self.client_socket.sendall(length_prefix.encode('utf-8') + message)
        except Exception as e:
            print(f"Error sending data: {e}")
            self._handle_disconnect_scheduled()

    def receive_data(self):
        """Receive a full message with length prefix and deserialize JSON."""
        if not self.client_socket:
            return None
            
        try:
            length_prefix = self.client_socket.recv(10).decode('utf-8').strip()
            if not length_prefix:
                return None
                
            message_length = int(length_prefix)
            
            full_message = b''
            bytes_received = 0
            while bytes_received < message_length:
                chunk = self.client_socket.recv(min(message_length - bytes_received, 2048))
                if not chunk:
                    break
                full_message += chunk
                bytes_received += len(chunk)
            
            if bytes_received < message_length:
                 print("Warning: Did not receive full message.")
                 return None

            return json.loads(full_message.decode('utf-8'))

        except ConnectionResetError:
            print("Connection forcibly closed by the remote host.")
            arcade.schedule(lambda dt: self._handle_disconnect_scheduled(), 0)
            return None
        except Exception:
            if self.client_socket:
                arcade.schedule(lambda dt: self._handle_disconnect_scheduled(), 0)
            return None

    def _listen_for_data(self):
        """Background thread continuously listening and scheduling received messages."""
        while self.client_socket:
            data = self.receive_data()
            if data is None:
                break
                
            arcade.schedule(lambda dt: self._process_command(data), 0)
            
        print("Network listener thread stopped.")

    def _process_command(self, data):
        """Process incoming network commands on the main thread."""
        if isinstance(data, list):
            for item in data:
                self._process_command(item)
            return
        
        command = data.get("command")
        
        if command == "ATTACK":
            key = data.get("target")
            self._handle_incoming_attack(key)
        
        elif command == "ATTACK_RESPONSE":
            result = data.get("result") # 0=Miss,1=Hit,2=Sunk
            key = data.get("target")
            effected_ships = data.get("effected_ships") 
            check_end = data.get("check_end", False)
            self._handle_attack_response(key, result, effected_ships, check_end)

        elif command == "SETUP_DATA":
            player_number = data.get("player")
            ship_data = data.get("ship_data")
            board_data = data.get("board_data")
            
            if player_number == 1:
                self.player1_setup_data = ship_data
                self.player1_board = board_data
            else:
                self.player2_setup_data = ship_data
                self.player2_board = board_data
                
            print(f"Received setup data for Player {player_number}.")
            
            if self.player1_setup_data and self.player2_setup_data:
                self.send_data({"command": "START_GAME"})
                self.start_game()
        
        elif command == "START_GAME":
            if self.player1_setup_data and self.player2_setup_data:
                self.start_game()
        else:
            print(f"Unknown command received: {command}")

    # =========================================================================
    # 2. CONNECTION HANDLERS (Host/Join)
    # =========================================================================

    def show_connection_screen(self):
        """Display initial connect view with Host/Join options."""
        connect_view = ConnectView()
        self.show_view(connect_view)

    def host_connect(self, host_ip):
        """Begin acting as server host and start listening for connection."""
        self.game_role = 'host'
        self.host_ip = host_ip
        self.start_server()

    def join_connect(self, host_ip):
        """Attempt to connect as a client to the host server."""
        self.game_role = 'client'
        port = 5555 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            print(f"Attempting to connect to {host_ip}:{port}...")
            client_socket.connect((host_ip, port))
            
            print("Successfully connected to host!")
            self.client_socket = client_socket
            
            threading.Thread(target=self._listen_for_data, daemon=True).start()
            
            # Client starts setup (Player 2)
            self.show_player_setup(player_number=2)
            
        except socket.error as e:
            print(f"Connection failed: Could not reach host at {host_ip}:{port}")
            print(f"Error details: {e}")
            client_socket.close()
    
    def start_server(self):
        """Start server thread to wait for incoming client connections."""
        threading.Thread(target=self.wait_for_connection, daemon=True).start()
    
    def wait_for_connection(self):
        """Listen for one client connection and then start data listener."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            self.server_socket.bind((self.host_ip, self.port))
            self.server_socket.listen(1)
            print(f"Server listening on {self.host_ip}:{self.port}")

            self.client_socket, address = self.server_socket.accept() 
            
            print(f"Connection established with client at {address}")
            
            threading.Thread(target=self._listen_for_data, daemon=True).start()
            
            arcade.schedule(self._start_host_setup, 0)
            
        except Exception as e:
            print(f"Server error: {e}")

    def _start_host_setup(self, dt):
        """Switch to player 1 setup view on the main thread after connection."""
        self.show_player_setup(player_number=1) 
        arcade.unschedule(self._start_host_setup) 

    def _handle_disconnect_scheduled(self):
        """Scheduled handler to perform disconnect tasks safely on main thread."""
        self._handle_disconnect()
        
    def _handle_disconnect(self):
        """Clean up sockets and return to connection screen on disconnect."""
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

        # Server socket is typically closed after client connects; ignored here.
            
        print("Disconnected. Returning to connection screen.")
        self.show_connection_screen()
        
    def reset_game_state(self):
        """Reset game data to allow a new match to start."""
        self.player1_setup_data = None
        self.player2_setup_data = None
        self.player1_board = blank_board.copy()
        self.player2_board = blank_board.copy()
        self.current_player = 1 
        self.game_role = None

    # =========================================================================
    # 3. GAME FLOW AND VIEW SWITCHING
    # =========================================================================
    
    def show_waiting_screen(self):
        """Display WaitingView to indicate opponent's turn."""
        print("Switching to Waiting View. Opponent's turn.")
        waiting_view = WaitingView(self)
        self.show_view(waiting_view)
        
    def show_player_setup(self, player_number):
        """Show SetupView for the specified player."""
        board = self.player1_board if player_number == 1 else self.player2_board
        setup_view = SetupView(player_number, self, board)
        self.show_view(setup_view)

    def show_player_battle(self, player_number):
        """Show BattleView for the specified player, letting it handle turn logic."""
        setup_data = self.player1_setup_data if player_number == 1 else self.player2_setup_data
        your_board = self.player1_board if player_number == 1 else self.player2_board
        opponents_board = self.player2_board if player_number == 1 else self.player1_board

        battle_view = BattleView(
            player_number, 
            self, 
            setup_data, 
            your_board, 
            opponents_board, 
        )
        self.show_view(battle_view)

    def show_end_screen(self, winner_player_number):
        """Show GameOverView indicating the winner."""
        game_over_view = GameOverView(self, winner_player_number)
        self.show_view(game_over_view)

    def on_setup_finished(self, player_number, ship_data, board):
        """Called by SetupView after player finishes ship placement.

        Saves local data and sends it to opponent over the network.
        """
        if player_number == 1:
            self.player1_setup_data = ship_data
            self.player1_board = board
        else:
            self.player2_setup_data = ship_data
            self.player2_board = board
            
        setup_message = {
            "command": "SETUP_DATA",
            "player": player_number,
            "ship_data": ship_data,
            "board_data": board
        }
        self.send_data(setup_message)
        
        print(f"Player {player_number} setup complete. Waiting for opponent's data...")

    def start_game(self):
        """Begin the battle phase when setup is complete on both sides."""
        print("Starting the battle!")
        self.current_player = 1  # Host (player 1) always starts
        
        my_player_number = 1 if self.game_role == 'host' else 2
        
        # BattleView will switch to WaitingView if it's not this player's turn
        self.show_player_battle(my_player_number)

    # =========================================================================
    # 4. BATTLE LOGIC (Networking Integrated)
    # =========================================================================

    def request_attack(self, player_number, key):
        """Send an attack request to opponent.

        Called by BattleView when player clicks on opponent's grid.
        """
        if not self.client_socket:
            print("Cannot attack: No connection.")
            return

        attack_data = {
            "command": "ATTACK",
            "target": key, 
            "attacker": player_number
        }
        self.send_data(attack_data)
        print(f"Attack request sent to opponent at {key}. Waiting for response...")

    def _handle_incoming_attack(self, key):
        """Process an attack from opponent and respond accordingly."""
        your_player_number = 1 if self.game_role == 'host' else 2
        
        board = self.player1_board if your_player_number == 1 else self.player2_board
        ship_data = self.player1_setup_data if your_player_number == 1 else self.player2_setup_data
        effected_ships = []
        result = 0 # 0=Miss, 1=Hit, 2=Sunk
        
        if key in board and board.get(key) == 1:
            board[key] = 2  # Mark hit
            result = 1
            
            for ship in ship_data:
                for part_index, part in enumerate(ship):
                    (x, y, angle), hit = part
                    
                    # Convert coords to grid key
                    col = int((x - (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                    row = int((y - (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                    part_key = chr(ord('A') + row) + str(col + 1)

                    if part_key == key:
                        ship[part_index][1] = 1  # Mark hit flag
                        if all(p[1] == 1 for p in ship):
                            # Mark entire ship as destroyed
                            for p in ship:
                                (px, py, _), _ = p
                                c = int((px - (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                                r = int((py - (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                                destroyed_key = chr(ord('A') + r) + str(c + 1)
                                if destroyed_key in board:
                                    board[destroyed_key] = 4
                                    effected_ships.append(destroyed_key)
                            result = 2  # Ship sunk
                        break
        else:
            if key in board and board.get(key) == 0:
                board[key] = 3  # Mark miss
        
        check_end = self.check_if_game_end(your_player_number)

        response = {
            "command": "ATTACK_RESPONSE",
            "target": key,
            "result": result,
            "effected_ships": effected_ships,
            "check_end": check_end
        }
        self.send_data(response)
        
        # Update local state
        if your_player_number == 1:
            self.player1_board = board
            self.player1_setup_data = ship_data
        else:
            self.player2_board = board
            self.player2_setup_data = ship_data

        if check_end:
            winner_number = 1 if your_player_number == 2 else 2
            print(f"Game Over! Player {winner_number} won.")
            self.show_end_screen(winner_number)
            return

        # Switch turn to defender (player that just responded)
        self.current_player = your_player_number
        self.show_player_battle(your_player_number)

    def _handle_attack_response(self, key, result, effected_ships=None, check_end=None):
        """Process the server's reply to your attack and update board representation."""
        your_player_number = 1 if self.game_role == 'host' else 2
        
        opponents_board = self.player2_board if your_player_number == 1 else self.player1_board
        
        if result == 0:  # Miss
            opponents_board[key] = 3
            print(f"Attack on {key}: MISS")
        elif result == 1:  # Hit
            opponents_board[key] = 2
            print(f"Attack on {key}: HIT")
        elif result == 2:  # Sunk
            opponents_board[key] = 4
            print(f"Attack on {key}: SHIP SUNK!")
            if effected_ships:
                for part_key in effected_ships:
                    opponents_board[part_key] = 4
        
        # Update tracking board locally
        if your_player_number == 1:
            self.player2_board = opponents_board
        else:
            self.player1_board = opponents_board
            
        if check_end:
            self.show_end_screen(your_player_number)
            return 
        
        # Turn switches to opponent (defender)
        self.current_player = 1 if your_player_number == 2 else 2
        
        # Show BattleView for this (now passive) player
        self.show_player_battle(your_player_number)

    def check_if_game_end(self, player_number):
        """Return True if the specified player has no remaining ship pieces."""
        board = self.player1_board if player_number == 1 else self.player2_board
        for value in board.values():
            if value == 1:  # Ship piece unhit found
                return False
        return True  # No ship parts remain; game over