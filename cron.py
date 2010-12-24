#!/usr/bin/env python

"""Simple cron implementation in python.

Based on Brian's answer in
http://stackoverflow.com/questions/373335/suggestions-for-a-cron-like-scheduler-in-python

"""


from datetime import datetime, timedelta
import logging
from subprocess import Popen
import sys
import time


def main():
    logging.basicConfig(level=logging.DEBUG)
    crontab_data = open(sys.argv[1]).read()
    events = parse_crontab(crontab_data)
    logging.debug("Parsed crontab as:\n%s" %
                  '\n'.join([str(e) for e in events]))
    cron = Cron(events)
    cron.run()


def parse_crontab(data):
    """Returns a list of Events, one per line."""
    events = []
    for line in data.splitlines():
        line = line.strip()
        logging.debug("Parsing crontab line: %s" % line)
        if len(line) == 0 or line[0] == '#':
            continue
        if line[0] == '@':
            freq, cmd = line[1:].split(None, 1)
            if freq == 'weekly':
                event = Event(make_cmd_runner(cmd), 0, 0, dow=0)
            else:
                raise NotImplementedError() # TODO
        else:
            chunks = line.split(None, 5)
            args = [parse_arg(a) for a in chunks[:5]]
            event = Event(make_cmd_runner(chunks[5]), args[0], args[1],
                          args[2], args[3], args[4])
        events.append(event)
    return events


def make_cmd_runner(cmd):
    """Takes a path to a cmd and returns a function that when called, will run
    it.
    
    """
    def run_cmd():
        Popen(cmd, shell=True, close_fds=True)
    r = run_cmd
    r.__doc__ = cmd
    return r


def parse_arg(arg):
    """Takes a crontab time arg and converts it to a python int, iterable, or
    set.
    
    """
    try:
        return(int(arg))
    except ValueError:
        pass
    if arg == '*':
        return all_match
    raise NotImplementedError("The crontab line is malformed or isn't "
                              "supported.")


class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True


all_match = AllMatch()


def conv_to_set(obj):  # Allow single integer to be provided
    if isinstance(obj, (int,long)):
        return set([obj])  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj


# The actual Event class
class Event(object):
    def __init__(self, action, min=all_match, hour=all_match,
                       day=all_match, month=all_match, dow=all_match,
                       args=(), kwargs={}):
        self.mins = conv_to_set(min)
        self.hours= conv_to_set(hour)
        self.days = conv_to_set(day)
        self.months = conv_to_set(month)
        self.dow = conv_to_set(dow)
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute     in self.mins) and
                (t.hour       in self.hours) and
                (t.day        in self.days) and
                (t.month      in self.months) and
                (t.weekday()  in self.dow))

    def check(self, t):
        if self.matchtime(t):
            self.action(*self.args, **self.kwargs)
    
    def __str__(self):
        return ("Event(%s, %s, %s, %s, %s, %s)" %
                (self.mins, self.hours, self.days, self.months, self.dow,
                 self.action.__doc__))


class Cron(object):
    def __init__(self, events):
        self.events = events

    def run(self):
        t = datetime(*datetime.now().timetuple()[:5])
        while True:
            for e in self.events:
                e.check(t)
            
            t += timedelta(minutes=1)
            while datetime.now() < t:
                now = datetime.now()
                dt = t - now
                secs = dt.seconds + float(dt.microseconds) / 1000000
                logging.debug("Sleeping from %s to %s (%s secs)" % (now, t, secs))
                time.sleep(secs)


if __name__ == '__main__':
    main()
