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

#Create a Schedule for all the teams, Randomized and add it to the SCHEDULE Golabal Variable

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
            match_date = start_date + timedelta(days=i*2)  # Matches every other day
            schedule_with_dates[match_date.strftime("%Y-%m-%d")] = match
        return schedule_with_dates



class Player:
    POSITIONS = ["PG", "SG", "SF", "PF", "C"]

    def __init__(self, number):
        self.name = self.get_random_name(self)
        self.number = number
        self.position = random.choice(self.POSITIONS)
        #Start of Flusahble per Game Temporary Stats
        self.points = 0
        self.fatigue = 0
        self.fouls = 0
        #end of Flushable per Game Temporary Stats

        #Start of Accumalted lifetime Stats
        #Todo do Alltime stats for Each player every after a Game/Game Simulation it adds the temporary stats into this then flushes those
        self.assign_position_based_stats()

    def assign_position_based_stats(self):
        self.passing = self.assign_stat("passing")
        self.dribbling = self.assign_stat("dribbling")
        self.defense = self.assign_stat("defense")
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
        self.defense -= self.fatigue
        self.speed -= self.fatigue

    def recover_stats(self):  # Stats Recovery when their on the bench
        self.three_point_shooting += self.fatigue
        self.mid_range_shooting += self.fatigue
        self.passing += self.fatigue
        self.dribbling += self.fatigue
        self.defense += self.fatigue
        self.speed += self.fatigue



#Todo: Distribute Points Efficiently, Current Distribution is OP and also isnt limited to 100
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
                "defense": 0.03,
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
                "defense": 0.05,
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
                "defense": 0.10,
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
                "defense": 0.15,
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
                "defense": 0.20,
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
    STRATEGIES = ["Offensive", "Defensive", "Balanced", "Offensive Paint", "Offensive Outside", "Iso: Star", "Iso: Hot Hand"]

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
        return max(self.players, key=lambda player: player.points + player.rebounds + player.assists)



class Game:
    def __init__(self, team1, team2, ai_vs_ai=True):
        self.team1 = team1
        self.team2 = team2
        self.score = {self.team1.name: 0, self.team2.name: 0}
        self.quarter = 0
        self.foul_limit = 6  # Player is Fouled out and Cant be Subbed in when this is Reached
        self.fatigue_limit = 500  # Should be adjusted to a number that makes every Stat 50 probably regardless of its starting value
        self.QUARTER_TIME = 720 #in seconds
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
    def simulate_quarter(self):
        quarter_time = QUARTER_TIME  # in seconds, 12 minutes per quarter
        while quarter_time > 0:
            # Check if there are enough players in each team
            if len(self.team1.players) < 5 or len(self.team2.players) < 5:
                print("Not enough players to continue the game. Game over.")
                return

            possession_time = random.randint(4, 23)
            quarter_time -= possession_time
            if quarter_time < 0:  # no time left in the quarter
                break


            #Todo: Decide the Jumpball based on Rebounding and Height Stat + Luck, Stat WEights:70% Luck Weight: 30%
            if self.possesion == "":
                random.random() < 

            # Modify shot chances based on the team's strategy
            if offensive_team.strategy == "Offensive":
                three_point_attempt_chance = (
                    0.3  # Increased chance for a 3-point attempt
                )
                mid_range_attempt_chance = (
                    0.6  # Increased chance for a mid-range attempt
                )
            elif offensive_team.strategy == "Defensive":
                three_point_attempt_chance = (
                    0.1  # Decreased chance for a 3-point attempt
                )
                mid_range_attempt_chance = (
                    0.4  # Decreased chance for a mid-range attempt
                )
            else:  # Balanced strategy
                three_point_attempt_chance = 0.2
                mid_range_attempt_chance = 0.5

            # Use active_players for game simulation
            offensive_player = random.choice(offensive_team.active_players)
            defensive_player = random.choice(defensive_team.active_players)

            # Check for foul
            foul_chance = (0.5 / (4 * 10)) * (
                defensive_player.defense / 100
            )  # Increase foul chance

            if random.random() < foul_chance:
                defensive_player.fouls += 1
                logging.info(
                    f"{defensive_team.name}'s {defensive_player} commits a foul!"
                )

                if defensive_player.fouls >= 6:
                    logging.info(
                        f"{defensive_team.name}'s {defensive_player} is fouled out!"
                    )
                    defensive_team.players.remove(defensive_player)
                else:
                    # Free throw attempt
                    if random.random() < offensive_player.three_point_shooting / 100:
                        self.score[offensive_team.name] += 1
                        offensive_player.points += 1
                        logging.info(
                            f"{offensive_team.name}'s {offensive_player} makes the free throw! Current score: {self.score}"
                        )

            # Check for steal
            steal_chance = (1.1 / (4 * 10)) * (defensive_player.stealing / 100)
            if random.random() < steal_chance:
                logging.info(
                    f"{defensive_team.name}'s {defensive_player} steals the ball!"
                )
                continue  # possession ends, move to the next one

            # Choose type of shot
            if random.random() < 0.2:  # 20% chance for a 3-point attempt
                shot_success = offensive_player.three_point_shooting
                points = 3
            elif random.random() < 0.5:  # 30% chance for a mid-range attempt
                shot_success = offensive_player.mid_range_shooting
                points = 2
            else:  # 50% chance for a finish attempt
                shot_success = offensive_player.finishing
                points = 2

            # Check for block
            block_chance = (0.7 / (4 * 10)) * (defensive_player.blocking / 100)
            if random.random() < block_chance:
                logging.info(
                    f"{defensive_team.name}'s {defensive_player} blocks the shot!"
                )
                continue  # possession ends, move to the next one

            # During the game
            shot_chance = (
                shot_success / 100 - offensive_player.fatigue / FATIGUE_LIMIT
            )  # Reduce shot success rate by fatigue
            shot_chance = max(
                shot_chance, 0.05
            )  # Ensure there's at least a 5% chance to score
            if random.random() < shot_chance:  # shot success rate
                self.score[offensive_team.name] += points
                offensive_player.points += points
                logging.info(
                    f"Excellent shot by {offensive_team.name}'s {offensive_player}! That's {points} points for them. "
                    f"Current score: {self.score}"
                )
            else:
                print(
                    f"{offensive_team.name}'s {offensive_player} misses the shot! The possession changes."
                )

            # Increase fatigue only for active players
            for player in offensive_team.active_players + defensive_team.active_players:
                player.fatigue += 1
                player.decrease_stats()

            self.substitute_players()

    def simulate_game(self):
        for self.quarter in range(1, 5):  # 4 quarters
            # Quarter start
            logging.info(
                f"\nQuarter {self.quarter} is about to start! Let's see some action!\nCurrent score: {self.score}"
            )
            self.choose_strategy(self.team1)  # Let the user choose a strategy
            self.simulate_quarter()
            # ...

            # Quarter end
            logging.info(
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
        logging.info(
            f"\nWhat a game! The {winner} team takes the victory with a final score of {self.score[winner]} to {self.score[loser]}!"
        )
        if winner == self.team1.name:
            mvp = self.team1.get_mvp()
        else:
            mvp = self.team2.get_mvp()
        logging.info(
            f"MVP of the game: {mvp.name} from {winner} with {mvp.points} points"
        )


def new_game():
    while True:
        print("\nChoose a team:")
        for i, team_name in enumerate(TEAM_NAMES, 1):
            logging.info(f"{i}. {team_name}")

        choice = input("Enter choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(TEAM_NAMES):
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
        else:
            print("Invalid choice. Please try again.")                


def new_game():
    print("\nChoose a team:")
    for i, team_name in enumerate(TEAM_NAMES, 1):
        logging.info(f"{i}. {team_name}")

    choice = input("Enter choice: ")
    try:
        logging.info(
            "\nCreating and Generating Team Names, Player Names, Numbers and Stats, PLease wait..\nThis might take a while.."
        )
        #Todo: Geenrate Names only if there is no player.json or it is empty, otherwise load names from that
        user_team = Team(TEAM_NAMES[int(choice) - 1])

        #Todo: Make the AI Team based on The Schedule
        ai_team = Team(
            random.choice(
                [name for i, name in enumerate(TEAM_NAMES) if i != int(choice) - 1]
            )
        )
        game = Game(user_team, ai_team)
        while menu(game):  # Keep the game running until the user chooses to quit
            game.simulate_game()
    except (IndexError, ValueError):
        print("Invalid choice. Please try again.")
        new_game()

#Todo: Fix and Implement tho Modified Menu
def menu(game):
    while True:
        print("\nWhat would you like to do?")
        print("1. Simulate Other Games and Play to the Next Game")
        print("2. Check Your Team Roster")
        print("3. Check other Teams") #Todo: Should be able to Show New Choice Menu for All the Other Teams and in there show Stats for Players in the Team Selected
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
                logging.info(
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

#Todo Fix Save and Load to JSON format, Save every stat and make it Loadable as Well
def save_game(game):
    with open("save_file.json", "w") as f:
        json.dump(game.__dict__, f)
    print("Game saved!")


def load_game():
    if os.path.exists("save_file.json"):
        with open("save_file.json", "r") as f:
            game_data = json.load(f)
        game = Game(game_data["user_team"], game_data["ai_team"])
        logging.info(f"Loaded game: {game.score}")
        game.simulate_game()
    else:
        print("No saved game found.")
        main_menu()


def quit():
    print("Thank you for playing!")
    exit()


if __name__ == "__main__":
    main_menu()
