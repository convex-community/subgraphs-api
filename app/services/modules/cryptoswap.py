from typing import List

A_MULTIPLIER = 10000


def _geometric_mean(unsorted_x, sort=True):
    """
    (x[0] * x[1] * ...) ** (1/N)
    """
    n = len(unsorted_x)
    x = unsorted_x
    if sort:
        x = sorted(x)
    D = x[0]
    for i in range(255):
        D_prev = D
        tmp = 10**18
        for _x in x:
            tmp = tmp * _x / D
        D = D * ((n - 1) * 10**18 + tmp) / (n * 10**18)
        if D > D_prev:
            diff = D - D_prev
        else:
            diff = D_prev - D
        if diff <= 1 or diff * 10**18 < D:
            return D
    return 0


def get_crypto_d(ANN, gamma, x_unsorted):
    n = len(x_unsorted)
    # Initial value of invariant D is that for constant-product invariant
    x = sorted(x_unsorted)

    D = n * _geometric_mean(x, False)
    S = 0
    for x_i in x:
        S += x_i

    for i in range(255):
        D_prev = D

        K0 = 10**18
        for _x in x:
            K0 = K0 * _x * n / D

        _g1k0 = gamma + 10**18
        if _g1k0 > K0:
            _g1k0 = _g1k0 - K0 + 1
        else:
            _g1k0 = K0 - _g1k0 + 1

        # D / (A * N**N) * _g1k0**2 / gamma**2
        mul1 = (
            10**18 * D / gamma * _g1k0 / gamma * _g1k0 * A_MULTIPLIER / ANN
        )

        # 2*N*K0 / _g1k0
        mul2 = (2 * 10**18) * n * K0 / _g1k0

        neg_fprime = (
            (S + S * mul2 / 10**18) + mul1 * n / K0 - mul2 * D / 10**18
        )

        # D -= f / fprime
        D_plus = D * (neg_fprime + S) / neg_fprime
        D_minus = D * D / neg_fprime
        if 10**18 > K0:
            D_minus += (
                D * (mul1 / neg_fprime) / 10**18 * (10**18 - K0) / K0
            )
        else:
            D_minus -= (
                D * (mul1 / neg_fprime) / 10**18 * (K0 - 10**18) / K0
            )

        if D_plus > D_minus:
            D = D_plus - D_minus
        else:
            D = (D_minus - D_plus) / 2

        diff = 0
        if D > D_prev:
            diff = D - D_prev
        else:
            diff = D_prev - D
        if diff * 10**14 < max(
            10**16, D
        ):  # Could reduce precision for gas efficiency here
            # Test that we are safe with the next newton_y
            for _x in x:
                frac = _x * 10**18 / D
                assert (frac > 10**16 - 1) and (
                    frac < 10**20 + 1
                )  # dev: unsafe values x[i]
            return D


def get_crypto_y(ANN, gamma, x, D, i):
    """
    Calculating x[i] given other balances x[0..N_COINS-1] and invariant D
    ANN = A * N**N
    """
    n = len(x)
    y = D / n
    K0_i = 10**18
    S_i = 0

    x_sorted: List[int] = x
    x_sorted[i] = 0
    x_sorted = sorted(x_sorted)  # From high to low

    convergence_limit = max(max(x_sorted[0] / 10**14, D / 10**14), 100)
    for j in range(2, n + 1):
        _x = x_sorted[n - j]
        y = y * D / (_x * n)  # Small _x first
        S_i += _x
    for j in range(n - 1):
        K0_i = K0_i * x_sorted[j] * n / D  # Large _x first

    for j in range(255):
        y_prev = y

        K0 = K0_i * y * n / D
        S = S_i + y

        _g1k0: int = gamma + 10**18
        if _g1k0 > K0:
            _g1k0 = _g1k0 - K0 + 1
        else:
            _g1k0 = K0 - _g1k0 + 1

        # D / (A * N**N) * _g1k0**2 / gamma**2
        mul1 = (
            10**18 * D / gamma * _g1k0 / gamma * _g1k0 * A_MULTIPLIER / ANN
        )

        # 2*K0 / _g1k0
        mul2 = 10**18 + (2 * 10**18) * K0 / _g1k0

        yfprime = 10**18 * y + S * mul2 + mul1
        _dyfprime = D * mul2
        if yfprime < _dyfprime:
            y = y_prev / 2
            continue
        else:
            yfprime -= _dyfprime
        fprime: int = yfprime / y

        # y -= f / f_prime;  y = (y * fprime - f) / fprime
        # y = (yfprime + 10**18 * D - 10**18 * S) // fprime + mul1 // fprime * (10**18 - K0) // K0
        y_minus = mul1 / fprime
        y_plus = (yfprime + 10**18 * D) / fprime + y_minus * 10**18 / K0
        y_minus += 10**18 * S / fprime

        if y_plus < y_minus:
            y = y_prev / 2
        else:
            y = y_plus - y_minus

        diff = 0
        if y > y_prev:
            diff = y - y_prev
        else:
            diff = y_prev - y
        if diff < max(convergence_limit, y / 10**14):
            frac = y * 10**18 / D
            assert (frac > 10**16 - 1) and (
                frac < 10**20 + 1
            )  # dev: unsafe value for y
            return y
