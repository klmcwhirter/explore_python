
import sympy as sp


def test_can_calc_limit(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = (x**2 - 1) / (x - 1)
    expected = 2  # as x => 1

    actual = sp.limit(expr, x, 1)
    print(f'{actual=}', end=' ')

    assert expected == actual


def test_can_calc_limit_from_left(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x / abs(x)
    expected = -1  # as x => 0-

    actual = sp.limit(expr, x, 0, '-')
    print(f'{actual=}', end=' ')

    assert expected == actual


def test_can_calc_limit_from_right(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x / abs(x)
    expected = 1  # as x => 0+

    actual = sp.limit(expr, x, 0, '+')
    print(f'{actual=}', end=' ')

    assert expected == actual


def test_can_calc_1st_deriv(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x**5
    expected = '5*x**4'

    actual = sp.diff(expr, x, 1)
    print(f'{actual=}', end=' ')

    assert expected == str(actual)


def test_can_calc_2nd_deriv(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x**5
    expected = '20*x**3'

    actual = sp.diff(expr, x, 2)
    print(f'{actual=}', end=' ')

    assert expected == str(actual)


def test_can_calc_3rd_deriv(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x**5
    expected = '60*x**2'

    actual = sp.diff(expr, x, 3)
    print(f'{actual=}', end=' ')

    assert expected == str(actual)
