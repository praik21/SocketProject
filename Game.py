import random

class PlayingCard:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank}{self.suit}"

class CardDeck:
    def __init__(self):
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
        self.cards = [PlayingCard(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        else:
            raise ValueError("No more cards in the deck.")

class GamePlayer:
    def __init__(self, player_name):
        self.player_name = player_name
        self.hand = []
        self.face_up_status = [False] * 6

    def add_card(self, card):
        self.hand.append(card)

    def reveal_card(self, index):
        self.face_up_status[index] = True

    def replace_card(self, index, new_card):
        if index < 0 or index >= len(self.hand):
            raise IndexError("Invalid card index.")
        replaced_card = self.hand[index]
        self.hand[index] = new_card
        self.face_up_status[index] = True
        return replaced_card

    def calculate_score(self):
        total_score = 0
        for i in range(0, 6, 2):
            if self.face_up_status[i] and self.face_up_status[i + 1] and self.hand[i].rank == self.hand[i + 1].rank:
                continue
            for j in range(2):
                if self.face_up_status[i + j]:
                    current_card = self.hand[i + j]
                    if current_card.rank == 'A':
                        total_score += 1
                    elif current_card.rank == '2':
                        total_score -= 2
                    elif current_card.rank in ['J', 'Q']:
                        total_score += 10
                    elif current_card.rank == 'K':
                        total_score += 0
                    else:
                        total_score += int(current_card.rank)
        return total_score

class Game:
    def __init__(self, player_names, number_of_holes):
        self.players = [GamePlayer(name) for name in player_names]
        self.number_of_holes = number_of_holes
        self.active_player_index = 0
        self.card_deck = None
        self.discard_stack = []

    def distribute_cards(self):
        self.card_deck = CardDeck()
        for _ in range(6):
            for player in self.players:
                player.add_card(self.card_deck.draw_card())
        for player in self.players:
            indices_to_reveal = random.sample(range(6), 2)
            for index in indices_to_reveal:
                player.reveal_card(index)
        self.discard_stack = [self.card_deck.draw_card()]

    def take_turn(self, draw_from_deck=True, swap_index=None):
        current_player = self.players[self.active_player_index]
        drawn_card = self.card_deck.draw_card() if draw_from_deck else self.discard_stack.pop()

        if swap_index is not None and 0 <= swap_index < len(current_player.hand):
            replaced_card = current_player.replace_card(swap_index, drawn_card)
            self.discard_stack.append(replaced_card)
        else:
            self.discard_stack.append(drawn_card)

        self.active_player_index = (self.active_player_index + 1) % len(self.players)

    def is_round_complete(self):
        return all(all(player.face_up_status) for player in self.players)

    def play_round(self):
        self.distribute_cards()
        while not self.is_round_complete():
            current_player = self.players[self.active_player_index]
            # For simplicity, draw from the deck and swap the first card
            # In a real game, you would prompt for these choices or simulate AI logic
            self.take_turn(True, random.choice([i for i in range(6) if not current_player.face_up_status[i]]))

    def execute_game(self):
        player_scores = [0] * len(self.players)
        for _ in range(self.number_of_holes):
            self.play_round()
            for idx, player in enumerate(self.players):
                player_scores[idx] += player.calculate_score()
        winner_index = min(range(len(player_scores)), key=player_scores.__getitem__)
        return self.players[winner_index].player_name, player_scores
