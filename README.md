# About

Each of the three scripts in this repository can be used independently. However, for the smoothest experience, `ctaspeedtest.py` is where you will want to start.

- `tracker.py` will grab CTA bus data for the selected lines and put all readings in a CSV in the `data` folder.
- `parser.py` will parse all CTA bus data files in the `data` folder and calculate total distance, total time, and average speed for each bus tracked with more than one data point.
- `ctaspeedtest.py` combines the functionality of the two other files, and can continuously re-read data every x minutes for a user-selected amount of time to produce a final average speed along each line in the time period being measured.


### Example Usage: tracker.py

```
python3 ./tracker.py --key <your_api_key> <your_lines>
```

This will grab raw positional readings once from the lines you select.


### Example Usage: parser.py

```
python3 ./parser.py
```

The parser script will consume all data files you currently have in your data folder. You will get weird results if you have data from multiple days.

At some point I should add an argument to specify what date you want to use data from.


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
python3 ./ctaspeedtest.py --key <your_api_key> --southboundary 41.884268 --duration 15 --increment 1 49 X49 50 94
```

You can add north, west, and east boundaries as well. You can add just one, or two, or all four, or none at all if you just want the full line data.

# Other Notes

If, for some reason, you wanted to gather data from every line... here's the list.

1 2 3 4 X4 N5 6 7 8 8A 9 X9 10 11 12 J14 15 18 19 20 21 22 24 26 28 29 30 31 34 35 36 37 39 43 44 47 48 49 49B X49 50 51 52 52A 53 53A 54 54A 54B 55 55A 55N 56 57 59 60 62 62H 63 63W 65 66 67 68 70 71 72 73 74 75 76 77 78 79 80 81 81W 82 84 85 85A 86 87 88 90 91 92 93 94 95 96 97 100 103 106 108 111 111A 112 115 119 120 121 124 125 126 130 134 135 136 143 146 147 148 151 152 155 156 157 165 169 171 172 192 201 206
