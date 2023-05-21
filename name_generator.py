import json
from faker import Faker


def generate_player_names(num_players):
    fake = Faker()
    male_player_names = []
    while len(male_player_names) < num_players:
        name = fake.first_name_male() + " " + fake.last_name_male()
        if name not in male_player_names:
            male_player_names.append(name)
    return male_player_names


def main():
    num_players = 1200  # Number of players to generate
    player_names = generate_player_names(num_players)

    if player_names:
        players_data = {"players": player_names}
        with open("players.json", "w") as file:
            json.dump(players_data, file, indent=4)
            print(f"{num_players} male player names saved to players.json.")
    else:
        print("No male player names to save.")


if __name__ == "__main__":
    main()
