##########################################################
# Module to manipulate image from module Image.          #
# Functions defined here allow the user to:              #
# * add white space around an image                      #
# * create a black frame around an image                 #
# * grow the size of an image                            #
#                                                        #
# Author: Olivier Bouillot                               #
# Email: olivier.bouillot@u-pem.fr                       #
# Creation Date: 11 may 2020                             #
#                                                        #
# Modifications:                                         #
# --------------                                         #
#                                                        #
#                                                        #
# Next modifications to do:                              #
# -------------------------                              #
#                                                        #
#                                                        #
##########################################################


from PIL import Image
import io


def add_space_around_an_img(img, left, top, right, bottom):
    """ Add space around an image. Moreprecisely, it adds:
    * left white rows on the left of the image
    * right white rows on the right of the image
    * top white lines on the top of the image
    * below white lines on the bottom of the image

    :param img: Image
    :param left, top, right, bottom: int
    :return value: Image

    >>> img_1 = Image.new('RGB', (3, 2), 'white')
    >>> L_1 = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    >>> L_2 = [(255, 255, 0), (255, 0, 255), (0, 255, 255)]
    >>> lst_1 = L_1 + L_2
    >>> img_1.putdata(lst_1)
    >>> img_2 = add_space_around_an_img(img_1, 2, 2, 2, 2)
    >>> lst_2 = list(img_2.getdata())
    >>> white_line = [(255, 255, 255)] * 7
    >>> white_side = [(255, 255, 255)] * 2
    >>> theoretical_lst_2 = white_line * 2 + \
                            white_side + lst_1[:3] + white_side + \
                            white_side + lst_1[3:] + white_side + \
                            white_line * 2
    >>> lst_2 == theoretical_lst_2
    True
    """
    width, height = img.size
    new_width = width + left + right
    new_length = height + top + bottom
    new_img = Image.new('RGB', (new_width, new_length), 'white')
    new_img.paste(img, (left, top))
    return new_img


def demultiply(lst, repetition):
    """ repeat repetition times each element of the list lst

    :param lst: List
    :param repetition: int
    :return value: List

    >>> demultiply([], 2)
    []
    >>> demultiply([2, 3], 3)
    [2, 2, 2, 3, 3, 3]

    """
    return sum([[elt for i in range(repetition)] for elt in lst], [])


def magnify_img(img, rate):
    """ Grow a pixel: a pixel becomes a square of rate pixels for each sides

    :param img: Image
    :param rate: int
    :return value: Image

    >>> img_1 = Image.new('RGB', (3, 2), 'white')
    >>> L_1 = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    >>> L_2 = [(255, 255, 0), (255, 0, 255), (0, 255, 255)]
    >>> lst_1 = L_1 + L_2
    >>> img_1.putdata(lst_1)
    >>> img_2 = magnify_img(img_1, 2)
    >>> lst_2 = list(img_2.getdata())
    >>> line_1 = demultiply(lst_1[:3], 2)
    >>> line_2 = demultiply(lst_1[3:], 2)
    >>> lst_2 == line_1 * 2 + line_2 * 2
    True
    """
    width, height = img.size
    pixels = list(img.getdata())
    new_pixels_tmp = []
    for line_nb in range(height):
        line = pixels[line_nb * width:(line_nb + 1) * width]
        new_line = demultiply(line, rate)
        for i in range(rate):
            new_pixels_tmp.append(new_line)
    new_pixels = sum(new_pixels_tmp, [])
    new_img = Image.new('RGB', (width * rate, height * rate), 'white')
    new_img.putdata(new_pixels)
    return new_img


def display_preparing_of_img(img, size_max):
    """ Prepare the display of an image in a phase portrait widget,
    ie:
    * grow the image by duplicating pixels, if its size is at least
      four time smaller than the available space for displaying the image
    * resize the image to fit the available space for displaying the image
    """
    width, height = img.size
    if max(width, height) < size_max:
        # the phase portrait is smaller than the space to display it,
        # a square of size_max pixels
        rate = int(size_max / max(width, height))
        left = int((size_max - rate * width) / 2)
        right = size_max - left - rate * width
        top = int((size_max - rate * height) / 2)
        bottom = size_max - top - rate * height
        tmp_img = magnify_img(img, rate)
        tmp_img = add_space_around_an_img(tmp_img, left, top, right, bottom)
    else:
        if width < height:
            tmp_img = add_space_around_an_img(img,
                                              (height - width) // 2, 0,
                                              (height - width) // 2, 0
                                              )
        elif width > height:
            tmp_img = add_space_around_an_img(img,
                                              0, (width - height) // 2,
                                              0, (width - height) // 2
                                              )
        else:
            tmp_img = img
    # Now, the phase portrait is too big to be displayed or too big
    # to be magnifies manually. So, we resize the image using
    # the resize tool of Image package
    new_size = (size_max, size_max)
    return tmp_img.resize(new_size, Image.ANTIALIAS)


def PIL_image_2_byte_im(img):
    # Convert the image into a binary format of a .png image,
    # in order to put it in an Image widget:
    # 1. create a buffer
    # 2. save the image in it as a .png file
    # 3. takes finaly the binary format of the image
    buffer = io.BytesIO()
    img.save(buffer, format='png')
    return buffer.getvalue()


if __name__ == '__main__':
    from doctest import testmod
    testmod()
