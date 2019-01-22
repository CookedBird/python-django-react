from django.test import TestCase
from django.test import Client
import json

from bowling.models import Game, ScoreSheet, Round
from bowling.utils import *

# Create your tests here.

class BowlingTestCase(TestCase):
    def test_perfect_game(self):
        data = create_new_game()

        for r in range(0, 12):
            update_score_sheet(data['game'], data['score_sheet'], data['rounds'], 10)

        self.assertEquals(data['game'].complete, True)
        for r in range(0, 10):
            self.assertEquals(data['rounds'][r].score, (r + 1) * 30)

    def test_zero_game(self):
        data = create_new_game()

        for r in range(0, 20):
            update_score_sheet(data['game'], data['score_sheet'], data['rounds'], 0)

        self.assertEquals(data['game'].complete, True)
        for r in range(0, 10):
            self.assertEquals(data['rounds'][r].score, 0)


class BowlingApiTestCase(TestCase):
    def test_api_get(self):
        c = Client()
        response = c.get('/bowling/api/games/', follow=True)

        self.assertEquals(response.status_code, 200)

    def test_api_post_greater_than_10(self):
        c = Client()

        # check that a round can't have a sum greater than 10
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 9, 'throw_2': 2},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

        # check that the first throw can't be greater than 10
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 11},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

        # check that the second throw can't be greater than 10
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 13},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

    def test_api_post_duplicate(self):
        c = Client()

        # check that there can't be duplicate rounds
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

    def test_api_post_strike_second_throw(self):
        c = Client()

        # check that there can't be duplicate rounds
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10, 'throw_2': 1},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

    def test_api_post_final_strike(self):
        c = Client()

        # check a valid strike
        data = {
            "score_sheets": [{
                "throw_filler": 0,
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 1, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 0}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 201)

        # check a valid round where the second throw is a strike
        data = {
            "score_sheets": [{
                "throw_filler": 5,
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 1, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 201)

        # check a valid round where the second throw is not a strike
        data = {
            "score_sheets": [{
                "throw_filler": 5,
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 1, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 5}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 201)

        # check an invalid round where the second throw is not a strike
        data = {
            "score_sheets": [{
                "throw_filler": 6,
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 1, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 5}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

    def test_api_post_final_normal(self):
        c = Client()

        # check a valid throw
        data = {
            "score_sheets": [{
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 1, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 2, "throw_2": 4}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 201)

        # check an invalid throw
        data = {
            "score_sheets": [{
                "rounds": [
                    {"round": 0, "throw_1": 0, 'throw_2': 1},
                    {"round": 1, "throw_1": 0, 'throw_2': 1},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 8, "throw_2": 4}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)

        self.assertEquals(response.status_code, 500)

    def test_api_post_scores(self):
        c = Client()

        # check that a perfect game has a score of 300
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data = json.loads(response.content.decode("utf-8"))
        print(response.content.decode("utf-8"))

        self.assertEquals(data['score_sheets'][0]['rounds'][0]['score'], 30)
        self.assertEquals(data['score_sheets'][0]['rounds'][1]['score'], 60)
        self.assertEquals(data['score_sheets'][0]['rounds'][2]['score'], 90)
        self.assertEquals(data['score_sheets'][0]['rounds'][3]['score'], 120)
        self.assertEquals(data['score_sheets'][0]['rounds'][4]['score'], 150)
        self.assertEquals(data['score_sheets'][0]['rounds'][5]['score'], 180)
        self.assertEquals(data['score_sheets'][0]['rounds'][6]['score'], 210)
        self.assertEquals(data['score_sheets'][0]['rounds'][7]['score'], 240)
        self.assertEquals(data['score_sheets'][0]['rounds'][8]['score'], 270)
        self.assertEquals(data['score_sheets'][0]['rounds'][9]['score'], 300)

        # check a valid game
        data = {
            "score_sheets": [{
                "throw_filler": 8,
                "rounds": [
                    {"round": 0, "throw_1": 9, "throw_2": 1},
                    {"round": 1, "throw_1": 0, "throw_2": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 6, "throw_2": 2},
                    {"round": 5, "throw_1": 7, "throw_2": 3},
                    {"round": 6, "throw_1": 8, "throw_2": 2},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 9, "throw_2": 0},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['score_sheets'][0]['rounds'][0]['score'], 10)
        self.assertEquals(data['score_sheets'][0]['rounds'][1]['score'], 30)
        self.assertEquals(data['score_sheets'][0]['rounds'][2]['score'], 56)
        self.assertEquals(data['score_sheets'][0]['rounds'][3]['score'], 74)
        self.assertEquals(data['score_sheets'][0]['rounds'][4]['score'], 82)
        self.assertEquals(data['score_sheets'][0]['rounds'][5]['score'], 100)
        self.assertEquals(data['score_sheets'][0]['rounds'][6]['score'], 120)
        self.assertEquals(data['score_sheets'][0]['rounds'][7]['score'], 139)
        self.assertEquals(data['score_sheets'][0]['rounds'][8]['score'], 148)
        self.assertEquals(data['score_sheets'][0]['rounds'][9]['score'], 176)

    def test_api_post_twice(self):
        c = Client()

        # post a game with an id
        data = {
            'id': 150,
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data2 = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data2['id'], 150)

        # post a game with the same id
        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 200)

        data2 = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data2['id'], 150)

    def test_api_post_delete(self):
        c = Client()

        # post a game with an id
        data = {
            'id': 200,
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.post('/bowling/api/games/', json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['id'], 200)

        # delete a game with the same id
        response = c.delete('/bowling/api/games/200', content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 200)

        # delete a game with the same id
        response = c.delete('/bowling/api/games/200', content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 404)

    def test_api_put_new(self):
        c = Client()

        # put a game with an id
        id = 312
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.put('/bowling/api/games/' + str(id), json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['id'], id)

    def test_api_put_update(self):
        c = Client()

        # put a game with an id
        id = 101
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.put('/bowling/api/games/' + str(id), json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['id'], id)

        # put again
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                ]}
            ]}

        response = c.put('/bowling/api/games/' + str(id), json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['id'], id)
        self.assertEquals(data['score_sheets'][0]['rounds'][9]['score'], None)

    def test_api_patch(self):
        c = Client()

        # put a game with an id
        id = 536
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 10},
                    {"round": 1, "throw_1": 10},
                    {"round": 2, "throw_1": 10},
                    {"round": 3, "throw_1": 10},
                    {"round": 4, "throw_1": 10},
                    {"round": 5, "throw_1": 10},
                    {"round": 6, "throw_1": 10},
                    {"round": 7, "throw_1": 10},
                    {"round": 8, "throw_1": 10},
                    {"round": 9, "throw_1": 10, "throw_2": 10}
                ]}
            ]}

        response = c.put('/bowling/api/games/' + str(id), json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 201)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['id'], id)
        self.assertEquals(data['score_sheets'][0]['rounds'][9]['score'], 300)

        # put again
        data = {
            "score_sheets": [{
                "throw_filler": 10,
                "rounds": [
                    {"round": 0, "throw_1": 2, "throw_2": 8},
                ]}
            ]}

        response = c.patch('/bowling/api/games/' + str(id), json.dumps(data),
                          content_type='application/json', follow=True)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content.decode("utf-8"))
        self.assertEquals(data['id'], id)
        self.assertEquals(data['score_sheets'][0]['rounds'][9]['score'], 290)