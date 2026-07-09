import argparse
import csv
import os
import sys
import requests
import xml.etree.ElementTree as ET

import secret # secret.py, ignored from source control.

# Get the timestamp
def get_api_time(key: str) -> str:
    systime_response = requests.get("https://www.ctabustracker.com/bustime/api/v3/gettime?key="+key)
    # systime_response = requests.get("https://www.ctabustracker.com/bustime/api/v3/gettime")
    # To check the status code, you'd validate systime_response.status_code
    #print(systime_response.content) # This returns a bitstream, and CTA sends their data in XML format.
    # So, you have to un-bitstream it, then un-XML it.
    #print(systime_response.text) # This returns the text, un-byte-ified. Now we just have to un-XML-ify it.

    time = ""

    # Parsing CTA's XML data
    root = ET.fromstring(systime_response.text)
    for item in root.findall('.'): # Get every value in the XML, in this case it's just one bustime.
        #print(item.tag, item.attrib)
        for child in item:
            #print(child.tag, child.attrib, child.text) # tm has no attribute, just a value, which is the time.
            time = child.text

    return time

def get_raw_line_info(key: str, routes: list) -> list:
    # Send API request
    routes_string = ','.join(routes)
    base_url = "https://www.ctabustracker.com/bustime/api/v3/getvehicles"
    request = base_url + "?key=" + key + "&rt=" + routes_string
    response = requests.get(request)

    # Parse results into list[dict]
    root = ET.fromstring(response.text) # root = bustime-response
    vehicles = []
    for item in root.findall('.'):
        for vehicle in item:
            vehicleInfo = {}
            for child in vehicle:
                vehicleInfo[child.tag] = child.text
            vehicles.append(vehicleInfo)
    
    # Sanitize. For whatever reason, the first line is junk.
    sanitized_vehicles = []
    for reading in vehicles:
        if "vid" in reading:
            sanitized_vehicles.append(reading)

    return sanitized_vehicles

def filter_raw_line_info(
    readings: list,
    north: int = 90,
    south: int = -90,
    east: int = 180,
    west: int = -180
):
    filtered_readings = []
    for reading in readings:
        ok = True
        if float(reading["lat"]) > north:
            ok = False
        if float(reading["lat"]) < south:
            ok = False
        # Note, these two will break when Chicago annexes Vietnam,
        # because it doesn't handle the date line. Assume that the
        # west boundary will always have lower (more negative) longitude
        # than east boundary.
        if float(reading["lon"]) > east:
            ok = False
        if float(reading["lon"]) < west:
            ok = False
        # If we passed the checks, keep the reading.
        if ok:
            filtered_readings.append(reading)
    return filtered_readings

def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--key",
        type=str,
        required=True,
        help="API Key for CTA bus tracker. Can be acquired for free from their website."
    )
    parser.add_argument(
        "lines",
        help="Lines to be tracked",
        nargs="+"
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

    # Get info from API
    systemtime = get_api_time(args.key)
    vehicles = get_raw_line_info(args.key, args.lines)

    # Filter based on selected coordinates, if provided
    filtered_vehicles = filter_raw_line_info(
        vehicles,
        north=args.northboundary,
        south=args.southboundary,
        east=args.eastboundary,
        west=args.westboundary
    )

    # Write vehicle info to CSV, tagged with the timestamp
    filename = systemtime.replace(" ", "").replace(":", "") + ".csv"
    folder = "data"
    fields = list(filtered_vehicles[0].keys())
    with open(os.path.join(folder, filename), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for vehicle in filtered_vehicles:
            row = []
            for field in fields:
                row.append(vehicle[field])
            writer.writerow(row)

    return 0

if __name__ == "__main__":
    sys.exit(main())
