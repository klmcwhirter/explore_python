'''
Created with lambdify. Signature:

func(n, λ)

Expression:

Sum((-4/(2*n + 1) + 1/(n + λ))*RisingFactorial(-n + (2*n + 1)**2/(4*(n +...

Source code:

def _lambdifygenerated(n, λ):
    return (builtins.sum((-4/(2*n + 1) + 1/(n + λ))*(((gamma(-1 + (mpf(1)/mpf(4))*(2*n + 1)**2/(n + λ))/gamma(-n + (mpf(1)/mpf(4))*(2*n + 1)**2/(n + λ))) if (n - mpf(1)/mpf(4)*(2*n + 1)**2/(n + λ) < 0) else ((-1)**(n - 1)*gamma(n + 1 - mpf(1)/mpf(4)*(2*n + 1)**2/(n + λ))/gamma(2 - mpf(1)/mpf(4)*(2*n + 1)**2/(n + λ)))))/factorial(n) for n in range(1, 400+1))) + 4

# with scipy installed
def _lambdifygenerated(n, λ):
    return (builtins.sum((-4/(2*n + 1) + (n + λ)**(-1.0))*poch(-n + (1/4)*(2*n + 1)**2/(n + λ), n - 1)/factorial(n) for n in range(1, 400+1))) + 4

# using sympy
def _lambdifygenerated(n, λ):
    return (builtins.sum((-4/(2*n + 1) + 1/(n + λ))*RisingFactorial(-n + (1/4)*(2*n + 1)**2/(n + λ), n - 1)/factorial(n) for n in range(1, 400+1))) + 4

Imported modules:


'''
import datetime
import sys

import sympy as sym

THOUSAND = 1_000
MILLION = THOUSAND * THOUSAND

MAX_PREC = 50 * THOUSAND  # MILLION
MAX_TERMS = MAX_PREC

sys.set_int_max_str_digits(MAX_TERMS)


@sym.utilities.memoization.recurrence_memo([1])  # 0! = 1
def factorial(n, prev):
    return n * prev[-1]


def sinha_saha_pi_mpmath(n: int, λ_val, prec: int):
    import mpmath as mpm
    from mpmath import mpf

    mpm.mp.dps = prec

    terms = []
    for n in range(1, 400+1):
        # if (n % 10) == 0:
        print(n, flush=True)

        term = (-4/(2*n + 1) + 1/(n + λ_val)) * (
            ((mpm.gamma(-1 + (mpf(1)/mpf(4))*(2*n + 1)**2/(n + λ_val))/mpm.gamma(-n + (mpf(1)/mpf(4))*(2*n + 1)**2/(n + λ_val))) if (n - mpf(1)/mpf(4)*(2*n + 1)**2/(n + λ_val) < 0)
             else ((-1)**(n - 1)*mpm.gamma(n + 1 - mpf(1)/mpf(4)*(2*n + 1)**2/(n + λ_val))/mpm.gamma(2 - mpf(1)/mpf(4)*(2*n + 1)**2/(n + λ_val))))
        ) / factorial(n)

        terms.append(term)

    rc = (sum(terms)) + 4
    return rc


def sinha_saha_pi_scipy(n: int, λ_val, prec: int):
    import scipy.special as sc
    return (
        sum((-4/(2*n + 1) + (n + λ_val)**(-1.0)) * sc.poch(-n + (1/4)*(2*n + 1)**2/(n + λ_val), n - 1)
            /
            factorial(n)
            for n in range(1, 400+1)
            )
    ) + 4


def sinha_saha_pi_lambdify_sympy(num_terms: int, λ_val, prec: int):
    terms = []
    now = datetime.datetime.now()
    for n in range(1, num_terms+1):
        if (n % 1000) == 0:
            was, now = now, datetime.datetime.now()
            elapsed = now - was

            print(f'{str(now)} : {n=:_} in {str(elapsed)}', flush=True)

        term = (-4/(2*n + 1) + 1/(n + λ_val)) \
            * \
            sym.RisingFactorial(-n + 1/4 * (2*n + 1)**2 / (n + λ_val), n - 1) \
            / \
            factorial(n)

        terms.append(term.evalf(prec))

    rc = sum(terms) + 4

    return rc


def sinha_saha_pi_sympy(num_terms: int, λ_val: sym.Float, prec: int):
    n = sym.symbols('n', integer=True, positive=True)
    λ = sym.symbols('λ', real=True)

    sum_left = (1 / sym.factorial(n)) * (1 / (n+λ) - 4 / (2*n + 1))
    sum_right = (2*n + 1)**2 / (4 * (n + λ)).factor() - n

    SinhaSaha = 4 + sym.Sum(sum_left * sym.RisingFactorial(sum_right, n-1), (n, 1, num_terms))

    print('Substituting λ and simplifying ...', flush=True)
    SinhaSaha_simplified = SinhaSaha.subs({λ: λ_val}).simplify()

    print(f'Evaluating to {prec} digits prec ...', flush=True)
    rc = SinhaSaha_simplified.evalf(prec)
    return rc


if __name__ == '__main__':
    num_terms = MAX_TERMS
    λ = 575
    prec = MAX_PREC

    now = datetime.datetime.now()

    print(f'{str(now)} - check back at {str(now + datetime.timedelta(hours=1, minutes=22, seconds=30))}', flush=True)

    rc = sinha_saha_pi_sympy(num_terms, λ, prec)
    print({
        'rc': rc.evalf(130),
        'len': len(str(rc)),
    })

    print(f'{factorial.cache_length()=}')

    was, now = now, datetime.datetime.now()
    elapsed = now - was

    print(f'{str(now)} : done in {str(elapsed)}', flush=True)
