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
#                                                         #
# Next modifications to do:                               #
# -------------------------                               #
#                                                         #
#   Check pylava
#                                                         #
###########################################################


from Color import RGB
from RiemannSphere import RiemannSphere
from PIL import Image
import sqlite3
import math
from time import time
import os.path


def gcd(a, b, c):
    """ Compute the greatest common divisor of three integers

    :param a: int
    :param b: int
    :param c: int
    :return: int, the greatest common divisor of the three integers a, b and c

    >>> gcd(5, 15, 30)
    5
    >>> gcd(-2, 15, 30)
    1
    >>> gcd(3, -15, 30)
    3
    >>> gcd(1, 5, -10)
    1
    >>> gcd(-2, 8, -20)
    2
    >>> gcd(3, -9, -21)
    3
    """
    return math.gcd(a, math.gcd(b, c))


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
                 information=False, database=""):
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
        """
        self.function = function
        self.left_below = left_below
        self.right_upper = right_upper
        length_x = self.right_upper.real - self.left_below.real
        length_y = self.right_upper.imaginary - self.left_below.imaginary
        self.size = (int(length_x * resolution) + 1, int(length_y * resolution) + 1)
        self.resolution = resolution
        min_x = int(self.left_below.real * resolution)
        max_x = int(self.right_upper.real * resolution)
        self.liste_x = [x for x in range(min_x, max_x + 1)]
        min_y = int(self.left_below.imaginary * resolution)
        max_y = int(self.right_upper.imaginary * resolution)
        self.liste_y = [y for y in range(min_y, max_y + 1)]
        self.database = database
        self.values = self.compute(resolution, information)

    def recover_datas(self, resol, information):
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
        # Initialisation
        values = {}
        # Connection to the database
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        if information:
            print()
            print("**************************************")
            print("* Recuperation des donnees en cours. *")
            print("**************************************")
            print()
        t_0 = time()
        if information:
            print("Creation d'une table temporaire dans " +
                  "la base de donnees :")
            print("\tEn cours...")
        cursor.execute('''CREATE TABLE IF NOT EXISTS TMP(
                          multiplier INTEGER,
                          real INTEGER,
                          imaginary INTEGER);''')
        for y in self.liste_y:
            for x in self.liste_x:
                tmp = gcd(resol, x, y)
                cursor.execute('''INSERT \
                                  INTO TMP(multiplier, real, imaginary) \
                                  VALUES (?, ?, ?)''',
                               (resol / tmp, x / tmp, y / tmp,))
        connection.commit()
        if information:
            t_1 = time()
            print("\tTerminee en " + str(t_1 - t_0) + "s")
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
            print("SELECT realise en ", t_1 - t_0, " s.")
            print("Transformation des calculs deja fait " +
                  "en nombres complexes :")
            print("\tEn cours...")
        computed_value = cursor.fetchone()
        nb_computed_values = 0
        while computed_value is not None:
            z_mult = computed_value[0]
            z_real = computed_value[1]
            z_im = computed_value[2]
            val_real, val_im, val_inf = convert(computed_value[3],
                                                computed_value[4],
                                                computed_value[5])
            x = round((z_real / z_mult - self.left_below.real) * resol)
            y = round((z_im / z_mult - self.left_below.imaginary) * resol)
            values[x, y] = RiemannSphere(val_real, val_im, infinite=val_inf)
            nb_computed_values += 1
            computed_value = cursor.fetchone()
        if information:
            t_2 = time()
            nb_of_values_to_compute = len(self.liste_x) * len(self.liste_y)
            proportion = nb_computed_values / nb_of_values_to_compute
            print("\tTermine en " + str(t_2 - t_1) + "s.")
            print(int(10000 * proportion) / 100,
                  "% des donnees a calculer ont deja ete calculees " +
                  "au par avant.")
        cursor.execute('''DROP TABLE TMP;''')
        return values

    def compute_a_value(self, x, y, resol, values, cursor):
        """ Compute the image of the current complex function at
        the Riemann shpere complex number z = x + i y.

        :param resol: resolution value used to discretised the rectangle
                               [a, b] + [c, d] * i such that there will be
                               (resol + 1)^2 points in a square of area 1
        :param values: dictionnary whose keys/values described values already
                               computed of the current complex function
        :param cursor: Cursor object, created after being connected to
                         a sqlite3 database containing values of the function
                         we are currently graphing, used to add the complex
                         valueswe will compute here

        The values dictionnary will be updated, as well as the database related
        with the cursor object, during the execution of the compute_a_value
        function
        """
        x_pixel = round(x - self.left_below.real * resol)
        y_pixel = round(y - self.left_below.imaginary * resol)
        z = RiemannSphere(x / resol, y / resol)
        try:
            values[x_pixel, y_pixel] = self.function(z)
            gcd_tmp = gcd(resol, x, y)
            cursor.execute('''INSERT
                              INTO Z(multiplier, real, imaginary, infinite)
                              VALUES (?, ?, ?, ?)''', (resol / gcd_tmp,
                                                       x / gcd_tmp,
                                                       y / gcd_tmp, 0,))
            if values[x_pixel, y_pixel].is_infinite():
                infty = 1
            else:
                infty = 0
            cursor.execute('''INSERT INTO Value(real, imaginary, infinite)
                              VALUES (?, ?, ?)''',
                           (values[x_pixel, y_pixel].real,
                            values[x_pixel, y_pixel].imaginary,
                            infty,))
        except ValueError as exception:
            print("z = ", z, " - pixel", (x_pixel, y_pixel),
                  "non calcule :", exception)

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
        :param database: String, which is by default empty, which indicate
                         the path of a database containing values of
                         the function we are currently graphing ; if database
                         is non empty, we will use values already computing
                         and add some new ones

        :Return value: a dictionnary whose key are the complex number of
                       discretised rectangle [a, b] + [c, d] * i and the values
                       associated are the values of the current complex
                       function
        """
        if os.path.isfile(self.database):
            # Look back datas in the database
            values = self.recover_datas(resol, information)
        else:
            # Create the database to store the computed values
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
        # Computation of the necessary values
        if information:
            print()
            print("*********************")
            print("* calcul en cours : *")
            print("*********************")
            print()
        values_keys = values.keys()
        to_compute = [(x, y) for x in self.liste_x for y in self.liste_y
                      if (round(x - self.left_below.real * resol),
                          round(y - self.left_below.imaginary * resol))
                      not in values_keys]
        lenght = len(to_compute)
        one_half_per_cent = int(lenght / 200)
        if one_half_per_cent == 0:
            one_half_per_cent = 1
        t_0 = time()
        nb_of_element = 0
        for (x, y) in to_compute:
            self.compute_a_value(x, y, resol, values, cursor)
            nb_of_element += 1
            if nb_of_element % one_half_per_cent == 0:
                if information:
                    t_1 = time()
                    pourcentage = int(10000 * nb_of_element / lenght) / 100
                    print(str(pourcentage) +
                          "% realisé en " + str(int((t_1 - t_0) * 1000) / 1000) + "s.")
                connection.commit()
        connection.commit()
        cursor.close()
        if information:
            print("*****************")
            print("SORTIE DE CALCULS")
            print("*****************")
        return values

    def draw(self, information=False):
        """ Draw the current function in the current discretised rectangle
        and export the drawing in a .bmp file

        :param directory: directory where the .bmp file will be saved
        :param name: name of the .bmp file
        :return value: Image
        """
        size = self.size
        img = Image.new('RGB', size, "white")      # create a new black image
        pixels = img.load()                        # create the pixel map
        if information:
            print()
            print("********************************")
            print("* Calcul des couleurs en cours *")
            print("********************************")
            print()
        t_0 = time()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # for every pixel, set the colour accordingly
                try:
                    image_of_z = self.values[i, self.size[1] - j - 1]
#                    print("i = ", i, "j = ", j, "z = ", z)
                    pixels[i, j] = RGB(image_of_z)
                except KeyError:
                    z = RiemannSphere(self.left_below.real + i / self.resolution,
                                      self.right_upper.imaginary - j / self.resolution)
                    print("z = " + str(z) + " correspond au pixel (" + str(i) + ', ' + str(self.size[1] - j - 1) + ").")
                    print("Son image n'a pas été calculé")
            if information and i % 100 == 9:
                t_1 = time()
                print(str(100. * (i + 1) / (img.size[0] + 1)) +
                      "% realisé en " + str(int((t_1 - t_0) * 1000) / 1000) + "s")
        self.img = img

    def save(self, directory, name, information=False):
        if information:
            t_0 = time()
            print()
            print("*************************")
            print("* sauvegarde de l'image *")
            print("*************************")
            print()
        self.img.save(directory + name, format="png")
        if information:
            t_1 = time()
            print("sauvegarde de l'image effectuée en " + str(int((t_1 - t_0) * 1000) / 1000) + "s")
            print()


if __name__ == '__main__':
    from doctest import testmod
    testmod()
