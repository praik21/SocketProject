import socket
import json
import sys
from game import Game

class Player:
    def __init__(self, username, ipv4_address, tracker_port, player_port, tracker_ip, tracker_host_port):
        self.username = username
        self.ipv4_address = ipv4_address
        self.tracker_port = tracker_port
        self.player_port = player_port
        self.tracker_ip = tracker_ip
        self.tracker_host_port = tracker_host_port

    def execute_command(self, command_data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((self.tracker_ip, self.tracker_host_port))
                sock.sendall(json.dumps(command_data).encode('utf-8'))
                response = sock.recv(1024).decode('utf-8')
                return json.loads(response)
        except socket.timeout:
            return {'status': 'FAILURE', 'message': 'Connection timed out with the tracker.'}
        except ConnectionRefusedError:
            return {'status': 'FAILURE', 'message': 'Could not connect. Is the tracker service running?'}
        except Exception as error:
            return {'status': 'FAILURE', 'message': f'Error occurred: {str(error)}'}

    def register_player(self):
        command_data = {
            'action': 'register',
            'username': self.username,
            'ipv4': self.ipv4_address,
            'tracker_port': self.tracker_port,
            'player_port': self.player_port
        }
        return self.execute_command(command_data)

    def get_players(self):
        command_data = {'action': 'get_players'}
        return self.execute_command(command_data)

    def get_games(self):
        command_data = {'action': 'get_games'}
        return self.execute_command(command_data)

    def unregister_player(self):
        command_data = {
            'action': 'unregister',
            'username': self.username
        }
        return self.execute_command(command_data)

    def initiate_game(self, players_count, holes_count):
        command_data = {
            'action': 'initiate_game',
            'username': self.username,
            'players_count': players_count,
            'holes_count': holes_count
        }
        return self.execute_command(command_data)

    def conclude_game(self, game_id):
        command_data = {
            'action': 'conclude_game',
            'game_id': game_id,
            'username': self.username
        }
        return self.execute_command(command_data)

    def participate_in_game(self, game_data):
        game_instance = Game([player['username'] for player in game_data['players']], game_data['holes_count'])
        champion, results = game_instance.play_game()
        print(f"Game Finished! Champion: {champion}")
        print("Results:", results)
        return champion, results

def main():
    if len(sys.argv) != 7:
        print("Usage: python player.py <username> <ipv4> <tracker_port> <player_port> <tracker_ip> <tracker_host_port>")
        sys.exit(1)

    username, ipv4, tracker_port, player_port, tracker_ip, tracker_host_port = sys.argv[1:]
    player_instance = Player(username, ipv4, int(tracker_port), int(player_port), tracker_ip, int(tracker_host_port))

    print(f"Attempting to connect to tracker at {tracker_ip}:{tracker_host_port}")

    while True:
        print("\nMenu of Commands:")
        print("1. Register")
        print("2. View Players")
        print("3. View Games")
        print("4. Unregister")
        print("5. Initiate Game")
        print("6. Exit")

        user_choice = input("Select an option (1-6): ")

        if user_choice == '1':
            response = player_instance.register_player()
            print(response)
            if response['status'] == 'SUCCESS':
                print(f"Successfully registered as {username}")
            else:
                print(f"Registration failed: {response['message']}")
        elif user_choice == '2':
            response = player_instance.get_players()
            print(response)
        elif user_choice == '3':
            response = player_instance.get_games()
            print(response)
        elif user_choice == '4':
            response = player_instance.unregister_player()
            print(response)
            if response['status'] == 'SUCCESS':
                print(f"Successfully unregistered {username}")
            else:
                print(f"Unregistration failed: {response['message']}")
        elif user_choice == '5':
            players_count = int(input("Enter number of players (1-3): "))
            holes_count = int(input("Enter number of holes (1-9): "))
            response = player_instance.initiate_game(players_count, holes_count)
            print(response)
            if response['status'] == 'SUCCESS':
                champion, results = player_instance.participate_in_game(response)
                player_instance.conclude_game(response['game_id'])
        elif user_choice == '6':
            print("Exiting application...")
            break
        else:
            print("Invalid selection. Please choose a valid option.")

if __name__ == '__main__':
    main()
