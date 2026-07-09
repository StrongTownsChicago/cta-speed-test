import argparse
import csv
import geopy
import math # floor
import os
import requests
import sys
import time

# import parser
from tracker import *
from parser import *

import xml.etree.ElementTree as ET

def write_raw_line_info(vehicles: list, filename: str):
    # Write vehicle info to CSV in the `data` folder.
    folder = "data"
    fields = list(vehicles[0].keys())
    with open(os.path.join(folder, filename), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for vehicle in vehicles:
            row = []
            for field in fields:
                if field in vehicle:
                    row.append(vehicle[field])
                else:
                    print("WARNING: No field", field, "in vehicle info for vid", vehicle["vid"])
            writer.writerow(row)
    return

def main():
    parser = argparse.ArgumentParser(prog="ctaspeedtest")
    parser.add_argument(
        "lines",
        help="Lines to be tracked",
        nargs="+"
    )
    parser.add_argument(
        "-i",
        "--increment",
        type=int,
        default=2,
        help="Number of minutes between re-checking bus positions. Default 1 minute."
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        required=True,
        help="Total duration of the test in minutes. i.e., to check periodically for an hour, you would input --duration 60."
    )
    parser.add_argument(
        "--key",
        type=str,
        required=True,
        help="API Key for CTA bus tracker. Can be acquired for free from their website."
    )
    parser.add_argument(
        "-n",
        "--northboundary",
        type=float,
        default=90.0,
        help="Optional northern boundary for tracking buses. If provided, only coordinates with latitude less than this boundary will be included in the analysis."
    )
    parser.add_argument(
        "-s",
        "--southboundary",
        type=float,
        default=-90.0,
        help="Optional southern boundary for tracking buses. If provided, only coordinates with latitude greater than this value will be included in the analysis."
    )
    parser.add_argument(
        "-e",
        "--eastboundary",
        type=float,
        default=180.0,
        help="Optional eastern boundary for tracking buses. If provided, only coordinates with longitude greater than this value will be included in the analysis."
    )
    parser.add_argument(
        "-w",
        "--westboundary",
        type=float,
        default=-180.0,
        help="Optional western boundary for tracking buses. If provided, only coordinates with longitude less than this value will be included in the analysis."
    )

    args = parser.parse_args()

    print("Lines to be tracked:", args.lines)
    print("Duration of test:", args.duration)

    # Get system API time for the output file name.
    last_timestamp = get_api_time(args.key).replace(" ", "").replace(":", "")
    
    # Calculate number of readings to pull.
    iterations = int(math.floor(args.duration / args.increment))
    # Ensure we have at least two iterations.
    if (iterations < 2):
        print("ERROR: Cannot run fewer than one iteration. Need at least two data points for each bus to calculate speed!")
        print("Either increase duration or decrease the increment time.")
        return 1

    print("Repeating for", iterations, "loops...")
    all_raw_bus_info = [] # list[list[dict{}]]
    # Get start time to sync our clock
    starttime = time.monotonic()
    # Begin main reading loop.
    for i in range(0, iterations):
        systemtime = get_api_time(args.key)
        raw_bus_info = get_raw_line_info(args.key, args.lines)
        if len(raw_bus_info) > 0:
            print("Successfully read bus data from the server. (iteration " + str(i+1) + ")")
            filename = systemtime.replace(" ", "").replace(":", "") + ".csv"
            write_raw_line_info(raw_bus_info, filename)
        else:
            print("ERROR: Something went wrong. We didn't get any bus data back from the server.")
        all_raw_bus_info.append(raw_bus_info)
        # If we are looping again, wait for next iteration, controlling for code execution time
        if i != (iterations - 1):
            time.sleep(float(args.increment * 60.0) - ((time.monotonic() - starttime) % 60.0))

    # Begin parsing.
    # First, flatten and combine all bus data.
    combined_raw_bus_info = [] # list[dict{}]
    for collection in all_raw_bus_info:
        for reading in collection:
            combined_raw_bus_info.append(reading)
    
    # Filter out based on lat/long restrictions.
    filtered_raw_bus_info = filter_raw_line_info(
        combined_raw_bus_info,
        north=args.northboundary,
        south=args.southboundary,
        east=args.eastboundary,
        west=args.westboundary
    )

    # Organize remaining data by vehicle ID
    print("FILTERED RAW INFO:", filtered_raw_bus_info)
    vehicles = organize_by_vehicle_id(filtered_raw_bus_info)
    print("TYPE OF VEHICLES:", type(vehicles))
    #print(vehicles)
    print("^^^ VEHICLES ORGANIZED")
    print_vehicle_info(vehicles)

    # Post-processing (sort positions by time)
    for vid in vehicles.keys():
        vehicles[vid].sortPositions()
    
    # Calculate average speed per vehicle
    vehicle_statistics = calculate_vehicle_statistics(vehicles)

    # Write all statistics to file
    output_file = os.path.join("output", str(last_timestamp) + ".csv")
    with open(output_file, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["vid", "route", "destination", "distance", "minutes", "speed"])
        for vid in vehicle_statistics.keys():
            # SKIP any rows that are zero!
            if (vehicle_statistics[vid].distance != 0) and (vehicle_statistics[vid].minutes != 0):
                row = [
                    vid,
                    vehicle_statistics[vid].route,
                    vehicle_statistics[vid].destination,
                    vehicle_statistics[vid].distance,
                    vehicle_statistics[vid].minutes,
                    vehicle_statistics[vid].speed
                ]
                csv_writer.writerow([row])

    return 0

if __name__=="__main__":
    sys.exit(main())

