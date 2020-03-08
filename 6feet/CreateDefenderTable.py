import csv
from collections import defaultdict

SHOOTER_IDX = 0
CONTESTED_IDX = 1
NDD_IDX = 2
RELEASE_ANGLE_IDX = 3
CAS_IDX = 4

GAME_IDS = [
    "M_8279c1d6-4e02-11ea-ab59-024282923f19",
    "M_9672b049-537c-11ea-ab59-024282923f19",
    "M_17472065-4ad8-11ea-9084-0242bdc61da9",
    "M_a8114fce-5374-11ea-ab59-024282923f19",
    "M_aa5ba87c-4d2a-11ea-b7ea-0242bdc61da9",
    "M_ea97103a-537c-11ea-ab59-024282923f19"
]

def mean(samples):
    if not samples:
        return 0
    return sum(samples) / float(len(samples))

def read_shooter_csv(file_name):
    csv_file = {}
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue
            csv_file[int(row[0])] = float(row[1])
    return csv_file

def read_csv(file_name):
    csv_file = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            csv_file.append(row)
    return csv_file


shooter_table = read_shooter_csv("shooter_table_mens.csv")

defender_dict = defaultdict(list)

defender_table = []
defender_table.append(["Defender", "Delta_angle", "Total defense"])

for game_id in GAME_IDS:
    # game_id = "M_17472065-4ad8-11ea-9084-0242bdc61da9"
    shot_table_file = read_csv("shot_table_" + game_id + ".csv")
    for shot in shot_table_file[1:]:
        shooter_id = int(shot[SHOOTER_IDX])
        if shot[NDD_IDX] != 'NA':
            ndd_id = int(float(shot[NDD_IDX]))
        contested = int(shot[CONTESTED_IDX])
        angle = float(shot[RELEASE_ANGLE_IDX])
        if angle < 10:
            continue
        cas = (shot[CAS_IDX])

        if shooter_id not in shooter_table:
            print (shooter_id, "not in shooter table")
            continue

        if contested:
            shooter_avg_angle = shooter_table[shooter_id]
            defender_dict[ndd_id].append(abs(shooter_avg_angle - angle))


for defender_id in defender_dict:
    samples = defender_dict[defender_id]
    defender_table.append([str(defender_id), str(mean(samples)), str(len(samples))])

with open("defender_table_mens.csv", 'w') as output_csv:
    writer = csv.writer(output_csv)
    for row in defender_table:
        writer.writerow(row)

