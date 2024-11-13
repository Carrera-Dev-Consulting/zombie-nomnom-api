from zombie_nomnom import Command, Die, DieBag, DieColor, Face, Player, RoundState
from zombie_nomnom_api.game import Game, GameMaker
from zombie_nomnom_api.graphql_app.dependencies import DIContainer
from .schema import (
    Query,
    Mutation,
    GameResource,
    Move,
    DieResource,
    DieBagResource,
    PlayerResource,
    Round,
)
from .dependencies import bootstrap


@Query.games
def games_resolver(_, __, id: str = None, dependencies: DIContainer = bootstrap()):
    maker: GameMaker = dependencies[GameMaker]
    if id is not None:
        value = maker[id]
        return [value] if value else []
    return list(maker)


@Mutation.createGame
def create_game_resolver(
    _, __, players: list[str], dependencies: DIContainer = bootstrap()
):
    if len(players) == 0:
        return {"errors": ["No players provided"], "game": None}
    maker: GameMaker = dependencies[GameMaker]
    game = maker.make_game(players)
    return {"errors": [], "game": game}


@GameResource.gameOver
def game_over_resolver(game: Game, _):
    instance = game.game
    return instance.game_over


@GameResource.winner
def game_over_resolver(game: Game, _):
    instance = game.game
    if instance.game_over:
        return instance.winner
    return None


@GameResource.round
def game_round_resolver(game: Game, _):
    instance = game.game
    return instance.round


@GameResource.players
def game_players_resolver(game: Game, _):
    instance = game.game
    return instance.players


@GameResource.moves
def moves_resolver(game: Game, _):
    instance = game.game
    return instance.commands


@Move.name
def move_name_resolver(move: tuple[Command, RoundState], _):
    [command, _] = move
    return type(command).__name__


@Move.player
def move_player_resolver(move: tuple[Command, RoundState], _):
    [_, state] = move
    return state.player


@DieResource.sides
def die_sides_resolver(die: Die, _):
    return die.faces


@DieResource.color
def die_color_resolver(die: Die, _):
    brains = len([face for face in die.faces if face == Face.BRAIN])
    # this is a hack because the library does not provide a name directly.
    if brains == 3:
        return DieColor.GREEN
    elif brains == 2:
        return DieColor.YELLOW
    return DieColor.RED


@DieResource.currentFace
def die_current_face_resolver(die: Die, _):
    return die.current_face


@DieBagResource.drawnDice
def die_bag_draw_die_resolver(die_bag: DieBag, _):
    return die_bag.drawn_dice


@PlayerResource.score
def player_score_resolver(player: Player, _):
    return player.total_brains


@Round.points
def round_points_resolver(round: RoundState, _):
    # Might be better if the lib provided a count instead..
    return len(round.player.brains)
