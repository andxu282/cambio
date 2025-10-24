import unittest
from models import Player, Card, Rank, Suit, Action, Hand
from simulation import Game

class TestHand(unittest.TestCase):
    def setUp(self):
        self.hand = Hand()
    
    def test_deal(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        king = Card(Rank.KING, Suit.HEARTS)
        self.hand.add_cards([ace, king])
        drawn_card = self.hand.deal(1)
        self.assertEqual(drawn_card[0], ace)

    def test_deal_two(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        king = Card(Rank.KING, Suit.HEARTS)
        queen = Card(Rank.QUEEN, Suit.HEARTS)
        self.hand.add_cards([ace, king, queen])
        drawn_cards = self.hand.deal(2)
        self.assertEqual(len(drawn_cards), 2)
        self.assertEqual(drawn_cards[0], ace)
        self.assertEqual(drawn_cards[1], king)
    
    def test_deal_two_from_two(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        king = Card(Rank.KING, Suit.HEARTS)
        queen = Card(Rank.QUEEN, Suit.HEARTS)
        jack = Card(Rank.JACK, Suit.HEARTS)
        ten = Card(Rank.TEN, Suit.HEARTS)
        nine = Card(Rank.NINE, Suit.HEARTS)
        eight = Card(Rank.EIGHT, Suit.HEARTS)
        seven = Card(Rank.SEVEN, Suit.HEARTS)
        replacement_cards = [queen, jack, ten, nine, eight, seven]
        self.hand.add_cards([ace, king])
        drawn_cards = self.hand.deal(2, replacement_cards, 0)
        self.assertEqual(len(drawn_cards), 2)
        self.assertEqual(drawn_cards[0], ace)
        self.assertEqual(drawn_cards[1], king)
        self.assertEqual(len(self.hand.cards), 6)
        self.assertEqual(self.hand.cards[0], eight)
        self.assertEqual(self.hand.cards[1], ten)
        self.assertEqual(self.hand.cards[2], jack)
        self.assertEqual(self.hand.cards[3], queen)
        self.assertEqual(self.hand.cards[4], seven)
        self.assertEqual(self.hand.cards[5], nine)
    
    def test_deal_two_from_one(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        queen = Card(Rank.QUEEN, Suit.HEARTS)
        jack = Card(Rank.JACK, Suit.HEARTS)
        ten = Card(Rank.TEN, Suit.HEARTS)
        nine = Card(Rank.NINE, Suit.HEARTS)
        eight = Card(Rank.EIGHT, Suit.HEARTS)
        seven = Card(Rank.SEVEN, Suit.HEARTS)
        replacement_cards = [queen, jack, ten, nine, eight, seven]
        self.hand.add_cards([ace])
        drawn_cards = self.hand.deal(2, replacement_cards, 0)
        self.assertEqual(len(drawn_cards), 2)
        self.assertEqual(drawn_cards[0], ace)
        self.assertEqual(drawn_cards[1], eight)
        self.assertEqual(len(self.hand.cards), 5)
        self.assertEqual(self.hand.cards[0], ten)
        self.assertEqual(self.hand.cards[1], jack)
        self.assertEqual(self.hand.cards[2], queen)
        self.assertEqual(self.hand.cards[3], seven)
        self.assertEqual(self.hand.cards[4], nine)


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player()

    def test_handle_card(self):
        card = Card(Rank.ACE, Suit.DIAMONDS)
        action, opponent_index, own_index = self.player.handle_card(card, random_state=0)
        self.assertEqual(action, Action.REPLACE)
        self.assertIsNone(opponent_index)
        self.assertIsNotNone(own_index)

    def test_replace_card(self):
        card = Card(Rank.TWO, Suit.DIAMONDS)
        action, opponent_index, own_index = self.player.replace_card(card, random_state=0)
        self.assertEqual(action, Action.REPLACE)
        self.assertIsNone(opponent_index)
        self.assertIsNotNone(own_index)
    
    def test_play_none_power_card(self):
        card = Card(Rank.SIX, Suit.SPADES)
        action, opponent_index, own_index = self.player.play_card(card, random_state=0)
        self.assertEqual(action, Action.NONE)
        self.assertIsNone(opponent_index)
        self.assertIsNone(own_index)
    
    def test_play_7_or_8(self):
        card = Card(Rank.SEVEN, Suit.DIAMONDS)
        action, opponent_index, own_index = self.player.play_card(card, random_state=0)
        self.assertEqual(action, Action.SHOW)
        self.assertIsNotNone(opponent_index)
        self.assertIsNone(own_index)
    
    def test_play_9_or_T(self):
        card = Card(Rank.TEN, Suit.DIAMONDS)
        action, opponent_index, own_index = self.player.play_card(card, random_state=0)
        self.assertEqual(action, Action.SHOW)
        self.assertIsNone(opponent_index)
        self.assertIsNotNone(own_index)
    
    def test_play_J_or_Q(self):
        card = Card(Rank.JACK, Suit.DIAMONDS)
        action, opponent_index, own_index = self.player.play_card(card, random_state=0)
        self.assertEqual(action, Action.SWAP)
        self.assertIsNotNone(opponent_index)
        self.assertIsNotNone(own_index)
    
    def test_play_K(self):
        pass

    def test_try_discard_own_fail(self):
        top_card = Card(Rank.ACE, Suit.HEARTS)
        self.player.knowledge.own_hand.cards = [Card(Rank.KING, Suit.SPADES)]
        action, opp_index, own_index = self.player.try_discard(top_card)
        self.assertEqual(action, Action.NONE)
        self.assertIsNone(opp_index)
        self.assertIsNone(own_index)
    
    def test_try_discard_own_success(self):
        top_card = Card(Rank.ACE, Suit.HEARTS)
        self.player.knowledge.own_hand.cards = [Card(Rank.ACE, Suit.SPADES)]
        action, opp_index, own_index = self.player.try_discard(top_card)
        self.assertEqual(action, Action.DISCARD)
        self.assertIsNone(opp_index)
        self.assertEqual(own_index, 0)
    
    def test_try_discard_opp_success(self):
        top_card = Card(Rank.ACE, Suit.HEARTS)
        self.player.knowledge.opp_hand.cards = [Card(Rank.ACE, Suit.SPADES)]
        action, opp_index, own_index = self.player.try_discard(top_card)
        self.assertEqual(action, Action.DISCARD)
        self.assertEqual(opp_index, 0)
        self.assertIsNone(own_index)
        
    def test_try_discard_own_and_opp_success(self):
        top_card = Card(Rank.ACE, Suit.HEARTS)
        self.player.knowledge.own_hand.cards = [Card(Rank.ACE, Suit.SPADES)]
        self.player.knowledge.opp_hand.cards = [Card(Rank.ACE, Suit.CLUBS)]
        action, opp_index, own_index = self.player.try_discard(top_card)
        self.assertEqual(action, Action.DISCARD)
        self.assertIsNone(opp_index)
        self.assertEqual(own_index, 0)



class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        # self.game.player_one.hand.add_cards(self.deck.deal(4))
        # self.game.player_two.hand.add_cards(self.deck.deal(4))
        # self.game.discard.add_cards(self.deck.deal(1))
    
    def test_add_card(self):
        card = Card(Rank.ACE, Suit.HEARTS)
        # add the ace of hearts
        self.game.add_card(self.game.player_one, self.game.player_two, card)
        self.assertEqual(self.game.player_one.hand.cards[0], card)
        self.assertIsNone(self.game.player_one.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.opp_hand.cards[0])

    def test_delete_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace)
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, king)
        
        # delete the ace of hearts
        self.game.delete_card(self.game.player_one, self.game.player_two, 0)
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertIsNone(self.game.player_one.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.opp_hand.cards[0])

    def test_replace_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace)
        king = Card(Rank.KING, Suit.HEARTS)

        # replace the original ace of hearts with a king of hearts
        old_card = self.game.replace_card(self.game.player_one, self.game.player_two, 0, king)
        self.assertEqual(old_card, ace)
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertEqual(self.game.player_one.knowledge.own_hand.cards[0], king)
        self.assertIsNone(self.game.player_two.knowledge.opp_hand.cards[0])

    
    def test_swap_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace)
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_two, self.game.player_one, king)
        # swap the ace of hearts from player_one and the king of hearts from player_two
        self.game.swap_cards(self.game.player_one, self.game.player_two, 0, 0)
        # check hands
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertEqual(self.game.player_two.hand.cards[0], ace)

        # check players' knowledges
        self.assertIsNone(self.game.player_one.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_one.knowledge.opp_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.opp_hand.cards[0])

    def test_swap_card_player_one_knows_own_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace, known_card=True)
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_two, self.game.player_one, king)
        # swap the ace of hearts from player_one and the king of hearts from player_two
        self.game.swap_cards(self.game.player_one, self.game.player_two, 0, 0)
        # check hands
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertEqual(self.game.player_two.hand.cards[0], ace)

        # check players' knowledges
        self.assertIsNone(self.game.player_one.knowledge.own_hand.cards[0])
        self.assertEqual(self.game.player_one.knowledge.opp_hand.cards[0], ace)
        self.assertIsNone(self.game.player_two.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.opp_hand.cards[0])
    
    def test_swap_card_player_one_knows_own_card_and_opp_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace, known_card=True)
        
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_two, self.game.player_one, king)

        self.game.player_one.knowledge.opp_hand.cards[0] = king

        # swap the ace of hearts from player_one and the king of hearts from player_two
        self.game.swap_cards(self.game.player_one, self.game.player_two, 0, 0)
        # check hands
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertEqual(self.game.player_two.hand.cards[0], ace)

        # check players' knowledges
        self.assertEqual(self.game.player_one.knowledge.own_hand.cards[0], king)
        self.assertEqual(self.game.player_one.knowledge.opp_hand.cards[0], ace)
        self.assertIsNone(self.game.player_two.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.opp_hand.cards[0])

    def test_swap_card_player_two_knows_own_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace)
        
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_two, self.game.player_one, king, known_card=True)

        # swap the ace of hearts from player_one and the king of hearts from player_two
        self.game.swap_cards(self.game.player_one, self.game.player_two, 0, 0)
        # check hands
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertEqual(self.game.player_two.hand.cards[0], ace)

        # check players' knowledges
        self.assertIsNone(self.game.player_one.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_one.knowledge.opp_hand.cards[0])
        self.assertIsNone(self.game.player_two.knowledge.own_hand.cards[0])
        self.assertEqual(self.game.player_two.knowledge.opp_hand.cards[0], king)

    def test_swap_card_player_two_knows_own_card_and_opp_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace)

        self.game.player_two.knowledge.opp_hand.cards[0] = ace
        
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_two, self.game.player_one, king, known_card=True)
        

        # swap the ace of hearts from player_one and the king of hearts from player_two
        self.game.swap_cards(self.game.player_one, self.game.player_two, 0, 0)
        # check hands
        self.assertEqual(self.game.player_one.hand.cards[0], king)
        self.assertEqual(self.game.player_two.hand.cards[0], ace)

        # check players' knowledges
        self.assertIsNone(self.game.player_one.knowledge.own_hand.cards[0])
        self.assertIsNone(self.game.player_one.knowledge.opp_hand.cards[0])
        self.assertEqual(self.game.player_two.knowledge.own_hand.cards[0], ace)
        self.assertEqual(self.game.player_two.knowledge.opp_hand.cards[0], king)
    
    def test_show_own_card(self):
        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.add_card(self.game.player_one, self.game.player_two, ace)
        self.game.show_card(self.game.player_one, self.game.player_one, 0)
        self.assertEqual(self.game.player_one.knowledge.own_hand.cards[0], ace)
    
    def test_show_opp_card(self):
        king = Card(Rank.KING, Suit.HEARTS)
        self.game.add_card(self.game.player_two, self.game.player_one, king, known_card=True)
        self.game.show_card(self.game.player_one, self.game.player_two, 0)
        self.assertEqual(self.game.player_one.knowledge.opp_hand.cards[0], king)

    def test_discard_race_no_discards(self):
        queen = Card(Rank.QUEEN, Suit.HEARTS)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, queen)
        self.game.add_card(self.game.player_two, self.game.player_one, jack)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)
        self.assertEqual(self.game.player_one.hand.cards[0], queen)
        self.assertEqual(self.game.player_two.hand.cards[0], jack)

    def test_discard_race_player_one_own_discard(self):
        ace_one = Card(Rank.ACE, Suit.SPADES)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, ace_one, known_card=True)
        self.game.add_card(self.game.player_two, self.game.player_one, jack)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)
        self.assertEqual(len(self.game.player_one.hand.cards), 0)
        self.assertEqual(self.game.player_two.hand.cards[0], jack)
    
    def test_discard_race_player_two_own_discard(self):
        ace_one = Card(Rank.ACE, Suit.SPADES)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, jack)
        self.game.add_card(self.game.player_two, self.game.player_one, ace_one, known_card=True)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)
        self.assertEqual(self.game.player_one.hand.cards[0], jack)
        self.assertEqual(len(self.game.player_two.hand.cards), 0)

    def test_discard_race_player_one_opp_discard(self):
        self.game.deck.shuffle(random_state=0)
        ace_one = Card(Rank.ACE, Suit.SPADES)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, jack)
        self.game.add_card(self.game.player_two, self.game.player_one, ace_one)
        self.game.show_card(self.game.player_one, self.game.player_two, 0)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)

        eight = Card(Rank.EIGHT, Suit.HEARTS)
        four = Card(Rank.FOUR, Suit.HEARTS)

        self.assertEqual(self.game.player_one.hand.cards[0], jack)
        self.assertEqual(self.game.player_two.hand.cards[0], eight)
        self.assertEqual(self.game.player_two.hand.cards[1], four)
    
    def test_discard_race_player_two_opp_discard(self):
        self.game.deck.shuffle(random_state=0)
        ace_one = Card(Rank.ACE, Suit.SPADES)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, ace_one)
        self.game.add_card(self.game.player_two, self.game.player_one, jack)
        self.game.show_card(self.game.player_two, self.game.player_one, 0)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)

        eight = Card(Rank.EIGHT, Suit.HEARTS)
        four = Card(Rank.FOUR, Suit.HEARTS)

        self.assertEqual(self.game.player_one.hand.cards[0], eight)
        self.assertEqual(self.game.player_one.hand.cards[1], four)
        self.assertEqual(self.game.player_two.hand.cards[0], jack)

    # for random_state = 0, dice roll is 0.844, so defense loses, and player_one wins in all flips
    def test_discard_race_player_one_opp_discard_race(self):
        self.game.deck.shuffle(random_state=0)
        ace_one = Card(Rank.ACE, Suit.SPADES)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, jack)
        self.game.add_card(self.game.player_two, self.game.player_one, ace_one, known_card=True)
        self.game.show_card(self.game.player_one, self.game.player_two, 0)

        ace = Card(Rank.ACE, Suit.HEARTS)
        
        self.game.discard_race(ace, random_state=0)

        eight = Card(Rank.EIGHT, Suit.HEARTS)
        four = Card(Rank.FOUR, Suit.HEARTS)

        self.assertEqual(self.game.player_one.hand.cards[0], jack)
        self.assertEqual(self.game.player_two.hand.cards[0], eight)
        self.assertEqual(self.game.player_two.hand.cards[1], four)
    
    def test_discard_race_player_two_opp_discard_race(self):
        self.game.deck.shuffle(random_state=0)
        ace_one = Card(Rank.ACE, Suit.SPADES)
        jack = Card(Rank.JACK, Suit.HEARTS)

        self.game.add_card(self.game.player_one, self.game.player_two, ace_one, known_card=True)
        self.game.add_card(self.game.player_two, self.game.player_one, jack)
        self.game.show_card(self.game.player_two, self.game.player_one, 0)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)

        eight = Card(Rank.EIGHT, Suit.HEARTS)
        four = Card(Rank.FOUR, Suit.HEARTS)

        self.assertEqual(self.game.player_one.hand.cards[0], eight)
        self.assertEqual(self.game.player_one.hand.cards[1], four)
        self.assertEqual(self.game.player_two.hand.cards[0], jack)
    
    def test_discard_race_own_discard_race(self):
        self.game.deck.shuffle(random_state=0)
        ace_one = Card(Rank.ACE, Suit.SPADES)
        ace_two = Card(Rank.ACE, Suit.CLUBS)

        self.game.add_card(self.game.player_one, self.game.player_two, ace_one, known_card=True)
        self.game.add_card(self.game.player_two, self.game.player_one, ace_two, known_card=True)

        ace = Card(Rank.ACE, Suit.HEARTS)
        
        self.game.discard_race(ace, random_state=0)

        self.assertEqual(len(self.game.player_one.hand.cards), 0)
        self.assertEqual(self.game.player_two.hand.cards[0], ace_two)

    def test_discard_race_own_discard_race(self):
        self.game.deck.shuffle(random_state=0)
        ace_one = Card(Rank.ACE, Suit.SPADES)
        ace_two = Card(Rank.ACE, Suit.CLUBS)

        self.game.add_card(self.game.player_one, self.game.player_two, ace_one)
        self.game.add_card(self.game.player_two, self.game.player_one, ace_two)
        self.game.show_card(self.game.player_one, self.game.player_two, 0)
        self.game.show_card(self.game.player_two, self.game.player_one, 0)

        ace = Card(Rank.ACE, Suit.HEARTS)
        self.game.discard_race(ace, random_state=0)

        eight = Card(Rank.EIGHT, Suit.HEARTS)
        four = Card(Rank.FOUR, Suit.HEARTS)

        self.assertEqual(self.game.player_one.hand.cards[0], ace_one)
        self.assertEqual(self.game.player_two.hand.cards[0], eight)
        self.assertEqual(self.game.player_two.hand.cards[1], four)
        

if __name__ == '__main__':
    unittest.main()

