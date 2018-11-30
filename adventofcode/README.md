Make a script that can regularly post Advent of Code standings to a Slack Channel.

Uses Slack's "Incoming WebHooks" Custom Integration and Advent of Code's Private Leaderboard.

Look at config.yml.example for configuration required.

Then set up a cronjob using `crontab -e` like:

```
0 0 * * * /usr/bin/python3 /home/michael/personal/webhooks/adventofcode/advent256.py /home/michael/personal/webhooks/adventofcode/config.yml
```
