Development cron daemon. Intended as a debugging tool when developing anything
cron based where it would be difficult to use normal cron or what cron runs
must be modified for the dev environment.

For example, I have a django project that uses cron to run periodic tasks. The
crontab is in the source tree so it can be managed and deployed with the code.
While doing dev work, I need to run the cron tasks locally and modify the path
of the commands. The crontab looks something like:

# devcron delete /usr/local/bin/
* * * * * /usr/local/bin/update-stats.py

That works normally on the production server and when I'm working, I run:

devcron.py my-crontab

and it will run update-stats.py in the working directory (my development tree)
once a minute.



You can install with:

pip install -e hg+https://bitbucket.org/dbenamy/devcron#egg=devcron
