##########################################################
# Module to define special functions defined             #
# in a part of the complex plane, and valued in the      #
# complex plane                                          #
#                                                        #
# Author: Olivier Bouillot                               #
# Email: olivier.bouillot@u-pem.fr                       #
# Creation Date: march 2020                              #
#                                                        #
# Modifications:                                         #
# --------------                                         #
#                                                        #
# .                                                      #
#                                                        #
# Next modifications to do:                              #
# -------------------------                              #
#                                                        #
# .                                                      #
#                                                        #
##########################################################


from math import ceil, isinf
from math import pi
from math import sqrt, atan, log, exp, cos, sin
from RiemannSphere import RiemannSphere, INFTY

""" Module which defines some of the classical special functions :
* the identity map
* the complex square root map
* the complex cosinus and sinus map
* the Gamma function
* the Riemann Zeta function
"""


def id(z):
    """ Identity map

    :param z: RiemannSphere complex number
    :return value: RiemannSphere complex number

    >>> id(RiemannSphere(1, 1.2))
    1 + 1.2 i
    >>> id(INFTY)
    oo
    """
    return z


def complex_sqrt(z):
    """ Compute the principal branch of the square root map

    :param z: RiemannSphere complex number
    :return value: RiemannSphere complex number

    >>> complex_sqrt(RiemannSphere(0, 0))
    0
    >>> complex_sqrt(INFTY)
    oo
    >>> epsilon = 10e-8
    >>> z = complex_sqrt(RiemannSphere(1, 1))
    >>> th = RiemannSphere(sqrt(2 + sqrt(2)), sqrt(2 - sqrt(2)))
    >>> abs(z - sqrt(sqrt(2)) / 2 * th) <= epsilon
    True
    """
    r = abs(z)
    if isinf(r):
        return INFTY
    if r == 0:
        return RiemannSphere(0, 0)
    theta = z.argument()
    return sqrt(r) * RiemannSphere(cos(theta / 2), sin(theta / 2))


def complex_cos(z):
    """ Compute the complex cosinus map

    :param z: RiemannSphere complex number
    :return value: RiemannSphere complex number

    >>> complex_cos(RiemannSphere(0, 0))
    1.0
    >>> complex_cos(INFTY)
    oo
    >>> epsilon = 10e-8
    >>> z = complex_cos(RiemannSphere(1, 1))
    >>> abs(z.real - (exp(1) + exp(-1)) / 2 * cos(1)) <= epsilon
    True
    >>> abs(z.imaginary + (exp(1) - exp(-1)) / 2 * sin(1)) <= epsilon
    True
    >>> z.infinite
    False

    """
    II = RiemannSphere(0, 1)
    numerator = (II * z).complex_exp() + (- II * z).complex_exp()
    return numerator / 2


def complex_sin(z):
    """ Compute the complex sinus map

    :param z: RiemannSphere complex number
    :return value: RiemannSphere complex number

    >>> complex_sin(RiemannSphere(0, 0))
    0
    >>> complex_sin(INFTY)
    oo
    >>> epsilon = 10e-8
    >>> z = complex_sin(RiemannSphere(1, 1))
    >>> abs(z.real - (exp(1) + exp(-1)) / 2 * sin(1)) <= epsilon
    True
    >>> abs(z.imaginary - (exp(1) - exp(-1)) / 2 * cos(1)) <= epsilon
    True
    >>> z.infinite
    False
    """
    II = RiemannSphere(0, 1)
    numerator = (II * z).complex_exp() - (- II * z).complex_exp()
    return numerator / (2 * II)


def gamma(z, N=10):
    r""" Compute the gamma function, using the expansion
                                                 7
                                        -1/2   ____     g
                    -z    z    / 2 pi  \       \         k
        Gamma(z) ~ e   * z  * |  ----- |        |      ----   ,
                               \   z   /       /          k
                                               ----     z
                                               k = 0
    where g_0 = 1, g_1 = 1/12, g_2 = 1/288, ..., for Re z > 0.
    (See Formula 5.11.3 of https://dlmf.nist.gov/5.11#E3)

    To compute it on the whole complex space, we use:

    * N times the functionnal equation of the gamma function on the eastern
      part of the complex plane to accelerate the computation
                                    Gamma(z + n)
               Gamma(z) = -----------------------------------
                          (z + n - 1) * (z + n - 2) * ... * z

    * the reflexion equation Gamma(z) * Gamma(1 - z) = Pi / sin(Pi * z)
      on the western part of the complex plane


    :param z: int, float, or Riemann Sphere complex number
    :optional param N: int
    :return value: Riemann Sphere complex number, which is
                   an approximation of Gamma(z)


    >>> epsilon = 10e-8
    >>> pi = RiemannSphere(4 * atan(1), 0)

    Well-known values of the Riemann Zeta function :
    ------------------------------------------------

    >>> gamma(0)
    oo
    >>> abs(gamma(2) - 1) <= epsilon
    True
    >>> abs(gamma(4) - 6) <= epsilon
    True
    >>> abs(gamma(1/2) - sqrt(4 * atan(1))) <= 10e-8
    True
    >>> result = gamma(-1)
    >>> if result.is_infinite():
    ...     test = True
    ... else: # 1 / result should be approximatively null
    ...     # result.infinite is necessarily False
    ...     test = abs(1 / result) <= epsilon
    >>> test
    True

    Tests of the reflexion formula:
    -------------------------------

    >>> z = RiemannSphere(2, 1)
    >>> th_1 = RiemannSphere(.6529654964, 0.3430658398)
    >>> th_2 = RiemannSphere(-0.1715329199, -0.3264827482)
    >>> abs(gamma(z) - th_1) <= epsilon
    True
    >>> abs(gamma(1 - z) - th_2) <= epsilon
    True
    >>> abs(gamma(z) * gamma(1 - z) - pi / complex_sin(pi * z)) <= epsilon
    True
    """
    if isinstance(z, (int, float)):
        z = RiemannSphere(z, 0)
    g = [1, 1/12, 1/288, -139/51840, -571/2488320, 163879/209018880,
         5246819/75246796800]
    if z.real >= 1/2:
        z_tmp = z + N
        # Compute an approximation of Gamma(z + N)
        exponentielle = 1 / z_tmp.complex_exp()
        puissance = z_tmp ** z_tmp
        racine = complex_sqrt((2 * pi) / z_tmp)
        somme = 0
        z_k = 1
        for k in range(7):
            somme += g[k] / z_k
            z_k *= z_tmp
        approximation = exponentielle * puissance * racine * somme
        # Compute the denominator z (z + 1) ... (z + N - 1)
        denominateur = 1
        for i in range(N):
            denominateur *= z + i
        # Compute Gamma(z) = Gamma(z + N) / [z (z + 1) ... (z + N - 1)]
        return approximation / denominateur
    else:
        new_z = 1 - z
        value = gamma(new_z, N)
        s = complex_sin(pi * z)
        if s.is_null():
            return INFTY / value
        else:
            return pi / (s * value)


def zeta_in_NE_quadrant(s, d):
    """ Compute the value of the Riemann zeta function with d exact decimals
    at the complex point s such that Re s >= 1/2 and Im s >= 0, s != 1.

    The algorithm exposed in [1] is implemented here


    :param s: Riemann Sphere complex number
    :param d: int, which represents the number of wanted exact digits
    :Return value: Riemann Sphere complex number z such that:
                        |zeta(s, d) - z| <= 10^(-d)


    References:
    -----------
    [1] H. COHEN, M. OLIVIER,
        Calcul des valeurs de la fonction zêta de riemann en multiprécision.
        C.R. Acad. Sci., Paris Sér I Math., 314:427–430, 1992.

    >>> two_pi = RiemannSphere(8 * atan(1), 0)
    >>> half_pi = RiemannSphere(2 * atan(1), 0)
    >>> epsilon = 10e-8

    Well-known values of the Riemann Zeta function :
    ------------------------------------------------

    >>> z = RiemannSphere(2, 0)
    >>> result = RiemannSphere(1.6449340668482264365, 0)
    >>> abs(zeta_in_NE_quadrant(z, 10) - result) <= epsilon
    True
    >>> z = RiemannSphere(4, 0)
    >>> result = RiemannSphere(1.0823232337111381916, 0)
    >>> abs(zeta_in_NE_quadrant(z, 10) - result) <= epsilon
    True

    Others computed values:
    -----------------------

    >>> s = RiemannSphere(2, 1)
    >>> th = RiemannSphere(1.15035570325490267, -0.437530865919607881)
    >>> abs(zeta_in_NE_quadrant(s, 10) - th) <= epsilon
    True
    >>> s = RiemannSphere(0.5, 4)
    >>> th = RiemannSphere(0.606783764522437269, 0.0911121399725150297)
    >>> abs(zeta_in_NE_quadrant(s, 10) - th) <= epsilon
    True

    Tests of the first non-trivial zeros of the Riemann Zeta function:
    ------------------------------------------------------------------

    >>> epsilon = 10e-5
    >>> zeros = [RiemannSphere(0.5, 14.134725),
    ...          RiemannSphere(0.5, 21.022040),
    ...          RiemannSphere(0.5, 25.010856),
    ...          RiemannSphere(0.5, 30.424878),
    ...          RiemannSphere(0.5, 32.935057),
    ...          RiemannSphere(0.5, 37.586176),
    ...          RiemannSphere(0.5, 40.918720),
    ...          RiemannSphere(0.5, 43.327073),
    ...          RiemannSphere(0.5, 48.005150),
    ...          RiemannSphere(0.5, 49.773832)]
    >>> test = True
    >>> for zero in zeros:
    ...     test = test and abs(zeta_in_NE_quadrant(zero, 10)) <= epsilon
    >>> test
    True
    """
    u, t = s.real, s.imaginary

    # Initialisation
    D = d * log(10)
    if t == 0:
        beta = D + 0.61 + u * log(2 * pi / u)
        beta = D + 0.61 + u * log(2 * pi / u)
        if beta <= 0:
            p = 0
            N = ceil(exp(D / u) * exp(log(abs(s) / (2 * u)) / u))
        else:
            p = ceil(beta / 2)
            N = ceil(abs(s + 2 * p - 1) / (2 * pi))
    elif t > 0:
        alpha = D - 0.39 + u * log(2 * pi) - (u - 1) * log(abs(s)) - log(u)
        gamma = (alpha + u) / t - atan(u / t)
        if gamma <= 0:
            x_oo = 0
        else:
            # calcul de x_inf par la methode de Newton tel que
            # x_inf - arctan(x_inf) = gamma
            x_oo = 1
            for i in range(10):
                x_oo -= (x_oo - gamma - atan(x_oo)) / (1 - 1 / (1 + x_oo ** 2))
        if 1 - u + t * x_oo <= 0:
            p = 0
            exp_tmp = exp(log(abs(s) / (2 * u)) / u)
            N = ceil(exp(D / u) * exp_tmp)
        else:
            p = ceil((1 - u + t * x_oo) / 2)
            N = ceil(abs(s + 2 * p - 1) / (2 * pi))

    # Bernoulli (les 150 premiers)
    bernoulli = [1, -0.5, 0.16666666666666666, 0,
                 -0.03333333333333333, 0, 0.023809523809523808, 0,
                 -0.03333333333333333, 0, 0.07575757575757576, 0,
                 -0.2531135531135531, 0, 1.1666666666666667, 0,
                 -7.092156862745098, 0, 54.971177944862156, 0,
                 -529.1242424242424, 0, 6192.123188405797, 0,
                 -86580.25311355312, 0, 1425517.1666666667, 0,
                 -27298231.067816094, 0, 601580873.9006424, 0,
                 -15116315767.092157, 0, 429614643061.1667, 0,
                 -13711655205088.332, 0, 488332318973593.2, 0,
                 -1.9296579341940068e+16, 0, 8.416930475736826e+17, 0,
                 -4.0338071854059454e+19, 0, 2.1150748638081993e+21, 0,
                 -1.2086626522296526e+23, 0, 7.500866746076964e+24, 0,
                 -5.038778101481069e+26, 0, 3.6528776484818122e+28, 0,
                 -2.849876930245088e+30, 0, 2.3865427499683627e+32, 0,
                 -2.1399949257225335e+34, 0, 2.0500975723478097e+36, 0,
                 -2.093800591134638e+38, 0, 2.2752696488463515e+40, 0,
                 -2.6257710286239577e+42, 0, 3.212508210271803e+44, 0,
                 -4.159827816679471e+46, 0, 5.692069548203528e+48, 0,
                 -8.218362941978458e+50, 0, 1.2502904327166994e+53, 0,
                 -2.001558323324837e+55, 0, 3.3674982915364376e+57, 0,
                 -5.947097050313545e+59, 0, 1.1011910323627977e+62, 0,
                 -2.1355259545253502e+64, 0, 4.3328896986641194e+66, 0,
                 -9.188552824166933e+68, 0, 2.0346896776329074e+71, 0,
                 -4.700383395803573e+73, 0, 1.131804344548425e+76, 0,
                 -2.8382249570693707e+78, 0, 7.406424897967885e+80, 0,
                 -2.0096454802756605e+83, 0, 5.665717005080594e+85, 0,
                 -1.6584511154136216e+88, 0, 5.036885995049238e+90, 0,
                 -1.5861468237658186e+93, 0, 5.1756743617545625e+95, 0,
                 -1.7488921840217116e+98, 0, 6.116051999495218e+100, 0,
                 -2.2122776912707833e+103, 0, 8.272277679877097e+105, 0,
                 -3.195892511141571e+108, 0, 1.2750082223387793e+111, 0,
                 -5.250092308677413e+113, 0, 2.2301817894241627e+116, 0,
                 -9.76845219309552e+118, 0, 4.409836197845295e+121, 0,
                 -2.050857088646409e+124, 0, 9.821443327979128e+126, 0,
                 -4.841260079820888e+129, 0, 2.4553088801480982e+132, 0,
                 -1.2806926804084748e+135, 0, 6.867616710466858e+137, 0,
                 -3.7846468581969106e+140, 0]

    # Boucle
    sum = RiemannSphere(0, 0)
    for k in range(1, N + 1):
        sum += 1 / k ** s
    tmp_1 = 1 / N ** (s - 1)
    tmp_2 = 1 / (s - 1)
    sum += tmp_1 * tmp_2
    sum += (-1 / 2) * 1 / N ** s
    prod = s
    factorial = 2
    power = N ** (s + 1)
    terme = bernoulli[2] / factorial * prod / power
    sum += terme
    for k in range(2, p + 1):
        prod *= (s + 2 * k - 3) * (s + 2 * k - 2)
        factorial *= (2 * k - 1) * 2 * k
        power = 1 / N ** (s + 2 * k - 1)
        terme = bernoulli[2 * k] / factorial * prod * power
        sum += terme
    return sum


def zeta(s, d=10):
    """ Compute the value of the Riemann zeta function at the complex point s
    with d exact decimals.


    First, we reduce the cases such that Re(s) > 1/2 and Im(s) >= 0:

    * if the real part is lower than 1/2, then we use the reflexion formula
    for the zeta function (See Formula 25.4.1 of https://dlmf.nist.gov/25.4)
    * If the imaginary part is negative, then we use conjugaison:
                                     _______        _
                                     zeta(s) = zeta(s).
    * If s == 1, then the result is the infinite RiemannShpere complex number

    Then, the algorithm exposed in [1] is implemented in the function call
    computation(s, d).


    :param s: int, float or Riemann Sphere complex number
    :param d: int, which represents the number of wanted exact digits
    :Return value: Riemann Sphere complex number z such that:
                          |zeta(s, d) - z| <= 10^(-d)


    References:
    -----------
    [1] H. COHEN, M. OLIVIER,
        Calcul des valeurs de la fonction zêta de riemann en multiprécision.
        C.R. Acad. Sci., Paris Sér I Math., 314:427–430, 1992.


    >>> two_pi = RiemannSphere(8 * atan(1), 0)
    >>> half_pi = RiemannSphere(2 * atan(1), 0)
    >>> epsilon = 10e-8

    Well-known values of the Riemann Zeta function :
    ------------------------------------------------

    >>> abs(zeta(2) - 1.6449340668482264365) <= epsilon
    True
    >>> abs(zeta(4) - 1.0823232337111381916) <= epsilon
    True
    >>> abs(zeta(0) + 1 / 2) <= epsilon
    True
    >>> abs(zeta(-2)) <= epsilon
    True
    >>> abs(zeta(-4)) <= epsilon
    True
    >>> zeta(1) == INFTY
    True

    Tests of the reflexion formula, as long as the symetry along Im s = 0:
    ----------------------------------------------------------------------

    >>> s = RiemannSphere(2, 1)
    >>> th_1 = RiemannSphere(1.15035570325490267, -0.437530865919607881)
    >>> th_2 = RiemannSphere(0.016876151788174814, 0.11415648043238475)
    >>> abs(zeta(s) - th_1) <= epsilon
    True
    >>> abs(zeta(1 - s) - th_2) <= epsilon
    True
    >>> chi = 2 * complex_cos(half_pi * s) / (2 * pi) ** s * gamma(s)
    >>> abs(zeta(1 - s) - chi * zeta(s)) <= epsilon
    True

    >>> s = RiemannSphere(0.5, 4)
    >>> th_1 = RiemannSphere(0.60678376452243726, 0.091112139972515029)
    >>> th_2 = RiemannSphere(0.60678376452243726, -0.091112139972515029)
    >>> abs(zeta(s) - th_1) <= epsilon
    True
    >>> abs(zeta(1 - s) - th_2) <= epsilon
    True
    >>> zeta(s).real == zeta(1 - s).real
    True
    >>> zeta(s).imaginary + zeta(1 - s).imaginary
    0.0
    >>> chi = 2 * complex_cos(half_pi * s) / (2 * pi) ** s * gamma(s)
    >>> abs(zeta(1 - s) - chi * zeta(s)) <= epsilon
    True

    Tests of the first non-trivial zeros of the Riemann Zeta function:
    ------------------------------------------------------------------

    >>> epsilon = 10e-5
    >>> abs(zeta(RiemannSphere(0.5, 14.134725))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 21.022040))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 25.010856))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 30.424878))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 32.935057))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 37.586176))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 40.918720))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 43.327073))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 48.005150))) <= epsilon
    True
    >>> abs(zeta(RiemannSphere(0.5, 49.773832))) <= epsilon
    True
    """
    N = 10  # translation used in gamma computation
    if isinstance(s, (int, float)):
        s = RiemannSphere(s, 0)
    t = s.imaginary
    if s.real < 1/2:
        deux_puiss_s = 2 ** s
        gamma_un_moins_s = gamma(1 - s, N)
        zeta_un_moins_s = zeta(1 - s, d)
        sin_pi_s_sur_2 = complex_sin(s * (pi / 2))
        pi_puiss_s_moins_1 = pi ** (s - 1)
        try:
            return deux_puiss_s * pi_puiss_s_moins_1 * sin_pi_s_sur_2 \
                   * gamma_un_moins_s * zeta_un_moins_s
        except ValueError as excpt:
            if s.is_null():
                return RiemannSphere(-1/2, 0)
            print("WARNING : s = ", s, " : ", excpt, " => Mis a 0")
            return RiemannSphere(0, 0)
    if t < 0:
        return zeta(s.conjugate(), d).conjugate()
    else:
        if s.is_infinite():
            return RiemannSphere(0, 0)
        elif (s - 1).is_null():
            return INFTY
        else:
            return zeta_in_NE_quadrant(s, d)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
