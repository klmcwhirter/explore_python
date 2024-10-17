import sys

import sympy as sym
from pi_1000000 import read_pi_control

print('Initializing ...', flush=True)

sym.init_printing(pretty_print=True, use_latex=True, use_unicode=True, order='lex')


def mprint(msg: str, basic: sym.Basic | str | None = None, prec: int | None = None) -> None:
    if prec is not None:
        print(msg, end=' ')
        basic_str = str(basic) if type(basic) != str else basic
        prec = len(basic_str) if prec == -1 else prec
        print(f'>>{basic_str[:prec]}<<', end='')
        print(f'{basic_str[prec:]}', flush=True)
    else:
        print(msg)
        if basic is not None:
            sym.pprint(basic, use_unicode=True)
            print('', end='', flush=True)


n = sym.symbols('n', integer=True, positive=True)
λ = sym.symbols('λ', real=True)
SinhaSaha = sym.symbols('SinhaSaha', cls=sym.Function)

# read control file for 1_000_000 digits of pi
print('read control file for 1_000_000 digits of pi...', flush=True)

MILLION = 1_000_000
sys.set_int_max_str_digits(MILLION)

control_pi = read_pi_control('./pi_1000000.txt', MILLION)


def first_index_not_matched(s1: str, s2: str) -> int:
    for i, (c, p) in enumerate(zip(s1, s2)):
        if c != p:
            return i
    return -1


PREC = MILLION

DEBUG_PI = False
if DEBUG_PI:
    prec_pi = sym.pi.evalf(PREC)
    prec_control_pi = control_pi.evalf(PREC)

    accuracy = (prec_control_pi - prec_pi).evalf(PREC/2)
    digits: int = int(sym.Abs(sym.floor(sym.log(accuracy) / sym.log(10))))

    digits_match_until = first_index_not_matched(str(prec_control_pi), str(prec_pi))
    all_digits_matched = digits_match_until == -1

    # subtract 1 from len for decimal point ('.')
    mprint(f'len control_pi: {len(str(prec_control_pi))-1:_}')
    mprint(f'len pi: {len(str(prec_pi))-1:_}')

    mprint(f'do all digits match? {all_digits_matched}')
    mprint(f'{digits_match_until=:_}')

    # mprint('control_pi:\t', str(prec_control_pi), digits)
    # mprint('pi:\t\t', str(prec_pi), digits)

    # mprint('control_pi - pi:', accuracy)

    mprint(f'\n{digits} digits accuracy')
    print('\n\n')

print('Define expression...', flush=True)

# num_terms = sym.symbols('num_terms', integer=True, positive=True)
# num_terms = sym.oo
# num_terms = sym.Integer(400)
num_terms = sym.Integer(PREC)

sum_left = (1 / sym.factorial(n)) * (1 / (n+λ) - 4 / (2*n + 1))
sum_right = (2*n + 1)**2 / (4 * (n + λ)).factor() - n

SinhaSaha = 4 + sym.Sum(sum_left * sym.RisingFactorial(sum_right, n-1), (n, 1, num_terms))
mprint('SinhaSaha:', SinhaSaha)

λ_val = 575
mprint(f'Replacing  λ with {λ_val} ...')
sub_expr: sym.Add = SinhaSaha.subs({λ: λ_val}).doit(deep=False)
mprint('sub_expr:', sub_expr)

mprint('Evaluating expression ...')
# prec = 130
prec = PREC

SinhaSaha_prec = sub_expr.evalf(prec)
# mprint('SinhaSaha_prec:', SinhaSaha_prec)

mprint('Print metrics ...')

mprint(f'{num_terms=}')
mprint(f'{λ_val=}')
mprint(f'{prec=}')
mprint('')

pi = sym.pi.evalf(prec)
accuracy = (SinhaSaha_prec - pi).evalf(prec/2)
digits: int = int(sym.Abs(sym.floor(sym.log(accuracy) / sym.log(10))))

mprint('control_pi:\t', str(control_pi.evalf(prec)), digits)
mprint('pi:\t\t', str(pi), digits)

mprint('SinhaSaha:\t', str(SinhaSaha_prec), digits)

mprint('\nSinhaSaha - pi:', accuracy)

mprint(f'\n{digits} digits accuracy')

mprint('done.')
