from enum import Enum
import random
from uuid import uuid4
from utils import get_score
from typing import List

class Action(Enum):
    NONE = 'none'
    REPLACE = 'replace'
    SHOW = 'show'
    SWAP = 'swap'
    SHOW_AND_SWAP = 'show and swap'
    DISCARD = 'discard'


class Rank(Enum):
    ACE = 'Ace'
    TWO = 'Two'
    THREE = 'Three'
    FOUR = 'Four'
    FIVE = 'Five'
    SIX = 'Six'
    SEVEN = 'Seven'
    EIGHT = 'Eight'
    NINE = 'Nine'
    TEN = 'Ten'
    JACK = 'Jack'
    QUEEN = 'Queen'
    KING = 'King'

class Suit(Enum):
    HEARTS = 'Hearts'
    DIAMONDS = 'Diamonds'
    CLUBS = 'Clubs'
    SPADES = 'Spades'

RANK_TO_STRING = {
    Rank.ACE: 'A',
    Rank.TWO: '2',
    Rank.THREE: '3',
    Rank.FOUR: '4',
    Rank.FIVE: '5',
    Rank.SIX: '6',
    Rank.SEVEN: '7',
    Rank.EIGHT: '8',
    Rank.NINE: '9',
    Rank.TEN: 'T',
    Rank.JACK: 'J',
    Rank.QUEEN: 'Q',
    Rank.KING: 'K',
}

SUIT_TO_STRING = {
    Suit.HEARTS: 'H',
    Suit.DIAMONDS: 'D',
    Suit.CLUBS: 'C',
    Suit.SPADES: 'S',
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{RANK_TO_STRING[self.rank]}{SUIT_TO_STRING[self.suit]}"
    
    def __repr__(self):
        return f"Card(rank={self.rank}, suit={self.suit})"
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class Hand:
    def __init__(self):
        self.cards = []
    
    def peek(self):
        return self.cards[0]
    
    def add_cards(self, cards):
        self.cards.extend(cards)

    def is_empty(self):
        return len(self.cards) == 0

    def deal(self, n, replacement_cards=[], random_state=None):
        curr_num_cards = len(self.cards)
        if n < curr_num_cards:
            # if n is less than the number of cards, it's easy
            cards = self.cards[0: n]
            del self.cards[0: n]
        else:
            # otherwise, we return everything we have so far
            cards = self.cards[0:]
            self.cards = replacement_cards
            # and shuffle the replacement cards in
            # example: before deal: [AS]
            # we deal 2
            # cards = [AS]
            # replacement cards [AH, KH, QH]
            # self.cards = [AH, KH, QH]
            # shuffle cards
            # deal 1 more
            # cards = [AS, KH]
            self.shuffle(random_state)
            cards.extend(self.cards[0: n - curr_num_cards])
            del self.cards[0: n - curr_num_cards]

        return cards

    def shuffle(self, random_state=None):
        if random_state is not None:
            random.seed(random_state)
        random.shuffle(self.cards)

    def __str__(self):
        hand = ""
        for card in self.cards:
            hand += str(card) + " "
        return hand
    
    def hidden(self):
        hand = ""
        for _ in range(len(self.cards) // 2):
            hand += ".. "
        hand += "\n"
        for _ in range(len(self.cards) // 2, len(self.cards)):
            hand += ".. "
        return hand


class Deck(Hand):
    def __init__(self, include_jokers=False):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
    

class Knowledge:
    def __init__(self):
        self.opp_hand = Hand()
        self.own_hand = Hand()


class Player:
    def __init__(self):
        self.hand = Hand()
        self.has_called_cambio = False
        self.knowledge = Knowledge()
        self.id = uuid4()
    
    def __eq__(self, other):
        return self.id == other.id
    
    def handle_card(self, card, random_state=None):
        # figure out whether to replace or play this card
        if random_state is not None:
            random.seed(random_state)
        decision = random.random()
        if decision > 0.5:
            return self.replace_card(card)
        else:
            return self.play_card(card)
    
    def replace_card(self, card, random_state=None):
        if self.knowledge.own_hand.is_empty():
            return Action.NONE, None, None
        own_index = 0 # pick an index
        return Action.REPLACE, None, own_index

    def play_card(self, card, random_state=None):
        should_play = True
        if not should_play:
            return Action.NONE, None, None
        if card.rank == Rank.SEVEN or card.rank == Rank.EIGHT:
            # view one of opp's cards
            if self.knowledge.opp_hand.is_empty():
                return Action.NONE, None, None
            opp_index = 0 # pick any random one you don't know, but maybe also weight whether the opp has kept the card for a while/knows what it is
            return Action.SHOW, opp_index, None
        if card.rank == Rank.NINE or card.rank == Rank.TEN:
            # view one of own cards
            if self.knowledge.own_hand.is_empty():
                return Action.NONE, None, None
            own_index = 0 # pick any random one you don't know
            return Action.SHOW, None, own_index
        if card.rank == Rank.JACK or card.rank == Rank.QUEEN:
            # swap two cards
            if self.knowledge.opp_hand.is_empty() or self.knowledge.own_hand.is_empty():
                return Action.NONE, None, None
            opp_index = 0 # generate this somehow
            own_index = 0 # generate this somehow
            return Action.SWAP, opp_index, own_index
        if card.rank == Rank.KING:
            # view one of opp's card and swap two cards
            if self.knowledge.opp_hand.is_empty():
                return Action.NONE, None, None
            opp_index = 0 # pick any random one you don't know, but maybe also weight whether the opp has kept the card for a while/knows what it is
            return Action.SHOW_AND_SWAP, opp_index, None
        return Action.NONE, None, None
    
    def try_discard(self, top_card):
        # things to consider: right now, we are *always* favoring to throw away own own cards
        # however, there should be an EV calculation to ask oneself if it's better to throw away own card
        # or better to give the opp an extra card
        for i, card in enumerate(self.knowledge.own_hand.cards):
            if card is not None and top_card.rank == card.rank:
                return Action.DISCARD, None, i
        for i, card in enumerate(self.knowledge.opp_hand.cards):
            card = self.knowledge.opp_hand.cards[i]
            if card is not None and top_card.rank == card.rank:
                return Action.DISCARD, i, None
        return Action.NONE, None, None

    def decide_cambio(self, called_cambio, random_state=None):
        if called_cambio:
            return
        if self.knowledge.own_hand.is_empty():
            self.call_cambio()
            return
        if random_state is not None:
            random.seed(random_state)
        decision = random.random()
        if decision > 0.9:
            self.call_cambio()

    def call_cambio(self):
        self.has_called_cambio = True


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
