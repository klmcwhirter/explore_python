#!/usr/bin/env python

import math
import time
from decimal import Decimal, getcontext
from functools import cache, wraps
from math import factorial

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpmath import _mpf, mp, mpf

# Computing Pi to 10 digits took 0.000 seconds
# Computing Pi to 100 digits took 0.005 seconds
# Computing Pi to 1000 digits took 6.307 seconds
# Computing Pi to 1500 digits took 22.440 seconds
# Computing Pi to 2000 digits took 55.409 seconds


def timer(func):
    """
    Times how long functions take to run. 
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        return result, time.time() - start

    return wrapper


@cache
def cfactorial(n: int) -> int:
    return factorial(n)


@timer
def pi_digits_chud(n: int) -> Decimal:
    """
    Computes PI using the Chudnovsky formula according to:
    http://stackoverflow.com/questions/28284996/python-pi-calculation
    """
    # Set the decimal context
    getcontext().prec = n

    d12 = Decimal(12)
    d1point5 = Decimal(1.5)

    t = Decimal(0)
    pi = Decimal(0)
    d = Decimal(0)

    for k in range(n):
        t = ((-1)**k)*(cfactorial(6*k))*(13591409+545140134*k)
        d = cfactorial(3*k)*(cfactorial(k)**3)*(640320**(3*k))

        pi += Decimal(t) / Decimal(d)

    # pi = pi * d12 / Decimal(640320**(d1point5))
    # pi = 1 / pi

    pi = Decimal(640320**(d1point5)) / (pi * d12)

    return pi


def pi_digits_bbp_term(k: int):
    return 1/mpf(16)**k * \
        (mpf(4)/(8*k+1) -
         mpf(2)/(8*k+4) -
         mpf(1)/(8*k+5) -
         mpf(1)/(8*k+6))


@timer
def pi_digits_bbp(n: int) -> _mpf:
    '''From https://stackoverflow.com/a/28285228
    Also, https://en.wikipedia.org/wiki/Bailey%E2%80%93Borwein%E2%80%93Plouffe_formula
    '''
    mp.dps = max(n, mp.dps)

    rc = mp.nsum(pi_digits_bbp_term, [0, n], method='d')

    return rc


@timer
def pi_digits_bbp_decimal(n: int) -> Decimal:
    '''From https://stackoverflow.com/a/28285228'''
    getcontext().prec = n + 3
    return sum(1/Decimal(16)**k *
               (Decimal(4)/(8*k+1) -
               Decimal(2)/(8*k+4) -
               Decimal(1)/(8*k+5) -
               Decimal(1)/(8*k+6)) for k in range(n))


def gridplot(nums):
    """
    Plots a string of digits (removing decimal points) in a grid. 
    """
    # parse the text string into a numpy array
    nums = nums.replace(".", "")
    nums = np.array([int(num) for num in nums])

    # Find the nearest square to get the width and height
    lenn = len(nums)
    dims = int(math.ceil(math.sqrt(lenn)))
    nums = np.pad(nums, (0, (dims**2) - nums.shape[0]), mode='constant')
    nums = nums.reshape((dims, dims))

    # Visualize the grid
    fig, axe = plt.subplots(figsize=(10, 10))
    mat = axe.matshow(nums, cmap=cm.nipy_spectral)

    # Configure the figure
    plt.title("Pi visualized to {} places".format(lenn))
    axe.axis('off')

    # Add the colorbar to the right
    divider = make_axes_locatable(axe)
    cax = divider.append_axes("right", size="5%", pad=0.25)
    plt.colorbar(mat, cax=cax)

    # Show the figure
    plt.show()


if __name__ == "__main__":

    import argparse

    # Construct argument parser for command line.
    parser = argparse.ArgumentParser(description="Compute PI to n digits")  # version="pi 1.0",
    parser.add_argument("-b", "--bbp", action="store_true", help="Use BBP")
    parser.add_argument("-c", "--chud", action="store_true", help="Use Chudnovsky")
    parser.add_argument("-s", "--show", action="store_true", help="Visualize Pi with matplotlib")
    parser.add_argument("n", nargs=1, type=int, help="Number of digits to compute Pi to")
    args = parser.parse_args()

    num_digits = args.n[0]

    # Compute Pi and print output to the terminal.
    if (args.bbp):
        pi, elapsed = pi_digits_bbp(num_digits)
        mp.nprint(pi, num_digits)
    else:
        pi, elapsed = pi_digits_chud(num_digits)
        print(f'{cfactorial.cache_info()=}')
        print(pi)

    print(f"Computing Pi to {num_digits:_} digits took {elapsed:0.3f} seconds")

    # Perform visualization if requested
    if args.show:
        gridplot(nums=str(pi)[:num_digits+1])
