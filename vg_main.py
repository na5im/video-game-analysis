import pandas as pd
import subprocess
import json
import warnings
import pprint as pp
import re
import Levenshtein
import time

start_time = time.time()


def find_closest_match(game_name, game_data):
    min_distance = None
    closest_match = None

    for title in game_data.keys():
        distance = Levenshtein.distance(game_name.strip(), title.strip())

        if min_distance is None or distance < min_distance:
            min_distance = distance
            closest_match = title

    return closest_match

def load_data():
    with open('results.json', 'r') as file:
        game_data = {}
        for line in file:
            data = json.loads(line)
            title = data.get('title')
            total_shipped = data.get('total_shipped')
            if title:
                stripped_title = title.strip()
                if stripped_title not in game_data:
                    game_data[stripped_title] = []
                game_data[stripped_title].append(total_shipped)

        # Choose the first non-null value for each title
        for key in game_data:
            game_data[key] = next((x for x in game_data[key] if x != 'N/A'), 'N/A')

    return game_data

def get_game_data(game_name, units_shipped, counter, success):
    subprocess.run(["python", "vg_spider.py", game_name])
    data = load_data()
    print(f"Data retrieved: {data}")
    
    closest_match = find_closest_match(game_name, data)
    if closest_match:
        print(f"\n\n\nSCRAPING {game_name}...\nCURRENT LIST OF UNITS: {data[closest_match]}")
        return {closest_match: data[closest_match]}
    else:
        return {}

# change to read your own csv file with "name" column
df = pd.read_csv('uncleaned_full_data.csv')

# Initialize an empty list to store the units shipped data
units_shipped = [0] # Need this to print the units_shipped list as it's being built
none_games = []
LIMIT = 10
counter = 0
success = 0
# df2 = df.head(10)
df['cleaned_name'] = df['name'].apply(lambda x: re.sub(r'\W+', ' ', x))

for game_name in df['cleaned_name']:
    game_data = get_game_data(game_name, units_shipped, success, counter)
    if not game_data:
        units_shipped.append(None)
        none_games.append(game_name)
        counter += 1
        continue

    closest_match = list(game_data.keys())[0]
    units_shipped.append(game_data[closest_match])
    counter += 1
    if any(result.isdigit() for result in game_data[closest_match]):
        success += 1
    print(f"SUCCESS: {success}/{counter}\n\n\n\n")



end_time = time.time()

total_time = end_time - start_time


# Add the units shipped data to the DataFrame as a new column
del units_shipped[0]
df['units_shipped'] = units_shipped
df.to_csv("all_games_with_units2.csv")
# pp.pprint(df)
with open('none_games.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(none_games))
print('Total time:', total_time, 'seconds')
