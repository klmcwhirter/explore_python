# Experiments on Performance of NoGIL Compile-time Option of python3.13t

The perfects.py module finds perfect numbers from 1 up to and including some max_n value.

It supports this via the following execution models selectable on the command line:

* `Single` - standard single threaded execution model
* `Processes` - multiple processes each evaluating an equally sized range of value for n
* `Threads` - multiple threads each evaluating an equally sized range of value for n

It does this by simply executing the function for the range 1:max_n in the `Single` case,
uses concurrent.futures.ProcessPoolExecutor in the `Processes` case,
and uses concurrent.futures.ThreadPoolExecutor in the `Threads` case.

## Command-line Options

Note that the default execution model depends on whether the GIL is disabled or not.

If the GIL is disabled, the `Threads` execution model is the default, else the `Processes` model is the default.

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

The -n 1_000_000 and -w 10 options remain constant.

> Note the -w option is ignored when the -s option (`Single` execution model) is present.
> That is indicated below by the use of ~~strikethrough~~.

Here are the results from one typical run:

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| **python3.13** perfects.py -n 1_000_000 -w 10 | [6, 28, 496, 8128] | **0:00:03.762662** |
| python3.13 perfects.py -n 1_000_000 -w 10 -v | [6, 28, 496, 8128] | 0:00:04.305576 |
| python3.13 perfects.py -n 1_000_000 -w 10 -p | [6, 28, 496, 8128] | 0:00:04.827597 |
| python3.13 perfects.py -n 1_000_000 -w 10 -p -v | [6, 28, 496, 8128] | 0:00:04.155676 |
| python3.13 perfects.py -n 1_000_000 ~~-w 10~~ -s | [6, 28, 496, 8128] | 0:00:19.394819 |
| python3.13 perfects.py -n 1_000_000 ~~-w 10~~ -s -v | [6, 28, 496, 8128] | 0:00:19.334248 |
| python3.13 perfects.py -n 1_000_000 -w 10 -t | [6, 28, 496, 8128] | 0:00:20.177844 |
| python3.13 perfects.py -n 1_000_000 -w 10 -t -v | [6, 28, 496, 8128] | 0:00:20.012492 |
| python3.13t perfects.py -n 1_000_000 -w 10 | [6, 28, 496, 8128] | 0:00:05.262486 |
| python3.13t perfects.py -n 1_000_000 -w 10 -v | [6, 28, 496, 8128] | 0:00:05.429427 |
| python3.13t perfects.py -n 1_000_000 -w 10 -p | [6, 28, 496, 8128] | 0:00:05.099219 |
| python3.13t perfects.py -n 1_000_000 -w 10 -p -v | [6, 28, 496, 8128] | 0:00:05.016093 |
| **python3.13t** perfects.py -n 1_000_000 ~~-w 10~~ **-s** | [6, 28, 496, 8128] | **0:00:25.162151** |
| python3.13t perfects.py -n 1_000_000 ~~-w 10~~ -s -v | [6, 28, 496, 8128] | 0:00:25.243074 |
| python3.13t perfects.py -n 1_000_000 -w 10 -t | [6, 28, 496, 8128] | 0:00:04.758736 |
| python3.13t perfects.py -n 1_000_000 -w 10 -t -v | [6, 28, 496, 8128] | 0:00:05.491213 |

## Results Summary

It appears that the production executable (python3.13) with the GIL enabled is more performant when using
the `Processes` execution model than the experimental executable (python3.13t) with the GIL disabled.

Also, when using the `Threads` execution model its performance is a little worse than the `Single` model.
This makes sense because the GIL is in effect.

The `Threads` execution model with the experimental executable (python3.13t) is slightly more performant
than even when using the `Processes` model with python3.13 but the difference is within a reasonable margin of error.
So I am going to call those a wash.

The `Processes` execution model with python3.13t does indeed enjoy similar performance as when using the `Threads`
execution model. However both of these are very similar to using the `Processes` model with python3.13.

However, the risks associated with execution integrity explains why they do not support the python3.13t
executable in production. And my results do not show a compelling reason to do so.
