# What?

You might want to consider automating the running of this script. Otherwise, it's pretty hard to get a decent data set if you're relying on having access to your laptop and wifi for 20-30 minutes at a time consistently.

If you have access to a Linux server, the easiest way to do this is to set up a systemd timer. This is a pretty simple process. You'll just need to create three files on your server's system:

1. A wrapper to launch your set up and run your Python command
2. A systemd `.service` file to manage the running of that shell command
3. A systemd `.timer` file to trigger the service to run in the background at specific times.


## Example wrapper shell script

This can be placed anywhere. Just make sure your service file will be able to find it.

```bash
#!/bin/bash
source <location_of_your_venv>/bin/activate
python3 <location_of_this_git_repo>/ctaspeedtest.py \
--key <your_api_key> -n 41.924946 -s 41.884248 \
-w -87.702200 -e -87.632725 --duration 30 --increment 1 \
49 X49 50 94 66
```

(Replace `<location_of_your_venv>` with the location of your Python virtual environment (venv). You should be using one of these to install pip dependencies. It's considered best practice not to just install them to your machine, especially on Linux.)

(Replace `<your_api_key>` with your API key.)

You can call this script whatever you want.

Make sure to make your shell script executable!

```bash
chmod +x your_wrapper_script.sh
```

Before going any farther, you should make sure that your script works.

```bash
./your_wrapper_script.sh
```


## Example service file

Place this in `.config/systemd/user`. Name it something like `cta-speed-test.service`.

```
[Unit]
Description=Collect CTA data

[Service]
Type=oneshot
ExecStart=<your_wrapper_script>
```

Replace `<your_wrapper_script>` with the location of your shell script, i.e. `/home/yourname/cta-speed-test-wrapper.sh`.

## Example timer file

Place this in `.config/systemd/user`. Name it something like `cta-speed-test.timer`.

The example below will trigger the service every 30 minutes between 4AM and 10PM.

```
[Unit]
Description=Run CTA collector every five minutes between 04:00 and 22:00

[Timer]
OnCalendar=*-*-* 04..22:00,30:00
Persistent=true

[Install]
WantedBy=timers.target
```


## Starting the service

Start the service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now cta-speed-test.timer
```

Once it runs, you should be able to see the output of the Python script like this:

```bash
systemctl --user status cta-speed-test.service
```

And you can check the next timer trigger like this:

```bash
systemctl --user status cta-speed-test.timer
```

If you want to stop the process, all you have to do is:

```bash
systemctl --user stop cta-speed-test.timer
systemctl --user disable cta-speed-test.timer
```

If you ever have to update the python script or the service, you should run `systemctl --user daemon-reload` again.
