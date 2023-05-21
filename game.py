import os
import json
import random
import time
import requests
from statistics import mean
from datetime import datetime, timedelta


TEAM_NAMES = [
    "Bulls",
    "Lakers",
    "Heat",
    "Knicks",
    "Nets",
    "Warriors",
    "Spurs",
    "Clippers",
]
STANDINGS = {team: {"wins": 0, "losses": 0} for team in TEAM_NAMES}
API_URL = "https://api.namefake.com/english-united-states/male"
SCHEDULE = {}


class League:
    def __init(self):
        self.starting_year = 2023
        self.current_year = 2023
        self.fatigue = False
        self.injuries = False
        self.month = 1
        self.day = 1
        self.teams = [Team(name) for name in TEAM_NAMES]  # Add this line

    # Create a Schedule for all the teams, Randomized and add it to the SCHEDULE Golabal Variable

    def create_schedule(self):
        # Get the list of team names
        teams = TEAM_NAMES.copy()

        # Check if the number of teams is even
        if len(teams) % 2 != 0:
            # If not, add a dummy team
            teams.append(None)

        # Create the schedule
        schedule = []
        for round in range(len(teams) - 1):
            for i in range(len(teams) // 2):
                # Each team plays with every other team once
                match = (teams[i], teams[len(teams) - 1 - i])
                schedule.append(match)
            # Rotate the teams for the next round
            teams.insert(1, teams.pop())

        # Remove matches involving the dummy team
        schedule = [match for match in schedule if None not in match]

        schedule_with_dates = {}
        start_date = datetime.now()
        for i, match in enumerate(schedule):
            match_date = start_date + timedelta(days=i * 2)  # Matches every other day
            schedule_with_dates[match_date.strftime("%Y-%m-%d")] = match
        return schedule_with_dates


class Player:
    POSITIONS = ["PG", "SG", "SF", "PF", "C"]

    def __init__(self, number):
        self.name = self.get_random_name()
        self.number = number
        self.position = random.choice(self.POSITIONS)

        self.games_played = 0
        self.minutes_played = 0
        # Start of Flusahble per Game Temporary Stats

        self.points = 0
        self.field_goals_made = 0
        self.field_goals_attempted = 0
        self.field_goal_percentage = 0
        self.three_points_made = 0
        self.three_points_attempted = 0
        self.three_point_percentage = 0
        self.free_throws_made = 0
        self.free_throws_attempted = 0
        self.free_throw_percentage = 0
        self.offensive_rebounds = 0
        self.defensive_rebounds = 0
        self.rebounds = 0
        self.assists = 0
        self.turnovers = 0
        self.steals = 0
        self.blocks = 0
        self.fouls = 0

        # non transferrable to all_time_stats
        self.fatigue = 0
        # end of Flushable per Game Temporary Stats

        # Start of Accumalted lifetime Stats
        self.all_time_stats = {
            "games_played": 0,
            "minutes_played": 0,
            "points": 0,
            "field_goals_made": 0,
            "field_goals_attempted": 0,
            "field_goal_percentage": 0,
            "three_points_made": 0,
            "three_points_attempted": 0,
            "three_point_percentage": 0,
            "free_throws_made": 0,
            "free_throws_attempted": 0,
            "free_throw_percentage": 0,
            "offensive_rebounds": 0,
            "defensive_rebounds": 0,
            "rebounds": 0,
            "assists": 0,
            "turnovers": 0,
            "steals": 0,
            "blocks": 0,
            "fouls": 0,
        }
        # End of Alltime stats

        self.assign_position_based_stats()

        # Tendencies
        self.finish_tendency = random.uniform(0, 1)
        self.mid_range_tendency = random.uniform(0, 1 - self.finish_tendency)
        self.three_point_tendency = 1 - self.finish_tendency - self.mid_range_tendency

        self.passing_tendency = random.uniform(0, 1)

        self.steal_tendency = random.uniform(0, 1)

        self.block_tendency = random.uniform(0, 1)

        self.foul_tendency = random.uniform(0, 1)

    def assign_position_based_stats(self):
        self.three_point_shooting = self.assign_stat("three_point_shooting")
        self.mid_range_shooting = self.assign_stat("mid_range_shooting")
        self.finishing = self.assign_stat("finishing")
        self.free_throw_shooting = self.assign_stat("free_throw_shooting")

        self.rebounding = self.assign_stat("rebounding")

        self.passing = self.assign_stat("passing")

        self.speed = self.assign_stat("speed")

        self.dribbling = self.assign_stat("dribbling")

        self.stealing = self.assign_stat("stealing")

        self.blocking = self.assign_stat("blocking")

        self.endurance = self.assign_stat("endurance")

    def decrease_stats(self):  # Decreasing Stats based on their Fatigue Level
        self.three_point_shooting -= self.fatigue
        self.mid_range_shooting -= self.fatigue
        self.finishing -= self.fatigue
        self.free_throw_shooting -= self.fatigue

        self.rebounding -= self.fatigue

        self.passing -= self.fatigue

        self.speed -= self.fatigue

        self.dribbling -= self.fatigue

        self.stealing -= self.fatigue

        self.blocking -= self.fatigue

        self.endurance -= self.fatigue

    def recover_stats(self):  # Stats Recovery when their on the bench
        self.three_point_shooting += self.fatigue
        self.mid_range_shooting += self.fatigue
        self.finishing += self.fatigue
        self.free_throw_shooting += self.fatigue

        self.rebounding += self.fatigue

        self.passing += self.fatigue

        self.speed += self.fatigue

        self.dribbling += self.fatigue

        self.stealing += self.fatigue

        self.blocking += self.fatigue

        self.endurance += self.fatigue

    # Todo: Distribute Points Efficiently, Current Distribution is OP and also isnt limited to 100
    def assign_stat(self, stat):
        position_weights = {
            "PG": {  # Point Guard
                "three_point_shooting": 0.20,
                "mid_range_shooting": 0.15,
                "finishing": 0.05,
                "free_throw_shooting": 0.15,
                "rebounding": 0.05,
                "passing": 0.20,
                "speed": 0.20,
                "dribbling": 0.20,
                "stealing": 0.10,
                "blocking": 0.05,
                "endurance": 0.15,
            },
            "SG": {  # Shooting Guard
                "three_point_shooting": 0.20,
                "mid_range_shooting": 0.15,
                "finishing": 0.10,
                "free_throw_shooting": 0.15,
                "rebounding": 0.05,
                "passing": 0.15,
                "speed": 0.15,
                "dribbling": 0.15,
                "stealing": 0.10,
                "blocking": 0.05,
                "endurance": 0.15,
            },
            "SF": {  # Small Forward
                "three_point_shooting": 0.15,
                "mid_range_shooting": 0.15,
                "finishing": 0.15,
                "free_throw_shooting": 0.10,
                "rebounding": 0.10,
                "passing": 0.10,
                "speed": 0.15,
                "dribbling": 0.15,
                "stealing": 0.10,
                "blocking": 0.05,
                "endurance": 0.10,
            },
            "PF": {  # Power Forward
                "three_point_shooting": 0.05,
                "mid_range_shooting": 0.15,
                "finishing": 0.20,
                "free_throw_shooting": 0.10,
                "rebounding": 0.20,
                "passing": 0.10,
                "speed": 0.10,
                "dribbling": 0.10,
                "stealing": 0.05,
                "blocking": 0.15,
                "endurance": 0.10,
            },
            "C": {  # Center
                "three_point_shooting": 0.05,
                "mid_range_shooting": 0.10,
                "finishing": 0.25,
                "free_throw_shooting": 0.10,
                "rebounding": 0.25,
                "passing": 0.05,
                "speed": 0.05,
                "dribbling": 0.05,
                "stealing": 0.05,
                "blocking": 0.20,
                "endurance": 0.10,
            },
        }

        weight = position_weights[self.position].get(stat, 0)
        base_stat = random.uniform(50, 70)  # base_stat range from 50 to 70

        # potential factor for a player with tier-based approach
        tier = random.uniform(0, 1)
        if tier < 0.97:  # 97% of players have potential in 0.7 - 1.0 range
            potential = random.uniform(0.7, 1.0)
        else:  # 3% of players have potential in 1.0 - 1.2 range
            potential = random.uniform(1.0, 1.2)

        bonus = weight * base_stat * potential  # bonus stat with respect to potential
        return min(int(base_stat + bonus), 100)

    def get_player_overall(self):
        return (
            self.three_point_shooting
            + self.mid_range_shooting
            + self.finishing
            + self.free_throw_shooting
            + self.rebounding
            + self.passing
            + self.speed
            + self.dribbling
            + self.stealing
            + self.blocking
            + self.endurance
        ) // 11

    @staticmethod
    def get_random_name():
        with open("players.json", "r") as file:
            data = json.load(file)
            names = data["players"]
            if not names:
                return f"Player_{random.randint(1, 9999)}"  # Fallback to random name
            name = random.choice(names)
            names.remove(name)
            with open("players.json", "w") as file:
                json.dump({"players": names}, file)
            return name

    def flush_stats(self):
        # Increment all time stats
        for stat in self.all_time_stats.keys():
            self.all_time_stats[stat] += getattr(self, stat)

        # Reset per-game stats
        self.points = 0
        self.field_goals_made = 0
        self.field_goals_attempted = 0
        self.field_goal_percentage = 0
        self.three_points_made = 0
        self.three_points_attempted = 0
        self.three_point_percentage = 0
        self.free_throws_made = 0
        self.free_throws_attempted = 0
        self.free_throw_percentage = 0
        self.offensive_rebounds = 0
        self.defensive_rebounds = 0
        self.rebounds = 0
        self.assists = 0
        self.turnovers = 0
        self.steals = 0
        self.blocks = 0
        self.fouls = 0

        # non transferrable to all_time_stats
        self.fatigue = 0

    def __str__(self):
        return self.name


class Team:
    STRATEGIES = [
        "Offensive",
        "Defensive",
        "Balanced",
        "Offensive Paint",
        "Offensive Outside",
        "Iso: Star",
        "Iso: Hot Hand",
        "Defensive Paint",
        "Defensive Three",
    ]

    def __init__(self, name, strategy="Balanced"):
        self.name = name
        self.strategy = strategy
        self.players = [Player(i) for i in range(1, 16)]  # 15 players
        self.active_players = self.players[:5]  # Starting 5
        self.bench_players = self.players[5:]  # Remaining players on the bench

    def get_team_avg_stat(self, stat):
        return mean(getattr(player, stat) for player in self.players)

    """GetMVP :Todo Fix and make the MVP Selection based on Overall Stats not just points, 
    Here's the Weight scoring = 40%, Defense = 40% and 20% overall stats, 
    so Star Players have a high chance than Regular players to be MVP """

    def get_mvp(self):
        return max(
            self.players,
            key=lambda player: player.points + player.rebounds + player.assists,
        )

    def get_star_player(self):
        return max(
            self.players,
            key=lambda player: mean(
                [
                    player.passing,
                    player.dribbling,
                    player.speed,
                    player.three_point_shooting,
                    player.mid_range_shooting,
                    player.finishing,
                    player.blocking,
                    player.stealing,
                    player.rebounding,
                    player.endurance,
                ]
            ),
        )

    def get_hot_hand_player(self):
        return max(self.players, key=lambda player: player.points)

    """ Todo Fix Simulate Quarter with new Complex Method taking advantage of all the Player Stats
        Also make a Flush Temporary Stats
    """

    # STRATEGIES = ["Offensive", "Defensive", "Balanced", "Offensive Paint", "Offensive Outside", "Iso: Star", "Iso: Hot Hand", "Defensive Paint", "Defensive Three"]
    # Get both teams Strategies First
    # get teams First 5
    # Check if Strategy of Offensive Team is ISO: Star, if it is, Chance of Picking the Star PLayer to have the POssesion is 80%
    # Check if Strategy of Offensive Team is ISO: Hot Hand, if it is, Chance of Picking the Highest Point in the First 5 is 80%
    # If this is Start of the Game, 0-0 points, get both of their Centers
    # Todo: Decide the Jumpball based on : Stat rebounding:70% Luck random 0-30% for both of them, Then Compare, If they have matching values do a 50/50 instead
    # Start possesion, Set offensive team to the winner of Jumpball, Check the Strategy of the Offensive team
    # possesion_setup
    # if not start of game pick the Player on the Offensive team to handle the ball it should be 20% normally per player in starting 5, unless strategy is ISO
    # Pick the Defensive player on the Defensive team, It should match the POsition of the OFfensive PLayer, if theres no Similar pos, Randomize

    # Offensive Team Setup
    # If offensive, have a boost of 5% to the Offensive Player's Offense
    # if defensive no effect since this is offensive
    # if Balanced, no effect
    # if offensive paint the Shot Percentages Tendency of finishing is now 70%, midrange is 20% and 3 point is 10%
    # if offensive Outside the Shot Percentages Tendency of finishing is now 10%, midrange is 10% and 3 point is 80%
    # if defensive paint or defensive three, do nothing
    # Defensive team Setup
    # If offensive, defense -5%
    # if defensive, 5% in defense stats
    # if Balanced, no effect
    # if offensive paint, no effect
    # if offensive Outside, no effect
    # if defensive paint, defensive boost for defensive player +10 when offensive player is finishing
    # if defensive three, defensive boost for defensive player +10 when offensive player is threepointer
    # setup
    # fatigue should lower the players stats by Fatigue / 10

    # Pre-Possesion
    # randomize 1-5, set pre-possesion time
    # check for steal, steal chance = 0, compare steal of defensive vs driibling if steal is higher add 1% steal chance per point difference
    # radomize if it should be stolen depending on the steal chance
    # if Stolen , set the defensive player as the Offensive player and compare his speed with the player he stole it from, if he is higher, then he would do a Fastbreak for 2 points
    # add 1 fatigue to the fastbreak guy then return possesion to the one they stole it to
    # possesion
    # check type of shot depending on the tendencies of the player
    # check if block, compare offensive stat vs Block, difference would add 1 is to 1 to block chance
    # randomize if it should be blocked
    # randomize if there should be Foul the higher the difference between offensive player and defensive players overall stats, the higher the cance of the foul, but should not exceed 8%
    # Check if the Shot goes in
    # if not go to post possesion
    # post-possesion
    # check the average rebound stats of both teams,
    # defensive team should have base 70% chance of rebound
    # offensive team has 30% chance
    # change that according to the difference in rebounding stat average
    # Add fatigue to the players, 1 if they are offensive and defensive,
    # 0.2 if they didint touch the ball in offensive
    # 0.3 if they didnt touch the ball in defensive


class Game:
    def __init__(self, team1, team2, ai_vs_ai=True):
        self.team1 = team1
        self.team2 = team2
        self.score = {self.team1.name: 0, self.team2.name: 0}
        self.quarter = 0
        self.foul_limit = (
            6  # Player is Fouled out and Cant be Subbed in when this is Reached
        )
        self.fatigue_limit = 500  # Should be adjusted to a number that makes every Stat 50 probably regardless of its starting value
        self.quarter_time = 720  # in seconds
        self.possession = ""
        self.already_jumped = False
        self.last_ally_handler = None
        self.ball_handler = None

    def game_print(self, text):
        team_color = "\033[94m" if self.possession == "team2" else "\033[91m"
        reset_color = "\033[0m"
        print(f"{team_color}{text}{reset_color}")

    def to_dict(self):
        return {
            "team1": self.team1.to_dict(),
            "team2": self.team2.to_dict(),
            # Add other attributes as needed
        }

    def choose_strategy(self, team):
        print(f"\nChoose a strategy for the {team.name} team:")
        for i, strategy in enumerate(Team.STRATEGIES, 1):
            print(f"{i}. {strategy}")

        while True:
            try:
                choice = int(input("Enter your choice: ")) - 1
                team.strategy = Team.STRATEGIES[choice]
                break
            except (IndexError, ValueError):
                print("Invalid choice. Please try again.")

    def simulate_quarter(self):
        while self.quarter_time > 0:
            if self.quarter_time < 0:  # no time left in the quarter
                break
            quarter_time_minutes = (
                self.quarter_time // 60
            )  # Integer division to get the whole number of minutes
            quarter_time_seconds = (
                self.quarter_time % 60
            )  # Remainder gives the remaining seconds

            print(
                f"Remaining Time on the Clock : {quarter_time_minutes:02d}:{quarter_time_seconds:02d}"
            )
            self.calculate_percentages()
            # Get both teams Strategies First
            offensive_strategy = (
                self.team1.strategy
                if self.possession == "team1"
                else self.team2.strategy
            )
            defensive_strategy = (
                self.team2.strategy
                if self.possession == "team1"
                else self.team1.strategy
            )
            # jumpball
            if self.already_jumped == False:
                self.jump_ball()

            # Get teams First 5
            offensive_players = (
                self.team1.active_players[:5]
                if self.possession == "team1"
                else self.team2.active_players[:5]
            )
            defensive_players = (
                self.team2.active_players[:5]
                if self.possession == "team1"
                else self.team1.active_players[:5]
            )
            # Select offensive player based on strategy
            if self.last_ally_handler == None:
                # print(f"DevMode: last_ally_handler is None")
                offensive_player = self.select_offensive_player(
                    offensive_strategy, offensive_players
                )
            else:
                # print(f"DevMode: last_ally_handler has a Value loading that")
                offensive_player = self.ball_handler
            # add Tendencies
            offensive_player = self.modify_tendencies_based_on_strategy(
                offensive_player, offensive_strategy
            )

            # Select defensive player based on offensive player's position
            defensive_player = self.select_defensive_player(
                offensive_player, defensive_players
            )

            # Pre-Possesion
            pre_possession_time = random.randint(1, 5)
            self.quarter_time -= pre_possession_time
            pass_the_ball = None
            if self.quarter_time < 0:  # no time left in the quarter
                break

            # Check if Player will pass the Ball
            pass_the_ball = self.pass_the_ball_check(offensive_player, defensive_player)
            if pass_the_ball == False:
                # Check for steal
                fastbreak = self.check_for_steal(offensive_player, defensive_player)
                if fastbreak:
                    # print(f"DevMode: Scored from Fastbreak")
                    pass
                elif fastbreak == False:
                    # print(f"DevMode: Normal Havent Scored from Fast break")
                    # Possession
                    # Check type of shot depending on the tendencies of the player

                    shot_type = self.select_shot_type(offensive_player)

                    # Check for block
                    block_occurred = self.check_for_block(
                        offensive_player, defensive_player, shot_type
                    )

                    # If the shot wasn't blocked, check if it goes in
                    if not block_occurred:
                        shot_made = self.shot_computation(offensive_player, shot_type)
                    else:
                        shot_made = False
                    # Randomize if there should be a foul
                    if shot_made == True:
                        self.check_for_foul(
                            offensive_player, defensive_player, shot_type, shot_made
                        )
                        if self.last_ally_handler != None:
                            self.last_ally_handler.assists += 1
                            self.game_print(
                                f"That's an assist to {self.last_ally_handler}"
                            )
                    else:
                        self.check_for_foul(
                            offensive_player, defensive_player, shot_type, shot_made
                        )

                    # Post-Possesion
                    # Rebound if shot misses, if it goes in, Just change Possession
                    if not shot_made:
                        # print(f"DevMode: Missed Shot")
                        self.check_for_rebound()
                    elif block_occurred:
                        self.check_for_rebound()
                    else:
                        # print(f"DevMode: Made Shot")
                        self.possession_switch()
                    # Add fatigue to the players
                    self.add_fatigue()
            else:
                self.quarter_time -= random.randint(3, 7)
        self.prep_for_next_quarter()

    def jump_ball(self):
        # Randomly assign the first possession
        self.possession = random.choice(["team1", "team2"])
        if self.possession == "team1":
            self.game_print(f"The jump ball is won by {self.team1.name}!")
        else:
            self.game_print(f"The jump ball is won by {self.team2.name}!")
        self.already_jumped = True

    def prep_for_next_quarter(self):
        self.quarter_time = 720  # in seconds

    def modify_tendencies_based_on_strategy(self, offensive_player, offensive_strategy):
        if offensive_strategy == "Offensive":
            offensive_player.finish_tendency += 0.05
            offensive_player.mid_range_tendency += 0.05
            offensive_player.three_point_tendency += 0.05
        elif offensive_strategy == "Defensive":
            # No effect on offensive tendencies
            pass
        elif offensive_strategy == "Balanced":
            # No effect on offensive tendencies
            pass
        elif offensive_strategy == "Offensive Paint":
            offensive_player.finish_tendency = 0.70
            offensive_player.mid_range_tendency = 0.20
            offensive_player.three_point_tendency = 0.10
        elif offensive_strategy == "Offensive Outside":
            offensive_player.finish_tendency = 0.10
            offensive_player.mid_range_tendency = 0.10
            offensive_player.three_point_tendency = 0.80
        elif offensive_strategy == "Defensive Paint":
            # No effect on offensive tendencies
            pass
        elif offensive_strategy == "Defensive Three":
            # No effect on offensive tendencies
            pass
        return offensive_player

    def select_offensive_player(self, offensive_strategy, offensive_players):
        if offensive_strategy == "Iso: Star":
            star_player = (
                self.team1.get_star_player()
                if self.possession == "team1"
                else self.team2.get_star_player()
            )
            offensive_player = random.choices(
                offensive_players,
                weights=[
                    0.8 if player == star_player else 0.05
                    for player in offensive_players
                ],
                k=1,
            )[0]
        elif offensive_strategy == "Iso: Hot Hand":
            hot_hand_player = (
                self.team1.get_hot_hand_player()
                if self.possession == "team1"
                else self.team2.get_hot_hand_player()
            )
            offensive_player = random.choices(
                offensive_players,
                weights=[
                    0.8 if player == hot_hand_player else 0.05
                    for player in offensive_players
                ],
                k=1,
            )[0]
        else:
            offensive_player = random.choice(offensive_players)
        self.game_print(
            f"{offensive_player.name} from {self.team1.name if self.possession == 'team1' else self.team2.name} has the ball!"
        )
        return offensive_player

    def select_defensive_player(self, offensive_player, defensive_players):
        matching_defensive_players = [
            player
            for player in defensive_players
            if player.position == offensive_player.position
        ]
        defensive_player = (
            random.choice(matching_defensive_players)
            if matching_defensive_players
            else random.choice(defensive_players)
        )
        self.game_print(
            f"{defensive_player.name} from {self.team2.name if self.possession == 'team1' else self.team1.name} is defending!"
        )
        return defensive_player

    def select_shot_type(self, offensive_player):
        shot_type = random.choices(
            ["finish", "mid_range", "three_point"],
            weights=[
                offensive_player.finish_tendency,
                offensive_player.mid_range_tendency,
                offensive_player.three_point_tendency,
            ],
            k=1,
        )[0]
        if self.possession == "team1":
            if shot_type == "finish":
                self.game_print(
                    f"{offensive_player.name} from {self.team1.name} goes for a layup!"
                )
            else:
                self.game_print(
                    f"{offensive_player.name} from {self.team1.name} attempts a {shot_type} shot!"
                )
        else:
            if shot_type == "finish":
                self.game_print(
                    f"{offensive_player.name} from {self.team2.name} goes for a layup!"
                )
            else:
                self.game_print(
                    f"{offensive_player.name} from {self.team2.name} attempts a {shot_type} shot!"
                )
        return shot_type

    def pass_the_ball_check(self, offensive_player, defensive_player):
        # Decide if the player will pass the ball or not (50% passing tendency, 50% random)
        pass_decision = (
            random.random() < 0.5 * (offensive_player.passing_tendency / 100) + 0.5
        )

        if pass_decision:
            # Roll a 10-sided die
            roll = random.randint(1, 10)

            # If the roll is 8 or less, the pass is successful
            if roll <= 8:
                pass_success = True
            else:
                # If the roll is 9 or 10, the success of the pass depends on the player's passing ability and the opponent's stealing ability
                pass_success_chance = 0.8 * (offensive_player.passing / 100) - 0.2 * (
                    defensive_player.stealing / 100
                )
                pass_success = random.random() < pass_success_chance

            if pass_success:
                # If the pass is successful, set last_ally_handler to the player who passed the ball
                self.last_ally_handler = offensive_player

                # Randomly select a new active player (excluding the passer) to be the new ball handler
                if self.possession == "team1":
                    potential_receivers = [
                        player
                        for player in self.team1.active_players
                        if player != offensive_player
                    ]
                else:
                    potential_receivers = [
                        player
                        for player in self.team2.active_players
                        if player != offensive_player
                    ]

                new_ball_handler = random.choice(potential_receivers)
                self.ball_handler = new_ball_handler
                self.game_print(
                    f"{offensive_player.name} passes the ball to {new_ball_handler.name}!"
                )

                # Increase the player's number of passes
                return True
            else:
                # If the Pass failed
                self.game_print(
                    f"{offensive_player.name} pass to nothing!, That's a Turnover."
                )
                offensive_player.turnovers += 1
                self.possession_switch()
                return True
        return False

    def check_for_steal(self, offensive_player, defensive_player):
        steal_chance = (
            max(0, defensive_player.stealing - offensive_player.dribbling) / 100
        )
        if random.random() < steal_chance:
            # when the steal is succesful
            defensive_player.steals += 1
            offensive_player.turnovers += 1
            if self.possession == "team1":
                self.game_print(
                    f"{defensive_player.name} from {self.team2.name} steals the ball!"
                )
                # Swap possession
                self.possession_switch()
                # Check for fastbreak
                if defensive_player.speed > offensive_player.speed:
                    self.game_print(
                        f"{defensive_player.name} from {self.team2.name} makes a fastbreak for easy 2 points!"
                    )
                    self.score[self.team2.name] += 2
                    defensive_player.points += 2
                    defensive_player.fatigue += 1
                    self.show_score()
                    self.possession_switch()
                    return True
            else:
                self.game_print(
                    f"{defensive_player.name} from {self.team1.name} steals the ball!"
                )
                # Swap possession
                self.possession_switch()
                # Check for fastbreak
            if defensive_player.speed > offensive_player.speed:
                # if the Fastbreak is Succesful
                defensive_player.field_goals_made += 1
                defensive_player.field_goals_attempted += 1
                defensive_player.points += 2

                self.game_print(
                    f"{defensive_player.name} from {self.team1.name} makes a fastbreak for easy 2 points!"
                )
                self.score[self.team1.name] += 2
                defensive_player.points += 2
                defensive_player.fatigue += 1
                self.possession_switch()
                return True
        return False

    def check_for_block(self, offensive_player, defensive_player, shot_type):
        if shot_type == "finish":
            shot_skill = getattr(offensive_player, "finishing")
        else:
            shot_skill = getattr(offensive_player, f"{shot_type}_shooting")

        block_chance = max(0, defensive_player.blocking - shot_skill) / 100

        if random.random() < block_chance:
            # if Block is Succesful
            defensive_player.blocks += 1
            if self.possession == "team1":
                self.game_print(
                    f"{defensive_player.name} from {self.team2.name} blocks the shot!"
                )
            else:
                self.game_print(
                    f"{defensive_player.name} from {self.team1.name} blocks the shot!"
                )
            possession_time = random.randint(12, 23)
            self.quarter_time -= possession_time
            return True
        return False

    def check_for_foul(self, offensive_player, defensive_player, shot_type, shot_made):
        if shot_type == "finish":
            shot_skill = getattr(offensive_player, "finishing")
        else:
            shot_skill = getattr(offensive_player, f"{shot_type}_shooting")

        shot_success_chance = shot_skill * offensive_player.endurance / 10000

        foul_chance = min(
            0.08,
            abs(
                defensive_player.get_player_overall()
                - offensive_player.get_player_overall()
            )
            / 100,
        )

        if random.random() < foul_chance:
            # Get defensive team and offensive team based on current possession
            if self.possession == "team1":
                defensive_team = self.team2
                offensive_team = self.team1
            else:
                defensive_team = self.team1
                offensive_team = self.team2

            self.game_print(
                f"{defensive_player.name} from {defensive_team.name} commits a foul!"
            )
            defensive_player.fouls += 1

            if defensive_player.fouls >= self.foul_limit:
                self.game_print(
                    f"{defensive_player.name} from {defensive_team.name} is fouled out!"
                )
                defensive_team.active_players.remove(defensive_player)

                if defensive_team.bench_players:
                    substitute = defensive_team.bench_players.pop(0)
                    defensive_team.active_players.append(substitute)
                    self.game_print(
                        f"{substitute.name} from {defensive_team.name} is substituted in!"
                    )

            if shot_made:
                free_throw_attempts = 1
                self.game_print(
                    f"AND ONE! {offensive_player.name} from {offensive_team.name} makes the shot despite the foul!"
                )
            else:
                free_throw_attempts = 3 if shot_type == "three_point" else 2

            for attempt in range(free_throw_attempts):
                offensive_player.free_throws_attempted += 1
                if random.random() < offensive_player.free_throw_shooting / 100:
                    self.game_print(
                        f"{offensive_player.name} from {offensive_team.name} makes free throw {attempt + 1}!"
                    )
                    self.score[offensive_team.name] += 1
                    offensive_player.free_throws_made += 1
                    offensive_player.points += 1
                else:
                    self.game_print(
                        f"{offensive_player.name} from {offensive_team.name} misses free throw {attempt + 1}!"
                    )

    def check_for_rebound(self):
        offensive_rebound_avg = sum(
            player.rebounding
            for player in getattr(self, self.get_team_with_the_ball()).active_players
        ) / len(getattr(self, self.get_team_with_the_ball()).active_players)
        defensive_rebound_avg = sum(
            player.rebounding for player in self.team2.active_players
        ) / len(self.team2.active_players)

        # Defensive team should have base 70% chance of rebound
        # Offensive team has 30% chance
        rebound_chance = 0.7 + (defensive_rebound_avg - offensive_rebound_avg) / 100

        if random.random() < rebound_chance:  # This means Normal Defensive Rebound
            # This means that the Defensive Rebound is Successful
            rebounder = random.choices(
                getattr(self, self.get_opposite_team()).active_players,
                weights=[
                    player.rebounding
                    for player in getattr(self, self.get_opposite_team()).active_players
                ],
                k=1,
            )[0]
            self.game_print(
                f"{rebounder.name} from {getattr(self, self.get_opposite_team()).name} gets the rebound!"
            )
            rebounder.defensive_rebounds += 1
            rebounder.rebounds += 1
            self.possession_switch()

        else:  # This means OFfensive Rebound
            # Offensive Rebound is Succesful
            rebounder = random.choices(
                self.team1.active_players,
                weights=[
                    player.rebounding
                    for player in getattr(
                        self, self.get_team_with_the_ball()
                    ).active_players
                ],
                k=1,
            )[0]
            self.game_print(
                f"{rebounder.name} from {getattr(self, self.possession).name} gets the Offensive rebound!"
            )
            rebounder.offensive_rebounds += 1
            rebounder.rebounds += 1

    def calculate_shot_success_chance(self, offensive_player, shot_type):
        if shot_type == "finish":
            shot_skill = getattr(offensive_player, "finishing")
        else:
            shot_skill = getattr(offensive_player, f"{shot_type}_shooting")
        shot_success_chance = (
            shot_skill * offensive_player.endurance / 10000
        )  # Assuming both stats are out of 100
        return shot_success_chance

    def shot_computation(self, offensive_player, shot_type):
        # Calculate the chance of shot success
        shot_success_chance = self.calculate_shot_success_chance(
            offensive_player, shot_type
        )

        # Reduce the quarter time by a random value between 8 and 23
        self.quarter_time -= random.randint(8, 23)

        # Identify the offensive team before the shot is taken
        if self.possession == "team1":
            offensive_team = self.team1
        else:
            offensive_team = self.team2

        # Regardless of whether the shot is made or not, the player has attempted a field goal
        offensive_player.field_goals_attempted += 1

        # If the shot type is a three pointer, increment the three points attempted
        if shot_type == "three_point":
            offensive_player.three_points_attempted += 1

        # If the random number is less than shot_success_chance, the shot is successful
        if random.random() < shot_success_chance:
            # Increment the number of field goals made by the offensive player
            offensive_player.field_goals_made += 1

            # If the shot type is a three pointer, increment the three points made and set points to 3
            if shot_type == "three_point":
                offensive_player.three_points_made += 1
                points = 3
            else:  # If the shot type is not a three pointer, set points to 2
                points = 2

            # Update the score and points of the player and print the message
            self.score[offensive_team.name] += points
            offensive_player.points += points
            self.game_print(
                f"{offensive_player.name} from {offensive_team.name} makes the {shot_type} shot for {points} points!"
            )
            offensive_player.fatigue += 3
            self.show_score()

            return True
        else:  # If the shot was not successful, print a random commentary about the missed shot
            missed_shot_commentary = [
                f"{offensive_player.name} from {offensive_team.name} misses the shot! It bounces off the rim.",
                f"{offensive_player.name} from {offensive_team.name} can't find the mark. The shot goes wide.",
                f"{offensive_player.name} from {offensive_team.name} takes the shot but it's no good. It falls short.",
            ]

            self.game_print(random.choice(missed_shot_commentary))

            return False

    def possession_switch(self):
        if self.possession == "team1":
            self.possession = "team2"
        else:
            self.possession = "team1"
        # print(f"possession Changes!")
        self.ball_handler = None
        self.last_ally_handler = None

    def get_opposite_team(self):
        return "team1" if self.possession == "team2" else "team2"

    def get_team_with_the_ball(self):
        return "team2" if self.possession == "team2" else "team1"

    def add_fatigue(self):
        for player in self.team1.active_players + self.team2.active_players:
            player.fatigue += 1
            if player.fatigue >= self.fatigue_limit:
                print(
                    f"{player.name} from {self.team1.name} is too fatigued and is substituted out!"
                )
                self.team1.active_players.remove(player)
                if self.team1.bench_players:
                    substitute = self.team1.bench_players.pop(0)
                    self.team1.active_players.append(substitute)
                    print(
                        f"{substitute.name} from {self.team1.name} is substituted in!"
                    )

    def show_score(self):
        print(f"Current Score:{self.score}")

    def calculate_percentages(self):
        # Loop over each team
        for team in [self.team1, self.team2]:
            # For each player in the team (including both active and bench players)
            for player in team.players:
                # Calculate and print free throw percentage
                if player.free_throws_attempted > 0:  # Avoid division by zero
                    free_throw_percentage = (
                        player.free_throws_made / player.free_throws_attempted * 100
                    )
                    player.free_throw_percentage = free_throw_percentage

                # Calculate and print field goal percentage
                if player.field_goals_attempted > 0:  # Avoid division by zero
                    field_goal_percentage = (
                        player.field_goals_made / player.field_goals_attempted * 100
                    )
                    player.field_goal_percentage = field_goal_percentage

                # Calculate and print three-point percentage
                if player.three_points_attempted > 0:  # Avoid division by zero
                    three_point_percentage = (
                        player.three_points_made / player.three_points_attempted * 100
                    )
                    player.three_point_percentage = three_point_percentage

    def simulate_game(self):
        for self.quarter in range(1, 5):  # 4 quarters
            # Quarter start
            print(
                f"\nQuarter {self.quarter} is about to start! Let's see some action!\n{self.show_score()}"
            )
            self.choose_strategy(self.team1)  # Let the user choose a strategy
            self.simulate_quarter()
            # Quarter end
            print(
                f"That's the end of quarter {self.quarter}. The players are taking a breather.\n{self.show_score()}"
            )

            print("\nGame Stats:")
            for team in [self.team1, self.team2]:
                print(f"\n{team.name}:")
                for player in team.active_players:
                    print(
                        f"\n========\n{player.name} {player.position}\n"
                        f"Points: {player.points}\n"
                        f"Fouls: {player.fouls}\n"
                        f"Fatigue: {player.fatigue}\n"
                        f"FG: {player.field_goals_made}/{player.field_goals_attempted} - {player.field_goal_percentage}%\n"
                        f"Three Point FG: {player.three_points_made}/{player.three_points_attempted} - {player.three_point_percentage}%\n"
                        f"Free Throw FG: {player.free_throws_made}/{player.free_throws_attempted} - {player.free_throw_percentage}%\n"
                        f"Rebounds (O/D - Total): {player.offensive_rebounds}/{player.defensive_rebounds} - {player.rebounds}\n"
                        f"Assists: {player.assists}\n"
                        f"Turnovers: {player.turnovers}\n"
                        f"Steals: {player.steals}\n"
                        f"Blocks: {player.blocks}\n========\n"
                    )

            time.sleep(1)  # pause for a second between quarters

        self.print_result()
        self.flush_stats()

    def substitute_players(self):
        for team in [self.team1, self.team2]:
            for player in team.active_players:
                if (
                    player.fouls >= self.foul_limit
                    or player.fatigue >= self.fatigue_limit
                ):
                    if team.bench_players:  # If there are players on the bench
                        # Substitute player with the first player on the bench
                        bench_player = team.bench_players.pop(0)
                        team.active_players.remove(player)
                        team.active_players.append(bench_player)
                        # Move the substituted player to the bench
                        team.bench_players.append(player)
                        # Reset fatigue for the substituted player
                        player.fatigue = 0
                        player.recover_stats()  # Recover stats after resting

    def print_result(self):
        winner = max(self.score, key=self.score.get)
        loser = min(self.score, key=self.score.get)

        # Game end
        print(
            f"\nWhat a game! The {winner} team takes the victory with a final score of {self.score[winner]} to {self.score[loser]}!"
        )
        if winner == self.team1.name:
            mvp = self.team1.get_mvp()
        else:
            mvp = self.team2.get_mvp()
        player = mvp
        print(
            f"MVP of the game:{player.name} {player.position}\n"
            f"Points: {player.points}\n"
            f"Fouls: {player.fouls}\n"
            f"Fatigue: {player.fatigue}\n"
            f"FG: {player.field_goals_made}/{player.field_goals_attempted} - {player.field_goal_percentage}%\n"
            f"Three Point FG: {player.three_points_made}/{player.three_points_attempted} - {player.three_point_percentage}%\n"
            f"Free Throw FG: {player.free_throws_made}/{player.free_throws_attempted} - {player.free_throw_percentage}%\n"
            f"Rebounds (O/D - Total): {player.offensive_rebounds}/{player.defensive_rebounds} - {player.rebounds}\n"
            f"Assists: {player.assists}\n"
            f"Turnovers: {player.turnovers}\n"
            f"Steals: {player.steals}\n"
            f"Blocks: {player.blocks}\n\n"
        )

    def flush_stats(self):
        for player in self.team1.active_players:
            player.flush_stats()
        for player in self.team1.bench_players:
            player.flush_stats()
        for player in self.team2.active_players:
            player.flush_stats()
        for player in self.team2.bench_players:
            player.flush_stats()
        self.score = {self.team1.name: 0, self.team2.name: 0}


def main_menu():
    while True:
        print("Welcome to the Basketball Simulator!")
        print("1. Start a new game")
        print("2. Load a saved game")
        print("3. Quit")

        choice = input("Enter your choice: ")
        if choice == "1":
            new_game()
            break
        elif choice == "2":
            load_game()
            break
        elif choice == "3":
            quit()
        else:
            print("Invalid choice. Please try again.")


def new_game():
    print("\nChoose a team:")
    for i, team_name in enumerate(TEAM_NAMES, 1):
        print(f"{i}. {team_name}")

    choice = input("Enter choice: ")
    try:
        print(
            "\nCreating and Generating Team Names, Player Names, Numbers and Stats, Please wait..\nThis might take a while.."
        )
        user_team = Team(TEAM_NAMES[int(choice) - 1])

        # Get the schedule
        league = League()
        schedule = league.create_schedule()

        # Get the next team in the schedule for the user's team
        next_team_name = None
        for date, match in schedule.items():
            if user_team.name in match:
                next_team_name = match[0] if match[1] == user_team.name else match[1]
                break

        if next_team_name is None:
            raise Exception(
                "No next match found in the schedule for the selected team."
            )

        ai_team = Team(next_team_name)
        game = Game(user_team, ai_team)
        while menu(game):  # Keep the game running until the user chooses to quit
            game.simulate_game()
    except (IndexError, ValueError):
        print("Invalid choice. Please try again.")
        new_game()


# Todo: Fix and Implement tho Modified Menu
def menu(game):
    while True:
        print("\nWhat would you like to do?")
        print("1. Simulate Other Games and Play to the Next Game")
        print("2. Check Your Team Roster")
        print("3. Check other Teams")
        print("4. Check League Standings")
        print("5. Save")
        print("6. Save and Exit")
        print("7. Exit without Saving")

        choice = input("Enter your choice: ")
        if choice == "1":
            return True
        elif choice == "2":
            # logging.info the user team's roster
            print("\nYour Team Roster:")
            for player in game.team1.players:
                print(
                    f"\n========\n{player.name} ({player.position}) :\n"
                    f"Overall: {player.get_player_overall()}\n"
                    f"Offense:\n"
                    f"3pt: {player.three_point_shooting}\n"
                    f"Midrange: {player.mid_range_shooting}\n"
                    f"Finishing: {player.finishing}\n"
                    f"Passing: {player.passing}\n"
                    f"Dribbling: {player.dribbling}\n"
                    f"Speed: {player.speed}\n"
                    f"Rebounding: {player.rebounding}\n\n"
                    f"Defense:\n"
                    f"Stealing: {player.stealing}\n"
                    f"Blocking: {player.blocking}\n========"
                )

        elif choice == "3":
            # Show stats for players in the selected team
            print("\nChoose a team:")
            for i, team_name in enumerate(TEAM_NAMES, 1):
                print(f"{i}. {team_name}")
            team_choice = input("Enter choice: ")
            selected_team = Team(TEAM_NAMES[int(team_choice) - 1])
            print(f"\n{selected_team.name} Roster:")
            for player in selected_team.players:
                print(
                    f"\n========\n{player.name} ({player.position}) :\n"
                    f"Overall: {player.get_player_overall()}\n"
                    f"Offense:\n"
                    f"3pt: {player.three_point_shooting}\n"
                    f"Midrange: {player.mid_range_shooting}\n"
                    f"Finishing: {player.finishing}\n"
                    f"Passing: {player.passing}\n"
                    f"Dribbling: {player.dribbling}\n"
                    f"Speed: {player.speed}\n"
                    f"Rebounding: {player.rebounding}\n\n"
                    f"Defense:\n"
                    f"Stealing: {player.stealing}\n"
                    f"Blocking: {player.blocking}\n========"
                )
        elif choice == "5":
            # Save the game
            save_game(game)
            print("Game saved!")
        elif choice == "6":
            # Save and exit
            save_game(game)
            print("Game saved!")
            return False
        elif choice == "7":
            # Exit without saving
            return False
        else:
            print("Invalid choice. Please try again.")


# Todo Fix Save and Load to JSON format, Save every stat and make it Loadable as Well
def save_game(game):
    with open("save_file.json", "w") as f:
        json.dump(game.__dict__, f)
    print("Game saved!")


def load_game():
    if os.path.exists("save_file.json"):
        with open("save_file.json", "r") as f:
            game_data = json.load(f)
        game = Game(game_data["user_team"], game_data["ai_team"])
        print(f"Loaded game: {game.score}")
        game.simulate_game()
    else:
        print("No saved game found.")
        main_menu()


def quit():
    print("Thank you for playing!")
    exit()


if __name__ == "__main__":
    main_menu()
