import os
import csv
from collections import defaultdict
import math
import numpy as np

#1828mm = 6feet
#609mm = 2 feet
#1515mm = 5 feet
CONTESTED_THRESHOLD = 1515

RELEASE_TIME_DURATION = 40

PLAYBYPLAY_DIR = "./explore-shottracker/playbyplay"
TIMESERIES_DIR = "./explore-shottracker/timeseries"

# OUTPUT_FILE = "shot_table_men.csv"

#pbp data indices
TIMESTAMP_IDX = 0
BLK_IDX = 6
FGA3_IDX = 14
FGA3_CAS_IDX = 26
PLAYER_ID_IDX = 2
PBP_TEAM_IDX = 1

#player loc indices
PLAYER_LOC_TEAM_IDX = 5
PLAYER_LOC_PLAYER_IDX = 6
PLAYER_X = 8
PLAYER_Y = 9
PLAYER_Z = 10

#ball_loc indices
BALL_X = 6
BALL_Y = 7
BALL_Z = 8


# shots_table = []
#
# shots_table.append(["Shooter", "Contested", "NDD", "Release_Angle", "CAS"])


def read_csv(file_name):
    csv_file = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            csv_file.append(row)
    return csv_file

def read_csv_ball(file_name):
    csv_file = {}
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue
            csv_file[int(row[TIMESTAMP_IDX])] = row
    return csv_file

def read_csv_player(file_name):
    #csv_file[time_stamp][player_id] = row
    first_row = True
    csv_file = defaultdict(dict)
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if first_row:
                first_row = False
                continue
            csv_file[int(row[TIMESTAMP_IDX])][int(float(row[PLAYER_LOC_PLAYER_IDX]))] = row
    return csv_file


def dist(a, b):
    return math.sqrt((float(a[0]) - float(b[0]))**2 + (float(a[1]) - float(b[1]))**2 + (float(a[2]) - float(b[2]))**2)

def two_d_dist(a, b):
    return math.sqrt((float(a[0]) - float(b[0])) ** 2 + (float(a[1]) - float(b[1])) ** 2)

def calculate_angle(initial, released):
    horizontal_dist = two_d_dist((initial[0], initial[1]), (released[0], released[1]))
    vertical_dist = abs(float(initial[2]) - float(released[2]))
    return math.atan2(vertical_dist, horizontal_dist) / math.pi * 180.0

def check_ndd(shotX, shotY, nearestDX, nearestDY, hoopX, hoopY):
    shot_pos = np.array(shotX, shotY)
    nearest_pos = np.array(nearestDX, nearestDY)
    hoop_pos = np.array(hoopX, hoopY)
    shot_dist = np.linalg.norm(hoop_pos - shot_pos)
    nearestD_dist = np.linalg.norm(hoop_pos - nearest_pos)
    if nearestD_dist < shot_dist:
        return True
    else:
        return False



for pbp_file_name in os.listdir(PLAYBYPLAY_DIR):

    shots_table = []

    shots_table.append(["Shooter", "Contested", "NDD", "Release_Angle", "CAS"])

    if pbp_file_name[0] == "W":
        continue

    if pbp_file_name[0] == ".":
        continue
    game_id = pbp_file_name[:-4]
    print("game id is:", game_id)

    pbp_file_path = PLAYBYPLAY_DIR + "/" + pbp_file_name
    ball_loc_path = TIMESERIES_DIR + "/" + game_id + "/" + game_id + "_ballLocations.csv"
    shot_path = TIMESERIES_DIR + "/" + game_id + "/" + game_id + "_shots.csv"
    player_loc_path = TIMESERIES_DIR + "/" + game_id + "/" + game_id + "_playerLocations.csv"

    pbp_file = read_csv(pbp_file_path)
    ball_loc_file = read_csv_ball(ball_loc_path)
    player_loc_file = read_csv_player(player_loc_path)
    shot_file = read_csv_ball(shot_path)

    print(pbp_file[1][PLAYER_ID_IDX])

    for i in range(1, len(pbp_file)):
        # get all 3pt shots that are not blocked
        if pbp_file[i][FGA3_IDX] == '1.0' and pbp_file[i-1][BLK_IDX] != "1.0":
            shooter_id = int(pbp_file[i][PLAYER_ID_IDX])
            time_stamp = int(pbp_file[i][TIMESTAMP_IDX])
            shooter_team_id = pbp_file[i][PBP_TEAM_IDX]
            cas = pbp_file[i][FGA3_CAS_IDX]
            otd = pbp_file[i][FGA3_CAS_IDX + 2]

            # neither a cas nor a otd
            if cas == otd:
                print ("ERROR: Neither a cas nor a otd")
                continue

            shooter_pos = None
            defenders = []
            # find the NDD candidates
            for dis in range(100):
                new_time = time_stamp - dis
                if new_time in player_loc_file:
                    print ("found new time minus")
                if new_time in player_loc_file and shooter_id in player_loc_file[new_time]:
                    shooter_row = player_loc_file[new_time][shooter_id]
                    shooter_pos = (shooter_row[PLAYER_X], shooter_row[PLAYER_Y], shooter_row[PLAYER_Z])

                    for player_row_key in player_loc_file[new_time]:
                        player_row = player_loc_file[new_time][player_row_key]
                        if player_row[PLAYER_LOC_TEAM_IDX] != shooter_team_id:
                            defenders.append([player_row[PLAYER_LOC_PLAYER_IDX], (player_row[PLAYER_X], player_row[PLAYER_Y], player_row[PLAYER_Z])])
                    break

                new_time = time_stamp + dis
                if new_time in player_loc_file:
                    print ("found new time plus")
                if new_time in player_loc_file and shooter_id in player_loc_file[new_time]:
                    shooter_row = player_loc_file[new_time][shooter_id]
                    shooter_pos = (shooter_row[PLAYER_X], shooter_row[PLAYER_Y], shooter_row[PLAYER_Z])

                    for player_row_key in player_loc_file[new_time]:
                        player_row = player_loc_file[new_time][player_row_key]
                        if player_row[PLAYER_LOC_TEAM_IDX] != shooter_team_id:
                            defenders.append([player_row[PLAYER_LOC_PLAYER_IDX],
                                              (player_row[PLAYER_X], player_row[PLAYER_Y], player_row[PLAYER_Z])])
                    break

            this_half = True
            hoop_X = None
            hoop_Y = None

            if shooter_pos and time_stamp in shot_file:
                hoop_X = shot_file[time_stamp][14]
                hoop_Y = shot_file[time_stamp][15]
                if float(shot_file[time_stamp][15]) * float(shooter_pos[1]) < 0:
                    print("Not a shot in this half court, skipped")
                    print("  time:", time_stamp)
                    print("  game_id:", game_id)
                    this_half = False


            if not this_half:
                continue

            if not shooter_pos:
                print ("ERROR: Shooter position not found")
                print("  time:", time_stamp)
                print("  game_id:", game_id)
                continue
            else:
                print ("found shooter position")

            neareat_dist = float('inf')
            nearest_pos = None
            ndd = "NA"

            for defender_id, defender_pos in defenders:
                if dist(defender_pos, shooter_pos) < neareat_dist:
                    neareat_dist = dist(defender_pos, shooter_pos)
                    nearest_pos = defender_pos
                    ndd = defender_id

            contested = 0
            print("ndd distance is", neareat_dist)
            if neareat_dist <= CONTESTED_THRESHOLD:
                if hoop_X and two_d_dist((hoop_X, hoop_Y), (nearest_pos[0], nearest_pos[1])) < two_d_dist((hoop_X, hoop_Y), (shooter_pos[0], shooter_pos[1])):
                    contested = 1

            if not contested:
                ndd = "NA"

            initial_ball_pos = None
            initial_ball_time_stamp = 0
            released_ball_pos = None

            ### Find the shooting arc ball pos
            for dis in range(100):
                new_time = time_stamp + dis
                if new_time in ball_loc_file:
                    initial_ball_row = ball_loc_file[new_time]
                    initial_ball_pos = (initial_ball_row[BALL_X], initial_ball_row[BALL_Y], initial_ball_row[BALL_Z])
                    initial_ball_time_stamp = new_time
                    break



            for dis in range(100):
                released_new_time = initial_ball_time_stamp + RELEASE_TIME_DURATION + dis
                if released_new_time in ball_loc_file:
                    released_ball_row = ball_loc_file[released_new_time]
                    released_ball_pos = (released_ball_row[BALL_X], released_ball_row[BALL_Y], released_ball_row[BALL_Z])
                    break

            if not (initial_ball_pos and released_ball_pos):
                print("ERROR: Didn't find ball positions for shot", initial_ball_pos, released_ball_pos)
                print("  time:", time_stamp)
                print("  game_id:", game_id)
                continue

            angle = calculate_angle(initial_ball_pos, released_ball_pos)

            output_row = [str(shooter_id), str(contested), ndd, str(angle), cas]
            print(output_row)
            shots_table.append(output_row)



    with open("5feet/shot_table_" + game_id + ".csv", 'w') as output_csv:
        writer = csv.writer(output_csv)
        for row in shots_table:
            writer.writerow(row)