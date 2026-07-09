import csv
import os
import sys

import geopy.distance

folder = "data"

class Position:
    def __init__(self, timestamp: str, latitude: float, longitude: float):
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
    
    def getCoordinates(self) -> tuple:
        return (float(self.latitude), float(self.longitude))
    
    def getMinutes(self) -> int:
        # CTA timestamps look like yyyyMMdd hh:mm
        timestamp_split = self.timestamp.split(' ')[1].split(':') # (hour, minute)
        minutes = int(timestamp_split[0]) * 60 + int(timestamp_split[1])
        return minutes

class Vehicle:
    def __init__(self, vid, route, destination):
        self.vid = vid
        self.route = route
        self.destination = destination
        self.positions = []

    def addPosition(self, timestamp, latitude, longitude):
        # Check if a position with this timestamp already exists
        hasTimestamp = False
        for position in self.positions:
            if position.timestamp == timestamp:
                hasTimesatmp = True
        if not hasTimestamp:
            self.positions.append(Position(timestamp, latitude, longitude))
    
    def sortPositions(self):
        sorted_positions = sorted(self.positions, key=lambda d: d.timestamp)
        self.positions = sorted_positions

    def getTotalDistance(self) -> float:
        self.sortPositions()
        total_distance = 0
        last_position = (0.0, 0.0)
        for position in self.positions:
            # Add to total distance traveled if this is not our first waypoint
            if last_position != (0.0, 0.0):
                total_distance += geopy.distance.geodesic(last_position, position.getCoordinates()).mi
            last_position = position.getCoordinates()
        return total_distance
            
    def getTotalTime(self) -> int:
        self.sortPositions()
        total_time = 0
        last_minutes = 0
        for position in self.positions:
            if last_minutes != 0:
                total_time += position.getMinutes() - last_minutes
            last_minutes = position.getMinutes()
        return total_time
    
    def getSpeed(self) -> float:
        distance = self.getTotalDistance()
        minutes = self.getTotalTime()
        hours = float(minutes) / 60.0
        speed = 0 if hours == 0 else distance / hours
        return speed

class VehicleStatistic:
    def __init__(self, vehicle: Vehicle):
        self.vid = vehicle.vid
        self.route = vehicle.route
        self.destination = vehicle.destination
        self.distance = vehicle.getTotalDistance()
        self.minutes = vehicle.getTotalTime()
        self.speed = vehicle.getSpeed()

def organize_by_vehicle_id(readings: list) -> dict:
    vehicles = {} # dict{vid: Vehicle}
    for row in readings:
        # Add vehicle if we haven't seen it already.
        vid = row["vid"]
        if vid not in vehicles.keys():
            vehicles[vid] = Vehicle(vid=vid, route=row["rt"], destination=row["des"])

        # Add this position to the log for this vehicle
        vehicles[vid].addPosition(timestamp=row["tmstmp"], latitude=row["lat"], longitude=row["lon"])
    
    return vehicles

def print_vehicle_info(vehicles: dict):
    for vid in vehicles.keys():
        print("Vehicle:", vid)
        print("\tRoute:", vehicles[vid].route)
        print("\tDestination:", vehicles[vid].destination)
        for position in vehicles[vid].positions:
            print("\t\tPosition at " + position.timestamp + ": " + str(position.latitude) + ", " + str(position.longitude))

def calculate_vehicle_statistics(vehicles: dict) -> dict:
    vehicle_statistics = {}
    for vid in vehicles.keys():
        vehicle_statistics[vid] = VehicleStatistic(vehicles[vid])
    return vehicle_statistics

def get_vehicles_from_file(filepaths: list) -> dict:
    vehicles = {}
    for filepath in filepaths:
        with open(os.path.join(folder, filepath), 'r') as f:
            csvreader = csv.reader(f)
            fields = next(csvreader)
            for row in csvreader:
                vid = 0
                route = ""
                destination = ""
                lat = 0.0
                lon = 0.0
                time = ""
                # print(row)
                for i in range(0, len(row)):
                    # Order of cols matches order of fields
                    if fields[i] == "vid":
                        vid = int(row[i])
                    elif fields[i] == "rt":
                        route = row[i]
                    elif fields[i] == "des":
                        destination = row[i]
                    elif fields[i] == "lat":
                        lat = row[i]
                    elif fields[i] == "lon":
                        lon = row[i]
                    elif fields[i] == "tmstmp":
                        timestamp = row[i]

                if vid not in vehicles:
                    vehicles[vid] = Vehicle(vid=vid, route=route, destination=destination)

                # Add this position to the log for this vehicle
                vehicles[vid].addPosition(timestamp=timestamp, latitude=lat, longitude=lon)

    return vehicles

def main() -> int:
    dirtyfiles = os.listdir(folder)
    # Sanitize down to only .csv files
    datafiles = []
    last_timestamp = 0
    for file in dirtyfiles:
        file_extension = os.path.splitext(file)[1] # (file, extension)
        if file_extension == ".csv":
            file_timestamp = int(os.path.splitext(file)[0])
            if file_timestamp > last_timestamp:
                last_timestamp = file_timestamp
            datafiles.append(file)

    # Boil down all available files to create a dictionary of Vehicle objects
    vehicles = get_vehicles_from_file(datafiles) # dict{vid: Vehicle}
    
    # Post-processing (sort positions by time)
    for vid in vehicles.keys():
        vehicles[vid].sortPositions()
    
    # Calculate average speed per vehicle
    vehicle_statistics = calculate_vehicle_statistics(vehicles)

    # TODO: Filter out stopped vehicles (<1mph)
    # TODO: Filter by starting and ending locations within a zone
    # TODO: Commandline-ify this whole tool to run for a period of time, track an arbitrary combination of routes, optionally take latitude and longitude min/max boundaries, and output either (A) a final CSV of time, distance, and speed averages across lines and destinations, or (B) a full list of buses and their speed stats.

    # Write all statistics to file
    output_file = os.path.join("output", str(last_timestamp) + ".csv")
    with open(output_file, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["vid", "route", "destination", "distance", "minutes", "speed"])
        for vid in vehicle_statistics.keys():
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
