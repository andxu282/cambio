from models import Rank, Suit

def score_of_card(card):
    if card.rank == Rank.ACE:
        return 1
    if card.rank == Rank.TWO:
        return 2
    if card.rank == Rank.THREE:
        return 3
    if card.rank == Rank.FOUR:
        return 4
    if card.rank == Rank.FIVE:
        return 5
    if card.rank == Rank.SIX:
        return 6
    if card.rank == Rank.SEVEN:
        return 7
    if card.rank == Rank.EIGHT:
        return 8
    if card.rank == Rank.NINE:
        return 9
    if card.rank == Rank.TEN:
        return 10
    if card.rank == Rank.JACK or card.rank == Rank.QUEEN:
        return 11
    if card.rank == Rank.KING:
        if card.suit == Suit.CLUBS or card.suit == Suit.SPADES:
            return 30
        else:
            return -1

def get_score(player):
    score = 0
    for card in player.hand.cards:
        score += score_of_card(card)
    return score