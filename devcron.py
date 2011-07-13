#!/usr/bin/env python

# Uses Brian's python cron code from
# http://stackoverflow.com/questions/373335/suggestions-for-a-cron-like-scheduler-in-python


from datetime import datetime, timedelta
import logging
import optparse
from subprocess import Popen
import sys
import time


def main():
    prog = 'devcron.py'
    usage = 'usage: %prog [options] crontab'
    description = 'A development cron daemon. See README.txt for more info.'

    op = optparse.OptionParser(prog=prog, usage=usage, description=description)
    op.add_option('-v', '--verbose', dest='verbose', action='store_true',
	              help='verbose logging.')

    (options, args) = op.parse_args()

    if len(args) != 1:
        op.print_help()
        sys.exit(1)

    log_level = logging.WARN
    if options.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    crontab_data = open(args[0]).read()
    crontab_data = fold_crontab_lines(crontab_data)
    crontab_data = edit_crontab_data(crontab_data)
    logging.debug("Edited crontab looks like:\n%s\n" % crontab_data)
    events = parse_crontab(crontab_data)
    logging.debug("Parsed crontab as:\n%s\n" %
                  '\n'.join([str(e) for e in events]))
    cron = Cron(events)
    cron.run()


def fold_crontab_lines(data):
    return data.replace('\\\n', '')


def edit_crontab_data(data):
    deletions = []
    for line in data.splitlines():
        delete_cmd = '# devcron delete_str '
        if line.startswith(delete_cmd):
            if line[-1] == ' ':
                logging.warn("There is a significant trailing space on line "
                             "'%s'." % line)
            deletions.append(line[len(delete_cmd):])
    logging.debug("Deleting the following strings: %s\n" % deletions)
    for d in deletions:
        data = data.replace(d, '')
    return data


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
            event = Event(make_cmd_runner(chunks[5]),
                          parse_arg(chunks[0]),
                          parse_arg(chunks[1]),
                          parse_arg(chunks[2]),
                          parse_arg(chunks[3]),
                          parse_arg(chunks[4],
                                    lambda dow: 7 if dow == 0 else dow))
        events.append(event)
    return events


def make_cmd_runner(cmd):
    """Takes a path to a cmd and returns a function that when called, will run
    it.

    """
    def run_cmd():
        return Popen(cmd, shell=True, close_fds=True)
    run_cmd.__doc__ = cmd
    return run_cmd


def no_change(x):
    return x


def parse_arg(arg, converter=no_change):
    """This takes a crontab time arg and converts it to a python int, iterable,
    or set.

    If a callable is passed as converter, it translates numbers in arg with
    the converter.

    """
    if arg == '*':
        return all_match
    try:
        return [converter(int(n)) for n in arg.split(',')]
    except ValueError:
        raise NotImplementedError("The crontab line is malformed or isn't "
                                  "supported.")


class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True


all_match = AllMatch()


def convert_to_set(obj):
    if isinstance(obj, (int,long)):
        return set([obj])
    if not isinstance(obj, set):
        obj = set(obj)
    return obj


class Event(object):
    def __init__(self, action, min=all_match, hour=all_match,
                       day=all_match, month=all_match, dow=all_match,
                       args=(), kwargs={}):
        """
        day: 1 - num days
        month: 1 - 12
        dow: mon = 1, sun = 7
        """
        self.mins = convert_to_set(min)
        self.hours= convert_to_set(hour)
        self.days = convert_to_set(day)
        self.months = convert_to_set(month)
        self.dow = convert_to_set(dow)
        self.action = action
        self.args = args
        self.kwargs = kwargs
#        self.process = None                    # Current process

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute        in self.mins) and
                (t.hour          in self.hours) and
                (t.day           in self.days) and
                (t.month         in self.months) and
                (t.isoweekday()  in self.dow))

    def check(self, t):
        if self.matchtime(t):
            # Avoid spawning another process if the last run didn't finish yet.
#            if self.process:
#                self.process.poll()
#                if self.process.returncode != None:
#                    self.process = None
#                else:
#                    return
            self.process = self.action(*self.args, **self.kwargs)

    def __str__(self):
        return ("Event(%s, %s, %s, %s, %s, %s)" %
                (self.mins, self.hours, self.days, self.months, self.dow,
                 self.action.__doc__))


class Cron(object):
    def __init__(self, events):
        self.events = events

    def run(self):
        next_event = datetime(*datetime.now().timetuple()[:5])
        while True:
            for e in self.events:
                e.check(next_event)

            next_event += timedelta(minutes=1)
            now = datetime.now()
            while now < next_event:
                dt = next_event - now
                secs = dt.seconds + float(dt.microseconds) / 1000000
                logging.debug("Sleeping from %s to %s (%s secs)" % (now, next_event, secs))
                time.sleep(secs)
                now = datetime.now()


if __name__ == '__main__':
    main()
