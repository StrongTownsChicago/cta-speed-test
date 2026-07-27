import argparse
import csv
import os
import sys

# TODO: Take a file pattern as input instead of a folder.
# TODO: Split into separate scripts for generating counts and weighted averages.

def parse_timestamp(s: str):
    # TODO: Do this more sophisticatedly in the future.
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    hour = int(s[8:10])
    minute = int(s[10:12])
    second = int(s[12:14])
    return year, month, day, hour, minute, second

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--folder",
        required=True,
        help="Path to folder containing csv files to average"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output folder for the averaged results"
    )

    args = parser.parse_args()

    # Lint input arguments
    # Get csv files in folder, if folder is a folder
    if not os.path.isdir(args.folder):
        print("ERROR: Folder is not a folder. Exiting...")
        return 1
    # If output folder argument exists, it must be a folder.
    if args.output:
        if not os.path.isdir(args.output):
            print("ERROR: Output folder was provided but is not a folder. Exiting...")
            return 2

    count_statistics = dict() # 2D dictionary, indexed by timestamp, then by route
    weighted_average_statistics = dict() # 2D dictionary, indexed by timestamp, then by route
    routes = set() # Route set

    folder_path = os.path.abspath(args.folder)
    for item in os.listdir(folder_path):
        itempath = os.path.join(folder_path, item)
        itemname = os.path.splitext(item)[0]

        year, month, day, hour, minute, second = parse_timestamp(itemname)

        # Store flat average
        route_count = {}            # Indexed by route (str)
        route_speed_sums = {}       # Indexed by route (str)
        route_flat_average = {}     # Indexed by route (str)

        # Store time-weighted average
        route_distance_sums = {}    # Indexed by route (str)
        route_time_sums = {}        # Indexed by route (str)
        route_fleet_average = {}    # Indexed by route (str)

        # Calculate timestamp (hh:mm:ss XM)
        datestamp = str(year).zfill(4) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2)
        timestamp = str(hour).zfill(2) + ":" + str(minute).zfill(2) + ":" + str(second).zfill(2)

        with open (itempath, "r") as f:
            # Iterate over lines
            reader = csv.DictReader(f)

            # Get columns
            for row in reader:
                route = row["route"]
                distance = float(row["distance"])
                hours = float(row["minutes"]) / 60.0
                speed = float(row["speed"])

                # Log count
                if route not in route_count.keys():
                    route_count[route] = 1
                else:
                    route_count[route] += 1

                # Log speed
                if route not in route_speed_sums.keys():
                    route_speed_sums[route] = speed
                else:
                    route_speed_sums[route] += speed

                # Log distance
                if route not in route_distance_sums.keys():
                    route_distance_sums[route] = distance
                else:
                    route_distance_sums[route] += distance

                # Log time
                if route not in route_time_sums.keys():
                    route_time_sums[route] = hours
                else:
                    route_time_sums[route] += hours

        # Write results to super-dictionary
        for route in route_count.keys():
            # Add bus count to statistics dictionary
            if timestamp not in count_statistics.keys():
                count_statistics[timestamp] = {}
            count_statistics[timestamp][route] = route_count[route]

            # Add weighted average to statistics dictionary
            if timestamp not in weighted_average_statistics.keys():
                weighted_average_statistics[timestamp] = {}
            weighted_average_statistics[timestamp][route] = route_distance_sums[route] / route_time_sums[route]
            
            # Add route to routes set if not already there
            routes.add(route)

        # # Write output
        # # newline='' is required, otherwise the writer inserts blank lines in between every row.
        # output_file = itemname + "_output.csv"
        # if args.output:
        #     # We have already linted args.output to make sure it is a folder
        #     output_file = os.path.join(os.path.abspath(args.output), output_file)
        # with open(output_file, 'w', newline='') as f:
        #     fieldnames = ["route", "flat_average_speed", "weighted_average_speed", "count"]
        #     writer = csv.DictWriter(f, fieldnames=fieldnames)
        #     writer.writeheader()
        #     for route in route_count.keys():
        #         flat_average = route_speed_sums[route] / route_count[route]
        #         weighted_average = route_distance_sums[route] / route_time_sums[route]
        #         writer.writerow({"route": route, "flat_average_speed": flat_average, "weighted_average_speed": weighted_average, "count": route_count[route]})

    # NEW FEATURE: Output to a single file. Treat routes as columns.
    clean_output_dict = {}
    count_output_file = datestamp + "__counts.csv"
    weighted_average_output_file = datestamp + "__fleet_averages.csv"
    if args.output:
        # We have already linted args.output to make sure it is a folder.
        # Add the folder path to our files.
        count_output_file = os.path.join(os.path.abspath(args.output), count_output_file)
        weighted_average_output_file = os.path.join(os.path.abspath(args.output), weighted_average_output_file)

    with open(count_output_file, 'w', newline='') as f:
        routes_list = list(routes)
        routes_list.sort()
        timestamp_list = list(weighted_average_statistics.keys())
        timestamp_list.sort()
        fieldnames = ["timestamp"] + routes_list
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for timestamp in timestamp_list:
            rowdictionary = {"timestamp": timestamp}
            for route in routes:
                try:
                    rowdictionary[route] = count_statistics[timestamp][route]
                except KeyError:
                    rowdictionary[route] = ""
            writer.writerow(rowdictionary)

    with open(weighted_average_output_file, 'w', newline='') as f:
        routes_list = list(routes)
        routes_list.sort()
        timestamp_list = list(weighted_average_statistics.keys())
        timestamp_list.sort()
        fieldnames = ["timestamp"] + routes_list
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for timestamp in timestamp_list:
            rowdictionary = {"timestamp": timestamp}
            for route in routes:
                try:
                    rowdictionary[route] = weighted_average_statistics[timestamp][route]
                except KeyError:
                    rowdictionary[route] = ""
            writer.writerow(rowdictionary)

    return

if __name__ == "__main__":
    sys.exit(main())
