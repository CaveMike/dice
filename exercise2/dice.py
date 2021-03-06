#!/usr/bin/env python3
from __future__ import division
import itertools
import logging
import math
import random
import unittest

from collections import deque

class DieBase:
    def __init__(self, sides, source=None):
        self._sides = sides
        self.source = source

    @property
    def sides(self):
        return self._sides

    def roll(self):
        raise Exception('Not implemented')

    def __call__(self, count=1):
        return [self.roll() for i in range(0, count)]

    def __str__(self):
        return 'sides={}, source=({})'.format(self.sides, self.source)

class DiePerfect(DieBase):
    def __init__(self, sides, num_dice=1):
        super(DiePerfect, self).__init__(sides=sides, source=None)
        self.num_dice = num_dice
        self.num_rolls = 0

        ranges = [range(1, sides + 1) for n in range(0, self.num_dice)]
        self.rolls = itertools.cycle(DiePerfect.__each(current=[], ranges=deque(ranges)))

    @staticmethod
    def __each(current, ranges):
        if not len(ranges):
            return current

        range = ranges.popleft()

        results = []
        for i in range:
            current.append(i)
            results.extend(DiePerfect.__each(current, ranges))
            current.pop()

        ranges.appendleft(range)

        return results

    def roll(self):
        self.num_rolls += 1
        r = next(self.rolls)
        return r

class TestDiePerfect(unittest.TestCase):
    def test2d2(self):
        die = DiePerfect(sides=2, num_dice=2)
        self.assertEqual(die(count=8), [1, 1, 1, 2, 2, 1, 2, 2])

    def test2d4(self):
        die = DiePerfect(sides=4, num_dice=2)
        self.assertEqual(die(count=32), [1, 1, 1, 2, 1, 3, 1, 4, 2, 1, 2, 2, 2, 3, 2, 4, 3, 1, 3, 2, 3, 3, 3, 4, 4, 1, 4, 2, 4, 3, 4, 4])

class DieTester:
    def __init__(self, die):
        self.die = die
        self.rolls = {i:0 for i in range(1, self.die.sides+1)}

    def __call__(self, count=1):
        rolls = self.die(count=count)
        for roll in rolls:
            self.rolls[roll] += 1

    @property
    def num_rolls(self):
        return sum(self.rolls.values())

    @property
    def sum(self):
        return sum([k * v for k, v in self.rolls.items()])

    @property
    def average(self):
        if self.num_rolls:
            return self.sum / self.num_rolls
        else:
            return math.nan

    @property
    def theorectial_average(self):
        return sum([i for i in range(1, self.die.sides + 1)]) / self.die.sides

    @property
    def average_deviation(self):
        return abs(self.average - self.theorectial_average)

    @property
    def exp(self):
        return self.num_rolls / self.die.sides

    def summary(self):
        return 'num_rolls={}, sum={}, theorectial_average={:3.2f}, average={:3.2f}, average_deviation={:3.2f}'.format(self.num_rolls, self.sum, self.theorectial_average, self.average, self.average_deviation)

    def __str__(self):
        a = []
        a.append('die: ({})'.format(self.die))
        a.append('num_rolls={}, sum={}, theorectial_average={:3.2f}, average={:3.2f}, average_deviation={:3.2f}'.format(self.num_rolls, self.sum, self.theorectial_average, self.average, self.average_deviation))
        if self.num_rolls:
            a.append('{: >4}, {: >4}, {: >5}, {}'.format('roll', 'num', '%', 'dev'))
            a.extend(['{: 4}, {: 4}, {: 3.2f}, {}'.format(k, v, (v / self.num_rolls * 100), int(pow(self.exp-v, 2))) for (k, v) in self.rolls.items()])
        a.append('')
        return '\n'.join(a)

class Die(DieBase):
    def roll(self):
        return random.randint(1, self.sides)

class TestDie(unittest.TestCase):
    def go(self, count, die, average_deviation=0.25):
        tester = DieTester(die)
        tester(count=count)
        logging.info(tester.summary())
        self.assertTrue(tester.average_deviation < average_deviation)

    def test_1000d4(self):
        self.go(count=1000, die=Die(sides=4))

    def test_1000d6(self):
        self.go(count=1000, die=Die(sides=6))

    def test_10000d20(self):
        self.go(count=10000, die=Die(sides=20))

    def test_100000d100(self):
        self.go(count=100000, die=Die(sides=100))

class DieDivider(DieBase):
    def __init__(self, sides, source):
        super(DieDivider, self).__init__(sides=sides, source=source)

        if source.sides % sides != 0:
            raise Exception('Cannot divide a die from {} sides, to {} sides.'.format(source.sides, sides))

        self.divisor = self.source.sides // self.sides

    def roll(self):
        return math.ceil(self.source.roll() / self.divisor)

class TestDieDivider(unittest.TestCase):
    def go(self, die):
        tester = DieTester(die)
        tester(count=die.source.sides)
        logging.info(tester.summary())
        self.assertFalse(tester.average_deviation)

    def test_d3_from_d6(self):
        self.go(die=DieDivider(sides=3, source=DiePerfect(sides=6)))

    def test_d4_from_d12(self):
        self.go(die=DieDivider(sides=4, source=DiePerfect(sides=12)))

    def test_d6_from_d12(self):
        self.go(die=DieDivider(sides=6, source=DiePerfect(sides=12)))

    def test_d9_from_d18(self):
        self.go(die=DieDivider(sides=9, source=DiePerfect(sides=18)))

class DiePower(DieBase):
    def __init__(self, sides, source):
        super(DiePower, self).__init__(sides=sides, source=source)
        """ TODO: Calculate the number of dice to be used. """

    def roll(self):
        raise Exception("""

TODO:

Implement a roll function using a source die. Have this function return an
integer from 1 to self.sides.

You can use multiple dice to create larger numbers. Each die can represent a
digit of a larger number.

For example, consider a d10 die, labelled from 0 to 9.  If you roll two of these
dice, the first die can represent the tens-place and the second the ones-place.
This effectively creates a d100 die with numbers from 00 to 99.  Alternatively,
00 can be considered 100 for a range of 1 to 100.

This same technique can be used for any die.  Two d6 dice labelled from 0 to 5
could be used to create a two-digit number in base 6.

For a die with S sides, labelled from 1 to S, rolling N dice gives a range of
rolls from 0 to (S^N - 1).  Some examples:

S   N   Range
---------------
10  2   0-99
10  3   0-999
6   2   0-35
6   3   215

If the range is too large, you can safely ignore the rolls that are out of range
and re-roll.  For example, 2d10 can create a range from 1 to 100. This can be
used to create a d80 by ignoring values from 81 to 100 and re-roll.

With enough rolls, you can use this technique to synthesize any larger die from
a smaller die. Implement this function to synthensize any die roll using any
source die.

""")

class TestDiePower(unittest.TestCase):
    def go(self, count, max_rolls, die):
        tester = DieTester(die)
        tester(count=count)
        logging.info(tester.summary())
        self.assertFalse(tester.average_deviation)
        self.assertEqual(die.source.num_rolls // die.source.num_dice, max_rolls)

    def test_d16_from_2d6(self):
        self.go(count=32, max_rolls=68, die=DiePower(sides=16, source=DiePerfect(sides=6, num_dice=2)))

    def test_d200_from_3d6(self):
        self.go(count=400, max_rolls=431, die=DiePower(sides=200, source=DiePerfect(sides=6, num_dice=3)))

    def test_d80_from_2d10(self):
        self.go(count=160, max_rolls=198, die=DiePower(sides=80, source=DiePerfect(sides=10, num_dice=2)))

    def test_d4000_from_4d8(self):
        self.go(count=8000, max_rolls=8191, die=DiePower(sides=4000, source=DiePerfect(sides=8, num_dice=4)))

    def test_d12_from_2d6(self):
        self.go(count=144, max_rolls=428, die=DiePower(sides=12, source=DiePerfect(sides=6, num_dice=2)))

    def test_d50_from_2d10(self):
        self.go(count=200, max_rolls=395, die=DiePower(sides=50, source=DiePerfect(sides=10, num_dice=2)))

    def test_d45_from_2d10(self):
        self.go(count=180, max_rolls=394, die=DiePower(sides=45, source=DiePerfect(sides=10, num_dice=2)))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    unittest.main()