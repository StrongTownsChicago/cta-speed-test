# About

Each of the three scripts in this repository can be used independently. However, for the smoothest experience, `ctaspeedtest.py` is where you will want to start.

- `tracker.py` will grab CTA bus data for the selected lines and put all readings in a CSV in the `data` folder.
- `parser.py` will parse all CTA bus data files in the `data` folder and calculate total distance, total time, and average speed for each bus tracked with more than one data point.
- `ctaspeedtest.py` combines the functionality of the two other files, and can continuously re-read data every x minutes for a user-selected amount of time to produce a final average speed along each line in the time period being measured.


### Example Usage: tracker.py


### Example Usage: parser.py


### Example Usage: ctaspeedtest.py

```bash
python3 ./ctaspeedtest.py --key <your_api_key> --duration 5 --increment 1 49 X49 50 94
```

If we want to restrict the locations of the buses we are tracking, we can add arguments accordingly. For example, the code below will create a southern boundary so that we only track buses that are north of Lake Street:

```bash
python3 ./ctaspeedtest.py --key <your_api_key> --southborder 41.884268 --duration 5 --increment 1 49 X49 50 94
```
