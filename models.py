from enum import Enum
import random
from uuid import uuid4

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
