# Clean up script for the datasets NEA gives.
# Essentially groups points which are close to each other as a single unit
# I made this an N**2 algorithm because I am lazy. This would be a pain to run. Defo

import json

EPSILON = 5e-6 #Arbitrary circle size

final_json_list = []
counter = 0

with open('data.json') as data_file:
    data = json.load(data_file)

    for datapoint in data:
        counter += 1
        if (counter % 1000 == 0):
            print (counter)
        lat = datapoint[0]
        long = datapoint[1]
        seen_before = False
        for previous in final_json_list:
            if (previous[0] - lat)**2 + (previous[1] - long)**2 < EPSILON:
                seen_before = True
                break
        if seen_before:
            continue
        lat = round (lat, 4)
        long = round (long, 4)
        final_json_list.append([lat, long])

    print (len(final_json_list))

file = open("cleanupData.json", "w")
file.write(str(final_json_list))
file.close()
