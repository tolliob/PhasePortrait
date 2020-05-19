##########################################################
# Module to define the Riemann Sphere complex numbers    #
#                                                        #
# Author: Olivier Bouillot                               #
# Email: olivier.bouillot@u-pem.fr                       #
# Creation Date: july 2017                               #
#                                                        #
# Modifications:                                         #
# --------------                                         #
#                                                        #
# 12/03/2020 Modifies docstring and doctest              #
#                                                        #
# Next modifications to do:                              #
# -------------------------                              #
#                                                        #
#                                                        #
##########################################################

from math import pi, ceil, log
from RiemannSphere import RiemannSphere


def approx(f):
    """ Approxime the float number f to the nearest integer

    :return value: the nearest integer of f

    >>> approx(2.1)
    2
    >>> approx(2.51)
    3
    >>> approx(-2.49)
    -2
    >>> approx(-2.51)
    -3
    >>> approx(2.5)
    2
    """
    if abs(f - int(f)) <= 1/2:
        return int(f)
    elif f >= 0:
        return int(f) + 1
    else:
        return int(f) - 1


def HSL(z):
    """ Compute the HSL, hue, saturation, lightness associated
    to the complex number z via the following bijection:

    hue = arg(self) + pi (en radian)
    saturation = 1
    lightness = ln(|self|) / ln(10) / (1 + |ln(|self|) / ln(10)|)

    :return value: a triplet composed by (hue, saturation, lightness)

    Warning : z can also be NaN or Inf, ie can also be a float...

    >>> from math import sqrt
    >>> epsilon = 0.01
    >>> hsl = HSL(RiemannSphere(1/2, sqrt(3)/2))
    >>> abs(hsl[0] - 60) <= epsilon
    True
    >>> abs(hsl[1] - 1) <= epsilon
    True
    >>> abs(hsl[2] - 0.5) <= epsilon
    True

    >>> hsl1 = HSL(RiemannSphere(1, 0))
    >>> hsl1[0] == 0 or hsl1[0] == 360
    True
    >>> abs(hsl1[1] - 1) <= epsilon
    True
    >>> abs(hsl1[2] - 1/2) <= epsilon
    True

    >>> hsl2 = HSL(RiemannSphere(1.92211, 1.92211))
    >>> hsl2[0] == 45
    True
    >>> abs(hsl2[1] - 1) <= epsilon
    True
    >>> abs(hsl2[2] - 3/4) <= epsilon
    True

    >>> hsl3 = HSL(RiemannSphere(-6.39911, 3.69453))
    >>> hsl3[0] == 150
    True
    >>> abs(hsl3[1] - 1) <= epsilon
    True
    >>> abs(hsl3[2] - 5/6) <= epsilon
    True

    >>> hsl4 = HSL(RiemannSphere(-0.1839397, -0.318593))
    >>> hsl4[0] == 240
    True
    >>> abs(hsl4[1] - 1) <= epsilon
    True
    >>> abs(hsl4[2] - 1/4) <= epsilon
    True

    >>> hsl5 = HSL(RiemannSphere(0.117204, -0.067668))
    >>> hsl5[0] == 330
    True
    >>> abs(hsl5[1] - 1) <= epsilon
    True
    >>> abs(hsl5[2] - 1/6) <= epsilon
    True

    >>> hsl6 = HSL(RiemannSphere(-1, 0))
    >>> hsl6[0] == 180
    True
    >>> abs(hsl6[1] - 1) <= epsilon
    True
    >>> abs(hsl6[2] - 1/2) <= epsilon
    True
    """
    if isinstance(z, RiemannSphere):
        if z.is_null():
            lightness = 0
            hue = 0
            saturation = 1
        elif z.is_infinite():
            lightness = 1
            hue = 0
            saturation = 1
        else:
            hue = z.argument() * 180 / pi
            if hue <= 0:
                hue += 360
            hue = approx(hue)
            saturation = 1
            r = abs(z)
            if r == 0:
                lightness = 0
            else:
                logarithm = log(r)
                lightness = (logarithm / (1 + abs(logarithm)) + 1) / 2
        return approx(hue), saturation, lightness
    else:
        raise ValueError("HSL ne s'applique que sur un complexe de la sphere" +
                         " de Riemann...")


def RGB(z):
    """ Compute the RGB components associated to the HLS components
        associated to the complex number z.

        The formulae are the foolwing, where 0 <= H < 360, 0 <= S, L <= 1
        :return value: a triplet composed by (R, G, B)

        Warning : z can also be NaN or Inf, ie can also be a float...

    >>> z1 = RiemannSphere(1, 0)
    >>> rgb_1 = RGB(z1)
    >>> rgb_1[0] == 255 and rgb_1[1] == 0 and rgb_1[2] == 0
    True

    >>> z2 = RiemannSphere(1.92211, 1.92211)
    >>> rgb_2 = RGB(z2)
    >>> rgb_2[0] == 255 and rgb_2[1] == 223 and rgb_2[2] == 127
    True

    >>> z3 = RiemannSphere(-6.39911, 3.69453)
    >>> rgb_3 = RGB(z3)
    >>> rgb_3[0] == 170 and rgb_3[1] == 255 and rgb_3[2] == 213
    True

    >>> z4 = RiemannSphere(-0.1839397, -0.318593)
    >>> rgb_4 = RGB(z4)
    >>> rgb_4[0] == 0 and rgb_4[1] == 0 and rgb_4[2] == 128
    True

    >>> z5 = RiemannSphere(0.117204, -0.067668)
    >>> rgb_5 = RGB(z5)
    >>> rgb_5[0] == 85 and rgb_5[1] == 0 and rgb_5[2] == 43
    True

    >>> z6 = RiemannSphere(-1, 0)
    >>> rgb_6 = RGB(z6)
    >>> rgb_6[0] == 0 and rgb_6[1] == 255 and rgb_6[2] == 255
    True
    """
    hue, saturation, lightness = HSL(z)
    C = (1 - abs(2 * lightness - 1)) * saturation
    hue_prime = hue / 60
    X = C * (1 - abs(hue_prime % 2 - 1))
    m = lightness - C/2
    if ceil(hue_prime) <= 1:
        r_tmp, g_tmp, b_tmp = C, X, 0
    elif ceil(hue_prime) == 2:
        r_tmp, g_tmp, b_tmp = X, C, 0
    elif ceil(hue_prime) == 3:
        r_tmp, g_tmp, b_tmp = 0, C, X
    elif ceil(hue_prime) == 4:
        r_tmp, g_tmp, b_tmp = 0, X, C
    elif ceil(hue_prime) == 5:
        r_tmp, g_tmp, b_tmp = X, 0, C
    elif ceil(hue_prime) == 6:
        r_tmp, g_tmp, b_tmp = C, 0, X
    else:
        print("Probleme at z = ", z, "H' = ", hue_prime)
        r_tmp, g_tmp, b_tmp = 0, 0, 0
    r = approx((r_tmp + m) * 255)
    g = approx((g_tmp + m) * 255)
    b = approx((b_tmp + m) * 255)
    return (r, g, b)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
