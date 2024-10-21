import socket
import threading
import json
import uuid
import random
import logging

class GameTracker:
    def __init__(self, host_address, port_number=3000):
        self.host_address = host_address
        self.port_number = port_number
        self.registered_players = {}
        self.active_games = {}
        self.lock = threading.Lock()

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def start_tracker(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host_address, self.port_number))
            server_socket.listen()
            logging.info(f"GameTracker running on {self.host_address}:{self.port_number}")

            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client_connection, args=(client_socket,))
                client_thread.start()
        except Exception as e:
            logging.error(f"Error starting the tracker: {e}")
        finally:
            server_socket.close()

    def handle_client_connection(self, client_socket):
        try:
            while True:
                received_data = client_socket.recv(1024).decode('utf-8')
                if not received_data:
                    break
                command_data = json.loads(received_data)
                response_data = self.process_client_command(command_data)
                client_socket.send(json.dumps(response_data).encode('utf-8'))
        except Exception as error:
            logging.error(f"Error with client connection: {error}")
            response_data = {'status': 'FAILURE', 'message': f'Error: {str(error)}'}
            client_socket.send(json.dumps(response_data).encode('utf-8'))
        finally:
            client_socket.close()

    def process_client_command(self, command_data):
        command_type = command_data.get('command')
        command_map = {
            'register': self.register_player,
            'query_players': self.get_players,
            'query_games': self.get_games,
            'de_register': self.deregister_player,
            'start_game': self.create_game,
            'end_game': self.terminate_game
        }
        if command_type in command_map:
            try:
                return command_map[command_type](**command_data)
            except TypeError as e:
                return {'status': 'FAILURE', 'message': f'Invalid command parameters: {e}'}
        else:
            return {'status': 'FAILURE', 'message': 'Command not recognized'}

    def register_player(self, player, ipv4, t_port, p_port):
        with self.lock:
            if player in self.registered_players:
                return {'status': 'FAILURE', 'message': 'Player is already registered'}
            if not (3001 <= t_port <= 3499) or not (3001 <= p_port <= 3499):
                return {'status': 'FAILURE', 'message': 'Port number out of allowed range'}
            self.registered_players[player] = {
                'ipv4': ipv4,
                'tracker_port': t_port,
                'player_port': p_port,
                'status': 'available'
            }
            logging.info(f"Player {player} registered successfully.")
            return {'status': 'SUCCESS'}

    def get_players(self):
        with self.lock:
            return {
                'status': 'SUCCESS',
                'total_players': len(self.registered_players),
                'players': [{'name': name, **details} for name, details in self.registered_players.items()]
            }

    def get_games(self):
        with self.lock:
            return {
                'status': 'SUCCESS',
                'total_games': len(self.active_games),
                'games': self.active_games
            }

    def deregister_player(self, player):
        with self.lock:
            if player not in self.registered_players:
                return {'status': 'FAILURE', 'message': 'Player not found'}
            for game in self.active_games.values():
                if player in game['players']:
                    return {'status': 'FAILURE', 'message': 'Player is currently participating in a game'}
            del self.registered_players[player]
            logging.info(f"Player {player} has been deregistered.")
            return {'status': 'SUCCESS'}

    def create_game(self, player, num_players, num_holes):
        with self.lock:
            if player not in self.registered_players or self.registered_players[player]['status'] != 'available':
                return {'status': 'FAILURE', 'message': 'Host player is either invalid or not available'}

            if not (1 <= num_players <= 3):
                return {'status': 'FAILURE', 'message': 'Invalid number of players specified'}

            if not (1 <= num_holes <= 9):
                return {'status': 'FAILURE', 'message': 'Invalid number of holes specified'}

            available_players = [p for p in self.registered_players if self.registered_players[p]['status'] == 'available' and p != player]
            if len(available_players) < num_players:
                return {'status': 'FAILURE', 'message': 'Not enough players available'}

            chosen_players = random.sample(available_players, num_players)
            chosen_players.insert(0, player)

            new_game_id = str(uuid.uuid4())
            self.active_games[new_game_id] = {
                'host': player,
                'players': chosen_players,
                'holes': num_holes,
                'status': 'active'
            }

            for p in chosen_players:
                self.registered_players[p]['status'] = 'playing'

            return {
                'status': 'SUCCESS',
                'game_id': new_game_id,
                'holes': num_holes,
                'players': [{'name': p, **self.registered_players[p]} for p in chosen_players]
            }

    def terminate_game(self, game_id, player):
        with self.lock:
            if game_id not in self.active_games or self.active_games[game_id]['host'] != player:
                return {'status': 'FAILURE', 'message': 'Invalid game ID or host player'}

            for p in self.active_games[game_id]['players']:
                self.registered_players[p]['status'] = 'available'

            del self.active_games[game_id]
            logging.info(f"Game {game_id} terminated successfully.")
            return {'status': 'SUCCESS'}

    def shutdown_tracker(self):
        logging.info("Shutting down GameTracker.")
        # Additional logic to close open connections and clean up can be added here.

if __name__ == '__main__':
    try:
        game_tracker = GameTracker('0.0.0.0', 3000)  # Listening on all interfaces
        game_tracker.start_tracker()
    except KeyboardInterrupt:
        game_tracker.shutdown_tracker()
        logging.info("Tracker has been shut down.")
