----------
Bowling REST api
----------
This django server is for creating and scoring a bowling game.

----------
Since there was a little ambiguity with the requirements, I made a few assumptions. I wasn’t sure if it was supposed to be a service that returned whole html web pages or just a simple api that returned json, so I made both. 

-bowling/app/ - a web app where a simple front end is presented and a user can add a throw containing the number of pins they knocked down and it will be added to the score sheet. Returns html.
-bowling/api/ - a rest api where the user can use the standard GET, POST, PUT, PATCH, and DELETE methods to add, create, update, and delete bowling games. Returns json.

----------
There are five main files that I worked on for this service.

-views.py – contains endpoints needed to interact with the service.
-models.py – contains models used to store data.
-serializers.py – contains the serializers that can turn json data into the models and vice versa.
-utils.py – a middle layer for processing data, such as business logic.
-test.py – contains units test.

I only used three models for this service. 

-Game - which contains the current throw, whether the game is complete, and the score sheets. 
-ScoreSheet - which contains the filler throw and the rounds.
-Round – which contains the first and second throw, and the score.

I tried to set it up in such a way where it would be easy to add a Player model, that could have a one-to-many relation with ScoreSheet. Adding that seemed out of the scope of this project though, so I didn’t implement it.

----------
Web App
----------
All endpoints behind /app return html.

GET
-bowling/app/ - returns all the incomplete games.
-bowling/app/<int:game_id>/ - returns a specific game.
POST
-bowling/app/newgame/ - creates a new game and redirects the user to that game’s page.
-bowling/app/<int:game_id>/throw – takes number of pins knocked down and adds the pins to the active throw, updating the score and incrementing the active throw.

----------
REST Api
----------
All endpoints behind /api return json.

-bowling/api/games/
--GET – returns all the games.
--POST – if the data contains a game id, create or update that game, otherwise create a new game.

-bowling/api/games/<int:game_id>/
--GET – returns a specific game.
--PUT – create or replace the game.
--PATCH – if the game exists, update the game, otherwise return 404.
--DELETE – delete the game if it exists, otherwise return 404.

Every POST, PUT, and PATCH endpoint should include a request body containing information about what needs to be changed.  See example json below

{
	"id": int, 
	"throw": int, 
	"complete": boolean, 
	"score_sheets": [{
		"throw_filler": int, 
		"rounds": [
			{"round": 0, "throw_1": int, "throw_2": int}, 
			{"round": 1, "throw_1": int, "throw_2": int}, 
			{"round": 2, "throw_1": int, "throw_2": int}, 
			{"round": 3, "throw_1": int, "throw_2": int}, 
			{"round": 4, "throw_1": int, "throw_2": int}, 
			{"round": 5, "throw_1": int, "throw_2": int}, 
			{"round": 6, "throw_1": int, "throw_2": int}, 
			{"round": 7, "throw_1": int, "throw_2": int}, 
			{"round": 8, "throw_1": int, "throw_2": int}, 
			{"round": 9, "throw_1": int, "throw_2": int}
		]}
	]
}

id – The id of the game.
throw – 0 indexed throw position. e.g: The second throw on round 5 would be 10
complete – whether or not the game is over.
score_sheets – list of score sheets, presumably one for each player. Each score sheet can optionally include a throw_filler and a list of rounds. Rounds not provided will be created for you with default throws of null. 
