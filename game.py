import os
import pickle
import random
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)


QUARTER_TIME = 720
FATIGUE_LIMIT = 500
FOUL_LIMIT = 5


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


class Player:
    POSITIONS = ["PG", "SG", "SF", "PF", "C"]

    def __init__(self, number):
        self.name = self.get_random_name()
        self.number = number
        self.position = random.choice(self.POSITIONS)
        self.points = 0
        self.fatigue = 0
        self.fouls = 0
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
        except (requests.RequestException, KeyError):
            logging.error("Failed to fetch name from API, using a default name.")
            return f"Player_{random.randint(1, 9999)}"  # Fallback to random name

    def __str__(self):
        return self.name


class Team:
    STRATEGIES = ["Offensive", "Defensive", "Balanced"]

    def __init__(self, name, strategy="Balanced"):
        self.name = name
        self.strategy = strategy
        self.players = [Player(i) for i in range(1, 16)]  # 15 players
        self.active_players = self.players[:5]  # Starting 5
        self.bench_players = self.players[5:]  # Remaining players on the bench

    def get_team_avg_stat(self, stat):
        return sum(getattr(player, stat) for player in self.players) / len(self.players)

    def get_mvp(self):
        return max(self.players, key=lambda player: player.points)


class Game:
    def __init__(self, user_team, ai_team):
        self.user_team = user_team
        self.ai_team = ai_team
        self.score = {self.user_team.name: 0, self.ai_team.name: 0}
        self.quarter = 0
        self.foul_limit = 5  # Player must sit after reaching this foul limit
        self.fatigue_limit = 500  # Player must rest after reaching this fatigue limit

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
        quarter_time = QUARTER_TIME  # in seconds, 12 minutes per quarter
        while quarter_time > 0:
            # Check if there are enough players in each team
            if len(self.user_team.players) < 5 or len(self.ai_team.players) < 5:
                logging.info("Not enough players to continue the game. Game over.")
                return

            possession_time = random.randint(4, 23)
            quarter_time -= possession_time
            if quarter_time < 0:  # no time left in the quarter
                break

            if random.random() < 0.5:  # 50% chance for each team to attempt
                offensive_team = self.user_team
                defensive_team = self.ai_team
            else:
                offensive_team = self.ai_team
                defensive_team = self.user_team

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
                f"\nQuarter {self.quarter} is about to start! Let's see some action!\n"
            )
            self.choose_strategy(self.user_team)  # Let the user choose a strategy
            self.simulate_quarter()
            # ...

            # Quarter end
            logging.info(
                f"That's the end of quarter {self.quarter}. The players are taking a breather."
            )
            print("\nGame Stats:")
            for team in [self.user_team, self.ai_team]:
                print(f"\n{team.name}:")
                for player in team.players:
                    print(
                        f"{player.name} - Points: {player.points}, Fouls: {player.fouls}, Fatigue: {player.fatigue}"
                    )

            time.sleep(1)  # pause for a second between quarters

        self.print_result()

    def substitute_players(self):
        for team in [self.user_team, self.ai_team]:
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
        if winner == self.user_team.name:
            mvp = self.user_team.get_mvp()
        else:
            mvp = self.ai_team.get_mvp()
        logging.info(
            f"MVP of the game: {mvp.name} from {winner} with {mvp.points} points"
        )


def main_menu():
    logging.info("Welcome to the Basketball Simulator!")
    logging.info("1. Start a new game")
    logging.info("2. Load a saved game")
    logging.info("3. Quit")

    choice = input("Enter your choice: ")
    if choice == "1":
        new_game()
    elif choice == "2":
        load_game()
    elif choice == "3":
        quit()
    else:
        logging.info("Invalid choice. Please try again.")
        main_menu()


def new_game():
    logging.info("\nChoose a team:")
    for i, team_name in enumerate(TEAM_NAMES, 1):
        logging.info(f"{i}. {team_name}")

    choice = input("Enter choice: ")
    try:
        logging.info(
            "\nCreating and Generating Team Names, Player Names, Numbers and Stats, PLease wait..\nThis might take a while.."
        )
        user_team = Team(TEAM_NAMES[int(choice) - 1])
        ai_team = Team(
            random.choice(
                [name for i, name in enumerate(TEAM_NAMES) if i != int(choice) - 1]
            )
        )
        game = Game(user_team, ai_team)
        while menu(game):  # Keep the game running until the user chooses to quit
            game.simulate_game()
    except (IndexError, ValueError):
        logging.info("Invalid choice. Please try again.")
        new_game()


def menu(game):
    while True:
        logging.info("\nWhat would you like to do?")
        logging.info("1. Play Next Game")
        logging.info("2. Check Roster")
        logging.info("3. Save")
        logging.info("4. Save and Exit")
        logging.info("5. Exit without Saving")

        choice = input("Enter your choice: ")
        if choice == "1":
            return True
        elif choice == "2":
            # logging.info the user team's roster
            logging.info("\nYour Team Roster:")
            for player in game.user_team.players:
                logging.info(
                    f"{player.name} ({player.position}) - {player.shooting}/{player.passing}/{player.dribbling}/{player.defense}/{player.speed}"
                )
        elif choice == "3":
            # Save the game
            save_game(game)
            logging.info("Game saved!")
        elif choice == "4":
            # Save and exit
            save_game(game)
            logging.info("Game saved!")
            return False
        elif choice == "5":
            # Exit without saving
            return False
        else:
            logging.info("Invalid choice. Please try again.")


def save_game(game):
    with open("save_file.json", "w") as f:
        json.dump(game.__dict__, f)
    logging.info("Game saved!")


def load_game():
    if os.path.exists("save_file.json"):
        with open("save_file.json", "r") as f:
            game_data = json.load(f)
        game = Game(game_data["user_team"], game_data["ai_team"])
        logging.info(f"Loaded game: {game.score}")
        game.simulate_game()
    else:
        logging.info("No saved game found.")
        main_menu()


def quit():
    logging.info("Thank you for playing!")
    exit()


if __name__ == "__main__":
    main_menu()
