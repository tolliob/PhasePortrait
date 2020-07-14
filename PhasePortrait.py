###########################################################
# Module to draw phase portrait of function defined       #
# in a part of the complex plane, and valued in the       #
# complex plane                                           #
#                                                         #
# Author: Olivier Bouillot                                #
# Email: olivier.bouillot@u-pem.fr                        #
# Creation Date: july 2017                                #
#                                                         #
# Modifications:                                          #
# --------------                                          #
#                                                         #
# 07/2018    Adds a database to save expensive values     #
#            to compute                                   #
# 03/2020    Modifies docstring and doctest               #
# 04/04/20   Take into account pylava warnings            #
# 15/05/20   Add the image representation as an attribute #
# 18/05/20   Degub the expression of the complex number   #
#            which have not been computed                 #
# 10/07/20   Allows floating points in corner components  #
#                                                         #
# Next modifications to do:                               #
# -------------------------                               #
#                                                         #
#   Check pylava                                          #
#   Add a few doctests                                    #
#                                                         #
###########################################################


from Color import RGB
from RiemannSphere import RiemannSphere
from PIL import Image
import sqlite3
from math import gcd
from fractions import Fraction
from time import time
import os.path


def convert(u, v, w):
    """ Convert the values u, v to a float number (NaN if not a float number)
    and w to a boolean

    :param u: float, a priori
    :param v: float, a priori
    :param w: 0 or 1, a priori
    :return value: a triplet (float, float, boolean), eventually,
                       he float numbers could be the NaN floating point

    >>> convert(0.1, 0.2, 0)
    (0.1, 0.2, False)
    >>> convert(1, 0.2, 0)
    (1, 0.2, False)
    >>> convert(1, 2, 1)
    (1, 2, True)
    """
    if not isinstance(u, (int, float)):
        u = float('NaN')
    if not isinstance(v, (int, float)):
        v = float('NaN')
    if w == 0:
        w = False
    else:
        w = True
    return u, v, w


class PhasePortrait:
    """ Class that realizes a phase portrait of a complex function, ie
    a function defined in a rectangle [a, b] + [c, d] * i of the complex
    number field and valued in C.

    :attribute function: represents the function C -> C which will be graphed
    :attribute left_below: represents the complex number a + i c
    :attribute right_upper: represents the complex number b + i d
    :attribute resolution: value used to discretised the rectangle
                           [a, b] + [c, d] * i such that there will be
                           (resolution + 1)^2 points in a square of
                           area 1
    :attribute size: tuple integer, expressing the number of nodes in
                            the x-axis and y-axis in the discretised grid of
                            the rectangle [a, b] + [c, d] * i
                            the rectangle [a, b] + [c, d] * i
    :attribute liste_x: list of abscissa of points where the current
                            function will be evaluated
    :attribute liste_y: list of ordinate of points where the current
                            function will be evaluated
    :attribute values: dictionnary whose keys are pixels that discretised
                            the rectangle [a, b] + [c, d] * i and whose
                            values are the value of the current fonction
                            at these points
    :attribute database: string which represents the path of a database
                            containing the values of the function we are
                            currently graphing ; if database is non empty,
                            we will use values already computing and add
                            some new ones
    :attribute img: Image, which contains a graphical representation of
                           the looked for phase portrait

    >>> a = RiemannSphere(0, 0)
    >>> b = RiemannSphere(1, 2)
    >>> def id(x):
    ...     return x
    >>> graph = PhasePortrait(id, a, b, 2)
    >>> dic = graph.compute(2, False)
    >>> dic_th = {(0, 0): RiemannSphere(0, 0),
    ...           (0, 1): RiemannSphere(0, 0.5),
    ...           (0, 2): RiemannSphere(0, 1),
    ...           (0, 3): RiemannSphere(0, 1.5),
    ...           (0, 4): RiemannSphere(0, 2),
    ...           (1, 0): RiemannSphere(0.5, 0),
    ...           (1, 1): RiemannSphere(0.5, 0.5),
    ...           (1, 2): RiemannSphere(0.5, 1),
    ...           (1, 3): RiemannSphere(0.5, 1.5),
    ...           (1, 4): RiemannSphere(0.5, 2),
    ...           (2, 0): RiemannSphere(1, 0),
    ...           (2, 1): RiemannSphere(1, 0.5),
    ...           (2, 2): RiemannSphere(1, 1),
    ...           (2, 3): RiemannSphere(1, 1.5),
    ...           (2, 4): RiemannSphere(1, 2),
    ...           }
    >>> dic == dic_th
    True
    """

    def __init__(self, function, left_below, right_upper, resolution,
                 information=False, database="", data_logger=None):
        """ Constructor of the class
        :param function: represents the function [a, b] + [c, d] * i -> C
                         whose phase portrait will be drawn
        :param left_below: represents the complex number a + i c
        :param right_upper: represents the complex number b + i d
        :param resolution: value used to discretised the rectangle
                               [a, b] + [c, d] * i such that there will be
                               (resolution + 1)^2 points in a square of area 1
        :param information: boolean, which is by default equals to False,
                            which indicates if the user wants to see
                            the progression of the calculation in order
                            to produce the image
        :param database: String, which is by default empty, which indicates
                         the path of a database containing values of
                         the function we are currently graphing ; if database
                         is non empty, we will use values already computing
                         and add some new ones
        :param data_logger: logging.logging.Logger, which is a data logger
                            to record information during computation
        """
        self.function = function
        self.left_below = left_below
        self.right_upper = right_upper
        length_x = self.right_upper.real - self.left_below.real
        length_y = self.right_upper.imaginary - self.left_below.imaginary
        self.size = (int(length_x * resolution) + 1, int(length_y * resolution) + 1)
        self.resolution = resolution
        self.liste_x = [self.left_below.real + Fraction(i, resolution)
                        for i in range(int((self.right_upper.real - self.left_below.real) * resolution) + 1)]
        self.liste_y = [self.left_below.imaginary + Fraction(i, resolution)
                        for i in range(int((self.right_upper.imaginary - self.left_below.imaginary) * resolution) + 1)]
        self.database = database
        self.data_logger = data_logger
        self.values = self.compute(resolution, information)


    def recover_datas(self, resol, information, connection, cursor):
        """ Recover datas already computed in the past and stored
        in the database of the current phase portrait

        :param resolution: value used to discretised the rectangle
                               [a, b] + [c, d] * i such that there will be
                               (resolution + 1)^2 points in a square of area 1
        :param information: boolean, which is by default equals to False,
                            which indicates if the user wants to see
                            the progression of the calculation in order
                            to produce the image

        :return value: a dictionnary whose keys/values described values already
                               computed of the current complex function
        """
        values = {}
        if information:
            text = "Loading datas in progress "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
            t_0 = time()
            text = "Creation of a temporary table in the database " +\
                   self.database + " "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
        cursor.execute('''CREATE TABLE IF NOT EXISTS TMP(
                          multiplier INTEGER,
                          real INTEGER,
                          imaginary INTEGER);''')
        for y in self.liste_y:
            for x in self.liste_x:
                lcm_tmp = abs(x.denominator * y.denominator) // gcd(x.denominator, y.denominator)
                cursor.execute('''INSERT \
                                  INTO TMP(multiplier, real, imaginary) \
                                  VALUES (?, ?, ?)''',
                               (lcm_tmp, int(x * lcm_tmp), int(y * lcm_tmp),))
        connection.commit()
        if information:
            t_1 = time()
            str_time = str(int((t_1 - t_0) * 1000) / 1000) + "s. "
            text = "Temporary table created in " + str_time
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
            t_0 = time()
        SQL = "SELECT Zmultiplier, Zreal, Zimaginary, " + \
              "       Value.real, Value.imaginary, Value.infinite " + \
              "FROM Value " + \
              "JOIN (SELECT Z.Id AS ZId, " + \
              "             Z.multiplier AS Zmultiplier, " + \
              "             Z.real AS Zreal, " + \
              "             Z.imaginary AS Zimaginary " + \
              "      FROM Z JOIN Tmp ON Z.multiplier = Tmp.Multiplier " + \
              "                      AND Z.real = Tmp.Real " + \
              "                      AND Z.imaginary = Tmp.Imaginary" + \
              "     ) ON ZId = Value.Id;"
        cursor.execute(SQL)
        if information:
            t_1 = time()
            str_time = str(int((t_1 - t_0) * 1000) / 1000) + " s. "
            text = "Recovery of already computed values realised in " + str_time
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
            text = "Transformation of the already done computations " + \
                   "into complex numbers in progress. "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
        computed_value = cursor.fetchone()
        nb_computed_values = 0
        while computed_value is not None:
            z_mult = computed_value[0]
            z_real = computed_value[1]
            z_im = computed_value[2]
            val_real, val_im, val_inf = convert(computed_value[3],
                                                computed_value[4],
                                                computed_value[5])
            x = Fraction(z_real, z_mult)
            y = Fraction(z_im, z_mult)
            pixel = (self.liste_x.index(x), self.liste_y.index(y))
            values[pixel] = RiemannSphere(val_real, val_im, infinite=val_inf)
            nb_computed_values += 1
            computed_value = cursor.fetchone()
        if information:
            t_2 = time()
            nb_of_values_to_compute = len(self.liste_x) * len(self.liste_y)
            proportion = nb_computed_values / nb_of_values_to_compute
            str_time = str(int((t_2 - t_1) * 1000) / 1000) + "s. "
            text = "Transformation into complex numbers finished in " + str_time
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
            text = str(int(10000 * proportion) / 100) + \
                  "% of the data to compute have already been computed. "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
        cursor.execute('''DROP TABLE TMP;''')
        return values

    def compute_a_value(self, z, pixel, resol, values, cursor):
        """ Compute the image of the current complex function at
        the Riemann sphere complex number z = x + i y and save it in the values dictionary.

        :param z: RiemannSphere complex number
        :param pixel: tuple of int, which represents the coordinates of
                      the colored pixel by the value of the current complex
                      function at the Riemannspphere complex number z
        :param values: dictionnary whose keys/values described values already
                               computed of the current complex function.
                               Keys are tuples which represents coordinates of
                               pixels, while values are the computed values of
                               the current function at the Riemann sphere
                               complex number z
        :param cursor: Cursor object, created after being connected to
                         a sqlite3 database containing values of the function
                         we are currently graphing, used to add the complex
                         valueswe will compute here

        The values dictionnary will be updated, as well as the database related
        with the cursor object, during the execution of the compute_a_value
        function
        """
        try:
            values[pixel] = self.function(z)
            if self.database != "":
                lcm_tmp = int(abs(z.real.denominator * z.imaginary.denominator) // gcd(z.real.denominator,
                                                                                       z.imaginary.denominator))
                cursor.execute('''INSERT
                                  INTO Z(multiplier, real, imaginary, infinite)
                                  VALUES (?, ?, ?, ?)''', (lcm_tmp,
                                                           int(z.real * lcm_tmp),
                                                           int(z.imaginary * lcm_tmp), 0,))
                if values[pixel].is_infinite():
                    infty = 1
                else:
                    infty = 0
                cursor.execute('''INSERT INTO Value(real, imaginary, infinite)
                                      VALUES (?, ?, ?)''',
                               (float(values[pixel].real),
                                float(values[pixel].imaginary),
                                infty,))
        except ValueError:
            text = "Pixel " + str(pixel) + " has no value: " + \
                   "the image of z = " + str(z) + " has not been computed "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.exception(text)

    def compute(self, resol, information):
        """ Compute all the images of the current complex function we want
        to draw. We consider the complex numbers that are in a grid of
        the discretised rectangle [a, b] + [c, d] * i such that there is
        (resol + 1)^2 points in a square of area 1 of the discretised
        rectangle [a, b] + [c, d] * i.

        :param resol: resolution value used to discretised the rectangle
                               [a, b] + [c, d] * i such that there will be
                               (resol + 1)^2 points in a square of area 1
        :param information: boolean, which is by default equals to False,
                               which indicates if the user wants to see
                               the progression of the calculation in order
                               to produce the image

        :Return value: a dictionnary whose key are the complex number of
                       discretised rectangle [a, b] + [c, d] * i and the values
                       associated are the values of the current complex
                       function
        """
        if os.path.isfile(self.database):
            # Connection to the database
            connection = sqlite3.connect(self.database)
            cursor = connection.cursor()
            # Look back datas in the database
            values = self.recover_datas(resol, information, connection, cursor)
            # Look for values to compute
            values_keys = values.keys()
            dict_x = {str(self.liste_x[pos]): pos for pos in range(len(self.liste_x))}
            dict_y = {str(self.liste_y[pos]): pos for pos in range(len(self.liste_y))}
            to_compute = [(x, y) for x in self.liste_x for y in self.liste_y
                          if (dict_x[str(x)], dict_y[str(y)]) not in values_keys]
#            to_compute = [(x, y) for x in self.liste_x for y in self.liste_y
#                          if (self.liste_x.index(x), self.liste_y.index(y)) not in values_keys]
        elif self.database != "":
            # Create the dictionnary to store the computed values
            values = {}
            # Connection to the database
            connection = sqlite3.connect(self.database)
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Z(
                                 Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                 multiplier INTEGER,
                                 real INTEGER,
                                 imaginary INTEGER,
                                 infinite BOOLEAN);''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS Value(
                                 Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                 real FLOAT,
                                 imaginary FLOAT,
                                 infinite BOOLEAN);''')
            # Look for values to compute
            to_compute = [(x, y) for x in self.liste_x for y in self.liste_y]
        else:
            # Look for values to compute
            to_compute = [(x, y) for x in self.liste_x for y in self.liste_y]
            # Create the dictionnary to store the computed values
            values = {}
            # False database connection variable
            cursor = None
        # Computation of the necessary values
        if information:
            if self.data_logger is None:
                print("Preliminary computations have started")
            else:
                self.data_logger.info("Preliminary computations have started ")
        lenght = len(to_compute)
        one_half_per_cent = int(lenght / 200)
        if one_half_per_cent == 0:
            one_half_per_cent = 1
        t_0 = time()
        nb_of_element = 0
        for (x, y) in to_compute:
            z = RiemannSphere(x, y)
            pixel = (self.liste_x.index(x), self.liste_y.index(y))
            self.compute_a_value(z, pixel, resol, values, cursor)
            nb_of_element += 1
            if nb_of_element % one_half_per_cent == 0:
                if information:
                    t_1 = time()
                    per_cent = str(int(10000 * nb_of_element / lenght) / 100)
                    str_time = str(int((t_1 - t_0) * 1000) / 1000) + "s. "
                    text = "% of computations realised in "
                    if self.data_logger is None:
                        print(per_cent + text + str_time)
                    else:
                        self.data_logger.info(per_cent + text + str_time)
                if self.database != "":
                    connection.commit()
        if self.database != "":
            connection.commit()
            cursor.close()
        if information:
            if self.data_logger is None:
                print("Preliminary computations are finished ")
            else:
                self.data_logger.info("Preliminary computations are finished ")
        else:
            if self.data_logger is None:
                print("Computations finished ")
            else:
                self.data_logger.info("Computation finished ")
        return values

    def draw(self, information=False):
        """ Draw the current function in the current discretised rectangle
        and export the drawing in a .bmp file

        :param directory: directory where the .bmp file will be saved
        :param name: name of the .bmp file
        :return value: Image
        """
        img = Image.new('RGB', self.size, "white")      # create a new black image
        pixels = img.load()                             # create the pixel map
        if information:
            text = "Preliminary color computations have started "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)
        t_0 = time()
        five_per_cent = int(5 * img.size[0] / 100)
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # for every pixel, set the colour accordingly
                try:
                    image_of_z = self.values[i, self.size[1] - j - 1]
                    pixels[i, j] = RGB(image_of_z)
                except KeyError:
                    re = self.left_below.real + Fraction(i, self.resolution)
                    im = self.right_upper.imaginary - Fraction(j, self.resolution)
                    z = RiemannSphere(re, im)
                    coords = str(i) + ', ' + str(self.size[1] - j - 1)
                    text = "Pixel (" + coords + ") has no computed valued: " +\
                           "it is related to z = " + str(z) + " "
                    if self.data_logger is None:
                        print(text)
                    else:
                        self.data_logger.error(text)
            if information and five_per_cent != 0 and i % five_per_cent == five_per_cent - 1:
                t_1 = time()
                per_cent = str(int(10000. * (i + 1) / (img.size[0] + 1)) / 100)
                time_str = str(int((t_1 - t_0) * 1000) / 1000) + "s"
                text = " of color computations realised in "
                if self.data_logger is None:
                    print(per_cent + "%" + text + time_str)
                else:
                    self.data_logger.info(per_cent + "%" + text + time_str + " ")
        if information:
            if self.data_logger is None:
                print("Color computations are finished")
            else:
                self.data_logger.info("Color computations are finished ")
        self.img = img

    def save(self, directory, name, information=False):
        if information:
            t_0 = time()
        self.img.save(directory + name, format="png")
        if information:
            t_1 = time()
            text = "Image saved in " + str(int((t_1-t_0) * 1000) / 1000) + "s "
            if self.data_logger is None:
                print(text)
            else:
                self.data_logger.info(text)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
