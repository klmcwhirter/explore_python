import sympy as sp


def test_will_combine_terms(symbols) -> None:
    _, _, _, x, y, z, _, _ = symbols

    y = x+x + z + 3*z
    print(f'{y=}', end=' ')

    expected = '2*x + 4*z'
    assert expected == str(y)


def test_simplify_will_find_factors(symbols) -> None:
    _, _, _, x, y, _, alpha, _ = symbols

    y = alpha * x**3 + 3*x**3
    print(f'{y=}', end=' ')
    print(f'{sp.simplify(y)=}', end=' ')

    expected = 'x**3*(alpha + 3)'
    assert expected == str(sp.simplify(y))


def test_collect_to_control_factors(symbols) -> None:
    _, _, _, x, y, _, alpha, _ = symbols

    expr = alpha * x**3 + 3*x**3
    print(f'{expr=}', end=', ')

    actual = sp.collect(expr, x**3)
    print(f'{actual=}', end=' ')

    expected = 'x**3*(alpha + 3)'
    assert expected == str(actual)


def test_simplify_will_find_trig_identities(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols

    expr = sp.sin(x) / sp.cos(x)
    print(f'{expr=}', end=' ')
    print(f'{sp.simplify(expr)=}', end=' ')

    expected = 'tan(x)'
    assert expected == str(sp.simplify(expr))


def test_cancel_to_simplify_fract_exprs(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols

    expr = (x**2 - 1) / (x + 1)
    print(f'{expr=}', end=', ')

    actual = expr.cancel()
    print(f'{actual=}', end=' ')

    expected = 'x - 1'
    assert expected == str(actual)


def test_sp_cancel_can_be_passed_expr(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols

    expr = (x**2 - 1) / (x + 1)
    print(f'{expr=}', end=', ')

    actual = sp.cancel(expr)
    print(f'{actual=}', end=' ')

    expected = 'x - 1'
    assert expected == str(actual)


def test_together_finds_gcd(symbols) -> None:
    _, _, _, x, _, z, _, _ = symbols

    expr = x + 1/x + 1/z
    print(f'{expr=}', end=', ')

    actual = sp.together(expr)
    print(f'{actual=}', end=' ')

    expected = '(x**2*z + x + z)/(x*z)'
    assert expected == str(actual)


def test_powsimp_combines_exponents(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols

    print('expr=x**5 * x**11', end=', ')

    actual = sp.powsimp(x**5 * x**11)
    print(f'{actual=}', end=' ')

    expected = 'x**16'
    assert expected == str(actual)


def test_trigsimp_will_find_trig_identities(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols

    print('expr=sin(x) / cos(x)', end=', ')

    actual = sp.trigsimp(sp.sin(x) / sp.cos(x))
    print(f'{actual=}', end=' ')

    expected = 'tan(x)'
    assert expected == str(actual)


def test_can_factor_quadratics(symbols) -> None:
    _, _, _, x, _, _, _, _ = symbols

    expr = x**2 - 5*x + 6
    print(f'{expr=}', end=', ')

    factors = sp.factor(expr)

    expected = [3, 2]
    exp_factors_str = '*'.join([f'(x - {c})' for c in expected])
    print(f'{exp_factors_str=}', end=', ')

    actual_factors_str = str(factors)
    print(f'{actual_factors_str=}', end=' ')

    assert exp_factors_str == actual_factors_str
