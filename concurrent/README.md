# Experiments on Performance of NoGIL Compile-time Option Added in python3.13t

## Background

In Python 3.13 an implementation of [PEP-703](https://peps.python.org/pep-0703/) was made available on an experimental basis. The abstract of that PEP claims that:
> The GIL is an obstacle to using multi-core CPUs from Python efficiently. This PEP proposes adding a build configuration (--disable-gil) to CPython to let it run Python code without the global interpreter lock and with the necessary changes needed to make the interpreter thread-safe.

## Overview

The [`perfects.py`](./perfects.py) module in this project finds [perfect numbers](https://mathworld.wolfram.com/PerfectNumber.html) from 1 up to and including some `max_n` value.

This problem is suitable for testing parallelism with concurrent execution models because:

* while there is a formula for predicting where perfect numbers appear - a brute force method is used by `perfects.py` to find perfect numbers. This presents as a normalizing effect on the characteristics of the execution model being tested
* the process for testing each value of `n` is independent from all other values of `n`; meaning parallelism can be maximized

[`perfects.py`](./perfects.py) supports the test goals via the following execution models selectable on the command line:

* `Single` - standard single threaded execution model
* `Interpreters` - multiple threads each evaluating an equally sized range of values for `n` in their own interpreter (new in 3.14)
* `Processes` - multiple processes each evaluating an equally sized range of values for `n`
* `Threads` - multiple threads each evaluating an equally sized range of values for `n`

It does this by:
* simply executing the function that tests for perfect numbers for the range `1:max_n` in the `Single` case,
* using [concurrent.futures.InterpreterPoolExecutor](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor) in the `Interpreters` case,
* using [concurrent.futures.ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor) in the `Processes` case,
* and using [concurrent.futures.ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) in the `Threads` case.
* explicitly avoiding any shared state between the workers except for things that will not change (e.g. `ctx.worker_name(idx)`).

This makes the function that tests for perfect numbers completely reusable; eliminating any code differences due to execution model.

> NOTE: I did not bother with an *asyncio* implementation because I purposely avoided I/O as an additional testing variable. I do realize
that design decision makes the test less like *real world* scenarios. But the goal was to test parallelism and concurrency in isolation from other features.
In other words, what is the significance of the NoGIL behavior and its direct effect on execution models?

Also, I eliminated concurrency as a variable by carefully designing away shared state. The worker function simply takes some inputs and returns found perfect numbers in the range of numbers it is evaluating.

> This project is named `concurrent` because initially I thought I would be testing for the underlying risk of the missing GIL - namely data corruption when using libraries like `numpy`, etc. Was the promise of maintained thread-safety (PEP-703) in the interpreter truly realized or not?
>
> But I realized there was an underlying assumption that led to that concern. Many were assuming that eliminating the GIL would lead inherently to better performance with CPU bound problems.
>
> And so this project was pivoted to validate that assumption. I am glad I did. _See_ **TL;DR** _below._
>
> When and if a point is reached where there is a measurable performance gain, then (and only then) I will return to experimenting with the additional complexity involved in accomplishing concurrency with a NoGIL Python interpreter.

If performance cannot be increased by utilizing threads across multiple cores with a stateless worker design, then there is no point in testing shared, concurrent state.

Until then ...

### TL;DR

The effect of NoGIL on performance is not much if anything with lower values of `max_n`; and significantly worse performance with higher values.

Since the perceived benefit of NoGIL is the potential for utilizing multiple cores via multiple threads to help solve for CPU bound problem sets, it
seems that Guido van Rossum was absolutely justified to introduce the GIL.

Other efforts such as Per-Interpreter GIL ([PEP-684](https://peps.python.org/pep-0684/)), InterpreterPoolExecutor ([PEP-734](https://peps.python.org/pep-0684/)), etc. have provided a less intrusive solution to the multi-core utilization issue then disabling the GIL ([PEP-703](https://peps.python.org/pep-0703/)).

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
  -i, --interpreters    force use of interpreters in threads
  -p, --processes       force use of processes instead of threads
  -s, --single-thread   force use of no parallelization
  -t, --threads         force use of threads instead of processes
  -v, --verbose         Enable verbose mode
```

## Goal of perfects_driver.sh

The goal of [`perfects_driver.sh`](./perfects_driver.sh) is to compare the validity of the results produced,
and time the actual execution component of the process of a matrix of the options.

The `-n 1_000_000` and `-w 10` options remain constant.

> Note the `-w` option is ignored when the -s option (`Single` execution model) is requested.
> That is indicated below by the use of ~~strikethrough~~.

The **lowest** and **highest** execution times in each group are indicated with **bold** typeface.

Here are the [results](./perfects_driver-py313-fed40.out) from one typical run with Python3.13 on Fedora WS 40 that is summarized below:

_I retested with Python 3.14.0a1 on Fedora 41. Here are those [results](./perfects_driver-py314a1-fed41.out)._

_I retested with Python 3.14.0a6 on Fedora 41 and added the `-i` option. Here are those [results](./perfects_driver-py314a6-fed41.out). See **Appendix B** below._

### Production Executable (python3.13)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| **python3.13** perfects.py -n 1_000_000 -w 10 | [6, 28, 496, 8128] | **0:00:04.192254** |
| python3.13 perfects.py -n 1_000_000 -w 10 -v | [6, 28, 496, 8128] | 0:00:04.215628 |
| python3.13 perfects.py -n 1_000_000 -w 10 -p | [6, 28, 496, 8128] | 0:00:04.196177 |
| python3.13 perfects.py -n 1_000_000 -w 10 -p -v | [6, 28, 496, 8128] | 0:00:04.243090 |
| python3.13 perfects.py -n 1_000_000 ~~-w 10~~ -s | [6, 28, 496, 8128] | 0:00:19.412308 |
| python3.13 perfects.py -n 1_000_000 ~~-w 10~~ -s -v | [6, 28, 496, 8128] | 0:00:19.406344 |
| python3.13 perfects.py -n 1_000_000 -w 10 -t | [6, 28, 496, 8128] | 0:00:20.159437 |
| **python3.13** perfects.py -n 1_000_000 -w 10 -t -v | [6, 28, 496, 8128] | **0:00:20.342431** |

### Experimental Executable (python3.13t)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| **python3.13t** perfects.py -n 1_000_000 -w 10 | [6, 28, 496, 8128] | **0:00:04.841594** |
| python3.13t perfects.py -n 1_000_000 -w 10 -v | [6, 28, 496, 8128] | 0:00:05.208515 |
| python3.13t perfects.py -n 1_000_000 -w 10 -p | [6, 28, 496, 8128] | 0:00:05.306935 |
| python3.13t perfects.py -n 1_000_000 -w 10 -p -v | [6, 28, 496, 8128] | 0:00:05.952637 |
| python3.13t perfects.py -n 1_000_000 ~~-w 10~~ -s | [6, 28, 496, 8128] | 0:00:25.363863 |
| **python3.13t** perfects.py -n 1_000_000 ~~-w 10~~ **-s** -v | [6, 28, 496, 8128] | **0:00:26.044659** |
| python3.13t perfects.py -n 1_000_000 -w 10 -t | [6, 28, 496, 8128] | 0:00:05.137568 |
| python3.13t perfects.py -n 1_000_000 -w 10 -t -v | [6, 28, 496, 8128] | 0:00:05.254062 |

## Results Summary

### Production Executable (python3.13)

It appears that the production executable (python3.13) with the GIL enabled is slightly more performant when using
the `Processes` execution model than the experimental executable (python3.13t) with the GIL disabled.

Also, when using the `Threads` execution model its performance is a little worse than the `Single` model.
This makes sense because the GIL is in effect and there is a little overhead associated with using a thread pool,
and multiple threads in general.

### Experimental Executable (python3.13t)

The `Threads` execution model with the experimental executable (python3.13t) is slightly less performant
than even when using the `Processes` model with python3.13 but the difference is within a reasonable margin of error.
So I am going to call those a wash.

The `Threads` execution model with python3.13t does enjoy similar performance as when using the `Processes`
execution model because it is able to use multiple cores with the NoGIL behavior. However both of these are very similar
to using the `Processes` model with python3.13.

And, as `max_n` increases (see **Appendix A** below) the performance benefits trail off significantly.

The performance of the `Single` model lags behind the production executable for some unknown reason.

In addition, the potential risks associated with execution integrity without the GIL explains why using the python3.13t
executable in production is not supported yet. And the results above do not show a compelling reason to do so.


### Development Executable (python3.14)

In Python 3.14 the [`concurrent.futures.InterpreterPoolExecutor`](https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor) class was added per [PEP-734](https://peps.python.org/pep-0734/#interpreterpoolexecutor).

As described in PEP-734, this class extends the ThreadPoolExecutor class where each worker runs in its own interpreter. This takes the GIL out of the way of using multiple cores. This happens because each interpreter has its own GIL.

It performs well - as well as ProcessPoolExecutor. _See **Appendix B** below for a snapshot of the results._

But it has limitations.

Communication with the threads (and their interpreters) is done via pickle. See the docs linked above and in PEP-734 for discussion of how pickle (and alternates) are used. This fact does drive the app design to some extent.

In general, I avoided the need for concurrency (i.e., no shared state) to minimize the impact.

### Recommendation:

Just stick with the `Processes` model for now while the experimentation continues. It is supported as early as Python 3.5.

The `Interpreters` model could become the preferred (i.e., safe) alternative, however, once Python 3.14 is released in Oct 2025 (See [PEP-745](https://peps.python.org/pep-0745/)). I say _safe_ because the GIL is still in effect suggesting that most flows through the Python interpreter, stdlib and 3rd-party library code are flows through long-time existing code. But please do test fit for your purpose.


## Appendix A - Results with `-n 33_551_000` and `-w 12`

These results were purposely (albeit selfishly, because of time commitment) trimmed down to perhaps the most interesting data points.

> As `max_n` grows in size, the experimental executable loses its performance similarity. *This is more than likely due to the overhead
associated with more aggressive context switching; resulting in additional resource contention.*

### Production Executable (python3.13)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.13 perfects.py -n 33_551_000 -w 12 | [6, 28, 496, 8128, 33550336] | 0:14:46.709272 |
| **python3.13** perfects.py -n 33_551_000 -w 12 -v | [6, 28, 496, 8128, 33550336] | **0:14:46.351818** |
| python3.13 perfects.py -n 33_551_000 -w 12 -p | [6, 28, 496, 8128, 33550336] | 0:14:47.447327 |
| **python3.13** perfects.py -n 33_551_000 -w 12 -p -v | [6, 28, 496, 8128, 33550336] | **0:14:49.279411** |

### Experimental Executable (python3.13t)

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.13t perfects.py -n 33_551_000 -w 12 | [6, 28, 496, 8128, 33550336] | 0:18:21.164616 |
| python3.13t perfects.py -n 33_551_000 -w 12 -v | [6, 28, 496, 8128, 33550336] | 0:18:28.153575 |
| **python3.13t** perfects.py -n 33_551_000 -w 12 -p | [6, 28, 496, 8128, 33550336] | **0:18:02.101572** |
| python3.13t perfects.py -n 33_551_000 -w 12 -p -v | [6, 28, 496, 8128, 33550336] | 0:18:10.316738 |
| **python3.13t** perfects.py -n 33_551_000 -w 12 -t | [6, 28, 496, 8128, 33550336] | **0:18:35.191395** |
| python3.13t perfects.py -n 33_551_000 -w 12 -t -v | [6, 28, 496, 8128, 33550336] | 0:18:27.886885 |


## Appendix B - InterpreterPoolExecutor vs ProcessPoolExecutor

### Development Executable (python3.14)

This first section captures the relative performance of the various options with python3.14(t).

There is no suprise here, except the newcomer - **-i** - which is the clear winner.

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.14 perfects.py -n 1_000_000 -w 10 -v -p  | [6, 28, 496, 8128] | 0:00:03.408228 |
| **python3.14** perfects.py -n 1_000_000 -w 10 -v **-i**  | [6, 28, 496, 8128] | **0:00:03.303046** |
| python3.14 perfects.py -n 1_000_000 -w 10 -v -s  | [6, 28, 496, 8128] | 0:00:15.990855 |
| python3.14 perfects.py -n 1_000_000 -w 10 -v -t  | [6, 28, 496, 8128] | 0:00:16.590999 |

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| python3.14t perfects.py -n 1_000_000 -w 10 -v -p  | [6, 28, 496, 8128] | 0:00:04.471091 |
| python3.14t perfects.py -n 1_000_000 -w 10 -v -i  | [6, 28, 496, 8128] | 0:00:04.827538 |
| python3.14t perfects.py -n 1_000_000 -w 10 -v -s  | [6, 28, 496, 8128] | 0:00:23.126717 |
| **python3.14t** perfects.py -n 1_000_000 -w 10 -v **-t**  | [6, 28, 496, 8128] | **0:00:04.735871** |


### Results with `-n 33_551_000` and `-w 12`

In this section the `max_n` is bumped up as well as the number of workers.

This makes it clear that `InterpreterPoolExecutor` is walking away from the pack.

| Command Line | Results | Elapsed Time |
| :-- | :--: | --: |
| **python3.14** perfects.py -n 33_551_000 -w 12 **-i** -v | [6, 28, 496, 8128, 33550336] | **0:10:23.770246** |
| python3.14 perfects.py -n 33_551_000 -w 12 -p -v | [6, 28, 496, 8128, 33550336] | 0:10:31.152181 |
