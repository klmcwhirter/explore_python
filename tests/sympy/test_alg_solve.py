
import sympy as sp


def test_can_create_symbols(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    print(f'{type(x)=}', end=' ')


def test_can_solve_polynomial(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x**2 - 1
    expected = [-1, 1]
    actuals = sp.solve(expr, x)
    print(f'{actuals=}', end=', ')

    assert expected == actuals

    solutions = [expr.subs({x: sub}) for sub in actuals]
    print(f'{solutions=}', end=' ')

    assert all(x == 0 for x in solutions)


def test_solutions_map_to_factors(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols
    expr = x**2 - 5*x + 6

    expected = [2, 3]

    solutions = sp.solve(expr, x)
    print(f'{solutions=}', end=', ')
    assert expected == solutions

    exp_factors_str = '*'.join([f'(x - {c})' for c in reversed(expected)])
    print(f'{exp_factors_str=}', end=', ')

    factors = sp.factor(expr)

    actual_factors_str = str(factors)
    print(f'{actual_factors_str=}', end=' ')
    assert exp_factors_str == actual_factors_str


def test_solves_system_of_eq(symbols) -> None:
    _, _, _, x, y, _, _, _ = symbols
    exprs = [
        2*x + 3*y - 7,
        5*x + 7*y - 10,
    ]
    expected = {x: -19, y: 15}

    solution = sp.solve(exprs, (x, y))
    print(f'{solution=}', end=' ')

    assert expected == solution

    # assert solution works for each expr in system
    for expr in exprs:
        expr_actual: sp.Float = expr.evalf(subs=expected)
        assert (1.e-100) > expr_actual
