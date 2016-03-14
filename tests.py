import unittest

import datetime
import time
import signal
import mock

import devcron


class TestParsing(unittest.TestCase):

    def test_folding(self):
        input = '\n'.join([
            'one \\',
            'two',
            'three \\\\',
            'four'
        ])
        output = '\n'.join([
            'one two',
            'three \\four'
        ])
        self.assertEqual(devcron.fold_crontab_lines(input), output)

    def test_parse_simple(self):
        cnt = 5
        events = devcron.parse_crontab('1 2 3 4 5 cmd\n' * cnt)
        self.assertEqual(len(events), cnt)
        for e in events:
            self.assertEqual(
                (e.mins, e.hours, e.days, e.months, e.dow, e.args, e.kwargs),
                ({1}, {2}, {3}, {4}, {5}, tuple(), dict())
            )

    def test_parse_asterisk(self):
        events = devcron.parse_crontab('* * * * * cmd')
        self.assertEqual(len(events), 1)
        e = events[0]
        for x in (e.mins, e.hours, e.days, e.months, e.dow):
            self.assertIsInstance(x, devcron.AllMatch)

    def test_parse_comments(self):
        events = devcron.parse_crontab('* * * * * cmd\n#comment\n1 2 3 4 5 cmd')
        self.assertEqual(len(events), 2)

    def test_whitespace(self):
        events = devcron.parse_crontab('     \n\n   1   2   3   4   5   cmd    \n\n\n')
        self.assertEqual(len(events), 1)

    def test_weekly(self):
        events = devcron.parse_crontab('@weekly cmd')
        self.assertEqual(len(events), 1)
        e = events[0]
        self.assertEqual((e.mins, e.hours, e.dow), ({0}, {0}, {0}))
        self.assertIsInstance(e.days, devcron.AllMatch)
        self.assertIsInstance(e.months, devcron.AllMatch)

    def test_unknown_freq(self):
        with self.assertRaises(NotImplementedError):
            devcron.parse_crontab('@daily cmd')

    def test_bad_format(self):
        bad_inputs = [
            '1',
            '1 2 3 cmd',
            'one 2 3 4 5 cmd',
            '1 2 3 4 *5 cmd',
        ]

        for input in bad_inputs:
            with self.assertRaises(NotImplementedError):
                devcron.parse_crontab(input)


class TestMatching(unittest.TestCase):

    def test_all_match(self):
        self.assertTrue(all(x in devcron.AllMatch() for x in range(366)))

    def test_simple(self):
        e = devcron.Event(action=None, min={43}, hour={8}, day={14}, month={3}, dow={1})
        self.assertTrue(e.matchtime(datetime.datetime(2016, 3, 14, 8, 43, 12, 12345)))
        self.assertFalse(e.matchtime(datetime.datetime(2015, 3, 14, 8, 43, 12, 12345)))
        self.assertFalse(e.matchtime(datetime.datetime(2016, 3, 14, 8, 44, 12, 12345)))


class TestCall(unittest.TestCase):

    def test_args(self):
        f = mock.Mock()
        e = devcron.Event(action=f, min={43}, hour={8}, day={14}, month={3}, dow={1}, args=(1, 2), kwargs={'x': 3})
        e.check(datetime.datetime(2016, 3, 14, 8, 43, 12, 12345))
        f.assert_called_with(1, 2, x=3)


class TestRun(unittest.TestCase):

    def __check_call_times(self, call_times, period):
        # time between first 2 calls might be less or equal to period
        self.assertTrue(call_times[1] - call_times[0] <= period)
        # all subsequent call must be once in period
        for i in range(2, 5):
            self.assertTrue(period-0.1 <= call_times[i] - call_times[i-1] <= period+0.1)

    @mock.patch('devcron.Cron.step', 1)
    def test_period(self):
        call_times = []

        def save_time():
            call_times.append(time.time())

        ev = devcron.Event(save_time)
        devcron.Cron([ev]).run(stop_condition = lambda: len(call_times) >= 5)

        self.__check_call_times(call_times, 1)

    @mock.patch('devcron.Cron.step', 2)
    def test_signal(self):
        call_times = []

        def save_time():
            call_times.append(time.time())
            signal.alarm(1)

        ev = devcron.Event(save_time)

        signal.signal(signal.SIGALRM, lambda sig, stack: None)
        devcron.Cron([ev]).run(stop_condition = lambda: len(call_times) >= 5)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)

        self.__check_call_times(call_times, 2)


if __name__ == '__main__':
    unittest.main()
