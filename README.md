# About

Each of the three scripts in this repository can be used independently. However, for the smoothest experience, `ctaspeedtest.py` is where you will want to start.

- `tracker.py` will grab CTA bus data for the selected lines and put all readings in a CSV in the `data` folder.
- `parser.py` will parse all CTA bus data files in the `data` folder and calculate total distance, total time, and average speed for each bus tracked with more than one data point.
- `ctaspeedtest.py` combines the functionality of the two other files, and can continuously re-read data every x minutes for a user-selected amount of time to produce a final average speed along each line in the time period being measured.


### Example Usage: tracker.py


### Example Usage: parser.py


### Example Usage: ctaspeedtest.py

Run `python ctaspeedtest.py --help` to see a list of available command line options.

Let's say I want to compare speeds for the 49, X49, 50, and 94 CTA branches. I could do so with the following script, which would run for 15 minutes and check bus positions every minute.

```bash
python3 ./ctaspeedtest.py --key <your_api_key> --duration 15 --increment 1 49 X49 50 94
```

This will create a `.csv` file in the `output` folder that shows the average speed of every bus ID currently operating on the provided lines. This allows you to compare speeds between buses on the same line, as well as on different lines.

Longer duration and smaller increments will give you more accurate data. Obviously, this will take longer to run.

If we want to restrict the locations of the buses we are tracking, we can add arguments accordingly. This will give us more accurate data for that stretch of the route. For example, the code below will create a southern boundary at latitude 41.884268 (latitude of the California Green Line stop) so that we only track buses that are north of Lake Street:

```bash
python3 ./ctaspeedtest.py --key <your_api_key> --southborder 41.884268 --duration 15 --increment 1 49 X49 50 94
```
