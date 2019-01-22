from django.shortcuts import render, loader, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from bowling.models import Game, ScoreSheet, Round
from bowling.utils import format_score_sheet, update_score_sheet, create_new_game
from bowling.serializers import GameSerializer, ScoreSheetSerializer

"""
since a lot of the requirements were vague
and everyone I could reach was on holiday vacation
I made a web app that uses Html and a REST api that just returns JSON
"""


def index(request):
    """The endpoint for the index page

    Used in the Web App

    URL
    ----------
    bowling/app/

    Parameters
    ----------
    request
        the request from the user

    Returns
    ----------
    html
        bowling/index.html
    """
    game_list = Game.objects.order_by('-id').filter(complete=False)
    context = {
        'game_list': game_list,
    }
    return render(request, 'bowling/index.html', context)


def game(request, game_id, error_message=False):
    """The endpoint for a specific game

    Used in the Web App

    URL
    ----------
    bowling/app/<int:game_id>/

    Parameters
    ----------
    request
        the request from the user
    game_id : int
        the game_id of the game to retrieve
    error_message : str, optional
        the error_message to display

    Returns
    ----------
    html
        bowling/game.html
    """
    game = get_object_or_404(Game, pk=game_id)
    score_sheet = get_object_or_404(ScoreSheet, game_id=game_id)
    formatted_score = format_score_sheet(get_list_or_404(Round, score_sheet_id=score_sheet.id), score_sheet)
    return render(request, 'bowling/game.html', {
        'game': game,
        'score': formatted_score,
        'error_message': error_message
    })


def new_game(request):
    """The endpoint to create a new game

    Used in the Web App

    URL
    ----------
    bowling/app/newgame/

    Returns
    ----------
    html
        bowling/game.html
    """
    data = create_new_game()

    return HttpResponseRedirect(reverse('bowling:game', args=(data['game'].id,)))


def throw(request, game_id):
    """The endpoint for adding a throw to the game

    Used in the Web App

    URL
    ----------
    bowling/app/<int:game_id>/throw/

    Returns
    ----------
    html
        bowling/game.html
    """
    g = get_object_or_404(Game, pk=game_id)

    score_sheet = get_object_or_404(ScoreSheet, game_id=game_id)
    rounds = get_list_or_404(Round.objects.order_by('round'), score_sheet_id=score_sheet.id)
    pins = request.POST['pins']

    try:
        error = update_score_sheet(g, score_sheet, rounds, pins)

        if not error:
            return HttpResponseRedirect(reverse('bowling:game', args=(game_id,)))
    except:
        return game(request, game_id, error_message='Error adding throw')
        # raise
    else:
        return game(request, game_id, error_message=error)


@csrf_exempt
def api_games(request):
    """The endpoint for GET and POST of the games resource

    Used in the REST api

    URL
    ----------
    bowling/api/games/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    if request.method == 'GET':
        return api_games_get(request)

    elif request.method == 'POST':
        return api_games_post(request)

    return HttpResponse("Error {method} doesn't exist.".format(method=request.method), status=500)


def api_games_get(request):
    """GET all the games

    Used in the REST api

    URL
    ----------
    bowling/api/games/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    serializer = GameSerializer(Game.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)


def api_games_post(request):
    """POST a game

    if the data contains an id and that resource exist, it will update that resource;
    otherwise create a new game

    Used in the REST api

    URL
    ----------
    bowling/api/games/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    if request.body:
        data = json.loads(request.body.decode("utf-8"))
    else:
        data = {}

    created = True
    id = data.get('id')
    if id:
        game, created = Game.objects.get_or_create(pk=id)
        serializer = GameSerializer(game, data=data)
    else:
        serializer = GameSerializer(data=data)

    if serializer.is_valid():
        serializer.save()

        status = 200
        if created:
            status = 201

        return JsonResponse(serializer.data, safe=False, status=status)
    else:
        return HttpResponse(str(serializer.errors), status=500)


@csrf_exempt
def api_games_id(request, game_id):
    """The endpoint for GET, PUT, PATCH, and DELETE of a game resource

    Used in the REST api

    URL
    ----------
    bowling/api/games/<int:game_id>/

    Returns
    ----------
    json
        a serialized version of the resource
    """

    if request.method == 'GET':
        return api_games_get_id(request, game_id)

    elif request.method == 'PUT':
        return api_games_put_id(request, game_id)

    elif request.method == 'PATCH':
        return api_games_patch_id(request, game_id)

    elif request.method == 'DELETE':
        return api_games_delete_id(request, game_id)

    return HttpResponse("Error {method} doesn't exist.".format(method=request.method), status=500)


def api_games_get_id(request, game_id):
    """GET the game

    Used in the REST api

    URL
    ----------
    bowling/api/games/<int:game_id>/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    serializer = GameSerializer(get_object_or_404(Game, pk=game_id))
    return JsonResponse(serializer.data, safe=False)


def api_games_delete_id(request, game_id):
    """DELETE the game

    Used in the REST api

    URL
    ----------
    bowling/api/games/<int:game_id>/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    game = get_object_or_404(Game, pk=game_id)
    serializer = GameSerializer(game)
    response = JsonResponse(serializer.data, safe=False)
    game.delete()
    return response


def api_games_patch_id(request, game_id):
    """PATCH the game

    Used in the REST api

    URL
    ----------
    bowling/api/games/<int:game_id>/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    if request.body:
        data = json.loads(request.body.decode("utf-8"))
    else:
        data = {}

    game = get_object_or_404(Game, pk=game_id)
    serializer = GameSerializer(game, data=data)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(str(serializer.errors), status=500)


def api_games_put_id(request, game_id):
    """PUT the game

    Used in the REST api

    URL
    ----------
    bowling/api/games/<int:game_id>/

    Returns
    ----------
    json
        a serialized version of the resource
    """
    if request.body:
        data = json.loads(request.body.decode("utf-8"))
    else:
        data = {}

    g = Game.objects.filter(pk=game_id)
    created = not g.count()

    g.delete()

    game = Game.objects.create(pk=game_id)
    serializer = GameSerializer(game, data=data)

    if serializer.is_valid():
        serializer.save()

        status = 200
        if created:
            status = 201

        return JsonResponse(serializer.data, safe=False, status=status)
    else:
        return HttpResponse(str(serializer.errors), status=500)
