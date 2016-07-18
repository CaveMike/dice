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
        raise Exception("""

TODO:

Implement a roll function using the random.randint() function.
Have this function return an integer from 1 to self.sides.

""")

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

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    unittest.main()