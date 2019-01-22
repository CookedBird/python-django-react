from bowling.models import Game, ScoreSheet, Round


def create_new_game():
    """Creates a new Game model and all its child models

    There is probably a better way to implement this,
    but this is my first time using django and I'm not sure
    where it should go.  A few solutions I found were to
    override the __init__() method of the model, or I could
    create a custom Manager for the models which create
    all the needed child models.

    There is probably also a way to make a stored procedure that could
    create all this data in one call

    Returns
    ----------
    dict
        a dict containing the game, score sheet, and rounds.
    """
    g = Game()
    g.save()
    s = ScoreSheet()
    s.game = g
    s.save()

    rounds = []
    for num in range(10):
        r = Round(round=num, score_sheet=s)
        r.save()
        rounds.append(r)

    return {
        'game': g,
        'score_sheet': s,
        'rounds': rounds
    }


def format_throw_1(throw_1):
    """Format the first throw for being displayed

    Will return an X if it is a strike

    Returns
    ----------
    str
        a string representing the throw
    """
    if throw_1 is not None:
        if throw_1 == 10:
            return 'X'
        return str(throw_1)
    else:
        return ''


def format_throw_2(throw_2, throw_1):
    """Format the second throw for being displayed

    Will return an / if it is a spare

    Returns
    ----------
    str
        a string representing the throw
    """
    if throw_2 is not None and throw_1 is not None:
        if throw_2 + throw_1 == 10:
            return '/'
        elif throw_1 == 10 and throw_2 == 10:  # for the final round
            return 'X'
        return throw_2
    else:
        return ''


def format_score(score):
    """Format the score for being displayed

    Will return an empty string if the score is None

    Returns
    ----------
    str
        a string representing the score
    """
    if score is not None:
        return score
    return ''


def format_round(throw_1, throw_2, score, throw_3=None):
    """Format the round for being displayed

    Returns
    ----------
    dict
        a dict containing the formatted throws and score
    """
    return {
        "throw_1": format_throw_1(throw_1),
        "throw_2": format_throw_2(throw_2, throw_1),
        "throw_3": format_throw_1(throw_3),
        "score": format_score(score),
    }


def format_score_sheet(rounds, score):
    """Format the score sheet for being displayed

    Returns
    ----------
    list
        a list containing each of the formatted rounds
    """
    round_list = []

    # format all but the last round
    for r in range(9):
        round_list.append(format_round(rounds[r].throw_1, rounds[r].throw_2, rounds[r].score))

    # format the last round with the filler throw
    round_list.append(format_round(rounds[9].throw_1, rounds[9].throw_2, rounds[9].score, throw_3=score.throw_filler))

    return round_list


def find_bonus(round, throws, remaining):
    """Find the bonus for a strike or spare

    Parameters
    ----------
    round : int
        the round the throw was made
    throws : list
        a list of each of the throws made on the score sheet
    remaining : int
        how many throws to be added to the bonus (2 for strike, 1 for spare)

    Returns
    ----------
    int
        the number of bonus points for the strike/spare
    """
    # we start checking the throws from the next round
    round += 1
    throw = round * 2

    # if this is the filler throw, go back one round
    if round == 10 and remaining == 2:
        throw -= 1

    # the bonus points awarded
    bonus = 0

    # iterate through the throws until we have the needed amount
    # or there are no more to check
    while remaining > 0 and throw <= 20:
        p = throws[throw]
        if p is not None:
            bonus += p
            remaining -= 1
        throw += 1

    # if we didn't find the needed amount, return None
    if remaining == 0:
        return bonus
    else:
        return None


def update_score(score_sheet, rounds):
    """Update the scores for the score sheet

    Parameters
    ----------
    score_sheet : ScoreSheet
        the ScoreSheet to update
    rounds : list
        a list of the rounds on the score sheet
    """
    # create a list of throws for finding any
    # bonus points awarded for strikes/spares
    throws = []
    for r in rounds:
        throws.append(r.throw_1)
        throws.append(r.throw_2)
    throws.append(score_sheet.throw_filler)

    # go through each round and update the score
    for i, round in enumerate(rounds):

        # get the score of the last round
        old_score = 0
        if i != 0:
            old_score = rounds[i - 1].score

        # if the previous round has a score and this round has a throw
        # we can score it
        if old_score is not None and round.throw_1 is not None:
            # if round is a strike, find and add bonus points to the total
            if round.is_strike():
                bonus = find_bonus(i, throws, 2)
                if bonus is not None:
                    round.score = round.throw_1 + bonus + old_score
                else:
                    round.score = None

            # if there is a second throw
            elif round.throw_2 is not None:
                # if its a spare, find and add bonus points to the total
                if round.is_spare():  # spare
                    bonus = find_bonus(i, throws, 1)
                    if bonus is not None:
                        round.score = round.throw_1 + round.throw_2 + bonus + old_score
                    else:
                        round.score = None

                # if normal round, add just the two throws
                else:
                    round.score = round.throw_1 + round.throw_2 + old_score
        # other wise we clear the score for this round
        else:
            round.score = None


def update_score_sheet(game, score_sheet, rounds, pins):
    """Update the score sheet by adding the pins to the current throw

    Parameters
    ----------
    game : Game
        the Game to update
    score_sheet : ScoreSheet
        the ScoreSheet to update
    rounds : list
        a list of the rounds on the score sheet
    pins : int
        the number of pins knocked down

    Returns
    ----------
    str
        the error text (or None if no errors)
    """
    # check if this is the first throw of the round
    first = game.throw % 2 == 0
    # get which round this is
    round = int(game.throw / 2)

    # validate the data

    # check if the game is already completed
    if game.complete:
        return 'Game is over'

    # check that pins is a number
    try:
        pins = int(pins)
    except:
        return 'Pins must be a number'

    # check that pins is between 0 and 10
    if pins < 0 or pins > 10:
        return 'Pins knocked down have to be at least 0 and at most 10'

    # if filler throw and final round wasn't a strike or spare
    # make sure the total pins knocked down is less than 10
    if game.throw == 20 and not rounds[9].throw_2 == 10 and not rounds[9].is_spare() and rounds[9].throw_2 + pins > 10:
        return 'Total Pins knocked down must be at most 10'
    # if second throw and not final round is a strike
    if not first and not rounds[9].is_strike():
        last_throw = rounds[round].throw_1
        if last_throw is not None and pins + last_throw > 10:
            return 'Total Pins knocked down must be at most 10'

    # check where the pins should be saved

    # if it is the filler throw
    if game.throw == 20:
        score_sheet.throw_filler = pins
    # if it was the first of the round
    elif first:
        rounds[round].throw_1 = pins
    # if it was the second of the round
    else:
        rounds[round].throw_2 = pins

    # check how the game should increment the throw, or be marked as complete

    # if this is the first throw of the last round and they got a strike
    if game.throw == 18 and pins == 10:
        game.throw += 1
    # if this is the second throw of the last round and they didn't get a spare
    elif game.throw == 19 and not (rounds[round].is_spare() or rounds[round].is_strike()):
        game.complete = True
    # if this is the filler throw
    elif game.throw >= 20:
        game.complete = True
    # if they got a strike
    elif first and pins == 10:
        game.throw += 2
    # normal case
    else:
        game.throw += 1

    # update the score on the score sheet
    update_score(score_sheet, rounds)

    # save all the data
    game.save()
    score_sheet.save()
    for r in rounds:
        r.save()

    # return no errors
    return None


def check_update_or_create(data, model, **kwargs):
    """Checks serialized data to see if the Model should be created or updated

    Parameters
    ----------
    data : object
        data containing the id (if there is any) and
    model : Model
        the Model to query
    kwargs
        arguments to be passed to the update_or_create method

    Returns
    ----------
    tuple (Model, bool)
        the model and whether it was created
    """
    id = data.get('id')
    if id:
        data.pop('id')
        return model.objects.update_or_create(pk=id,**kwargs, defaults=data)
    else:
        return model.objects.update_or_create(**kwargs, defaults=data)
