###########################################################
# Module to define the Riemann Sphere complex numbers     #
#                                                         #
# Author: Olivier Bouillot                                #
# Email: olivier.bouillot@u-pem.fr                        #
# Creation Date: july 2017                                #
#                                                         #
# Modifications:                                          #
# --------------                                          #
#                                                         #
# 03/2020    Modifies docstring and doctest               #
#            Emulates numeric types                       #
# 04/04/20   Take into account pylava warnings            #
# 17/04/20   The flag infinite becomes optionnal          #
# 10/07/20   Allow instanciation with Fraction components #
#                                                         #
# Next modifications to do:                               #
# -------------------------                               #
#                                                         #
#   * Add doctests                                        #
#   * Explicit some part of the doc                       #
#                                                         #
###########################################################


from math import sqrt, atan, exp, log, cos, sin, pi
from math import isnan, isinf
from fractions import Fraction


""" Module which defines:
* the RiemanSphere class.
* a constant INFTY which defines the infinite Riemann sphere complex number
"""


class RiemannSphere(object):
    """ Class that basically modelizes a complex number on the Riemann sphere.
    The main difference with the complex plan is that a RiemannSphere complex
    number can be infinite.

    :attribute real: int, float, Fraction, NaN
    :attribute imaginary: int float, Fraction, NaN
    :attribute infinite: boolean

    When initialized a RiemannSphere complex number is one of the following
    forms:
    * int/float/Fraction, int/float/Fraction, False   <->   standart RiemannSphere complex number
    * NaN, NaN, True                                  <->   infinite RiemannSphere complex number

    If the usual operations can not be perform on RiemannSphere complex
    numbers, because of an infinite RiemannSphere complex number,
    a ValueError is raised.

    Note that the infinity RiemannSphere instance of a complex number is
    unsigned. So z - oo = oo for all complex z.
    """

    def __init__(self, real, imaginary, infinite=False):
        """ Constructor of the class

        When initialized, we check that the module of the RiemannSphere
        complex number is not too big (i.e. the modulus is Inf):
        * if it is not too big, the complex number is given by its cartesian
        representation ; its attribute infinite is then defined to False.
        * if it is too big, the complex number has its cartesion coordinates
        initialised to float('NaN') and its attribute infinite set to True.

        :param real: represents the real part of the complex number
        :param imaginary: represents the imaginary part of the complex number
        :param infinite: represents a boolean which tells us if
                         the current complex number will be infinite or not

        :raised error: TypeError when the following equivalence is not
                       satisfied:

                               the parameter 'infinite' is true, if,
                               and only if, the parameters 'real' and
                               'imaginary' are equals to float('NaN')

        >>> z = RiemannSphere(1, 1)
        >>> z = RiemannSphere(1, 1.2)
        >>> z = RiemannSphere(1.2, 1)

        >>> z = RiemannSphere(float('Inf'), float('Inf'), infinite=True)
        Traceback (most recent call last):
            ...
        ValueError: A complex number is infinite if its components are NaN...

        >>> z = RiemannSphere(0, 0, infinite=True)
        Traceback (most recent call last):
            ...
        ValueError: A complex number is infinite if its components are NaN...

        >>> z = RiemannSphere(float('NaN'), 0, infinite=True)
        Traceback (most recent call last):
            ...
        ValueError: A complex number is infinite if its components are NaN...

        >>> z = RiemannSphere(float('NaN'), 0)
        Traceback (most recent call last):
            ...
        ValueError: A complex number with a NaN component has to be infinite!

        >>> z = RiemannSphere('NaN', 0)
        Traceback (most recent call last):
            ...
        TypeError: Components of RiemannSphere instance are integers or floats

        >>> z = RiemannSphere(10e+153, 10e+153)
        >>> isnan(z.real) and isnan(z.imaginary) and z.infinite
        True
        """
        if infinite:
            if not isnan(real) or not isnan(imaginary):
                raise ValueError("A complex number is infinite if " +
                                 "its components are NaN...")
            self.real = float('NaN')
            self.imaginary = float('NaN')
            self.infinite = True
        else:
            if not isinstance(real, (int, float, Fraction)) or \
                    not isinstance(imaginary, (int, float, Fraction)):
                raise TypeError("Components of RiemannSphere instance are " +
                                "integers, floats or Fractions")
            if isnan(real) or isnan(imaginary):
                raise ValueError("A complex number with a NaN component has " +
                                 "to be infinite!")
            try:
                m = real**2 + imaginary**2
                if isinf(m):
                    raise OverflowError("Too big modulus")
                else:
                    self.real = real
                    self.imaginary = imaginary
                    self.infinite = False
            except OverflowError:
                self.real = float('NaN')
                self.imaginary = float('NaN')
                self.infinite = True

    def __repr__(self):
        """ Transform the current complex number into a string
        The infinite RiemannSphere complex number is denoted 'oo'

        :Return value: String

        >>> INFTY
        oo
        >>> RiemannSphere(0, 0)
        0
        >>> RiemannSphere(0, 1)
        i
        >>> RiemannSphere(0, -1)
        -i
        >>> RiemannSphere(3.2, 0)
        3.2
        >>> RiemannSphere(0, 0.01)
        0.01 i
        >>> RiemannSphere(0, -0.01)
        -0.01 i
        >>> RiemannSphere(-3.2, 0)
        -3.2
        >>> RiemannSphere(3.2, 2.7)
        3.2 + 2.7 i
        >>> RiemannSphere(-3.2, 2.7)
        -3.2 + 2.7 i
        >>> RiemannSphere(3.2, -2.7)
        3.2 - 2.7 i
        >>> RiemannSphere(-3.2, -2.7)
        -3.2 - 2.7 i
        """
        if self.infinite:
            return "oo"
        if self.real == 0:
            if self.imaginary == 0:
                return "0"
            elif self.imaginary == 1:
                return "i"
            elif self.imaginary == -1:
                return "-i"
            else:
                return str(self.imaginary) + ' i'
        else:
            if self.imaginary == 0:
                return str(self.real)
            else:
                if self.imaginary > 0:
                    return str(self.real) + ' + ' + str(self.imaginary) + ' i'
                else:
                    return str(self.real) + ' - ' + str(-self.imaginary) + ' i'

    def __str__(self):
        """ Transform the current complex number into a string
        The infinite RiemannSphere complex number is denoted 'oo'

        :Return value: String

        >>> INFTY
        oo
        >>> RiemannSphere(0, 0)
        0
        >>> RiemannSphere(0, 1)
        i
        >>> RiemannSphere(3.2, 0)
        3.2
        >>> RiemannSphere(0, 0.01)
        0.01 i
        >>> RiemannSphere(0, -0.01)
        -0.01 i
        >>> RiemannSphere(-3.2, 0)
        -3.2
        >>> RiemannSphere(3.2, 2.7)
        3.2 + 2.7 i
        >>> RiemannSphere(-3.2, 2.7)
        -3.2 + 2.7 i
        >>> RiemannSphere(3.2, -2.7)
        3.2 - 2.7 i
        >>> RiemannSphere(-3.2, -2.7)
        -3.2 - 2.7 i
        """
        return self.__repr__()

    def __hash__(self):
        return int((self.real + self.imaginary) * 1000)

    def __eq__(self, other):
        """ Check the equality of the current RiemannSphere complex number
        with an other object

        :Return value: boolean

        >>> RiemannSphere(0, 0) == RiemannSphere(0, 0)
        True
        >>> RiemannSphere(0, 0) == RiemannSphere(1, 2)
        False
        >>> RiemannSphere(1, 2) == RiemannSphere(1, 2)
        True
        >>> zero = RiemannSphere(0, 0)
        >>> zero_copy = zero
        >>> zero == zero_copy
        True
        >>> INFTY == INFTY
        True
        """
        if isinstance(other, RiemannSphere):
            if self.is_infinite():
                return other.is_infinite()
            return self.real == other.real \
                and self.imaginary == other.imaginary \
                and self.infinite == other.infinite
        else:
            return False

    def __neq__(self, other):
        """ Check the non equality of the current RiemannSphere complex number
        with an other object

        :Return value: boolean

        >>> RiemannSphere(0, 0) != RiemannSphere(0, 0)
        False
        >>> RiemannSphere(0, 0) != RiemannSphere(1, 2)
        True
        >>> RiemannSphere(1, 2) != RiemannSphere(1, 2)
        False
        >>> zero = RiemannSphere(0, 0)
        >>> zero_copy = zero
        >>> zero != zero_copy
        False
        >>> INFTY != INFTY
        False
        """
        if isinstance(other, RiemannSphere):
            if self.is_infinite():
                return not other.is_infinite()
            return self.real != other.real \
                or self.imaginary != other.imaginary \
                or self.infinite != other.infinite
        else:
            return True

    def is_null(self):
        """ Check if the current RiemannSphere complex number is null or not

        :Return value: boolean

        >>> a = RiemannSphere(0, 0)
        >>> b = RiemannSphere(1, 2)
        >>> c = a
        >>> a.is_null()
        True
        >>> b.is_null()
        False
        >>> c.is_null()
        True
        >>> INFTY.is_null()
        False
        """
        return not self.infinite and self.real == 0 and self.imaginary == 0

    def is_infinite(self):
        """ Check if the current RiemannSphere complex number is null or not

        :Return value: boolean

        >>> a = RiemannSphere(0, 0)
        >>> b = RiemannSphere(1, 2)
        >>> c = RiemannSphere(float('NaN'), float('NaN'), infinite=True)
        >>> d = a
        >>> e = c
        >>> a.is_infinite()
        False
        >>> b.is_infinite()
        False
        >>> c.is_infinite()
        True
        >>> d.is_infinite()
        False
        >>> e.is_infinite()
        True
        """
        return self.infinite

    def __add__(self, other):
        """ Compute the addition of the current RiemannSphere complex number
        by an other one.

        For all complex z, oo + z = oo.

        :raised error: TypeError when 'other' is not of RiemannSphere type,
                       or integers and floats.

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> r = RiemannSphere(3.2, -3.2)
        >>> s = RiemannSphere(2.4, 2.8)
        >>> t = RiemannSphere(0, 0)
        >>> n = 3
        >>> f = 2.3

        >>> sum = r + s
        >>> sum_2 = s + r
        >>> sum == sum_2
        True
        >>> abs(sum.real - 5.6) <= epsilon
        True
        >>> abs(sum.imaginary + 0.4) <= epsilon
        True
        >>> sum.infinite
        False

        >>> r + t == r
        True
        >>> r + t == t + r
        True

        >>> r + INFTY == INFTY
        True
        >>> r + INFTY == INFTY + r
        True
        >>> INFTY + n == INFTY
        True
        >>> INFTY + f == INFTY
        True

        >>> sum = r + n
        >>> abs(sum.real - 6.2) <= epsilon
        True
        >>> abs(sum.imaginary + 3.2) <= epsilon
        True
        >>> sum.infinite
        False

        >>> sum = r + f
        >>> abs(sum.real - 5.5) <= epsilon
        True
        >>> abs(sum.imaginary + 3.2) <= epsilon
        True
        >>> sum.infinite
        False

        >>> r + 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        >>> INFTY + 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        """
        if self.is_infinite():
            if isinstance(other, (int, float, RiemannSphere)):
                return INFTY
            else:
                raise TypeError("Only RiemannSphere, integers or floats " +
                                "can be added to a RiemannSphere")
        if isinstance(other, RiemannSphere):
            if other.is_infinite():
                return INFTY
            else:
                return RiemannSphere(self.real+other.real,
                                     self.imaginary+other.imaginary)
        elif isinstance(other, (int, float)):
            return RiemannSphere(self.real + other, self.imaginary)
        else:
            raise TypeError("Only RiemannSphere, integers or floats " +
                            "can be added to a RiemannSphere")

    def __radd__(self, other):
        """ Compute the addition of an other number with the current
        RiemannSphere complex number.

        For all complex z, oo + z = oo.

        :raised error: TypeError when 'other' is not of RiemannSphere type,
                       or integers and floats.

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> r = RiemannSphere(3.2, -3.2)
        >>> s = RiemannSphere(2.4, 2.8)
        >>> t = RiemannSphere(0, 0)
        >>> n = 3
        >>> f = 2.3

        >>> sum = r + s
        >>> sum_2 = s + r
        >>> sum == sum_2
        True
        >>> abs(sum.real - 5.6) <= epsilon
        True
        >>> abs(sum.imaginary + 0.4) <= epsilon
        True
        >>> sum.infinite
        False

        >>> r + t == r
        True
        >>> r + t == t + r
        True

        >>> r + INFTY == INFTY
        True
        >>> r + INFTY == INFTY + r
        True

        >>> sum = n + r
        >>> abs(sum.real - 6.2) <= epsilon
        True
        >>> abs(sum.imaginary + 3.2) <= epsilon
        True
        >>> sum.infinite
        False

        >>> sum = f + r
        >>> abs(sum.real - 5.5) <= epsilon
        True
        >>> abs(sum.imaginary + 3.2) <= epsilon
        True
        >>> sum.infinite
        False

        >>> r + 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        >>> INFTY + 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        """
        if self.is_infinite():
            if isinstance(other, (int, float, RiemannSphere)):
                return INFTY
            else:
                raise TypeError("Only RiemannSphere, integers or floats " +
                                "can be added to a RiemannSphere")
        if isinstance(other, RiemannSphere):
            if other.is_infinite():
                return INFTY
            else:
                return RiemannSphere(self.real+other.real,
                                     self.imaginary+other.imaginary)
        elif isinstance(other, (int, float)):
            return RiemannSphere(self.real + other, self.imaginary)
        else:
            raise TypeError("Only RiemannSphere, integers or floats " +
                            "can be added to a RiemannSphere")

    def __sub__(self, other):
        """ Compute the substraction of the current RiemannSphere
        complex number by an other one

        For all complex z, oo - z = oo and z - oo = oo

        :raised error: TypeError when 'other' is not of Complex type,
                       integers or floats.

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> r = RiemannSphere(3.2, -3.2)
        >>> s = RiemannSphere(2.4, 2.8)
        >>> t = RiemannSphere(0, 0)
        >>> n = 3
        >>> f = 2.3

        >>> result = r - s
        >>> abs(result.real - .8) <= epsilon
        True
        >>> abs(result.imaginary + 6) <= epsilon
        True
        >>> result.infinite
        False

        >>> r - t == r
        True

        >>> r - INFTY == INFTY
        True
        >>> INFTY - n == INFTY
        True
        >>> INFTY - f == INFTY
        True

        >>> result = r - n
        >>> abs(result.real - .2) <= epsilon
        True
        >>> abs(result.imaginary + 3.2) <= epsilon
        True
        >>> result.infinite
        False

        >>> result = r - f
        >>> abs(result.real - .9) <= epsilon
        True
        >>> abs(result.imaginary + 3.2) <= epsilon
        True
        >>> result.infinite
        False

        >>> r - 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        >>> INFTY - 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        """
        if self.is_infinite():
            if isinstance(other, (int, float, RiemannSphere)):
                return INFTY
            else:
                raise TypeError("Only RiemannSphere, integers or floats " +
                                "can be substracted to a RiemannSphere")
        if isinstance(other, RiemannSphere):
            if other.is_infinite():
                return INFTY
            else:
                return RiemannSphere(self.real - other.real,
                                     self.imaginary - other.imaginary)
        elif isinstance(other, (int, float)):
            return RiemannSphere(self.real - other, self.imaginary)
        else:
            raise TypeError("Only RiemannSphere, integers or floats " +
                            "can be substracted to a RiemannSphere")

    def __rsub__(self, other):
        """ Compute the substraction of an other RiemannSphere number,
        an integer or a float by the current RiemannSphere complex number

        For all complex z, oo - z = oo and z - oo = oo

        :raised error: TypeError when 'other' is not of Complex type,
                       integers or floats.

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> z = RiemannSphere(3.2, -3.2)
        >>> n = 3
        >>> f = 2.3

        >>> n - INFTY
        oo
        >>> f - INFTY
        oo

        >>> result = n - z
        >>> abs(result.real + .2) <= epsilon
        True
        >>> abs(result.imaginary - 3.2) <= epsilon
        True
        >>> result.infinite
        False

        >>> result = f - z
        >>> abs(result.real + .9) <= epsilon
        True
        >>> abs(result.imaginary - 3.2) <= epsilon
        True
        >>> result.infinite
        False

        >>> 1j - z
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        >>> 1j - INFTY
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        """
        if self.is_infinite():
            if isinstance(other, (int, float, RiemannSphere)):
                return INFTY
            else:
                raise TypeError("Only RiemannSphere, integers or floats " +
                                "can be substracted to a RiemannSphere")
        if isinstance(other, RiemannSphere):
            if other.is_infinite():
                return INFTY
            else:
                return RiemannSphere(other.real - self.real,
                                     other.imaginary - self.imaginary)
        elif isinstance(other, (int, float)):
            return RiemannSphere(other - self.real, - self.imaginary)
        else:
            raise TypeError("Only RiemannSphere, integers or floats " +
                            "can be substracted to a RiemannSphere")

    def __mul__(self, other):
        """ Compute the multiplication of the current RiemannSphere
        complex number by an other one, a float or an integer.

        For all non zero complex number z, oo * z = oo
        Moreover, oo * oo = oo

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the multiplcation 0 * oo is performed,
                         because it is not well-defined

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> r = RiemannSphere(3.2, -3.2)
        >>> s = RiemannSphere(2.4, 2.8)
        >>> t = RiemannSphere(0, 0)

        >>> product = RiemannSphere(16.64, 1.28)
        >>> result = r * s
        >>> result_2 = s * r
        >>> result == result_2
        True
        >>> abs(product.real - result.real) <= epsilon
        True
        >>> abs(product.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False

        >>> product = RiemannSphere(0, 0)
        >>> result = r * t
        >>> result_2 = t * r
        >>> result == result_2
        True
        >>> abs(product.real - result.real) <= epsilon
        True
        >>> abs(product.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False

        >>> result = r * INFTY
        >>> result_2 = INFTY * r
        >>> result == result_2
        True
        >>> isnan(result.real)
        True
        >>> isnan(result.imaginary)
        True
        >>> result.infinite
        True

        >>> result = r * 2
        >>> abs(result.real - 6.4) <= epsilon
        True
        >>> abs(result.imaginary + 6.4 ) <= epsilon
        True
        >>> result.infinite
        False

        >>> result = r * 3.2
        >>> abs(result.real - 10.24) <= epsilon
        True
        >>> abs(result.imaginary + 10.24 ) <= epsilon
        True
        >>> result.infinite
        False

        >>> r * 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        >>> INFTY * 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere

        >>> t * INFTY
        Traceback (most recent call last):
            ...
        ValueError: 0 x oo is not defined!
        >>> INFTY * t
        Traceback (most recent call last):
            ...
        ValueError: oo x 0 is not defined!
        >>> INFTY * 0
        Traceback (most recent call last):
            ...
        ValueError: oo x 0 is not defined!
        """
        if self.is_infinite():
            if not isinstance(other, (int, float, RiemannSphere)):
                raise TypeError("Only RiemannSphere, integers or floats " +
                                "can be multiplied by a RiemannSphere")
            if (isinstance(other, RiemannSphere) and other.is_null()) \
                    or other == 0:
                raise ValueError(str(self) + " x " + str(other) +
                                 " is not defined!")
            else:
                return INFTY
        if isinstance(other, RiemannSphere):
            if other.is_infinite():
                if self.is_null():
                    raise ValueError(str(self) + " x " + str(other) +
                                     " is not defined!")
                else:
                    return INFTY
            real = self.real * other.real - self.imaginary * other.imaginary
            imag = self.real * other.imaginary + self.imaginary * other.real
            return RiemannSphere(real, imag)
        elif isinstance(other, (int, float)):
            return RiemannSphere(self.real * other,
                                 self.imaginary * other)
        else:
            raise TypeError("Only RiemannSphere, integers or floats " +
                            "can be multiplied by a RiemannSphere")

    def __rmul__(self, other):
        """ Compute the multiplication of the current RiemannSphere
        complex number by an other one, a float or an integer.

        For all non zero complex number z, oo * z = oo
        Moreover, oo * oo = oo

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the multiplcation 0 * oo is performed,
                         because it is not well-defined

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> r = RiemannSphere(3.2, -3.2)
        >>> s = RiemannSphere(2.4, 2.8)
        >>> t = RiemannSphere(0, 0)

        >>> product = RiemannSphere(16.64, 1.28)
        >>> result = r * s
        >>> result_2 = s * r
        >>> result == result_2
        True
        >>> abs(product.real - result.real) <= epsilon
        True
        >>> abs(product.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False

        >>> product = RiemannSphere(0, 0)
        >>> result = r * t
        >>> result_2 = t * r
        >>> result == result_2
        True
        >>> abs(product.real - result.real) <= epsilon
        True
        >>> abs(product.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False

        >>> result = r * INFTY
        >>> result_2 = INFTY * r
        >>> result == result_2
        True
        >>> isnan(result.real)
        True
        >>> isnan(result.imaginary)
        True
        >>> result.infinite
        True

        >>> result = 2 * r
        >>> abs(result.real - 6.4) <= epsilon
        True
        >>> abs(result.imaginary + 6.4 ) <= epsilon
        True
        >>> result.infinite
        False

        >>> result = 3.2 * r
        >>> abs(result.real - 10.24) <= epsilon
        True
        >>> abs(result.imaginary + 10.24 ) <= epsilon
        True
        >>> result.infinite
        False

        >>> 1j * r
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere
        >>> 1j * INFTY
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only RiemannSphere, integers or floats ... a RiemannSphere

        >>> t * INFTY
        Traceback (most recent call last):
            ...
        ValueError: 0 x oo is not defined!
        >>> INFTY * t
        Traceback (most recent call last):
            ...
        ValueError: oo x 0 is not defined!
        >>> INFTY * 0
        Traceback (most recent call last):
            ...
        ValueError: oo x 0 is not defined!
        """
        if self.is_infinite():
            if not isinstance(other, (int, float, RiemannSphere)):
                raise TypeError("Only RiemannSphere, integers or floats " +
                                "can be multiplied by a RiemannSphere")
            if (isinstance(other, RiemannSphere) and other.is_null()) \
                    or other == 0:
                raise ValueError(str(self) + " x " + str(other) +
                                 " is not defined!")
            else:
                return INFTY
        if isinstance(other, RiemannSphere):
            if other.is_infinite():
                if self.is_null():
                    raise ValueError(str(self) + " x " + str(other) +
                                     " is not defined!")
                else:
                    return INFTY
            real = self.real * other.real - self.imaginary * other.imaginary
            imag = self.real * other.imaginary + self.imaginary * other.real
            return RiemannSphere(real, imag)
        elif isinstance(other, (int, float)):
            return RiemannSphere(self.real * other,
                                 self.imaginary * other)
        else:
            raise TypeError("Only RiemannSphere, integers or floats " +
                            "can be multiplied by a RiemannSphere")

    def __matmul__(self, other):
        raise NotImplementedError

    def __rmatmul__(self, other):
        raise NotImplementedError

    def inverse(self):
        """ Compute the inverse of the current RiemannSphere
        complex number.

        If z = oo, 1 / z = 0
        If z = 0, 1 / z = oo

        Remark : If the current RiemannSphere complex number is
                 too small, its inverse will be infinite...

        :Return value: RiemannSphere

        >>> epsilon = 0.01
        >>> r = RiemannSphere(3.2, -3.2)
        >>> s = RiemannSphere(2.4, 2.8)
        >>> t = RiemannSphere(0, 0)

        >>> inverse = RiemannSphere(5 / 32, 5 / 32)
        >>> result = r.inverse()
        >>> abs(inverse.real - result.real) <= epsilon
        True
        >>> abs(inverse.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False

        >>> inverse = RiemannSphere(3 / 17, - 7 / 34)
        >>> result = s.inverse()
        >>> abs(inverse.real - result.real) <= epsilon
        True
        >>> abs(inverse.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False

        >>> inverse = RiemannSphere(0, 0)
        >>> result = t.inverse()
        >>> isnan(result.real)
        True
        >>> isnan(result.imaginary)
        True
        >>> result.infinite
        True

        >>> result = INFTY.inverse()
        >>> abs(inverse.real - result.real) <= epsilon
        True
        >>> abs(inverse.imaginary - result.imaginary) <= epsilon
        True
        >>> result.infinite
        False
        """
        if self.is_infinite():
            return RiemannSphere(0, 0)
        m = abs(self)
        if self.is_null() or isinf(1 / m):
            return INFTY
        else:
            m_sq = self.__abs_square__()
            return RiemannSphere(self.real / m_sq, - self.imaginary / m_sq)

    def __truediv__(self, other):
        """ Compute the division of the current RiemannSphere
        complex number by an other one, a float or an integer.

        For all non zero complex number z, oo * z = oo
        Moreover, oo * oo = oo

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the division is by a null number

        :Return value: RiemannSphere

        >>> z1 = RiemannSphere(2, 4)
        >>> z2 = RiemannSphere(2, 2)
        >>> zero = RiemannSphere(0, 0)
        >>> z1 / zero
        Traceback (most recent call last):
            ...
        ValueError: Can not compute a division by a null number!
        >>> abs(z1 / z2 - RiemannSphere(1.5, 0.5)) <= 10e-8
        True
        >>> z1 / 0
        Traceback (most recent call last):
            ...
        ValueError: Can not compute a division by a null number!
        >>> z1 / 2
        1.0 + 2.0 i
        >>> z1 / 2.
        1.0 + 2.0 i
        >>> z1 / 1j
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: A RiemannSphere can only be divided by ... a float
        """
        if isinstance(other, RiemannSphere):
            if other.is_null():
                raise ValueError("Can not compute a division " +
                                 "by a null number!")
            else:
                return self * other.inverse()
        elif isinstance(other, (int, float, Fraction)):
            if other == 0:
                raise ValueError("Can not compute a division " +
                                 "by a null number!")
            else:
                return self * (1 / other)
        else:
            raise TypeError("A RiemannSphere can only be divided by " +
                            "a RiemannSphere number, an integer, a float or a Fraction")

    def __rtruediv__(self, other):
        """ Compute the division of a RiemannSphere, an integer or a float
        by the current RiemannSphere complex number.

        For all non zero complex number z, oo * z = oo
        Moreover, oo * oo = oo

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the division is by a null number

        :Return value: RiemannSphere

        >>> z1 = RiemannSphere(2, 4)
        >>> z2 = RiemannSphere(2, 2)
        >>> zero = RiemannSphere(0, 0)
        >>> z1 / zero
        Traceback (most recent call last):
            ...
        ValueError: Can not compute a division by a null number!
        >>> abs(z1 / z2 - RiemannSphere(1.5, 0.5)) <= 10e-8
        True
        >>> z1 / 0
        Traceback (most recent call last):
            ...
        ValueError: Can not compute a division by a null number!
        >>> abs(2 / z1 - RiemannSphere(0.2, - 0.4)) <= 10e-8
        True
        >>> abs(2. / z1 - RiemannSphere(0.2, - 0.4)) <= 10e-8
        True
        >>> 1j / z1
        ... # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: Only a RiemannSphere, ... divided by a RiemannSphere number
        """
        if isinstance(other, RiemannSphere):
            if self.is_null():
                raise ValueError("Can not compute a division " +
                                 "by a null number!")
            else:
                return other * self.inverse()
        elif isinstance(other, (int, float, Fraction)):
            if self.is_null():
                raise ValueError("Can not compute a division " +
                                 "by a null number!")
            else:
                return other * self.inverse()
        else:
            raise TypeError("Only a RiemannSphere, an integer, a float or a Fraction " +
                            "can be divided by a RiemannSphere number")

    def __floordiv__(self, other):
        raise NotImplementedError

    def __rfloordiv__(self, other):
        raise NotImplementedError

    def __mod__(self, other):
        raise NotImplementedError

    def __rmod__(self, other):
        raise NotImplementedError

    def __divmod__(self, other):
        raise NotImplementedError

    def __rdivmod__(self, other):
        raise NotImplementedError

    def complex_exp(self):
        """ Compute the complex exponential of the current
        RiemannSphere complex number

        :return value: RiemannSphere complex number

        Note that, the infinite RiemannSphere being unsigned, its exponential
        is ambigously defined. By convention, it is defined to be the infinite
        RiemannSphere complex number.

        >>> RiemannSphere(0, 0).complex_exp()
        1.0
        >>> INFTY.complex_exp()
        oo
        >>> epsilon = 10e-8
        >>> z = RiemannSphere(1, 1).complex_exp()
        >>> th = RiemannSphere(exp(1) * cos(1), exp(1) * sin(1))
        >>> abs((z - th)) <= epsilon
        True
        """
        if self.is_infinite():
            return INFTY
        r = abs(self)
        if r == 0:
            return RiemannSphere(1., 0.)
        theta = self.argument()
        is_Inf = r * cos(theta) >= 709.1  # e^x == Inf if x >= 709.1
        if self.is_infinite() or is_Inf:
            return INFTY
        tmp = RiemannSphere(cos(r * sin(theta)), sin(r * sin(theta)))
        return exp(r * cos(theta)) * tmp

    def complex_log(self):
        """ Compute the principal branch of the complex logarithm
        of the current RiemannSphere complex number

        :raised error: ValueError if the current RiemannSphere complex
                       number is null

        :param z: RiemannSphere complex number
        :return value: RiemannSphere complex number

        >>> RiemannSphere(0, 0).complex_log()
        Traceback (most recent call last):
            ...
        ValueError: Logarithm of 0 is not defined
        >>> INFTY.complex_log()
        oo
        >>> epsilon = 10e-8
        >>> z = RiemannSphere(1, 1).complex_log()
        >>> th = RiemannSphere(log(sqrt(2)), atan(1))
        >>> abs(z - th) <= epsilon
        True
        """
        if self.is_null():
            raise ValueError("Logarithm of 0 is not defined")
        if self.is_infinite():
            return INFTY
        r = abs(self)
        theta = self.argument()
        return RiemannSphere(log(r), theta)

    def __pow__(self, other):
        """ Compute the exponentiation of the current RiemannSphere
        complex number by an other one, a float or an integer.

        For all non zero complex number z, oo * z = oo
        So that, oo ** oo = oo

        :param other: int, float, RiemannSphere
        :Return value: RiemannSphere

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the multiplication 0 * oo is
                         performed, because it is not well-defined, or
                         when computed the logarithm of 0

        :param power: int, float or RiemannSphere
        :return: RiemannSphere

        >>> RiemannSphere(1, 1) ** 0 == RiemannSphere(1, 0)
        True
        >>> RiemannSphere(1, 1) ** 3
        -2 + 2 i
        >>> RiemannSphere(0, 0) ** 1.2
        Traceback (most recent call last):
            ...
        ValueError: z ** alpha is not defined for z == 0
        >>> RiemannSphere(0, 0) ** RiemannSphere(0, 1)
        Traceback (most recent call last):
            ...
        ValueError: z ** alpha is not defined for z == 0
        >>> INFTY ** 0.
        Traceback (most recent call last):
            ...
        ValueError: 0 x oo is not defined!
        >>> INFTY ** RiemannSphere(0, 0)
        Traceback (most recent call last):
            ...
        ValueError: 0 x oo is not defined!
        >>> INFTY ** 2.
        oo
        >>> INFTY ** RiemannSphere(1, 2)
        oo
        >>> z = RiemannSphere(1 / 2, sqrt(3) / 2) ** 2.
        >>> th = RiemannSphere(-1 / 2, sqrt(3) / 2)
        >>> abs(z - th) <= 10e-8
        True
        >>> z_un = RiemannSphere(1/2, sqrt(3)/2)
        >>> z_deux = RiemannSphere(1, 1)
        >>> result = z_un ** z_deux
        >>> th = exp(- pi / 3) * RiemannSphere(1 / 2, sqrt(3) / 2)
        >>> abs(result - th) <= 10e-8
        True
        """
        if isinstance(other, int):
            p = RiemannSphere(1, 0)
            for i in range(other):
                p *= self
            return p
        if self.is_null():
            raise ValueError("z ** alpha is not defined for z == 0")
        if isinstance(other, float):
            if self.is_infinite():
                if other == 0:
                    raise ValueError("0 x oo is not defined!")
                return INFTY
            return (other * self.complex_log()).complex_exp()
        elif isinstance(other, RiemannSphere):
            if self.is_infinite():
                if other.is_null():
                    raise ValueError("0 x oo is not defined!")
                return INFTY
            return (other * self.complex_log()).complex_exp()
        raise ValueError("A power of a RiemannSphere number has " +
                         "to be an integer, a float or a RiemannSphere" +
                         " complex number")

    def __rpow__(self, other):
        """ Compute the exponentiation of an integer, a float or
        a RiemannSphere complex number by the current RiemannSphere
        complex number

        For all non zero complex number z, oo * z = oo
        So that, oo ** oo = oo

        :param other: int, float
        :Return value: RiemannSphere

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the multiplication 0 * oo is
                         performed, because it is not well-defined, or
                         when computed the logarithm of 0

        >>> 0 ** RiemannSphere(1, 1)
        Traceback (most recent call last):
            ...
        ValueError: z ** alpha is not defined for z == 0
        >>> 0. ** RiemannSphere(1, 1)
        Traceback (most recent call last):
            ...
        ValueError: z ** alpha is not defined for z == 0
        >>> z = 2 ** RiemannSphere(0, 1)
        >>> result = RiemannSphere(cos(log(2)), sin(log(2)))
        >>> abs(z - result) <= 10e-8
        True
        >>> z = exp(1) ** RiemannSphere(0, 1)
        >>> result = RiemannSphere(cos(1), sin(1))
        >>> abs(z - result) <= 10e-8
        True
        """
        if other == 0:
            raise ValueError("z ** alpha is not defined for z == 0")
        return (self * log(other)).complex_exp()

    def __lshift__(selfself, other):
        raise NotImplementedError

    def __rlshift__(selfself, other):
        raise NotImplementedError

    def __rshift__(selfself, other):
        raise NotImplementedError

    def __rrshift__(selfself, other):
        raise NotImplementedError

    def __and__(selfself, other):
        raise NotImplementedError

    def __rand__(selfself, other):
        raise NotImplementedError

    def __xor__(selfself, other):
        raise NotImplementedError

    def __rxor__(selfself, other):
        raise NotImplementedError

    def __or__(selfself, other):
        raise NotImplementedError

    def __ror__(selfself, other):
        raise NotImplementedError

    def __neg__(self):
        """ Compute the opposite of the current RiemannSphere complex number

        :Return value: RiemannSphere

        >>> - RiemannSphere(0, 0)
        0
        >>> - RiemannSphere(1, -2)
        -1 + 2 i
        >>> - INFTY == INFTY
        True
        """
        if self.is_infinite():
            return INFTY
        return RiemannSphere(- self.real, - self.imaginary)

    def __pos__(self):
        """ Define the unitary + operator on RiemannSphere complex numbers :

                 +z = z

        :return value: RiemannSphere

        >>> + RiemannSphere(1, -2)
        1 - 2 i
        >>> + INFTY
        oo
        """
        return self

    def __abs__(self):
        """ Compute the module of the current complex number, ie the distance
        between it and 0

        :Return value: Float or float('Inf')

        >>> epsilon = 0.01
        >>> a = RiemannSphere(0, 0)
        >>> b = RiemannSphere(1, 2)
        >>> c = RiemannSphere(-2, 1)
        >>> d = RiemannSphere(-2, -1)
        >>> e = RiemannSphere(2, -1)
        >>> abs(a)
        0.0
        >>> abs(abs(b) - sqrt(5)) <= epsilon
        True
        >>> abs(abs(c) - sqrt(5)) <= epsilon
        True
        >>> abs(abs(d) - sqrt(5)) <= epsilon
        True
        >>> abs(abs(e) - sqrt(5)) <= epsilon
        True
        >>> abs(INFTY)
        inf
        """
        if self.is_infinite():
            return float('Inf')
        else:
            return sqrt(self.real**2 + self.imaginary**2)

    def __abs_square__(self):
        """ Compute the module of the current complex number, ie the distance
        between it and 0

        :Return value: Float or float('Inf')

        >>> epsilon = 0.01
        >>> a = RiemannSphere(0, 0)
        >>> b = RiemannSphere(1, 2)
        >>> c = RiemannSphere(-2, 1)
        >>> d = RiemannSphere(-2, -1)
        >>> e = RiemannSphere(2, -1)
        >>> abs(a)
        0.0
        >>> abs(abs(b) - sqrt(5)) <= epsilon
        True
        >>> abs(abs(c) - sqrt(5)) <= epsilon
        True
        >>> abs(abs(d) - sqrt(5)) <= epsilon
        True
        >>> abs(abs(e) - sqrt(5)) <= epsilon
        True
        >>> abs(INFTY)
        inf
        """
        if self.is_infinite():
            return float('Inf')
        else:
            return self.real**2 + self.imaginary**2

    def __invert__(self):
        raise NotImplementedError

    def argument(self):
        """ Compute the argument of the current RiemannSphere complex number,
        ie the angle between the axis (Ox) and (Oz) if z is
        the current complex number.

        :raised error: ValueError when the current complex number is null
                       or infinite, because the argument of 0 or oo is not
                       well-defined.

        :Return value: float, included in ]-Pi ; Pi],
                              if z is a non zero and non infinite Riemann
                              sphere complex number.

        >>> epsilon = 0.01
        >>> a = RiemannSphere(0, 0)
        >>> b = RiemannSphere(1, 2)
        >>> c = RiemannSphere(-2, 1)
        >>> d = RiemannSphere(-2, -1)
        >>> e = RiemannSphere(2, -1)

        >>> a.argument()
        Traceback (most recent call last):
            ...
        ValueError: The zero complex number has no argument...

        >>> INFTY.argument()
        Traceback (most recent call last):
            ...
        ValueError: The infinite complex number has no argument...

        >>> abs(b.argument() - atan(2)) <= epsilon
        True
        >>> abs(c.argument() - (pi - atan(1/2))) <= epsilon
        True
        >>> abs(d.argument() - (-pi + atan(1/2))) <= epsilon
        True
        >>> abs(e.argument() - (- atan(1/2))) <= epsilon
        True
        >>> abs(RiemannSphere(0, 1).argument() - pi / 2) <= epsilon
        True
        >>> abs(RiemannSphere(0, -1).argument() + pi / 2) <= epsilon
        True
        """
        if self.is_infinite():
            raise ValueError('The infinite complex number has no argument...')
        if self.is_null():
            raise ValueError('The zero complex number has no argument...')
        if self.real > 0:
            return atan(self.imaginary / self.real)
        elif self.real < 0:
            if self.imaginary >= 0:
                return pi + atan(self.imaginary / self.real)
            else:
                return -pi + atan(self.imaginary / self.real)
        elif self.imaginary > 0:
            return pi / 2
        elif self.imaginary < 0:
            return - pi / 2

    def conjugate(self):
        """ Compute the conjugaison of the current RiemannSphere
        complex number

        :raised error: * TypeError when 'other' is not a RiemannSphere,
                         an integer or a float
                       * ValueError when the multiplcation 0 * oo is performed,
                         because it is not well-defined

        :return value: RiemannSphere

        >>> z = RiemannSphere(3.2, 9.4)
        >>> z.conjugate()
        3.2 - 9.4 i
        >>> z.conjugate().conjugate() == z
        True
        >>> INFTY.conjugate() == INFTY
        True
        """
        if self.is_infinite():
            return self
        return RiemannSphere(self.real, - self.imaginary)


INFTY = RiemannSphere(float('NaN'), float('NaN'), infinite=True)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
