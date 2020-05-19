###########################################################
# Module which define an interactive Jupyter widget       #
# in order to draw phase portrait of function defined     #
# in a part of the complex plane, and valued in the       #
# complex plane                                           #
#                                                         #
# Author: Olivier Bouillot                                #
# Email: olivier.bouillot@u-pem.fr                        #
# Creation Date: may 2019                                 #
#                                                         #
# Modifications:                                          #
# --------------                                          #
#                                                         #
#                                                         #
# Next modifications to do:                               #
# -------------------------                               #
#                                                         #
#   Check pylava                                          #
#   Documentation + doctest                               #
#                                                         #
###########################################################


import io
from RiemannSphere import RiemannSphere
from PhasePortrait import PhasePortrait
import matplotlib.pyplot as plt
from PIL import Image
import ipywidgets as widgets
from ipywidgets import Layout, GridBox


class RiemannSphereWidget(widgets.VBox):

    def __init__(self, description, min_value, max_value, step=1, value=None):
        # Initialisation
        super().__init__()
        mean = (min_value + max_value) / 2
        if value is None:
            self.value = RiemannSphere(mean, mean)
        else:
            self.value = value

        # Widgets
        zone_name = widgets.HTML(value="<b>" + description + "</b>")
        re = widgets.FloatSlider(value=self.value.real,
                                 min=min_value, max=max_value, step=step,
                                 description='Re',
                                 readout=False,
                                 style={'description_width': 'initial'},
                                 layout=Layout(padding='0px 0px 0px 5px', width='150px')
                                 )
        im = widgets.FloatSlider(value=self.value.imaginary,
                                 min=min_value, max=max_value, step=step,
                                 description='Im',
                                 readout=False,
                                 style={'description_width': 'initial'},
                                 layout=Layout(padding='0px 0px 0px 5px', width='150px')
                                 )

        RS_value = widgets.Label(value=str(self.value),
                                 layout=Layout(padding='15px 0px 30px 10px')
                                 )

        # Observe stuff
        re.observe(self.re_update, 'value')
        im.observe(self.im_update, 'value')

        # Add to children
        control_zone = widgets.HBox([widgets.VBox([re, im]), RS_value],
                                    layout=Layout(padding='0px 0px 0px 25px')
                                    )
        self.children = [zone_name, control_zone]

        # Layout
        self.layout = widgets.Layout(margin='0px 0px 0px 0px',
                                     padding='0px 0px 0px 0px'
                                     )
        self.style = {'description_width': 'initial'}

    def re_update(self, change):
        self.value.real = change.new
        self.children[1].children[1].value = '\t' + str(self.value)

    def im_update(self, change):
        self.value.imaginary = change.new
        self.children[1].children[1].value = '\t' + str(self.value)


class Directions(widgets.VBox):

    def __init__(self, associated_variable, step, name='', width='100%'):
        # Initialisation
        super().__init__()
        self.name = name
        self.variable = associated_variable
        self.step = step

        # Widgets
        text = widgets.Label(value=self.name + ": " + str(self.variable))
        up = widgets.Button(description='Up',
                            layout=widgets.Layout(width='70px', grid_area='up'),
                            style=widgets.ButtonStyle(button_color='moccasin'))
        left = widgets.Button(description='Left',
                              layout=widgets.Layout(width='70px', grid_area='left'),
                              style=widgets.ButtonStyle(button_color='moccasin'))
        right = widgets.Button(description='Right',
                               layout=widgets.Layout(width='70px', grid_area='right'),
                               style=widgets.ButtonStyle(button_color='moccasin'))
        down = widgets.Button(description='Down',
                              layout=widgets.Layout(width='70px', grid_area='down'),
                              style=widgets.ButtonStyle(button_color='moccasin'))
        grid_direction = GridBox(children=[up, left, right, down],
                                 layout=Layout(width='40%',
                                               grid_template_rows='auto auto auto',
                                               grid_template_columns='33% 33% 33%',
                                               grid_template_areas='''". up ."
                                                                      "left . right"
                                                                      ". down ."
                                                                   '''
                                               )
                                 )

        # Connect to listeners
        up.on_click(self.up_function)
        left.on_click(self.left_function)
        right.on_click(self.right_function)
        down.on_click(self.down_function)

        # Add to children
        self.children = [text, grid_direction]

    def up_function(self, b):
        self.variable.imaginary += self.step
        self.children[0].value = self.name + ": " + str(self.variable)

    def left_function(self, b):
        self.variable.real -= self.step
        self.children[0].value = self.name + ": " + str(self.variable)

    def right_function(self, b):
        self.variable.real += self.step
        self.children[0].value = self.name + ": " + str(self.variable)

    def down_function(self, b):
        self.variable.imaginary -= self.step
        self.children[0].value = self.name + ": " + str(self.variable)


class ButtonsAction(widgets.HBox):

    def __init__(self):
        # Initialisation
        super().__init__()
        self.phase_portrait = None

        # Widgets
        compute_button = widgets.Button(description="Compute the phase portrait",
                                        layout=Layout(width='33.3%', height='80px',
                                                      margin='1px 1px 1px 1px',
                                                      padding='0px 0px 0px 0px',
                                                      border='solid 1px black'),
                                        align_items='center')
        show_button = widgets.Button(description="Show the phase portrait",
                                     layout=Layout(width='33.3%', height='80px',
                                                   margin='1px 1px 1px 1px',
                                                   padding='0px 0px 0px 0px',
                                                   border='solid 1px black'),
                                     align_items='center')
        save_button = widgets.Button(description="Save the phase portrait",
                                     layout=Layout(width='33.3%', height='80px',
                                                   margin='1px 1px 1px 1px',
                                                   padding='0px 0px 0px 0px',
                                                   border='solid 1px black'),
                                     align_items='center')

        # Add to children
        self.children = [compute_button, show_button, save_button]

        # Layout
        self.layout = Layout(align_self='center',
                             object_position='bottom',
                             width='90%',
                             margin='0px 0px 10px 0px',
                             padding='0px 0px 0px 0px')

    def add_listeners(self, compute, show, save):
        # Connect buttons to listeners
        self.children[0].on_click(compute)
        self.children[1].on_click(show)
        self.children[2].on_click(save)


def add_space_around(img, left, top, right, bottom):
    """ Add space around an image. Moreprecisely, it adds:
    * left white rows on the left of the image
    * right white rows on the right of the image
    * top white lines on the top of the image
    * below white lines on the bottom of the image
    """
    width, height = img.size
    new_img = Image.new('RGB', (width + left + right, height + top + bottom), 'white')
    new_img.paste(img, (left, top))
    return new_img


def frame_of_an_img(img):
    width, height = img.size
    new_img = Image.new('RGB', (width + 2, height + 2), 'black')
    new_img.paste(img, (1,1))
    return new_img


def demultiply(lst, repetition):
    """ repeat repetition times each element of the list lst

    >>> demultiply([], 2)
    []
    >>> demultiply([2, 3], 3)
    [2, 2, 2, 3, 3, 3]

    """
    return sum([[elt for i in range(repetition)] for elt in lst], [])


def magnify_img(img, rate):
    """ grossi la taille d'un pixel rate fois sur chaque axe

    >>> img_1 = Image.new('RGB', (3, 2), 'white')
    >>> lst_1 = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    >>> img_1.putdata(lst_1)
    >>> img_2 = magnify_img(img_1, 2)
    >>> lst_2 = list(img_2.getdata())
    >>> lst_2 == [(255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 0, 255), (0, 0, 255),
                  (255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 0, 255), (0, 0, 255),
                  (255, 255, 0), (255, 255, 0), (255, 0, 255), (255, 0, 255), (0, 255, 255), (0, 255, 255),
                  (255, 255, 0), (255, 255, 0), (255, 0, 255), (255, 0, 255), (0, 255, 255), (0, 255, 255)]
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


class PhasePortraitGUI:

    def __init__(self, fct, fct_name):
        self.img_size = 575
        self.function = fct
        self.function_name = fct_name
        self.phase_portrait = None  # Will be defined once the user clicked on the Compute button
        self.phase_portrait_to_display = None  # Will be defined once the user clicked on the Draw button
        self.GUI = None  # Will be defined just below

        # Control widgets
        ## window on which the phase portrait is shown
        left_lower = RiemannSphereWidget("Left lower corner:", -20, 20, step=1, value=RiemannSphere(-1, -1))
        right_upper = RiemannSphereWidget("Right upper corner:", -20, 20, step=1, value=RiemannSphere(1, 1))

        ## drawing precision
        text_precision = widgets.HTML(value='<b>Number of pixels per unit:</b>')
        precision_slider = widgets.IntSlider(value=1, min=1, max=500.0, step=1)
        precision = widgets.VBox([text_precision, precision_slider])

        ## information checkbox
        infos = widgets.Checkbox(value=False, description='Information about computation duration',
                                 style={'description_width': 'initial'},
                                 layout=Layout(padding='0px 0px 0px 0px',
                                               margin='40px 0px 0px 0px'
                                               )
                                 )

        ## information text area
        text_output = widgets.Output(layout={'width': '300px'})

        # Output widgets
        ## image zone
        size = (self.img_size, self.img_size)
        img = Image.new('RGB', size, "white")  # create a new white image
        buffer = io.BytesIO()
        img.save(buffer, format='png')  # save the img image in the buffer as an png file
        byte_im = buffer.getvalue()  # is the corresponding binary format of the img image
        image = widgets.Image(value=byte_im,
                              format='png',
                              min_width=self.img_size, max_width=self.img_size,
                              min_height=self.img_size, max_height=self.img_size,
                              style={'description_width': 'initial'},
                              layout=Layout(object_position='center')
                              )

        ## buttons
        buttons = ButtonsAction()
        buttons.add_listeners(self.compute, self.show, self.save)

        # Part of the interactive GUI
        controls_zone = widgets.VBox([left_lower, right_upper, precision, infos, text_output],
                                     layout=Layout(width='33%',
                                                   margin='0px 0px 0px 0px',
                                                   padding='0px 0px 0px 5px',
                                                   border='solid 1px black'
                                                   )
                                     )
        output_zone = widgets.VBox([image, buttons],
                                   layout=Layout(width='63%', height='100%',
                                                 margin='0px 0px 0px 10px',
                                                 padding='0px 0px 0px 5px',
                                                 border='solid 1px black')
                                   )

        # Interactive GUI
        self.GUI = widgets.HBox([controls_zone, output_zone])

        display(self.GUI)

    def compute(self, mybutton):
        a = self.GUI.children[0].children[0].value
        b = self.GUI.children[0].children[1].value
        output = self.GUI.children[0].children[4]
        output.clear_output()
        resolution = self.GUI.children[0].children[2].children[1].value
        infos = self.GUI.children[0].children[3].value
        with output:
            print("Computations started")
            self.phase_portrait = PhasePortrait(self.function, a, b, resolution, information=infos)
            print("Computations finished")

    def show(self, mybutton):
        # Output
        output = self.GUI.children[0].children[4]
        output.clear_output()
        # Draw the image in memory
        with output:
            self.phase_portrait.draw(information=self.GUI.children[0].children[3].value)
        # Image centering
        width, height = self.phase_portrait.size
        if max(width, height) < self.img_size:  # the phase portrait is smaller than the space to display it
            rate = int(self.img_size / max(width, height))
            left = int((self.img_size - rate * width) / 2)
            right = self.img_size - left - rate * width
            top = int((self.img_size - rate * height) / 2)
            bottom = self.img_size - top - rate * height
            self.phase_portrait_to_display = add_space_around(magnify_img(self.phase_portrait.img, rate),
                                                              left, top, right, bottom)
        else:
            self.phase_portrait_to_display = self.phase_portrait.img
        # Now, the phase portrait is too big to be displayed or too big to be magnifies manually
        # so, we resize the image using the resize tool of Image package
        self.phase_portrait_to_display = self.phase_portrait_to_display.resize((self.img_size, self.img_size),
                                                                               Image.ANTIALIAS)
        # Convert the image into a binary format of a png file image to put in an Image widget
        buffer = io.BytesIO()
        self.phase_portrait_to_display.save(buffer, format='png')  # save the img image in the buffer as an png file
        byte_im = buffer.getvalue()  # is the corresponding binary format of the img image
        # Update the image widget
        self.GUI.children[1].children[0].value = byte_im

    def save(self, mybutton):
        output = self.GUI.children[0].children[4]
        output.clear_output()
        infos = self.GUI.children[0].children[3].value
        a = self.GUI.children[0].children[0].value
        b = self.GUI.children[0].children[1].value
        end_name = "_on_" + str(int(a.real)) + '_' + str(int(b.real)) + '_times_' + str(int(a.imaginary)) + '_' + str(
            int(b.imaginary))
        complete_name = self.function_name + end_name + '.png'
        with output:
            self.phase_portrait.save('./', complete_name, information=infos)
        if infos:
            print("Save file", complete_name, "realised")


if __name__ == '__main__':
    from doctest import testmod
    testmod()
