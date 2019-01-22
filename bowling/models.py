from django.db import models


class Game(models.Model):
    """
    A Model to handel the base game and its current state

    Attributes
    ----------
    throw
        The current throw of the game
        divide by 2 to get the current round
    complete
        Is the game finished and should no longer accept changes
    score_sheets
        A list of score sheets associated which this game
    """

    throw = models.PositiveSmallIntegerField(default=0)
    complete = models.BooleanField(default=False)


class ScoreSheet(models.Model):
    """
    A Model to handel the score sheet and its current state

    Attributes
    ----------
    game
        The game associated with this score sheet
    throw_filler
        The extra throw in the tenth round if needed
    rounds
        A list of rounds associated which this score sheet
    """

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='score_sheets')
    throw_filler = models.PositiveSmallIntegerField(null=True)


class Round(models.Model):
    """
    A Model to handel the round and its current throws/score

    Attributes
    ----------
    score_sheet
        The score sheet associated with this round
    round
        The index of this round in the score sheet
    throw_1
        The pins knocked down of the first throw
    throw_2
        The pins knocked down of the second throw
    score
        The total score up to this round

    Methods
    ----------
    is_strike()
        Checks if this round is a strike
    is_spare()
        Checks if this round is a spare
    """

    score_sheet = models.ForeignKey(ScoreSheet, on_delete=models.CASCADE, related_name='rounds')
    round = models.PositiveSmallIntegerField(default=0)
    throw_1 = models.PositiveSmallIntegerField(null=True)
    throw_2 = models.PositiveSmallIntegerField(null=True)
    score = models.PositiveSmallIntegerField(null=True)

    def is_strike(self):
        """Checks if this round is a strike"""
        return self.throw_1 == 10

    def is_spare(self):
        """Checks if this round is a strike"""
        return self.throw_1 + self.throw_2 == 10
