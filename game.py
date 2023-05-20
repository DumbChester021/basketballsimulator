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

    # Create a Schedule for all the teams, Randomized and add it to the SCHEDULE Golabal Variable

    def create_schedule(self):
        # Get the list of teams
        teams = self.teams

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

    def get_schedule(self):
        return SCHEDULE


class Player:
    POSITIONS = ["PG", "SG", "SF", "PF", "C"]

    def __init__(self, number):
        self.name = self.get_random_name(self)
        self.number = number
        self.position = random.choice(self.POSITIONS)
        # Start of Flusahble per Game Temporary Stats
        self.points = 0
        self.fatigue = 0
        self.fouls = 0
        # end of Flushable per Game Temporary Stats

        # Start of Accumalted lifetime Stats
        # Todo do Alltime stats for Each player every after a Game/Game Simulation it adds the temporary stats into this then flushes those
        self.assign_position_based_stats()

    def assign_position_based_stats(self):
        self.passing = self.assign_stat("passing")
        self.dribbling = self.assign_stat("dribbling")
        self.speed = self.assign_stat("speed")
        self.three_point_shooting = self.assign_stat("three_point_shooting")
        self.mid_range_shooting = self.assign_stat("mid_range_shooting")
        self.finishing = self.assign_stat("finishing")
        self.blocking = self.assign_stat("blocking")
        self.stealing = self.assign_stat("stealing")
        self.rebounding = self.assign_stat("rebounding")
        self.endurance = self.assign_stat("endurance")

    def decrease_stats(self):  # Decreasing Stats based on their Fatigue Level
        self.three_point_shooting -= self.fatigue
        self.mid_range_shooting -= self.fatigue
        self.passing -= self.fatigue
        self.dribbling -= self.fatigue
        self.speed -= self.fatigue

    def recover_stats(self):  # Stats Recovery when their on the bench
        self.three_point_shooting += self.fatigue
        self.mid_range_shooting += self.fatigue
        self.passing += self.fatigue
        self.dribbling += self.fatigue
        self.speed += self.fatigue

    # Todo: Distribute Points Efficiently, Current Distribution is OP and also isnt limited to 100
    def assign_stat(self, stat):
        position_weights = {
            "PG": {  # Point Guard
                "passing": 0.20,
                "dribbling": 0.20,
                "speed": 0.15,
                "three_point_shooting": 0.15,
                "mid_range_shooting": 0.10,
                "stealing": 0.10,
                "endurance": 0.05,
                "finishing": 0.01,
                "blocking": 0.00,
                "rebounding": 0.01,
            },
            "SG": {  # Shooting Guard
                "passing": 0.10,
                "dribbling": 0.15,
                "speed": 0.15,
                "three_point_shooting": 0.20,
                "mid_range_shooting": 0.15,
                "stealing": 0.10,
                "endurance": 0.05,
                "finishing": 0.03,
                "blocking": 0.01,
                "rebounding": 0.01,
            },
            "SF": {  # Small Forward
                "passing": 0.10,
                "dribbling": 0.10,
                "speed": 0.10,
                "three_point_shooting": 0.15,
                "mid_range_shooting": 0.15,
                "stealing": 0.10,
                "endurance": 0.10,
                "finishing": 0.05,
                "blocking": 0.03,
                "rebounding": 0.02,
            },
            "PF": {  # Power Forward
                "passing": 0.05,
                "dribbling": 0.05,
                "speed": 0.08,
                "three_point_shooting": 0.10,
                "mid_range_shooting": 0.15,
                "stealing": 0.05,
                "endurance": 0.10,
                "finishing": 0.15,
                "blocking": 0.10,
                "rebounding": 0.02,
            },
            "C": {  # Center
                "passing": 0.05,
                "dribbling": 0.05,
                "speed": 0.05,
                "three_point_shooting": 0.05,
                "mid_range_shooting": 0.10,
                "stealing": 0.05,
                "endurance": 0.10,
                "finishing": 0.20,
                "blocking": 0.10,
                "rebounding": 0.05,
            },
        }

        base_stat = random.randint(50, 100)
        weight = position_weights[self.position].get(stat, 0)
        return int(base_stat + weight * base_stat)

    @staticmethod
    def get_random_name(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            return response.json()["name"]
        except (requests.RequestException, KeyError) as e:
            logging.error("Failed to fetch name from API, using a default name.")
            print(f"Error: {e}")
            return f"Player_{random.randint(1, 9999)}"  # Fallback to random name

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
        self.QUARTER_TIME = 720  # in seconds
        self.possession = ""

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

    def simulate_quarter(self):
        quarter_time = self.QUARTER_TIME
        while quarter_time > 0:
            possession_time = random.randint(4, 23)
            quarter_time -= possession_time
            if quarter_time < 0:  # no time left in the quarter
                break

            # TODO: Implement the rest of the simulation logic here
            # This will involve a lot of conditional logic based on the team's strategy,
            # the player's stats, and random chance. It will also involve updating the
            # game state (score, possession, etc.) based on the outcome of each possession.

            # Get both teams Strategies First
            offensive_strategy = self.team1.strategy
            defensive_strategy = self.team2.strategy

            # Get teams First 5
            offensive_players = self.team1.active_players[:5]
            defensive_players = self.team2.active_players[:5]

            # Check if Strategy of Offensive Team is ISO: Star, if it is, Chance of Picking the Star PLayer to have the POssesion is 80%
            if offensive_strategy == "Iso: Star":
                star_player = (
                    self.team1.get_star_player()
                )  # Assuming you have a method to get the star player
                offensive_player = random.choices(
                    offensive_players,
                    weights=[
                        0.8 if player == star_player else 0.05
                        for player in offensive_players
                    ],
                    k=1,
                )[0]
            # Check if Strategy of Offensive Team is ISO: Hot Hand, if it is, Chance of Picking the Highest Point in the First 5 is 80%
            elif offensive_strategy == "Iso: Hot Hand":
                hot_hand_player = (
                    self.team1.get_hot_hand_player()
                )  # Assuming you have a method to get the hot hand player
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

            # Pick the Defensive player on the Defensive team, It should match the POsition of the OFfensive PLayer, if theres no Similar pos, Randomize
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

            # TODO: Implement the rest of the simulation logic here
            # This will involve a lot of conditional logic based on the team's strategy,
            # the player's stats, and random chance. It will also involve updating the
            # game state (score, possession, etc.) based on the outcome of each possession.

            # Pre-Possesion
            pre_possession_time = random.randint(1, 5)
            quarter_time -= pre_possession_time
            if quarter_time < 0:  # no time left in the quarter
                break

            # Check for steal
            steal_chance = (
                max(0, defensive_player.stealing - offensive_player.dribbling) / 100
            )
            if random.random() < steal_chance:
                print(
                    f"{defensive_player.name} from {self.team2.name} steals the ball!"
                )
                # Swap offensive and defensive teams
                self.team1, self.team2 = self.team2, self.team1
                # Swap offensive and defensive players
                offensive_player, defensive_player = defensive_player, offensive_player
                # Check for fastbreak
                if defensive_player.speed > offensive_player.speed:
                    print(
                        f"{defensive_player.name} from {self.team2.name} makes a fastbreak for 2 points!"
                    )
                    self.score[self.team2.name] += 2
                    defensive_player.points += 2
                    defensive_player.fatigue += 1
                continue  # possession ends, move to the next one

            # Possession
            # Check type of shot depending on the tendencies of the player
            shot_type = random.choices(
                ["finish", "mid_range", "three_point"],
                weights=[
                    offensive_player.finish_tendency,
                    offensive_player.mid_range_tendency,
                    offensive_player.three_point_tendency,
                ],
                k=1,
            )[0]

            # Check for block
            block_chance = (
                max(0, defensive_player.blocking - offensive_player.shooting) / 100
            )
            if random.random() < block_chance:
                print(
                    f"{defensive_player.name} from {self.team2.name} blocks the shot!"
                )
                continue  # possession ends, move to the next one

            # Randomize if there should be a foul
            foul_chance = min(
                0.08, abs(defensive_player.overall - offensive_player.overall) / 100
            )
            if random.random() < foul_chance:
                print(f"{defensive_player.name} from {self.team2.name} commits a foul!")
                defensive_player.fouls += 1
                if defensive_player.fouls >= self.foul_limit:
                    print(
                        f"{defensive_player.name} from {self.team2.name} is fouled out!"
                    )
                    self.team2.active_players.remove(defensive_player)
                    if self.team2.bench_players:
                        substitute = self.team2.bench_players.pop(0)
                        self.team2.active_players.append(substitute)
                        print(
                            f"{substitute.name} from {self.team2.name} is substituted in!"
                        )
                # Check if the free throw goes in
                if random.random() < offensive_player.free_throw_shooting / 100:
                    print(
                        f"{offensive_player.name} from {self.team1.name} makes the free throw!"
                    )
                    self.score[self.team1.name] += 1
                    offensive_player.points += 1
                continue  # possession ends, move to the next one

            # Check if the shot goes in
            shot_success_chance = (
                offensive_player.shooting / 100
                - offensive_player.fatigue / self.fatigue_limit
            )
            if random.random() < shot_success_chance:
                points = 3 if shot_type == "three_point" else 2
                print(
                    f"{offensive_player.name} from {self.team1.name} makes the shot for {points} points!"
                )
                self.score[self.team1.name] += points
                offensive_player.points += points
            else:
                print(
                    f"{offensive_player.name} from {self.team1.name} misses the shot!"
                )

            # Post-Possesion
            # Check the average rebound stats of both teams
            offensive_rebound_avg = sum(
                player.rebounding for player in self.team1.active_players
            ) / len(self.team1.active_players)
            defensive_rebound_avg = sum(
                player.rebounding for player in self.team2.active_players
            ) / len(self.team2.active_players)

            # Defensive team should have base 70% chance of rebound
            # Offensive team has 30% chance
            rebound_chance = 0.7 + (defensive_rebound_avg - offensive_rebound_avg) / 100
            if random.random() < rebound_chance:
                print(f"{self.team2.name} gets the rebound!")
            else:
                print(f"{self.team1.name} gets the rebound!")
                # Swap offensive and defensive teams
                self.team1, self.team2 = self.team2, self.team1

            # Add fatigue to the players
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

    def simulate_game(self):
        for self.quarter in range(1, 5):  # 4 quarters
            # Quarter start
            print(
                f"\nQuarter {self.quarter} is about to start! Let's see some action!\nCurrent score: {self.score}"
            )
            self.choose_strategy(self.team1)  # Let the user choose a strategy
            self.simulate_quarter()
            # ...

            # Quarter end
            print(
                f"That's the end of quarter {self.quarter}. The players are taking a breather.\nThis is the Current score: {self.score}"
            )
            print("\nGame Stats:")
            for team in [self.team1, self.team2]:
                print(f"\n{team.name}:")
                for player in team.players:
                    print(
                        f"{player.name} - Points: {player.points}, Fouls: {player.fouls}, Fatigue: {player.fatigue}"
                    )

            time.sleep(1)  # pause for a second between quarters

        self.print_result()

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
        print(f"MVP of the game: {mvp.name} from {winner} with {mvp.points} points")


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
            for player in game.user_team.players:
                print(
                    f"{player.name} ({player.position}) - {player.three_point_shooting}/{player.mid_range_shooting}/{player.finishing}/{player.passing}/{player.dribbling}/{player.defense}/{player.speed}"
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
                    f"{player.name} ({player.position}) - {player.three_point_shooting}/{player.mid_range_shooting}/{player.finishing}/{player.passing}/{player.dribbling}/{player.defense}/{player.speed}"
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
