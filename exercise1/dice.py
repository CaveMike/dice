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

    def roll(self):
        raise Exception("""

TODO:

Implement a roll function using a source die. Have this function return an
integer from 1 to self.sides.

For example, a d6 could be used to create either a d3 or a d2:
d6  d3  d2
----------
1   1   1
2   1   1
3   2   1
4   2   2
5   3   2
6   3   2

While a d12 could be used to create a d6, d4, d3, or d2:
d12 d6  d4  d3  d2
------------------
1   1   1   1   1
2   1   1   1   1
3   2   1   1   1
4   2   2   1   1
5   3   2   2   1
6   3   2   2   1
7   4   3   2   2
8   4   3   2   2
9   5   3   3   2
10  5   4   3   2
11  6   4   3   2
12  6   4   3   2

You can get rolls from the source die by calling:
  self.source.roll()

The // operator is the integer division operator.
It will divide two numbers and return the integer part while the remainder will
be lost.  In our case that's ok since the remainder has to be 0.

The % operator is the modulus operator. It divides two numbers and returns the
remainder. The remainder should always be 0 for evenly divisible numbers. We
do this check in the __init__() function.

Keep in mind, you need to return a roll starting with 1. You may need to use
either the ceiling or the floor function.

The ceiling function takes any number and returns an integer that is equal to
or greater than the number. For example, giving it 1.0 would return a value of 1,
while giving it 1.1 would return 2.

The floor function takes any number an returns an integer that is equal to over
less than the number. For example, giving it 1.0 would return 1 and giving it
1.1 would also return 1.

To use these functions:
  x = math.ceil(number)
  y = math.floor(number)

""")

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

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    unittest.main()