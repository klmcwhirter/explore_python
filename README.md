# explore_python
Exploratory tests for python

## Running automated tests

```
pdm test # skip slow tests

pdm test --run-slow # skip slowest tests

pdm test --run-slowest # be prepared to wait 5 mins or so
```

## Concurrency Testing of python3.13t

I put together a simple test of the NoGIL behavior compiled into the experimental python3.13t executable.

The test plan and results can be found at [concurrent](./concurrent/).

## Jupyter notebooks

In the [jupyter](./jupyter/) dir there are several notebooks I have used to explore sympy.

## sympy

Sympy is an incredible library to model mathematics problems in a symbolic way.

What that means is that you can create expression graphs and modify them at runtime by saying things like:
* substitute the value 5 for the variable z - helpful especially when dealing with multivariate expressions / statements
* substitute say, cos(x) for the variable y - helpful when dealing with integration (variable substitution) - i.e., moving to the _u_ world

It has features that support several fields of (computational) mathematics
* arithmetic
* algrebra
* calculus
* statistics
* combinatorics
* concrete and discrete math
* ...
* as well as physics / engineering

And it is pure python!

## sympy optional installation dependencies

To get the best performance, I have also made sure to install these optional components.

* pdm add gmpy2
* pdm add mpmath[gmpy2]

One complex expression on which I was working went from 9 secs to 2.5 secs calc time once I installed these.

## References

* [Python docs](https://docs.python.org/)
* [sympy github](https://github.com/sympy/sympy/)
* [sympy docs](https://docs.sympy.org/)
