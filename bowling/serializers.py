from rest_framework import serializers

from bowling.models import Game, ScoreSheet, Round
from bowling.utils import update_score
from bowling.utils import check_update_or_create

class RoundSerializer(serializers.ModelSerializer):
    """
    A Serializer to serialize a Round Model
    """

    round = serializers.IntegerField(min_value=0, max_value=10)
    throw_1 = serializers.IntegerField(allow_null=True,min_value=0, max_value=10,default=None)
    throw_2 = serializers.IntegerField(allow_null=True,min_value=0, max_value=10,default=None)

    class Meta:
        fields = ('id', 'round', 'throw_1', 'throw_2', 'score')
        model = Round

    def validate(self, data):
        if data['round'] != 9 and \
                data['throw_1'] is not None and \
                data['throw_2'] is not None and \
                data['throw_1'] + data['throw_2'] > 10:
            raise serializers.ValidationError("Sum of throws must be at most 10")
        elif data['round'] != 9 and \
                data['throw_1'] == 10 and \
                data['throw_2'] is not None:
            raise serializers.ValidationError("Can't have a second throw if strike")
        return data


class ScoreSheetSerializer(serializers.ModelSerializer):
    """
    A Serializer to serialize a ScoreSheet Model
    """

    rounds = RoundSerializer(many=True)
    throw_filler = serializers.IntegerField(allow_null=True,min_value=0, max_value=10,default=None)

    class Meta:
        depth = 1
        fields = ('id', 'throw_filler', 'rounds')
        model = ScoreSheet

    def _dup_rounds(self, rounds):
        found = set()
        for r in rounds:
            if r['round'] in found:
                return True
            found.add(r['round'])
        return False

    def validate_rounds(self, rounds):
        if self._dup_rounds(rounds):
            raise serializers.ValidationError("Can't have duplicate rounds")
        return rounds

    def _valid_final_strike(self, round, filler):
        if round['throw_2'] is not None:
            if round['throw_2'] == 10:
                return
            elif filler is not None and \
                    round['throw_2'] + filler > 10:
                raise serializers.ValidationError("Sum of throws must be at most 10")
        return

    def _valid_final_spare(self, round, filler):
        return

    def _valid_final_normal(self, round, filler):
        if filler is not None:
            raise serializers.ValidationError("Filler must be None if no strike or spare")
        elif round['throw_1'] is not None and \
                round['throw_2'] is not None and \
                round['throw_1'] + round['throw_2'] > 10:
            raise serializers.ValidationError("Sum of throws must be at most 10")
        return

    def _valid_final_round(self, round, filler):
        if round['throw_1'] is not None:
            # check if strike
            if round['throw_1'] == 10:
                return self._valid_final_strike(round, filler)
            elif round['throw_2'] is not None and \
                    round['throw_1'] + round['throw_2'] == 10:
                return self._valid_final_spare(round, filler)
        return self._valid_final_normal(round, filler)

    def validate(self, data):
        for r in data['rounds']:
            if r['round'] == 9:
                self._valid_final_round(r, data['throw_filler'])

        return data


class GameSerializer(serializers.ModelSerializer):
    """
    A Serializer to serialize a Game Model
    """
    score_sheets = ScoreSheetSerializer(many=True,required=False)

    class Meta:
        depth = 2
        fields = ('id', 'throw', 'complete', 'score_sheets')
        model = Game

    def create(self, validated_data):
        """Creates a Game model from the serialized data

        Most of this code should be somewhere else. If I was
        going to be maintaining the project longer I would find it
        a better home, but this is my first time writing a django
        app and I'm not sure where the best place is. It feels like
        this should be split between the other Serializers, but everything
        I read in the documentation had the create or update happening in
        one method.

        There is probably also a way to make a stored procedure that could save
        all this data in one call

        Returns
        ----------
        Game
            A Game model populated with the serialized data
        """

        score_sheet_datas = validated_data.pop('score_sheets', [])
        game = Game.objects.create(**validated_data)

        for score_sheet_data in score_sheet_datas:

            # hold the round data
            round_datas = dict()
            rounds = []

            for round_data in score_sheet_data.pop('rounds', []):
                round_datas[round_data['round']] = round_data

            # create the score sheet model
            score_sheet = ScoreSheet.objects.create(game_id=game.id, **score_sheet_data)

            # add rounds in the correct order
            for r in range(0, 10):
                if r not in round_datas:
                    round = Round.objects.create(score_sheet_id=score_sheet.id,round=r)
                    rounds.append(round)
                    score_sheet.rounds.add(round)
                else:
                    round = Round.objects.create(score_sheet_id=score_sheet.id,**round_datas[r])
                    rounds.append(round)
                    score_sheet.rounds.add(round)

            # update the score of the rounds
            update_score(score_sheet, rounds)

            # save everything
            for r in rounds:
                r.save()

            score_sheet.save()
            game.score_sheets.add(score_sheet)


        game.save()

        return game

    def update(self, game, validated_data):
        """Creates a Game model from the serialized data

        Returns
        ----------
        Game
            A Game model populated with the serialized data
        """
        score_sheet_datas = validated_data.pop('score_sheets', [])

        game.throw = validated_data.get('throw', game.throw)
        game.complete = validated_data.get('complete', game.complete)

        for score_sheet_data in score_sheet_datas:

            # hold the round data
            round_datas = dict()
            rounds = []

            for round_data in score_sheet_data.pop('rounds', []):
                round_datas[round_data['round']] = round_data

            # create the score sheet model
            score_sheet, created = check_update_or_create(score_sheet_data, ScoreSheet, game_id=game.id)

            # add rounds in the correct order
            for r in range(10):
                if r not in round_datas:
                    round, created = Round.objects.get_or_create(score_sheet_id=score_sheet.id, round=r)
                    rounds.append(round)
                    score_sheet.rounds.add(round)
                else:
                    round, created = check_update_or_create(round_datas[r], Round, score_sheet_id=score_sheet.id,round=r)
                    rounds.append(round)
                    score_sheet.rounds.add(round)

            # update the score of the rounds
            update_score(score_sheet, rounds)

            # save everything
            for r in rounds:
                r.save()

            score_sheet.save()
            game.score_sheets.add(score_sheet)


        game.save()

        return game
