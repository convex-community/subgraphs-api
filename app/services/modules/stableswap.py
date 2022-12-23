"""
Util functions for stableswap pool related calculations
Adapted from CurveSim package
https://github.com/curveresearch/curvesim
"""
from gmpy2 import mpz


def get_stable_y(A, i, j, x, xp):
    r"""
    Parameters
    ----------
    A: int
        amplification parameter
    i: int
        index of coin; usually the "in"-token
    j: int
        index of coin; usually the "out"-token
    x: int
        balance of i-th coin in units of D
    xp: list of int
        coin balances in units of D
    Returns
    -------
    int
        The balance of the j-th coin, in units of D, for the other
        coin balances given.
    Note
    ----
    This is a "view" function; it doesn't change the state of the pool.
    """  # noqa
    xx = xp[:]
    D = get_stable_d(xx, A)
    D = mpz(D)
    xx[i] = x  # x is quantity of underlying asset brought to 1e18 precision
    n = len(xp)
    xx = [xx[k] for k in range(n) if k != j]
    Ann = A * n
    c = D
    for y in xx:
        c = c * D // (y * n)
    c = c * D // (n * Ann)
    b = sum(xx) + D // Ann - D
    y_prev = 0
    y = D
    while abs(y - y_prev) > 1:
        y_prev = y
        y = (y**2 + c) // (2 * y + b)
    y = int(y)
    return y


def get_stable_d(xp, A):
    r"""
    Parameters
    ----------
    xp: list of ints
        Coin balances normalized to 18 decimals
    A: int
        Amplification coefficient
    Returns
    -------
    int
        The stableswap invariant, `D`.
    Note
    ----
    This is a "view" function; it doesn't change the state of the pool.
    """  # noqa
    Dprev = 0
    S = sum(xp)
    D = S
    n = len(xp)
    Ann = A * n
    D = mpz(D)
    Ann = mpz(Ann)
    while abs(D - Dprev) > 1:
        D_P = D
        for x in xp:
            D_P = D_P * D // (n * x)
        Dprev = D
        D = (Ann * S + D_P * n) * D // ((Ann - 1) * D + (n + 1) * D_P)

    D = int(D)
    return D
