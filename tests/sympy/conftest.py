import pytest
import sympy as sp


@pytest.fixture
def symbols() -> list[sp.Symbol]:
    x, y, z, alpha, beta = sp.symbols('x y z alpha beta', real=True)
    i, j, k = sp.symbols('i j k', integer=True, positive=True)

    return [i, j, k, x, y, z, alpha, beta]
