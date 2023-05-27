import os
import json
import random
import time
import requests
from statistics import mean
import datetime
from datetime import datetime, timedelta, date
import pandas as pd
from itertools import combinations, product
from colorama import Fore, Style
import pickle
from cryptography.fernet import Fernet
from termcolor import colored
from collections import Counter, deque, defaultdict
from random import randint, shuffle, choice, sample, choices
from queue import PriorityQueue

# generate a key for encryption/decryption
# IMPORTANT: keep this key safe, if you lose it you won't be able to decrypt your data
key = Fernet.generate_key()
cipher_suite = Fernet(key)


# Global Variables


TEAM_NAMES = [
    "Atlanta",
    "Boston",
    "Brooklyn",
    "Charlotte",
    "Chicago",
    "Cleveland",
    "Dallas",
    "Denver",
    "Detroit",
    "Golden State",
    "Houston",
    "Indiana",
    "Las Vegas",
    "Los Angeles",
    "Memphis",
    "Miami",
    "Milwaukee",
    "Minnesota",
    "New Orleans",
    "New York",
    "Oklahoma City",
    "Orlando",
    "Philadelphia",
    "Phoenix",
    "Portland",
    "Sacramento",
    "San Antonio",
    "Toronto",
    "Utah",
    "Washington",
]

debug = True


class User:
    def __init(self):
        self.team = ""


# Init User Class
user = User()


class Schedule:
    def __init__(self):
        self.games = {}


class League:
    def __init__(self):
        print(f"League is now Initiated, Setting up..")

        # League Variables
        self.starting_year = 2023
        self.current_year = 2023
        self.fatigue = False
        self.injuries = False
        self.month = 6
        self.day = 21

        self.teams = {}  # A Tuple
        self.schedule = {}
        self.standings = {
            team: {"wins": 0, "losses": 0, "pct": 0.0} for team in TEAM_NAMES
        }

    # Create a Schedule for all the teams, Randomized and add it to the SCHEDULE Golabal Variable

    def create_teams(self):
        print(f"Creating teams..")
        teams = []  # Create an empty list to store the teams
        for name in TEAM_NAMES:
            team = Team(name)  # Create a Team instance
            teams.append(team)  # Append the team to the list
        for team in teams:
            """Use for DevMode Only
            print(
                f"\n\nCreated {team.name} and added it to The leagues' teams.\nPlayers:\n"
            )
            print
            for player in team.players:
                print(f"{player.name}")
            """
        return teams  # Return the list of teams

    """
    A function for an NBA like simulator game/GM/Coaching game
    function name : create_schedule(self)
    args Self
    returns Schedule = { date: {team1, team2}, {team1, team2} date: {team1, team2}, {team1, team2} } etc..

    variable reference:
        start_date = create_date(league.month, league.day, league.current_year) #This is the starting date of the Reular Season
        end_date = start_date + timedelta(days=6 * 30)  #Season lasts for 6months
        teams = league.teams #contains the teams

    --------------------------------------------------------
    -Each team will play a total of 58 games in the regular season. 
    -The regular season starts at june 21 2023 and Runs for 6 months
    -each team should battle every team twice
    -each team cant have more than 1 game at the same day
    -Avoid Back to Back games for teams as possible checking day before and day after
    -Each team can only play 5 times in 1 week
    -There should be 4 minimum games per day up to 12 maximum
    -matchup selection: team with fewer/fewest games played should be prioritized in matchup selection


    notes:
    -Please dont use "datetime." just direct those since i imported them already,
    -please dont change the league to self, since i have an object named league and im referenceing to that not to self
    -Dont put self to create_date, that's a global function
    """

    def create_schedule(self):
        teams = league.teams
        # Initialize game count and schedule
        game_counts = defaultdict(int)
        schedule = defaultdict(list)

        # Initialize dates and matchups
        start_date = create_date(league.month, league.day, league.current_year)
        end_date = start_date + timedelta(days=6 * 30)
        current_date = start_date

        # Generate all possible matchups
        all_matchups = (
            list(combinations(league.teams, 2)) * 2
        )  # each team plays every other team twice
        random.shuffle(all_matchups)  # shuffle matchups to ensure randomness

        # Auxiliary function to check if a team already has a game scheduled on a given date
        def has_game(team, date):
            for game in schedule[date]:
                if team in game:
                    return True
            return False

        while current_date <= end_date and all_matchups:
            # Try to schedule games for the current date
            games_today = schedule[current_date]
            for matchup in all_matchups[:]:
                team1, team2 = matchup

                # Ensure teams have not exceeded the game limit and are not already scheduled to play today
                if (
                    game_counts[team1] < 58
                    and game_counts[team2] < 58
                    and not has_game(team1, current_date)
                    and not has_game(team2, current_date)
                    and len(games_today) < 8
                ):
                    # Add game to schedule and update game count
                    games_today.append(matchup)
                    game_counts[team1] += 1
                    game_counts[team2] += 1
                    all_matchups.remove(matchup)

                    # Check if a team is scheduled to play the day before or the day after
                    if (
                        has_game(team1, current_date - timedelta(days=1))
                        or has_game(team1, current_date + timedelta(days=1))
                        or has_game(team2, current_date - timedelta(days=1))
                        or has_game(team2, current_date + timedelta(days=1))
                    ):
                        # If so, remove the game from the schedule and decrement the game count
                        games_today.remove(matchup)
                        game_counts[team1] -= 1
                        game_counts[team2] -= 1
                        all_matchups.append(matchup)

            # Update the schedule with today's games
            schedule[current_date] = games_today

            # Proceed to the next date
            current_date += timedelta(days=1)

        return dict(schedule)

    """Create a method for searching Upcoming matchup
    Searches the schedule for the next matchup involving the given team.
    Args:
        self, team_name

        Returns:
            The date and matchup of the next game involving the given team in datetime.date format 
    """

    def get_next_matchup(self, team_name):
        schedule = self.create_schedule()  # Use schedule from previous method
        upcoming_games = []

        for date in schedule:
            for matchup in schedule[date]:
                if team_name in matchup:
                    upcoming_games.append(
                        (date, matchup)
                    )  # Add date and matchup involving team

        upcoming_games.sort()  # Sort by date
        return upcoming_games[0]  # Return the first upcoming game

    def print_schedule(self):
        user_team = user.team
        schedule = league.schedule
        for date, matchups in sorted(schedule.items()):
            print(f"{date.strftime('%Y-%m-%d')}:")
            for matchup in matchups:
                team1_name = matchup[0].name
                team2_name = matchup[1].name
                match_str = f"\t{team1_name} vs {team2_name}"
                if user_team == team1_name or user_team == team2_name:
                    print(colored(match_str, "red"))
                else:
                    print(match_str)

    def sort_standings_by_wins(self):
        """
        Sorts the league's standings by wins (descending), then by losses (ascending).

        Args:
            self: The league object.

        Returns:
            A dictionary of the sorted standings.

        Raises:
            None.

        """
        # Sort the dictionary by wins (descending), then by losses (ascending).
        standings = dict(
            sorted(
                self.standings.items(),
                key=lambda item: (item[1]["wins"], -item[1]["losses"]),
                reverse=True,
            )
        )

        return standings

    def seek_standings(self, standings, team_name, mode=1):
        """
        Seeks a dictionary called "standings" using one of its key names.

        Args:
          standings: The dictionary to seek.
          team_name: The name of the team to seek.
          mode: The mode to print the standings in.

        Returns:
          The value associated with the team name in the dictionary, if it exists.
          None, if the team name does not exist in the dictionary.
        """

        for team_key, team_value in standings.items():
            if team_key == team_name:
                if mode == 1:
                    return team_key, team_value
                elif mode == 2:
                    return team_key, team_value["wins"], team_value["losses"]
                elif mode == 3:
                    return team_key
                elif mode == 4:
                    return team_value["wins"]
                elif mode == 5:
                    return team_value["losses"]

        return None

    def update_standings(self, standings, team_name, wins, losses):
        """
        Updates the standings of a team in a dictionary.

        Args:
          standings: The dictionary to update.
          team_name: The name of the team to update.
          wins: The number of wins to add to the team's standings.
          losses: The number of losses to add to the team's standings.

        Returns:
          The updated dictionary.
        """

        for team_key, team_value in standings.items():
            if team_key == team_name:
                team_value["wins"] += wins
                team_value["losses"] += losses
                team_value["pct"] = standings[team_name]["wins"] / (
                    standings[team_name]["wins"] + standings[team_name]["losses"]
                )

                break

        return standings

    def standings_add_win(self, team_name):
        """
        Adds a win to the standings of a team.

        Args:
          team_name: The name of the team to update.

        Returns:
          The updated dictionary.
        """

        standings = league.standings

        for team_key, team_value in standings.items():
            if team_key == team_name:
                team_value["wins"] += 1
                team_value["pct"] = standings[team_name]["wins"] / (
                    standings[team_name]["wins"] + standings[team_name]["losses"]
                )
                break

        return standings

    def standings_add_loss(self, team_name):
        """
        Adds a loss to the standings of a team.

        Args:
          team_name: The name of the team to update.

        Returns:
          The updated dictionary.
        """
        standings = league.standings

        for team_key, team_value in standings.items():
            if team_key == team_name:
                team_value["losses"] += 1
                team_value["pct"] = standings[team_name]["wins"] / (
                    standings[team_name]["wins"] + standings[team_name]["losses"]
                )
                break

        return standings

    def print_standings(self):
        """
        Prints the standings of all teams in a league, along with their wins, losses and GB.

        Args:
          self: The league object.

        Returns:
          None.

        Raises:
          None.

        """
        team_color = "\033[94m"
        reset_color = "\033[0m"

        standings = self.sort_standings_by_wins()
        best_record = list(standings.values())[0]

        print(f"\n\nLeague Standings:\n")
        print(f"{'Team':<20}{'W':<5}{'L':<5}{'Pct':<7}{'GB':<5}")
        for team_name, team_data in standings.items():
            wins = team_data["wins"]
            losses = team_data["losses"]
            pct = team_data["pct"]
            gb = ((best_record["wins"] - wins) + (losses - best_record["losses"])) / 2
            # Check if the current team name is equal to the user's team.
            if team_name == user.team:
                print(
                    f"{team_color}{team_name:<20}{wins:<5}{losses:<5}{pct:<7.3f}{gb:<5.1f} (my team){reset_color}"
                )
            else:
                print(f"{team_name:<20}{wins:<5}{losses:<5}{pct:<7.3f}{gb:<5.1f}")


# Initialize the League Class
league = League()


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
        # Schedule related
        self.games_played = 0
        self.games_today = 0
        self.games_last7days = deque(maxlen=7)
        self.back_to_back_count = 0

        self.name = name
        self.strategy = random.choice(self.STRATEGIES)

        self.players_copy = []

        # Player Creation
        self.players = []
        positions = ["PG", "SG", "SF", "PF", "C"] * 2  # Repeat each position twice
        for i in range(10):
            self.players.append(Player(i + 1, positions[i]))
        for i in range(10, 12):  # The last two players can be of any position
            self.players.append(Player(i + 1))

        # Sort players by their overall rating
        self.players.sort(key=lambda player: player.get_player_overall(), reverse=True)

        # Copy the Players to a New array to Create the ACtive Players and Bench players
        self.players_copy = self.players.copy()

        # Pick the best player for each position as the starting five
        self.active_players = []
        for position in ["PG", "SG", "SF", "PF", "C"]:
            for player in self.players_copy:
                if player.position == position:
                    self.active_players.append(player)
                    self.players_copy.remove(player)
                    break

        # Remaining players on the bench
        self.bench_players = self.players_copy
        # print(f"DevMode:\nInitial active players for {self.name}: {[player.name for player in self.active_players]}")

    def get_team_avg_stat(self, stat):
        return mean(getattr(player, stat) for player in self.players)

    def get_mvp(self):
        return max(
            self.players,
            key=lambda player: player.points
            + 2 * (player.rebounds + player.assists + player.steals + player.blocks),
        )

    def get_star_player(self):
        return max(
            self.players,
            key=lambda player: mean(
                [
                    player.three_point_shooting,
                    player.mid_range_shooting,
                    player.finishing,
                    player.free_throw_shooting,
                    player.rebounding,
                    player.passing,
                    player.speed,
                    player.dribbling,
                    player.stealing,
                    player.blocking,
                    player.endurance,
                ]
            ),
        )

    def get_hot_hand_player(self):
        return max(self.players, key=lambda player: player.points)

    def get_average_stats(self):
        total_stats = {
            "three_point_shooting": 0,
            "mid_range_shooting": 0,
            "finishing": 0,
            "free_throw_shooting": 0,
            "rebounding": 0,
            "passing": 0,
            "speed": 0,
            "dribbling": 0,
            "stealing": 0,
            "blocking": 0,
            "endurance": 0,
        }

        for player in self.players:
            total_stats["three_point_shooting"] += player.three_point_shooting
            total_stats["mid_range_shooting"] += player.mid_range_shooting
            total_stats["finishing"] += player.finishing
            total_stats["free_throw_shooting"] += player.free_throw_shooting
            total_stats["rebounding"] += player.rebounding
            total_stats["passing"] += player.passing
            total_stats["speed"] += player.speed
            total_stats["dribbling"] += player.dribbling
            total_stats["stealing"] += player.stealing
            total_stats["blocking"] += player.blocking
            total_stats["endurance"] += player.endurance

        average_stats = {
            stat: total / len(self.players) for stat, total in total_stats.items()
        }
        return average_stats

    def get_team_overall(self):
        total_stats = 0
        stat_count = 0

        for player in self.players:
            total_stats += player.three_point_shooting
            total_stats += player.mid_range_shooting
            total_stats += player.finishing
            total_stats += player.free_throw_shooting
            total_stats += player.rebounding
            total_stats += player.passing
            total_stats += player.speed
            total_stats += player.dribbling
            total_stats += player.stealing
            total_stats += player.blocking
            total_stats += player.endurance
            stat_count += 10  # We added 10 stats for each player

        average_stats = round(total_stats / stat_count)
        return average_stats


class Player:
    POSITIONS = ["PG", "SG", "SF", "PF", "C"]

    def __init__(self, number, position=None):
        self.name = self.get_random_name()
        self.number = number
        self.position = position if position else random.choice(self.POSITIONS)

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
        # print(f"DevMode: Flushed Stats")

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


class Game:
    def __init__(self, team1, team2, ai_vs_ai=False):
        self.ai_vs_ai = ai_vs_ai
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
        if self.ai_vs_ai == True:
            return
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
        if self.ai_vs_ai == False:
            print(f"Team1 Active players")
            for player in self.team1.players:
                print(f"\nPlayer: {player}")

        while self.quarter_time > 0:
            if self.quarter_time < 0:  # no time left in the quarter
                break
            quarter_time_minutes = (
                self.quarter_time // 60
            )  # Integer division to get the whole number of minutes
            quarter_time_seconds = (
                self.quarter_time % 60
            )  # Remainder gives the remaining seconds
            if self.ai_vs_ai == False:
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
            if self.possession == "team1":
                offensive_players = self.team1.active_players
            elif self.possession == "team2":
                offensive_players = self.team2.active_players
            else:
                print(f"DevMode: Possession Invalid : {possession}")

            defensive_players = (
                self.team2.active_players
                if self.possession == "team1"
                else self.team1.active_players
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
                    if self.ai_vs_ai == False:
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
            if self.ai_vs_ai == False:
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
        """print(
            f"DevMode:\nActive players for team1: {[player.name for player in self.team1.active_players]}"
        )
        print(
            f"DevMode:\nActive players for team2: {[player.name for player in self.team2.active_players]}"
        )"""

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
        print(
            f"\n\nMatch for today : {self.team1.name}, Ovr: {self.team1.get_team_overall()} v.s {self.team2.name} {self.team2.get_team_overall()}\n{self.team1.name}'s star player: {self.team1.get_star_player().name} = Ovr: {self.team1.get_star_player().get_player_overall()}\n{self.team2.name}'s star player: {self.team2.get_star_player().name} = Ovr: {self.team2.get_star_player().get_player_overall()}\n"
        )
        for self.quarter in range(1, 5):  # 4 quarters
            # Quarter start
            print(
                f"\nQuarter {self.quarter} is about to start! Let's see some action!\n{self.show_score()}\n"
            )
            self.choose_strategy(self.team1)  # Let the user choose a strategy
            self.simulate_quarter()
            # Quarter end
            print(
                f"\nThat's the end of quarter {self.quarter}. The players are taking a breather.\n{self.show_score()}\n"
            )

            self.print_team_stats()

            time.sleep(1)  # pause for a second between quarters

        self.print_result()
        self.post_game()
        self.flush_stats()

    def quick_simulate(self):
        print(
            f"\n\nSimulating : {self.team1.name}, Ovr: {self.team1.get_team_overall()} v.s {self.team2.name} {self.team2.get_team_overall()}\n{self.team1.name}'s star player: {self.team1.get_star_player().name} = Ovr: {self.team1.get_star_player().get_player_overall()}\n{self.team2.name}'s star player: {self.team2.get_star_player().name} = Ovr: {self.team2.get_star_player().get_player_overall()}\n"
        )
        for self.quarter in range(1, 5):  # 4 quarters
            # Quarter start
            print(f"\nSimulating Quarter {self.quarter}.")
            self.simulate_quarter()

            # Quarter end
            print(f"End of quarter {self.quarter}.\n")
            self.show_score()

        time.sleep(1)  # pause for a second between quarters

        self.print_result()
        self.post_game()
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
        if self.ai_vs_ai == False:
            print(
                f"\nWhat a game! The {winner} team takes the victory with a final score of {self.score[winner]} to {self.score[loser]}!"
            )
            if winner == self.team1.name:
                mvp = self.team1.get_mvp()
            else:
                mvp = self.team2.get_mvp()
            player = mvp
            print_player_game_stats(player)
        else:
            print(
                f"Simulation Complete: {winner} wins with a final score of {self.score[winner]} to {self.score[loser]}"
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

    def post_game(self):
        winner = max(self.score, key=self.score.get)
        loser = min(self.score, key=self.score.get)
        league.standings_add_win(winner)
        league.standings_add_loss(loser)

    def print_team_stats(self):
        print(f"{Fore.BLUE}\nGame Stats:{Style.RESET_ALL}")
        for team in [self.team1, self.team2]:
            print(f"\n{Fore.YELLOW}{team.name}:{Style.RESET_ALL}")
            for player in team.active_players:
                player_info = f"""
                {Fore.GREEN}========\n{player.name} {player.position}{Fore.RESET}
                {Fore.GREEN}Points:{Fore.RESET} {player.points}
                {Fore.GREEN}Fouls:{Fore.RESET} {player.fouls}
                {Fore.GREEN}Fatigue:{Fore.RESET} {player.fatigue}
                {Fore.GREEN}Field Goals (FG):{Fore.RESET} {player.field_goals_made}/{player.field_goals_attempted} - {round(player.field_goal_percentage, 2)}%
                {Fore.GREEN}Three Point FG:{Fore.RESET} {player.three_points_made}/{player.three_points_attempted} - {round(player.three_point_percentage, 2)}%
                {Fore.GREEN}Free Throw FG:{Fore.RESET} {player.free_throws_made}/{player.free_throws_attempted} - {round(player.free_throw_percentage, 2)}%
                {Fore.GREEN}Rebounds (O/D - Total):{Fore.RESET} {player.offensive_rebounds}/{player.defensive_rebounds} - {player.rebounds}
                {Fore.GREEN}Assists:{Fore.RESET} {player.assists}
                {Fore.GREEN}Turnovers:{Fore.RESET} {player.turnovers}
                {Fore.GREEN}Steals:{Fore.RESET} {player.steals}
                {Fore.GREEN}Blocks:{Fore.RESET} {player.blocks}
                {Fore.GREEN}========{Style.RESET_ALL}\n
                """
                print(player_info)


def main_menu():
    while True:
        print("Welcome to the Basketball Simulator!")
        print("1. Start a new game")
        print("2. Load a saved game")
        print("3. Settings")
        print("4. Quit")

        choice = input("Enter your choice: ")
        if choice == "1":
            new_game()
            break
        elif choice == "2":
            load_game()
            break
        elif choice == "4":
            quit()
        else:
            print("Invalid choice. Please try again.")


def settings():
    pass


def new_game():
    print("\nChoose a team:")
    # Enumerate Teams and Print them
    for i, team_name in enumerate(TEAM_NAMES, 1):
        print(f"{i}. {team_name}")

    while True:
        choice = input("[New_Game] Enter choice: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(TEAM_NAMES):
                print(
                    "\nCreating and Generating Team Names, Player Names, Numbers and Stats, Please wait..\nThis might take a while.."
                )
                # Assigning your Team
                user_team = TEAM_NAMES[choice - 1]
                print(f"\n\nYou picked the {user_team}\n\n")
                # Save User's Team
                user.team = user_team
                league.teams = league.create_teams()
                league.schedule = league.create_schedule()
                menu()
                break
            else:
                print("[New Game] Invalid choice. Please try again.")
        except ValueError:
            print("[New Game] Invalid input. Please enter a number.")


def get_team_by_name(team_name):
    """Returns the team object for the given team name."""
    return next(team for team in league.teams if team.name == team_name)


def menu():
    print("Loading Game Menu...")
    user_team = user.team
    date = create_date(league.month, league.day, league.current_year)
    while True:
        print(f"\nWorld Basketball League {league.current_year} - {date}")
        # Find today's games and print user_team's game in red
        date_str = date.strftime("%B %d")
        todays_games = [g for g in league.schedule[date] if user_team in g]
        for g in league.schedule[date]:
            if user_team == g[0].name or user_team == g[1].name:
                print(f"\033[31m{g[0].name} @ {g[1].name}\033[0m")
            else:
                print(f"{g[0].name} @ {g[1].name}")

        print("\nWhat would you like to do?")
        print(
            f"1. Simulate Other Games and Play to the Next Game ({user_team})"
            f"\n2. Check Your Team Roster ({user_team})"
            f"\n3. Check other Teams"
            f"\n4. Check Schedules"
            f"\n5. Check League Standings"
            f"\n6. Save"
            f"\n7. Save and Exit"
            f"\n8. Exit without Saving"
        )

        choice = input("[Menu] Enter your choice: ")
        if choice == "1":
            today = date
            schedule = league.schedule
            user_game = None

            # Separate user's game if there is one
            # print("Checking today's games for user's team:")
            for i in range(len(schedule[today])):
                """print(
                    f"  Checking game {i+1}: {schedule[today][i][0].name} vs {schedule[today][i][1].name}"
                )"""
                if (
                    user.team == schedule[today][i][0].name
                    or user.team == schedule[today][i][1].name
                ):
                    # print(f"  User's team found in game {i+1}")
                    user_game = schedule[today].pop(i)
                    break

            if user_game:
                print("User's game found:")
                print(user_game)
            else:
                print("User's game not found.")

            # Quick simulate the rest of the games
            for match in schedule[today]:
                game = Game(match[0], match[1], True)
                game.quick_simulate()

            # Simulate the user's game
            if user_game:
                game = Game(user_game[0], user_game[1], False)
                game.simulate_game()

            # Clear the games for the day
            del schedule[today]

            # Increment date
            date = increment_date(date)

        elif choice == "2":
            # logging.info the user team's roster
            print_team_roster(get_team_by_name(user.team))

        elif choice == "3":
            # Show stats for players in the selected team
            print("\nChoose a team:")
            for i, team_name in enumerate(TEAM_NAMES, 1):
                print(f"{i}. {team_name}")
            team_choice = input("Enter choice: ")
            selected_team = Team(TEAM_NAMES[int(team_choice) - 1])
            print(f"\n{selected_team.name} Roster:")
            print_team_roster(selected_team)

        elif choice == "4":
            league.print_schedule()
        elif choice == "5":
            league.print_standings()
        elif choice == "6":
            save_game(user, league)
        elif choice == "7":
            save_game(user, league)
            quit()
        elif choice == "8":
            quit()
        else:
            print("[Menu] Invalid choice. Please try again.")


def print_player_stats(player):
    player_info = f"""
    {Fore.YELLOW}==============
    {Fore.CYAN}Name: {Fore.GREEN}{player.name} 
    {Fore.CYAN}Position: {Fore.GREEN}{player.position}
    {Fore.CYAN}Overall: {Fore.GREEN}{player.get_player_overall()}

    {Fore.CYAN}Offense:
        {Fore.MAGENTA}3pt Shooting: {Fore.GREEN}{player.three_point_shooting}
        {Fore.MAGENTA}Midrange Shooting: {Fore.GREEN}{player.mid_range_shooting}
        {Fore.MAGENTA}Finishing: {Fore.GREEN}{player.finishing}
        {Fore.MAGENTA}Passing: {Fore.GREEN}{player.passing}
        {Fore.MAGENTA}Dribbling: {Fore.GREEN}{player.dribbling}
        {Fore.MAGENTA}Speed: {Fore.GREEN}{player.speed}
        {Fore.MAGENTA}Rebounding: {Fore.GREEN}{player.rebounding}

    {Fore.CYAN}Defense:
        {Fore.MAGENTA}Stealing: {Fore.GREEN}{player.stealing}
        {Fore.MAGENTA}Blocking: {Fore.GREEN}{player.blocking}
    {Fore.YELLOW}=============={Style.RESET_ALL}
    """
    print(player_info)


def print_team_roster(team):
    print(f"\n{Fore.CYAN}{team.name} {Fore.YELLOW}Roster:{Style.RESET_ALL}")
    for player in team.players:
        print_player_stats(player)


def print_player_game_stats(player):
    player_game_info = f"""
    {Fore.GREEN}MVP of the game: {Fore.RESET}{player.name} {player.position}
    {Fore.GREEN}Points: {Fore.RESET}{player.points}
    {Fore.GREEN}Fouls: {Fore.RESET}{player.fouls}
    {Fore.GREEN}Fatigue: {Fore.RESET}{player.fatigue}
    {Fore.GREEN}Field Goals (FG): {Fore.RESET}{player.field_goals_made}/{player.field_goals_attempted} - {round(player.field_goal_percentage, 2)}%
    {Fore.GREEN}Three Point FG: {Fore.RESET}{player.three_points_made}/{player.three_points_attempted} - {round(player.three_point_percentage, 2)}%
    {Fore.GREEN}Free Throw FG: {Fore.RESET}{player.free_throws_made}/{player.free_throws_attempted} - {round(player.free_throw_percentage, 2)}%
    {Fore.GREEN}Rebounds (O/D - Total): {Fore.RESET}{player.offensive_rebounds}/{player.defensive_rebounds} - {player.rebounds}
    {Fore.GREEN}Assists: {Fore.RESET}{player.assists}
    {Fore.GREEN}Turnovers: {Fore.RESET}{player.turnovers}
    {Fore.GREEN}Steals: {Fore.RESET}{player.steals}
    {Fore.GREEN}Blocks: {Fore.RESET}{player.blocks}
    """
    print(player_game_info)


def save_game(user, league):
    print(colored("\nSaving game... Please wait.", "yellow"))
    try:
        # Prepare data for saving
        data_to_save = {"user": user, "league": league}

        # Write data to file
        with open("game_save.pkl", "wb") as f:
            pickle.dump(data_to_save, f)

        print(colored("\nGame saved successfully!", "green"))
    except Exception as e:
        print(colored(f"\nAn error occurred while saving the game: {e}", "red"))


def load_game():
    print(colored("\nLoading game... Please wait.", "yellow"))
    try:
        if not os.path.exists("game_save.pkl"):
            raise FileNotFoundError("Save file not found.")

        # Load data from file
        with open("game_save.pkl", "rb") as f:
            loaded_data = pickle.load(f)

        # Reinitialize User and League classes
        user = User()
        league = League()

        # Load the data into the new instances
        user.__dict__ = loaded_data["user"].__dict__
        league.__dict__ = loaded_data["league"].__dict__

        print(colored("\nGame loaded successfully!", "green"))

        # Return to the main menu
        menu()
    except Exception as e:
        print(colored(f"\nAn error occurred while loading the game: {e}", "red"))


def quit():
    print("Thank you for playing!")
    exit()


# misc Def
def create_date(month, day, year):
    """Creates a date object.

    Args:
        month: The month of the date, as a int.
        day: The day of the date, as an integer.
        year: The year of the date, as an integer.

    Returns:
        A date object.
    """

    return date(year, month, day)


def increment_date(date):
    # Increment by 1 day
    new_date = date + timedelta(days=1)
    return new_date


def debug_print(message):
    if debug:
        print(f"Debug: {message}")


if __name__ == "__main__":
    main_menu()
