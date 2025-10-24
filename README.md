Currently gonna have the game keep track of what's actually going on. This is kinda like the universe in the real world, with the cards already being deterministic. In other words, the universe knows all the cards already that are face down and all the cards in order in the deck.

Each player also has a knowledge dict, which basically just has what that player currently knows. Not entirely sure if this is the most efficient approach, but I figured this most accurately represents what happens in real life.

thoughts on discard

# there is a threshold that represents the skill to determine which player will go first

# we will always favor the player who has their own cards, however. in general, let's

# say the person throwing away their own card wins 80% of the time, assuming same skill level

# roll a dice between 1 and 6. defender gets a plus roll for defense. but maybe there's an additional skill level too.

# dunno how biased i want this to be. let's just say it can be between 1 and 6.

# does this stuff matter anyway lol? let's just assume they're both equally good for now

some things that i still need to implement:

- weights for the probabilities of doing certain actions
- calculating the EV of the unknown cards
- have a random strategy maybe and have it iteratively improve each time?
- run 1 million games or something

- be able to actually play against this bot

ideally, everytime the deck becomes empty, we just put some replacement cards in and shuffle the cards again
done

now, i can run 1 million simulations of the game. it seems to be working quite well. player 1 wins 50.3104% of the time, which is interesting to see that going first does have a slight advantage, but not as much as i thought

hyperparameters:

- probability of winning the discard race on defense
- number of games

probabilities:

- probability of keeping a card (or throwing it away)
  => depends on what card it is
- probability of calling cambio on any given round

array of weights

- index 0-13: probability of keeping an Ace - Black King + Red King
- index 14: probability of calling cambio

wait, but these weights are not static. like they depend on the given situation.
realistically, as a human player, you can only really keep track of whether the 2 red kings have been played, the aces, and the 2's. possibly the face cards as well. outside of that, it's pretty hard to keep a good running sum of the total cards left. and it's really hard once the deck is shuffled again. perhaps we can assume optimal play for the bot for now. so it knows exactly the running sum and
the EV of a random unknown card.

what are the inputs in this situation?

- own_hand knowledge
- opp_hand knowledge
  advanced knowledge
- EV of a random card
