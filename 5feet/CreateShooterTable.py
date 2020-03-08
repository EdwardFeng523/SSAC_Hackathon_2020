import os
import csv
from collections import defaultdict
import math

GAME_IDS = [
    "M_8279c1d6-4e02-11ea-ab59-024282923f19",
    "M_9672b049-537c-11ea-ab59-024282923f19",
    "M_17472065-4ad8-11ea-9084-0242bdc61da9",
    # "M_a8114fce-5374-11ea-ab59-024282923f19",
    # "M_aa5ba87c-4d2a-11ea-b7ea-0242bdc61da9",
    "M_ea97103a-537c-11ea-ab59-024282923f19"
]


SHOOTER_IDX = 0
CONTESTED_IDX = 1
NDD_IDX = 2
RELEASE_ANGLE_IDX = 3
CAS_IDX = 4

#shooter_dict[shooter_id (int)][0 / 1 (int)]   1 - contested, 0 open
shooter_dict = defaultdict(lambda: defaultdict(list))

shooter_distribution = []
shooter_distribution.append(["Shooter", "Open_Mean", "Open_MSE", "Contested_Mean", "Contested_MSE", "Distribution_Diff"])


def read_csv(file_name):
    csv_file = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            csv_file.append(row)
    return csv_file

def mean(samples):
    if not samples:
        return 0
    return sum(samples) / float(len(samples))

#
def mse(samples, mean):
    if len(samples) == 0:
        return 0
    total = 0
    for sample in samples:
        total += (sample - mean) ** 2
    return total / float(len(samples))

def distribution_diff(mean1, mean2, mse1, mse2):
    return (abs(mean1 - mean2)) / (mse1 + mse2)

for game_id in GAME_IDS:
    # GAME_ID = "M_17472065-4ad8-11ea-9084-0242bdc61da9"
    shot_table_file = read_csv("shot_table_" + game_id + ".csv")

    for shot in shot_table_file[1:]:
        shooter_id = int(shot[SHOOTER_IDX])
        contested = int(shot[CONTESTED_IDX])
        angle = float(shot[RELEASE_ANGLE_IDX])
        if angle < 10:
            continue
        cas = (shot[CAS_IDX])
        # print (cas == '1.0')

        shooter_dict[shooter_id][contested].append(angle)

all_diff = []
for shooter_id in shooter_dict:
    shooter_info = shooter_dict[shooter_id]
    open_samples = shooter_info[0]
    contested_samples = shooter_info[1]

    open_mean = mean(open_samples)
    contested_mean = mean(contested_samples)
    open_mse = mse(open_samples, open_mean)
    contested_mse = mse(contested_samples, contested_mean)

    if (contested_mse == 0 and open_mse == 0) or contested_mean == 0 or open_mean == 0:
        dist_diff = -1
    else:
        dist_diff = distribution_diff(open_mean, contested_mean, open_mse, contested_mse)
        all_diff.append(dist_diff)

    row = [str(shooter_id), str(open_mean), str(open_mse), str(contested_mean), str(contested_mse), str(dist_diff), str(len(open_samples)), str(len(contested_samples))]
    # print (row)
    # if shooter_id == 67369:
    #     print ("id = 67369")
    #     print ("open samples: ", open_samples)
    #     print ("contested samples: ", contested_samples)
    #     print ("-=-=-=-=-=-=-=-=")
    #
    # if shooter_id == 67339:
    #     print ("id = 67339")
    #     print ("open samples: ", open_samples)
    #     print ("contested samples: ", contested_samples)
    #     print ("-=-=-=-=-=-=-=-=")
    #
    # if shooter_id == 68012:
    #     print ("id = 68012")
    #     print ("open samples: ", open_samples)
    #     print ("contested samples: ", contested_samples)
    #     print ("-=-=-=-=-=-=-=-=")
    shooter_distribution.append(row)

print(sum(all_diff) / len(all_diff))
with open("shooter_table_mens.csv", 'w') as output_csv:
    writer = csv.writer(output_csv)
    for row in shooter_distribution:
        writer.writerow(row)

