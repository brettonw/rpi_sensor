#! /usr/bin/env python3

from dataclasses import dataclass


@dataclass
class XYPair:
    x: float
    y: float


def interpolate(table: [XYPair], x: float) -> float:
    """
    :param table: tabular data of (x, y) pairs where y = f(x) for some sampled f, assumed to be
                  sorted in ascending order by x
    :param x: a value of x for which we want to know f(x)
    :return: f(x), interpolated linearly over the data points in the table
    """

    # the table needs at least 2 entries
    assert len(table) > 1

    def linear(high: int) -> float:
        low = high - 1
        interpolant = (x - table[low].x) / (table[high].x - table[low].x)
        return table[low].y + ((table[high].y - table[low].y) * interpolant)

    # if the requested value is outside the range of the table, we extrapolate from the two ends of
    # the table
    if x < table[0].x:
        return linear(1)
    if x > table[-1].x:
        return linear(-1)

    # find the bracketing pair
    high = 1
    while table[high].x < x:
        high += 1
    return linear(high)


def main():
    """
    test the interpolator
    """
    table = [XYPair(0, 0), XYPair(1, 1), XYPair(2, 4), XYPair(3, 9)]
    assert interpolate(table, -2) == -2
    assert interpolate(table, -1) == -1
    assert interpolate(table, 0) == 0
    assert interpolate(table, 1) == 1
    assert interpolate(table, 2) == 4
    assert interpolate(table, 3) == 9
    assert interpolate(table, 4) == 14
    assert interpolate(table, 5) == 19

    assert interpolate(table, 0.25) == 0.25
    assert interpolate(table, 0.5) == 0.5
    assert interpolate(table, 0.75) == 0.75
    assert interpolate(table, 1.5) == 2.5
    assert interpolate(table, 1.5) != 3.0
    assert interpolate(table, 2.5) == 6.5

    print("PASS")

if __name__ == '__main__':
    main()
