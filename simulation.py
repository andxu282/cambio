from models import Deck, Player, Hand, Action, Card, Rank, Suit
from utils import get_score
import random
from typing import List
import numpy as np

class Game:
    def __init__(self):
        self.deck = Deck()
        self.player_one = Player()
        self.discard = Hand()
        self.player_two = Player()
        self.num_rounds = 0
        self.current_player = self.player_one
        self.other_player = self.player_two
        self.cambio_player = None # represents the player who called cambio
    
    def start(self, random_state=None, verbose=False):
        # shuffle deck
        self.deck.shuffle(random_state=random_state)

        # deal cards
        self.add_cards(self.current_player, self.other_player, self.deck.deal(4))
        self.add_cards(self.other_player, self.current_player, self.deck.deal(4))
        top_card = self.deck.deal(1)[0]
        self.discard.add_cards([top_card])

        # show first 2 cards to each player
        self.show_card(self.player_one, self.player_one, 0)
        self.show_card(self.player_one, self.player_one, 1)
        self.show_card(self.player_two, self.player_two, 0)
        self.show_card(self.player_two, self.player_two, 1)

        # discard race at the beginning
        self.discard_race(top_card)

        called_cambio = False
        # start play
        while self.num_rounds < 50:
            self.num_rounds += 1

            # player decides whether or not to call cambio
            self.current_player.decide_cambio(called_cambio)
            if self.current_player.has_called_cambio:
                # if they do, then allow the loop run one more time
                self.cambio_player = self.current_player
                called_cambio = True
            else:
                # otherwise, draw a card
                drawn_card = self.deck.deal(1, self.discard.cards)[0]
                # player will handle the card
                action, opp_index, own_index = self.current_player.handle_card(drawn_card)
                # performs the action the player wants to
                self.perform_action(action, opp_index, own_index, drawn_card, called_cambio)

                if called_cambio:
                    break
                
            # switch players for the next turn
            self.current_player = self.player_one if self.num_rounds % 2 == 0 else self.player_two
            self.other_player = self.player_one if self.num_rounds % 2 == 1 else self.player_two
        
        return self.decide_winner(verbose)
    
    def discard_race(self, card, random_state=None):
        action_one, opp_index_one, own_index_one = self.current_player.try_discard(card)
        action_two, opp_index_two, own_index_two = self.other_player.try_discard(card)
        if action_one == Action.NONE and action_two == Action.NONE:
            return
        if action_one == Action.DISCARD and action_two == Action.NONE:
            # discard the card that current_player wants to do
            if opp_index_one is not None:
                self.delete_card(self.other_player, self.current_player, opp_index_one)
                penalties = self.deck.deal(2)
                for penalty in penalties:
                    self.add_card(self.other_player, self.current_player, penalty)
            if own_index_one is not None:
                self.delete_card(self.current_player, self.other_player, own_index_one)
            return
        if action_one == Action.NONE and action_two == Action.DISCARD:
            # discard the card that other_player wants to do
            if opp_index_two is not None:
                self.delete_card(self.current_player, self.other_player, opp_index_two)
                penalties = self.deck.deal(2)
                for penalty in penalties:
                    self.add_card(self.current_player, self.other_player, penalty)
            if own_index_two is not None:
                self.delete_card(self.other_player, self.current_player, own_index_two)
            return
        if action_one == Action.DISCARD and action_two == Action.DISCARD:
            if random_state is not None:
                random.seed(random_state)
            dice_roll = random.random()
            if opp_index_two is not None and own_index_one is not None:
                # current_player is playing defense, 0.8 chance to win
                if dice_roll < 0.8:
                    # current_player gets to discard own
                    self.delete_card(self.current_player, self.other_player, own_index_one)
                else:
                    # current_player receives penalty
                    self.delete_card(self.current_player, self.other_player, opp_index_two)
                    penalties = self.deck.deal(2)
                    for penalty in penalties:
                        self.add_card(self.current_player, self.other_player, penalty)
            if opp_index_one is not None and own_index_two is not None:
                # other_player is playing defense, 0.8 chance to win
                if dice_roll < 0.8:
                    self.delete_card(self.other_player, self.current_player, own_index_two)
                else:
                    self.delete_card(self.other_player, self.current_player, opp_index_one)
                    penalties = self.deck.deal(2)
                    for penalty in penalties:
                        self.add_card(self.other_player, self.current_player, penalty)
            if own_index_one is not None and own_index_two is not None:
                # it's a flip if both are trying to throw away their own card
                if dice_roll < 0.5:
                    self.delete_card(self.current_player, self.other_player, own_index_one)
                else:
                    self.delete_card(self.other_player, self.current_player, own_index_two)
            if opp_index_one is not None and opp_index_two is not None:
                # it's a flip if both are trying to throw away their opp's card
                if dice_roll < 0.5:
                    self.delete_card(self.current_player, self.other_player, opp_index_two)
                    penalties = self.deck.deal(2)
                    for penalty in penalties:
                        self.add_card(self.current_player, self.other_player, penalty)
                else:
                    self.delete_card(self.other_player, self.current_player, opp_index_one)
                    penalties = self.deck.deal(2)
                    for penalty in penalties:
                        self.add_card(self.other_player, self.current_player, penalty)

    def show_card(self, player: Player, card_from_player: Player, index):
        if player == card_from_player:
            player.knowledge.own_hand.cards[index] = card_from_player.hand.cards[index]
        else:
            player.knowledge.opp_hand.cards[index] = card_from_player.hand.cards[index]
        
    def swap_cards(self, player: Player, opp: Player, own_index: int, opp_index: int):
        # world update
        own_card = player.hand.cards[own_index]
        opp_card = opp.hand.cards[opp_index]

        player.hand.cards[own_index] = opp_card
        opp.hand.cards[opp_index] = own_card

        # update own knowledge
        # own knowledge about own card
        own_own_card_knowledge = player.knowledge.own_hand.cards[own_index]
        # own knowledge about opp card
        own_opp_card_knowledge = player.knowledge.opp_hand.cards[opp_index]

        player.knowledge.own_hand.cards[own_index] = own_opp_card_knowledge
        player.knowledge.opp_hand.cards[opp_index] = own_own_card_knowledge

        # update opp knowledge
        # opp knowledge about own card
        opp_own_card_knowledge = opp.knowledge.opp_hand.cards[own_index]
        # opp knowledge about opp card
        opp_opp_card_knowledge = opp.knowledge.own_hand.cards[opp_index]

        opp.knowledge.opp_hand.cards[own_index] = opp_opp_card_knowledge
        opp.knowledge.own_hand.cards[opp_index] = opp_own_card_knowledge

    def replace_card(self, player: Player, opp: Player, index: int, card: Card):
        old_card = self.delete_card(player, opp, index)
        self.add_card(player, opp, card, known_card=True)
        return old_card
    
    def delete_card(self, player: Player, opp: Player, index: int):
        card = player.hand.cards[index]
        # world update
        del player.hand.cards[index]
        # player knowledge update
        del player.knowledge.own_hand.cards[index]
        # opp knowledge update
        del opp.knowledge.opp_hand.cards[index]
        return card

    def add_card(self, player: Player, opp: Player, card: Card, known_card=False):
        # world update
        player.hand.add_cards([card])
        # player knowledge update
        if known_card:
            player.knowledge.own_hand.add_cards([card])
        else:
            player.knowledge.own_hand.add_cards([None])
        # opp knowledge update
        opp.knowledge.opp_hand.add_cards([None])
    
    def add_cards(self, player: Player, opp: Player, cards: List[Card], known_cards=False):
        [self.add_card(player, opp, card, known_card=known_cards) for card in cards]

    def perform_action(self, action, opp_index, own_index, drawn_card, called_cambio):
        if action == Action.NONE:
            return
        if action == Action.REPLACE:
            old_card = self.replace_card(self.current_player, self.other_player, own_index, drawn_card)
            self.discard.add_cards([old_card])
            self.discard_race(old_card)
        else:
            if action == Action.SHOW:
                if opp_index is not None:
                    self.show_card(self.current_player, self.other_player, opp_index)
                if own_index is not None:
                    self.show_card(self.current_player, self.current_player, own_index)
            if action == Action.SWAP and not called_cambio:
                self.swap_cards(self.current_player, self.other_player, own_index, opp_index)
            if action == Action.SHOW_AND_SWAP:
                self.show_card(self.current_player, self.other_player, opp_index)
                if not called_cambio:
                    action, opp_index, own_index = self.current_player.play_card(Card(Rank.JACK, Suit.SPADES)) # little bit jank, it passes it back as a Jack to swap
                    self.swap_cards(self.current_player, self.other_player, own_index, opp_index)
            self.discard.add_cards([drawn_card])
            self.discard_race(drawn_card)

    def decide_winner(self, verbose):
        # other things to log: num of each action
        # returns winner (0 for player_one, 1 for player_two), player_one hand, player_one_score, player_two hand, player_two_score num_rounds
        player_one_score = get_score(self.player_one)
        player_two_score = get_score(self.player_two)
        

        if player_one_score < player_two_score:
            winner = 0
        if player_two_score < player_one_score:
            winner = 1
        if player_one_score == player_two_score:
            if not self.player_one.has_called_cambio:
                winner = 0
            if not self.player_two.has_called_cambio:
                winner = 1
        
        if verbose:
            print(f"PLAYER {"ONE" if winner == 0 else "TWO"} WINS!")
            print("Stats")
            print("----")
            print(f"Player one cards: {self.player_one.hand}")
            print(f"Player one score: {player_one_score}")
            print(f"Player two cards: {self.player_two.hand}")
            print(f"Player two score: {player_two_score}")
            print(f"Number of rounds: {self.num_rounds}")
        return winner, self.player_one.hand, player_one_score, self.player_two.hand, player_two_score, self.num_rounds


if __name__ == '__main__':
    num_iterations = int(1e6)

    player_one_wins = 0
    player_two_wins = 0
    player_one_scores = []
    player_two_scores = []
    num_rounds_list = []
    for i in range(num_iterations):
        game = Game()
        if i % (num_iterations / 100) == 0:
            print(f"{i / (num_iterations / 100)}%")
        winner, player_one_hand, player_one_score, player_two_hand, player_two_score, num_rounds = game.start(random_state=i)
        if winner == 0:
            player_one_wins += 1
        else:
            player_two_wins += 1
        player_one_scores.append(player_one_score)
        player_two_scores.append(player_two_score)
        num_rounds_list.append(num_rounds)
    print(player_one_wins)
    print(player_two_wins)
    print(np.mean(num_rounds_list))
