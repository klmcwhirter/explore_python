# Experiments on Performance of NoGIL Compile-time Option of python3.13t

The `perfects.py` module finds [perfect numbers](https://mathworld.wolfram.com/PerfectNumber.html) from 1 up to and including some max_n value.

This problem is suitable for testing concurrent executions models because:

* while there is a formula for predicting where they appear - a brute force method is used by `perfects.py`. This presents as a normalizing effect on the execution characteristics of the model being employed.
* each value of `n` tested is independent from all other values of `n`; meaning parallelism can be maximized.

`perfects.py` supports the test goals via the following execution models selectable on the command line:

* `Single` - standard single threaded execution model
* `Processes` - multiple processes each evaluating an equally sized range of values for `n`
* `Threads` - multiple threads each evaluating an equally sized range of values for `n`

It does this by:
* simply executing the function for the range `1:max_n` in the `Single` case,
* using [concurrent.futures.ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor) in the `Processes` case,
* and using [concurrent.futures.ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) in the `Threads` case.

This makes the code completely reusable and eliminates any code differences due to execution model.

## Command-line Options

Note that the default execution model depends on whether the GIL is disabled or not.

*If the GIL is disabled, the `Threads` execution model is the default, else the `Processes` model is the default.*

```
usage: perfects.py [-h] [-n MAX_N] [-w NUM_WORKERS] [-p] [-s] [-t] [-v]

options:
  -h, --help            show this help message and exit
  -n, --max-n MAX_N     look for perfect numbers up to and including this value (default: 1_000_000)
  -w, --num-workers NUM_WORKERS
                        number of worker processes to use (default: 12)
  -p, --processes       force use of processes instead of threads
  -s, --single-threaded
                        force use of no parallelization
  -t, --threads         force use of threads instead of processes
  -v, --verbose         Enable verbose mode
```

## Goal of perfects_driver.sh

The goal of perfects_driver.sh is to compare the validity of the results produced,
and time the actual execution component of the process of a matrix of the options.

The `-n 1_000_000` and `-w 10` options remain constant.

> Note the `-w` option is ignored when the -s option (`Single` execution model) is requested.
> That is indicated below by the use of ~~strikethrough~~.

Here are the results from one typical run:

### Production Executable (python3.13)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| **python3.13** perfects.py -n 1_000_000 -w 10 | [6, 28, 496, 8128] | 0:00:04.291743 |
| python3.13 perfects.py -n 1_000_000 -w 10 -v | [6, 28, 496, 8128] | 0:00:04.294041 |
| python3.13 perfects.py -n 1_000_000 -w 10 -p | [6, 28, 496, 8128] | **0:00:04.263898** |
| python3.13 perfects.py -n 1_000_000 -w 10 -p -v | [6, 28, 496, 8128] | 0:00:04.696332 |
| python3.13 perfects.py -n 1_000_000 ~~-w 10~~ -s | [6, 28, 496, 8128] | 0:00:19.448831 |
| python3.13 perfects.py -n 1_000_000 ~~-w 10~~ -s -v | [6, 28, 496, 8128] | 0:00:19.344277 |
| python3.13 perfects.py -n 1_000_000 -w 10 -t | [6, 28, 496, 8128] | 0:00:20.141020 |
| python3.13 perfects.py -n 1_000_000 -w 10 -t -v | [6, 28, 496, 8128] | 0:00:20.273820 |

### Experimental Executable (python3.13t)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.13t perfects.py -n 1_000_000 -w 10 | [6, 28, 496, 8128] | 0:00:05.239328 |
| python3.13t perfects.py -n 1_000_000 -w 10 -v | [6, 28, 496, 8128] | 0:00:05.104479 |
| python3.13t perfects.py -n 1_000_000 -w 10 -p | [6, 28, 496, 8128] | 0:00:05.282542 |
| python3.13t perfects.py -n 1_000_000 -w 10 -p -v | [6, 28, 496, 8128] | 0:00:05.371516 |
| python3.13t perfects.py -n 1_000_000 ~~-w 10~~ -s | [6, 28, 496, 8128] | 0:00:25.078917 |
| **python3.13t** perfects.py -n 1_000_000 ~~-w 10~~ **-s** -v | [6, 28, 496, 8128] | **0:00:25.114644** |
| python3.13t perfects.py -n 1_000_000 -w 10 -t | [6, 28, 496, 8128] | 0:00:05.239508 |
| python3.13t perfects.py -n 1_000_000 -w 10 -t -v | [6, 28, 496, 8128] | 0:00:04.969282 |

## Results Summary

### Production Executable (python3.13)

It appears that the production executable (python3.13) with the GIL enabled is slightly more performant when using
the `Processes` execution model than the experimental executable (python3.13t) with the GIL disabled.

Also, when using the `Threads` execution model its performance is a little worse than the `Single` model.
This makes sense because the GIL is in effect.

### Experimental Executable (python3.13t)

The `Threads` execution model with the experimental executable (python3.13t) is slightly more performant
than even when using the `Processes` model with python3.13 but the difference is within a reasonable margin of error.
So I am going to call those a wash.

The `Processes` execution model with python3.13t does enjoy similar performance as when using the `Threads`
execution model. *I offer no explanation for this unexpected outcome.* However both of these are very similar to using the `Processes` model with python3.13.

However, the risks associated with execution integrity explains why they do not support the python3.13t
executable in production. And my results do not show a compelling reason to do so.

Just stick with the `Processes` model for now while the experimentation continues.

## Appendix A - Results with `-n 33_551_000` and `-w 12`

These results were purposely (albeit selfishly, because of time commitment) trimmed down to the perhaps interesting data points.

> As `max_n` grows in size, the experimental executable loses its performance similarity.

### Production Executable (python3.13)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.13 perfects.py -n 33_551_000 -w 12 | [6, 28, 496, 8128, 33550336] | 0:14:46.709272 |
| python3.13 perfects.py -n 33_551_000 -w 12 -v | [6, 28, 496, 8128, 33550336] | 0:14:46.351818 |
| python3.13 perfects.py -n 33_551_000 -w 12 -p | [6, 28, 496, 8128, 33550336] | 0:14:47.447327 |
| python3.13 perfects.py -n 33_551_000 -w 12 -p -v | [6, 28, 496, 8128, 33550336] | **0:14:49.279411** |

### Experimental Executable (python3.13t)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.13t perfects.py -n 33_551_000 -w 12 | [6, 28, 496, 8128, 33550336] | 0:18:21.164616 |
| python3.13t perfects.py -n 33_551_000 -w 12 -v | [6, 28, 496, 8128, 33550336] | 0:18:28.153575 |
| python3.13t perfects.py -n 33_551_000 -w 12 -p | [6, 28, 496, 8128, 33550336] | 0:18:02.101572 |
| python3.13t perfects.py -n 33_551_000 -w 12 -p -v | [6, 28, 496, 8128, 33550336] | 0:18:10.316738 |
| python3.13t perfects.py -n 33_551_000 -w 12 -t | [6, 28, 496, 8128, 33550336] | **0:18:35.191395** |
| python3.13t perfects.py -n 33_551_000 -w 12 -t -v | [6, 28, 496, 8128, 33550336] | 0:18:27.886885 |
