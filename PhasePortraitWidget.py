###########################################################
# Module which define intermediary interactive Jupyter    #
# widgets in order to draw phase portrait of functions    #
# defined in a part of the complex plane C (resp. C x C), #
# and valued in the complex plane                         #
#                                                         #
# Author: Olivier Bouillot                                #
# Email: olivier.bouillot@u-pem.fr                        #
# Creation Date: April 2020                               #
#                                                         #
# Modifications:                                          #
# --------------                                          #
#                                                         #
#  * May 2020: Creates an complete GUI                    #
#  * 01/06/20: Add a TwoDimensionalPhasePortraitGUI class #
#  * 07/06/20: Add logs and log file                      #
#  * 10/07/20: Allows visualization windows to have       #
#              fractionnal size                           #
#                                                         #
# Next modifications to do:                               #
# -------------------------                               #
#                                                         #
#  * Add *arsg and **kwargs to the __init__ method of     #
#    each created classes (see OutputWidgetHandler class) #
#                                                         #
#  * Refactor code between the two following class:       #
#    OneDimensionalPhasePortraitGUI                       #
#    TwoDimensionalPhasePortraitGUI                       #
#                                                         #
#  * When exporting the logs, create a .log file,         #
#  not .txt file                                          #
#                                                         #
#  * Check pylava                                         #
#                                                         #
#  * Save databases and images in a specific directory    #
#                                                         #
###########################################################


from math import log, ceil
from PIL import Image
import ipywidgets as widgets
from ipywidgets import Layout, GridspecLayout
from fractions import Fraction
from RiemannSphere import RiemannSphere
from PhasePortrait import PhasePortrait
from Image_manipulations import display_preparing_of_img, PIL_image_2_byte_im
import logging
import datetime


class ControlZone(widgets.VBox):
    """ Class that create a control zone for our phase portrait visualization
    tool. The control elements are :
    * the dimension (width and height), in unit, of the created image
      that contains the phase portrait
    * the number of pixels per unit, called *precision*
    * the base name of the produced file, when an image is saved
    * the name of the underlying database used to save computed values of
      images of the function whose phase portrait is displayed
    * the information flag which determine if complete detail of computation
      progress are displayed or not

    :attribute step: Fraction
    :attribute width: Fraction
    :attribute width_min: Fraction
    :attribute width_max: Fraction
    :attribute height: Fraction
    :attribute height_min: Fraction
    :attribute height_max: Fraction
    :attribute precision: int
    :attribute saved_file_name: string
    :attribute database_name: string
    :attribute infos: boolean
    """

    def __init__(self, min_max_step, width_min, width_max, height_min, height_max, max_precision,
                 step_observer, width_observer, height_observer,
                 precision_observer, saved_file_name_observer,
                 database_name_observer, infos_observer, default_precision=1,
                 saved_file_name="image", database_name=".sqlite"):
        """ Constructor of the class

        :param min_max_step: int, which encodes the minimal and maximal
                             possible value for the step of the width and height
                             sliders. The step of these sliders are integers or
                             inverse of integers contained in the following set:
                             {1 / min_max_step, 1 / (min_max_step - 1), ..., 1/2}
                             U {1, 2, ..., min_max_step}
        :param width_min: Fraction, which represents the minimal value of
                          the width slider
        :param width_max: Fraction, which represents the maximal value of
                          the width slider
        :param height_min: Fraction, which represents the minimal value of
                           the height slider
        :param height_max: Fraction, which represents the maximal value of
                           the height slider
        :param max_precision: int, which represents the maximal value of
                           the precision slider
        :param step_observer: funcion, which represents the observer of
                              the step observer
        :param width_observer: function, which represents the observer of
                               the width slider
        :param height_observer: function, which represents the observer of
                                the height slider
        :param precision_observer: function, which represents the observer
                                   of the precision slider
        :param saved_file_name_observer: function, which represents the
                                         observer of the prefix name of the
                                         future saving of the phase portrait
        :param database_name_observer: function, which represents the observer
                                       of the database name used to reuse
                                       the already computed values to draw
                                       the required phase portrait
        :param infos_observer: function, which represents the observer of
                               the checkbox about showing or not details
                               about the underlying computations
        :param default_precision: optionnal parameter ot type int ou float, which represents the steps
                                  of the different sliders
        :param saved_file_name: optionnal parameter ot type string, which gives the base of the future names
                                of the .png files that will be created
        :param database_name: optionnal parameter ot type string, which gives the name of the database where
                              the values are saved
        """
        # Initialisation
        super().__init__()
        self.step = Fraction(1)
        self.width_min = width_min
        self.width_max = width_max
        self.height_min = height_min
        self.height_max = height_max
        self.precision = default_precision
        self.saved_file_name = saved_file_name
        self.database_name = database_name
        self.infos = False

        # Widgets relative to the window on which the phase portrait is shown
        html = widgets.HTML(value="<b>Slider's step (in unit):</b>",
                            layout=Layout(padding='0px 0px 0px 5px')
                            )
        opt_before = [Fraction(1, min_max_step - k) for k in range(min_max_step - 1)]
        opt_after = [Fraction(k + 2) for k in range(min_max_step - 1)]
        opt = opt_before + [Fraction(1)] + opt_after
        step_widget_slider = widgets.SelectionSlider(options=opt,
                                                     layout=Layout(height='100%',
                                                                   width='80%'
                                                                   )
                                                     )
        step_widget_slider.index = min_max_step - 1
        step_widget = widgets.VBox([html, step_widget_slider])

        html = widgets.HTML(value="<b>Image width (in unit):</b>",
                            layout=Layout(padding='0px 0px 0px 5px')
                            )
        opt_w = [width_min + i * step_widget_slider.value
                 for i in range(int((width_max - width_min) / step_widget_slider.value) + 1)
                 ]
        width_slider = widgets.SelectionSlider(options=opt_w,
                                               value=opt_w[int(len(opt_w) / 2)],
                                               layout=Layout(height='100%',
                                                             width='80%'
                                                             )
                                               )
        width = widgets.VBox([html, width_slider])
        self.width = width_slider.value

        html = widgets.HTML(value="<b>Image height (in unit):</b>",
                            layout=Layout(padding='0px 0px 0px 5px')
                            )
        opt_h = [height_min + i * step_widget_slider.value
                 for i in range(int((height_max - height_min) / step_widget_slider.value) + 1)
                 ]
        height_slider = widgets.SelectionSlider(options=opt_h,
                                                value=opt_h[int(len(opt_h) / 2)],
                                                layout=Layout(height='100%',
                                                              width='80%'
                                                              )
                                                )
        height = widgets.VBox([html, height_slider])
        self.height = height_slider.value

        html_text_precision = '<b>Number of pixels per unit:</b>'
        text_precision = widgets.HTML(value=html_text_precision,
                                      layout=Layout(padding='0px 0px 0px 5px')
                                      )
        precision_slider = widgets.IntSlider(value=default_precision,
                                             min=1, max=max_precision, step=1,
                                             layout=Layout(height='100%',
                                                           width='80%'
                                                           )
                                             )
        precision = widgets.VBox([text_precision, precision_slider])

        step_widget_slider.observe(self.step_observer, 'value')
        window_zone = widgets.VBox([step_widget, width, height, precision],
                                   layout=Layout(height='auto',
                                                 margin='5px 5px 5px 5px',
                                                 padding='0px 0px 0px 0px',
                                                 border='solid 1px black'
                                                 )
                                   )

        # Widgets relative to the saved file name
        html_text_name = '<b>Prefix name of the png file name:</b>'
        text_name = widgets.HTML(value=html_text_name,
                                 layout=Layout(padding='0px 0px 0px 5px')
                                 )
        if self.saved_file_name == "image":
            text_file_name = "image (no extension needed)"
        else:
            text_file_name = self.saved_file_name
        saved_file_name_input = widgets.Text(value=text_file_name,
                                             placeholder='Type something',
                                             description='',
                                             disabled=False,
                                             layout=Layout(height='100%')
                                             )
        file_name = widgets.VBox([text_name, saved_file_name_input],
                                 layout=Layout(height='auto',
                                               margin='5px 5px 5px 5px',
                                               padding='0px 0px 0px 0px',
                                               border='solid 1px black'
                                               )
                                 )

        # Widgets relative to the name of the underlying database
        html_database = '<b>Name of the underlying database:</b>'
        text_database = widgets.HTML(value=html_database,
                                     layout=Layout(padding='0px 0px 0px 5px')
                                     )
        database_name_input = widgets.Text(value=self.database_name,
                                           placeholder='Type something',
                                           description='',
                                           disabled=False
                                           )
        database = widgets.VBox([text_database, database_name_input],
                                layout=Layout(height='auto',
                                              margin='5px 5px 5px 5px',
                                              padding='0px 0px 0px 0px',
                                              border='solid 1px black'
                                              )
                                )

        # Widgets relative to the information checkbox
        text_infos = 'Information about computation duration'
        infos = widgets.Checkbox(value=False,
                                 description=text_infos,
                                 style={'description_width': 'initial'},
                                 layout=Layout(height='auto',
                                               padding='0px 0px 0px 0px',
                                               margin='40px 0px 40px 0px'
                                               )
                                 )

        # Observe widgets to change attribute values
        step_widget_slider.observe(step_observer, 'value')
        width_slider.observe(width_observer, 'value')
        height_slider.observe(height_observer, 'value')
        precision_slider.observe(precision_observer, 'value')
        saved_file_name_input.observe(saved_file_name_observer, 'value')
        database_name_input.observe(database_name_observer, 'value')
        infos.observe(infos_observer, 'value')

        # Add to children
        self.children = [window_zone, file_name, database, infos]

        # Layout
        self.layout = Layout(margin='0px 0px 0px 0px',
                             padding='0px 0px 0px 0px',
                             border='solid 2px black'
                             )

    def step_observer(self, change):
        # Update the value of the step attribute
        self.step = change['new']
        # Update of the width slider
        self.children[0].children[1].children[1].step = change['new']
        value = self.children[0].children[1].children[1].value
        opt_w_before = [value - i * self.step
                        for i in range(int((value - self.width_min) / self.step) + 1)
                        ]
        opt_w_after = [value + i * self.step
                       for i in range(int((self.width_max - value) / self.step) + 1)
                       ]
        opt_w = opt_w_before[-1:0:-1] + opt_w_after
        self.children[0].children[1].children[1].options = opt_w
        self.children[0].children[1].children[1].index = opt_w.index(value)
        # Update of the height slider
        self.children[0].children[2].children[1].step = change['new']
        value = self.children[0].children[2].children[1].value
        opt_h_before = [value - i * self.step
                        for i in range(int((value - self.height_min) / self.step) + 1)
                        ]
        opt_h_after = [value + i * self.step
                       for i in range(int((self.height_max - value) / self.step) + 1)
                       ]
        opt_h = opt_h_before[-1:0:-1] + opt_h_after
        self.children[0].children[2].children[1].options = opt_h
        self.children[0].children[2].children[1].index = opt_h.index(value)


class Directions(widgets.VBox):
    """ Class that create a widget to allow to move a point represented
    by a RiemannSphere complex point in two dimensions
    The widgets are :
    * four buttons, to move the point
    * a text, which remind the current position of the point, or more
    precisely, the value of the RiemannSphere complex number associated
    to the point

    :attribute name: string representation
    :attribute variable: RiemannSphere complex number, with components of type Fraction,
                         or whatever numerical type
    :attribute step: Fraction, which defines the moving distance when clicking
                     on a utton
    """

    def __init__(self, associated_variable, min_max_step = 10, name=''):
        """ Constructor of the class

        :param associated_variable: a RiemannSphere complex number
                                    (previously defined or not)
        :param min_max_step: int, optional parameter which encodes the minimal
                             and maximal possible value for the step of
                             moving buttons. The step of these sliders are
                             integers or inverse of integers contained in the
                             following set:
                             {1 / min_max_step, 1 / (min_max_step - 1), ..., 1/2}
                             U {1, 2, ..., min_max_step}
        :param name: string, which represents the name of
                     the 'asssociated_variable'
        """
        # Initialisation
        super().__init__()
        self.name = name
        self.variable = associated_variable
        self.step = Fraction(1)

        # Text
        nb_decimales = ceil(log(min_max_step) / log(10))
        multiplier = 10 ** nb_decimales
        z = RiemannSphere(int(multiplier * self.variable.real) / multiplier,
                          int(multiplier * self.variable.imaginary) / multiplier)
        value = self.name + ": " + str(self.variable) + " ≈ " + str(z)
        text = widgets.Label(value=value,
                             layout=Layout(display='flex',
                                           justify_content='center',
                                           margin='0px 0px 0px 0px'
                                           ),
                             )

        # Slider
        html = widgets.HTML(value="Buttons' step:",
                            layout=Layout(width='100%',
                                          padding='0px 0px 0px 0px')
                            )
        opt_before_1 = [Fraction(1, min_max_step - k) for k in range(min_max_step - 1)]
        opt_after_1 = [Fraction(k + 2) for k in range(min_max_step - 1)]
        opt = opt_before_1 + [Fraction(1)] + opt_after_1
        step_widget_slider = widgets.SelectionSlider(options=opt,
                                                     layout=Layout(height='100%',
                                                                   width='200%'
                                                                   )
                                                     )
        step_widget_slider.index = min_max_step - 1
        step = widgets.HBox([html, step_widget_slider],
                            layout=Layout(width='50%',
                                          display='flex',
                                          justify_content='center',
                                          margin='0% 25% 0% 25%'
                                          )
                            )

        # Style
        style = widgets.ButtonStyle(button_color='moccasin')

        # Buttons
        up = widgets.Button(description='Up',
                            style=style,
                            layout=Layout(width='98%',
                                          padding='0px 0px 0px 0px',
                                          border='solid 1px black'
                                          )
                            )
        left = widgets.Button(description='Left',
                              style=style,
                              layout=Layout(width='98%',
                                            padding='0px 0px 0px 0px',
                                            border='solid 1px black'
                                            )
                              )
        right = widgets.Button(description='Right',
                               style=style,
                               layout=Layout(width='98%',
                                             padding='0px 0px 0px 0px',
                                             border='solid 1px black'
                                             )
                               )
        down = widgets.Button(description='Down',
                              style=style,
                              layout=Layout(width='98%',
                                            padding='0px 0px 0px 0px',
                                            border='solid 1px black'
                                            )
                              )

        # Grid
        grid = GridspecLayout(3, 3,
                              width='100%', height='100%',
                              justify_content='center')
        grid[1, 0] = left
        grid[1, 2] = right
        grid[0, 1] = up
        grid[2, 1] = down

        # Observer
        step_widget_slider.observe(self.step_observer, 'value')

        # Connect to listeners
        up.on_click(self.up_function)
        left.on_click(self.left_function)
        right.on_click(self.right_function)
        down.on_click(self.down_function)

        # Add to children
        self.children = [widgets.Box([grid],
                                     layout=Layout(display='flex',
                                                   justify_content='center',
                                                   margin='0% 0% 0% 0%'
                                                   )
                                     ),
                         step,
                         text
                         ]

        # Style and layout
        self.style = {'description_width': 'initial'},
        self.layout = Layout(object_position='center')

    def step_observer(self, change):
        self.step = change['new']

    def up_function(self, b):
        """ Event handler for the Up button.

        When the up button is clicked, the step attribute is added to
        the imaginary part of the associated variable
        """
        self.variable.imaginary += self.step
        self.update_text_widget_value()

    def left_function(self, b):
        """ Event handler for the Left button.

        When the left button is clicked, the step attribute is substracted to
        the real part of the associated variable
        """
        self.variable.real -= self.step
        self.update_text_widget_value()

    def right_function(self, b):
        """ Event handler for the Right button.

        When the right button is clicked, the step attribute is added to
        the real part of the associated variable
        """
        self.variable.real += self.step
        self.update_text_widget_value()

    def down_function(self, b):
        """ Event handler for the Down button.

        When the down button is clicked, the step attribute is substracted to
        the imaginary part of the associated variable
        """
        self.variable.imaginary -= self.step
        self.update_text_widget_value()

    def update_text_widget_value(self):
        """ Update the value of the text widget, after clicking
        on a direction button
        """
        min_max_step = self.children[1].children[1].options[-1]
        nb_decimales = ceil(log(min_max_step) / log(10))
        multiplier = 10 ** nb_decimales
        z = RiemannSphere(int(multiplier * self.variable.real) / multiplier,
                          int(multiplier * self.variable.imaginary) / multiplier)
        text = self.name + ": " + str(self.variable) + " ≈ " + str(z)
        self.children[2].value = text


class ButtonsAction(widgets.HBox):
    """ Class that create three buttons to control the possible actions
    on a phase portrait:
    * compute the necessary values of the function whose phase portrait
      is required
    * show the phase portrait
    * save the phase portrait

    The events associates to the three buttons are linkedt using the method
    'add_listeners(self, compute, show, save)'

    The user has to first click to the'Compute' button, so that the necessary
    image of the function whose phase portrait is required are computed. Then,
    the user has to click on the 'Show' button to display the phase portrait.
    If the user want, the phase portrait image can be saved by clicking on the
    'Save' button.

    :attribute phase_portrait: PhasePortrait, which is initially None, and
                               then constructed when clicking on the three
                               action buttons
    """
    def __init__(self):
        """ Constructor of the class """
        # Initialisation
        super().__init__()
        self.phase_portrait = None

        # Layout
        button_layout = Layout(width='33.3%', height='80px',
                               margin='1px 1px 1px 1px',
                               padding='0px 0px 0px 0px',
                               border='solid 1px black'
                               )

        # Widgets
        end_text = " the phase portrait"
        compute_button = widgets.Button(description="Compute" + end_text,
                                        layout=button_layout,
                                        align_items='center'
                                        )
        show_button = widgets.Button(description="Show" + end_text,
                                     layout=button_layout,
                                     align_items='center'
                                     )
        save_button = widgets.Button(description="Save" + end_text,
                                     layout=button_layout,
                                     align_items='center'
                                     )

        # Add to children
        self.children = [compute_button, show_button, save_button]

        # Layout
        self.layout = Layout(width='90%',
                             margin='0px 5% 0px 5%',
                             padding='0px 0px 0px 0px'
                             )

    def add_listeners(self, compute, show, save):
        """ Method that add the compute parameter to the Compute button of
        the current class, the show parameter to the Show button and
        the save parameter to the Save button

        :param compute: function, which is the listener of
                        the 'Compute the phase portrait' button
        :param show: function, which is the listener of
                     the 'Show the phase portrait' button
        :param save: function, which is the listener of
                     the 'Save the phase portrait' button
        """
        self.children[0].on_click(compute)
        self.children[1].on_click(show)
        self.children[2].on_click(save)


class ImageZone(widgets.VBox):
    """ Class that creates a zone to display phase portraits, i.e.
    a zone whose elements are :
    * an image widget
    * a Direction widget, to be able to move the center of the image

    The method set_image allows to modify the displayed image.

    :attribute image_widget: Image Widget
    """
    def __init__(self, img, available_image_size,
                 associated_variable, direction_str_text,
                 min_max_step=10, name=''):
        """ Constructor of the class

        :param img: PIL image
        :param available_image_size: int, which represents the size in pixel
                                     of the displayed image
        :param associated_variable: a RiemannSphere complex number
                                    (previously defined or not)
        :param direction_str_text: string, which represents the name of
                                   the 'asssociated_variable'
        :param min_max_step: int, optional parameter which encodes the minimal
                             and maximal possible value for the step of
                             the width and height sliders. The step of these
                             sliders are integers or inverse of integers
                             contained in the following set:
                             {1 / min_max_step, 1 / (min_max_step - 1), ..., 1/2}
                             U {1, 2, ..., min_max_step}
        :param step: float, which represents the value of the moving step
                     when a button is clicked
        """
        # Initialisation
        super().__init__()

        # Image
        new_img = display_preparing_of_img(img, available_image_size)
        byte_im = PIL_image_2_byte_im(new_img)
        self.image_widget = widgets.Image(value=byte_im, format='png')
        self.image_widget.style = {'description_width': 'initial'}
        self.image_widget.layout = Layout(object_position='center',
                                          object_fit='contain',
                                          height='65%'
                                          )

        # Buttons
        buttons = Directions(associated_variable, min_max_step=min_max_step,
                             name=direction_str_text)
        buttons.layout = Layout(height='35%')

        # Add to children
        if name != '':
            html_text = '<span style = "text-decoration: underline;">' +\
                        '<p style="text-align:center">' + name + '</p>' + \
                        '</span>'
            self.children = [widgets.HTML(value=html_text,
                                          object_position='center',
                                          object_fit='contain',
                                          ),
                             self.image_widget, buttons]
        else:
            self.children = [self.image_widget, buttons]
        self.layout = Layout(margin='1% 1% 0% 1%',
                             padding='0px 0px 0px 0px',
                             border='solid 1px black',
                             object_position='center'
                             )
        self.style = {'description_width': 'initial'}

    def set_image(self, img):
        """ Setter for PIL image of the class

        :param img: PIL image
        """
        self.image_widget.value = PIL_image_2_byte_im(img)


class MainZone(widgets.AppLayout):
    """ Class that creates a main zone to display phase portraits, i.e.
    a zone whose elements are :
    * an image zone
    * action buttons

    The method add_listeners allows to connect the three listeners to each
    action button. The method get_image/set_image allows to get/modify
    the image zone.
    """

    def __init__(self):
        """ Constructor of the class """
        # Initialisation
        super().__init__()

        # Widgets
        self.center = widgets.VBox(layout=Layout(height='600px'))
        self.footer = ButtonsAction()
        self.footer.layout.align_items = 'center'

        # Layout
        self.layout = Layout(margin='0px 0px 0px 1%',
                             padding='0px 0px 0px 0px',
                             border='solid 2px black'
                             )
        # Sizes
        self.pane_widths = ['33.33%', '33.33%', '33.33%']
        self.pane_heights = ['0%', '84%', '16%']

    def add_listeners(self, compute, show, save):
        """ Method that connect the three listeners given in parameters to
        the action buttons

        :param compute: function, which is the listener of
                        the 'Compute the phase portrait' button
        :param show: function, which is the listener of
                     the 'Show the phase portrait' button
        :param save: function, which is the listener of
                     the 'Save the phase portrait' button
        """
        self.footer.add_listeners(compute, show, save)

    def get_image_zone(self):
        """ Getter for image zone of the class """
        return self.center

    def set_image_zone(self, widget):
        """ Getter for image zone of the class

        :param widget: a priori an ImageZone widget, or a HBox of ImageZone
                       widgets, but could be any Jupyter Widget
        """
        self.center = widget


class OutputWidgetHandler(logging.Handler):
    """ Custom logging handler sending logs to an output widget

    Rmk: 90% of this code is coming from the Jupyter widgets documentation:
         https://ipywidgets.readthedocs.io/en/latest/examples/Output%20Widget.html
    """

    def __init__(self, *args, **kwargs):
        """ Constructor of the class """
        super(OutputWidgetHandler, self).__init__(*args, **kwargs)
        layout = {
            'width': '100%',
            'height': '120px'
        }
        self.out = widgets.Output(layout=layout)

    def emit(self, record):
        """ Overload of logging.Handler method

        :param record: logging.LogRecord
        """
        formatted_record = self.format(record)
        new_output = {
            'name': 'stdout',
            'output_type': 'stream',
            'text': formatted_record + '\n'
        }
        self.out.outputs = (new_output,) + self.out.outputs

    def get_outputs(self):
        """ Export the logs

        :return value: String
        """
        lst = []
        for dico in self.out.outputs:
            # The dico iterator is a record of the logs. It could be an Info, a warning, an error, ...
            # It is something like:
            # {'output_type': 'stream' or 'error', ...
            if dico['output_type'] == 'stream':
                # Add a tabulation at the begining of each line, except the first one,
                # if the record is longer than a line
                lst.append(dico['text'][:-2].replace('\n', '\n\t') + '\n')
            elif dico['output_type'] == 'error':
                for line in dico['traceback']:
                    for c in ['\x1b[0;31m', '\x1b[0;32m', '\x1b[1;32m', '\x1b[0;34m', '\x1b[0;36m', '\x1b[0m']:
                        line = line.replace(c, '')
                    lst.append(line + '\n')
        return ''.join(lst)

    def clear_logs(self):
        """ Clear the current logs """
        self.out.clear_output()


class Logs(widgets.AppLayout):
    """ Class that creates a log zone, i.e. a zone whose main element
    is an Output Widget

    :attribute data_logger: logging.Logger
    :attribute output: OutputWidgetHandler
    """

    def __init__(self, log_file_name):
        """ Constructor of the class

        :attribute data_logger: loggingLogger
        :attribute output: OutputWidgetHandler
        :attribute log_file_name: string
        """
        # Initialization
        super().__init__()
        self.log_file_name = log_file_name

        # Widgets
        text = widgets.HTML(value='<b>Logs:</b>',
                            layout=Layout(padding="0px 0px 0px 5px")
                            )
        self.data_logger = logging.getLogger(__name__)
        self.output = OutputWidgetHandler()
        msg = '%(asctime)s  - [%(levelname)s] %(message)s'
        self.output.setFormatter(logging.Formatter(msg))
        self.data_logger.addHandler(self.output)
        self.data_logger.setLevel(logging.INFO)
        print_state_button = widgets.Button(description='Print control datas',
                                            layout=Layout(padding='0px 0px 0px 0px',
                                                          margin='0px 10% 0px 10%',
                                                          border="solid 1px black"
                                                          )
                                            )
        export_button = widgets.Button(description='Export the logs',
                                       layout=Layout(padding='0px 0px 0px 0px',
                                                     margin='0px 10% 0px 10%',
                                                     border="solid 1px black"
                                                     )
                                       )

        # Add listener to the button
        export_button.on_click(self.export)

        # ApplLayout predefined zones
        self.left_sidebar = text
        self.center = self.output.out
        self.footer = widgets.HBox([print_state_button, export_button],
                                   layout=Layout(width='50%',
                                                 margin='0% 25% 0% 25%',
                                                 display='flex',
                                                 justify_content='center'
                                                 )
                                   )

        # Sizes
        self.pane_widths = ['5%', '95%', '0%']
        self.pane_heights = ['0%', '80%', '20%']
        self.layout.border = 'solid 2px black'
        self.layout.margin = '0.5% 0px 0px 0%'

    def add_print_state_button_listener(self, listener):
        self.footer.children[0].on_click(listener)

    def export(self, button):
        """ Export the logs into a text file """
        t = str(datetime.datetime.utcnow())
        export_time = t.replace(' ', '_').replace(':', '-').split('.')[0]
        if len(self.log_file_name) >= 4 and self.log_file_name[-4:] == '.txt':
            f = open(self.log_file_name[:-4] + '_' + export_time + '.txt', 'w')
        else:
            f = open(self.log_file_name + '_' + export_time + '.txt', 'w')
        try:
            f.write(self.output.get_outputs())
        except:
            self.data_logger.exception('An error occurred while exporting logs!')
        f.close()


class PhasePortraitApp(widgets.AppLayout):
    """ Class that creates the skeleton of the Graphical User Interface (GUI)
    to display phase portraits. The GUI contains four zone:
    * a name (the header of the GUI)
    * a control zone (the left sidebar of the GUI)
    * a main zone (typically. an image zone or two, with beside it,
                  action buttons)
    * a log zone (the footer of the GUI)

    The method add_listeners allows to connect the three listeners to each
    action button. The method get_image/set_image allows to get/modify
    the image zone.

    :attribute img_width: int
    :attribute img_height: int
    :attribute precision: int
    :attribute saved_file_name: String
    :attribute database_name: String
    :attribute infos: bool
    :attribute data_logger: logging.Logger
    :attribute output: Output Jupyter Widget
    """
    def __init__(self, app_name, log_file_name,
                 min_max_step=10,
                 min_width=1, max_width=10,
                 min_height=1, max_height=10,
                 default_precision=5, max_precision=100,
                 saved_file_name="image", database_name=".sqlite"):
        """ Constructor of the class

        :param app_name: string, which represents the name of
                         the Graphical User Interface (GUI) the developper
                         is currently developping
        :param log_file_name: string, which represents the base name
                              of the files where the logs could be saved
        :param min_max_step: int, optional parameter which encodes the minimal
                             and maximal possible value for the step of
                             the width and height sliders, as well as the step
                             of moving buttons. The step of these
                             sliders are integers or inverse of integers
                             contained in the following set:
                             {1 / min_max_step, 1 / (min_max_step - 1), ..., 1/2}
                             U {1, 2, ..., min_max_step}
        :param width_min: int, optional parameter which represents the minimal
                          value of the width slider
        :param width_max: int, optional parameter which represents the maximal
                          value of the width slider
        :param height_min: int, optional parameter which represents the minimal
                           value of the height slider
        :param height_max: int, optional parameter which represents the maximal
                           value of the height slider
        :param default_precision: int, optional parameter which represents
                                  the number of pixels per unit in the required
                                  phase portrait
        :param max_precision: int, optional parameter which represents
                              the maximal value of the precision slider, i.e.
                              the number of pixels per unit in the required
                              phase portrait
        :param saved_file_name: string, optionnal parameter which gives the base of the future names
                                of the .png files that will be created
        :param database_name: string, optionnal parameter which gives the name of the database where
                              the values are saved
        """
        # Initialisation
        super().__init__()

        # Control_zone
        control_zone = ControlZone(min_max_step, min_width, max_width, min_height, max_height,
                                   max_precision,
                                   self.step_observer, self.width_observer, self.height_observer,
                                   self.precision_observer,
                                   self.saved_file_name_observer,
                                   self.database_name_observer,
                                   self.infos_observer, default_precision=default_precision,
                                   saved_file_name=saved_file_name, database_name=database_name
                                   )
        self.step = control_zone.step
        self.img_width = control_zone.width
        self.img_height = control_zone.height
        self.precision = control_zone.precision
        self.saved_file_name = control_zone.saved_file_name
        self.database_name = control_zone.database_name
        self.infos = control_zone.infos

        # Main zone
        main_zone = MainZone()

        # Logs
        logs = Logs(log_file_name)
        self.data_logger = logs.data_logger
        self.output = logs.output
        logs.add_print_state_button_listener(self.print_control_datas_listener)

        # ApplLayout predefined zones
        self.header = self.create_HTML(app_name)
        self.left_sidebar = control_zone
        self.center = main_zone
        self.footer = logs

        # Sizes
        self.pane_widths = ['33%', '66%', '0%']
        self.pane_heights = ['5%', '75%', '20%']
        self.height = "830px"

    def create_HTML(self, text):
        """ Method that create an HTML widget with a bold text

        :param text: String
        """
        bold_text = '<b><p style="text-align:center">' + text + '</p></b>'
        return widgets.HTML(value=bold_text,
                            layout=Layout(width='100%',
                                          margin='0px 0px 0.5% 0%',
                                          padding='0px 0px 0px 0px',
                                          border='solid 2px black'
                                          )
                            )

    # Listeners
    def print_control_datas_listener(self, button):
        msg = "Current datas are:" + \
              "\n\tControl zone:" + \
              "\n\t\tSlider's step = " + str(self.step) + \
              "\n\t\tImage width (in unit) = " + str(self.img_width) + \
              "\n\t\tImage height (in unit) = " + str(self.img_height) +  \
              "\n\t\tNumber of pixels per unit = " + str(self.precision) + \
              '\n\t\tPrefix name of the png file = "' + str(self.saved_file_name) + '"'\
              '\n\t\tName of the underlying database = "' + str(self.database_name) + '"'\
              "\n\t\tInformation about computation duration = " + str(self.infos) + \
              "\n\tMain Zone:" + \
              "\n\t\tMoving step = " + str(self.center.get_image_zone().children[1].step) + \
              "\n\t\tPosition of the center of the image = " + str(self.center.get_image_zone().children[1].variable) + " "
        self.data_logger.info(msg)

    # Control observers
    def step_observer(self, change):
        """ Observer of the step parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        self.step = change['new']

    def width_observer(self, change):
        """ Observer of the width parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        self.img_width = change['new']

    def height_observer(self, change):
        """ Observer of the height parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        self.img_height = change['new']

    def precision_observer(self, change):
        """ Observer of the precision parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        self.precision = change['new']

    def saved_file_name_observer(self, change):
        """ Observer of the saved_file_name parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        if len(change['new']) >= 4 and change['new'][-4:] == '.png':
            self.saved_file_name = change['new'][:-4]
        else:
            self.saved_file_name = change['new']

    def database_name_observer(self, change):
        """ Observer of the database name parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        if len(change['new']) >= 7 and change['new'][-7:] == '.sqlite':
            self.database_name = change['new']
        else:
            self.database_name = change['new'] + '.sqlite'

    def infos_observer(self, change):
        """ Observer of the infos parameter of the control zone of
        the parent class

        :param change: dictionnary
        """
        self.infos = change['new']

    # Connect main zone buttons to listeners
    def add_listeners(self, compute, show, save):
        """ Method that connect the three listeners given in parameters to
        the action buttons of the main zone

        :param compute: function, which is the listener of
                        the 'Compute the phase portrait' button
        :param show: function, which is the listener of
                     the 'Show the phase portrait' button
        :param save: function, which is the listener of
                     the 'Save the phase portrait' button
        """
        self.center.add_listeners(compute, show, save)

    def get_image_zone(self):
        return self.center.get_image_zone()

    def set_image_zone(self, widget):
        self.center.set_image_zone(widget)


class OneDimensionalPhasePortraitGUI(PhasePortraitApp):
    """ Class that extends the PhasePortraitApp class in order to have
    a one dimensionnal GUI to draw phase portrait of function defined
    over (a part of) the complex plane, and valued in the complex plane

    The GUI contains four zone:
    * a name (the header of the GUI)
    * a control zone (the left sidebar of the GUI)
    * an image zone with beside it, action buttons
    * a log zone (the footer of the GUI)

    :attribute function: function, which represents the function whose phase
                         portrait is required
    :attribute center_position: RiemannSphere complex number, which represents
                                the center of the phase portrait
    :attribute phase_portrait: PhasePortrait, which contains the datas of
                               the required phase portrait
    :attribute img_to_display: PIL image, which represents the displayed
                               image of the phase portrait
    :attribute img_size: int, which represents in pixel the size of
                         the displayed image
    :attribute img_width: int
    :attribute img_height: int
    :attribute precision: int
    :attribute saved_file_name: String
    :attribute database_name: String
    :attribute infos: bool
    :attribute output: Output Jupyter Widget
    """
    def __init__(self, function, center_pos=RiemannSphere(0, 0),
                 min_max_step=10,
                 min_width=1, max_width=10,
                 min_height=1, max_height=10,
                 default_precision=5, max_precision=100,
                 saved_file_name="image", database_name=".sqlite"):
        """ Constructor of the class

        :param function: function, which represents the function whose
                         phase portrait is required
        :param center_pos: RiemannSphere complex number, which represents
                           the center of the phase portrait
        :param min_max_step: int, optional parameter which encodes the minimal
                             and maximal possible value for the step of
                             the width and height sliders, as well as the step
                             of moving buttons. The step of these
                             sliders are integers or inverse of integers
                             contained in the following set:
                             {1 / min_max_step, 1 / (min_max_step - 1), ..., 1/2}
                             U {1, 2, ..., min_max_step}
        :param width_min: int, optional parameter which represents the minimal
                          value of the width slider
        :param width_max: int, optional parameter which represents the maximal
                          value of the width slider
        :param height_min: int, optional parameter which represents the minimal
                           value of the height slider
        :param height_max: int, optional parameter which represents the maximal
                           value of the height slider
        :param default_precision: int, optional parameter which represents
                                  the number of pixels per unit in the required
                                  phase portrait
        :param max_precision: int, optional parameter which represents
                              the maximal value of the precision slider, i.e.
                              the number of pixels per unit in the required
                              phase portrait
        :param saved_file_name: string, optionnal parameter which gives the base of the future names
                                of the .png files that will be created
        :param database_name: string, optionnal parameter which gives the name of the database where
                              the values are saved
        """
        # Initialization
        super().__init__('One dimensional phase portrait visualization tool', 'LOGS_1D',
                         min_max_step=min_max_step,
                         min_width=min_width, max_width=max_width,
                         min_height=min_height, max_height=max_height,
                         default_precision=default_precision, max_precision=max_precision,
                         saved_file_name=saved_file_name, database_name=database_name)
        self.img_size = 575
        self.function = function
        self.center_position = center_pos
        self.phase_portrait = None  # defined by clicking the Compute button
        self.img_to_display = None  # defined by clicking the Draw button

        # Main Zone
        width = int(self.img_width * self.precision + 1)
        height = int(self.img_height * self.precision + 1)
        img = Image.new('RGB', (width, height), "white")
        image_zone = ImageZone(img, 385, self.center_position,
                               "Position of the center of the image",
                               min_max_step
                               )
        self.set_image_zone(image_zone)

        # Add listeners
        self.add_listeners(self.compute, self.show, self.save)

    def compute(self, button):
        """ Event handler for the "Compute the phase portrait" button
        which encapsulates the initialization of the phase portrait attribute

        :param button: Button Jupyter Widget
        """
        # Check if there is an integer number of pixel in the required phase portrait
        height = self.img_height * self.precision + 1
        if self.precision % self.img_height.denominator != 0:
            text = "Impossible to construct the required phase portrait: " +\
                   "its height need to have " + str(float(height)) + " pixels..., " +\
                   "which is not an integer number of pixels!"
            self.data_logger.error(text)
            return
        width = self.img_width * self.precision + 1
        if self.precision % self.img_width.denominator != 0:
            text = "Impossible to construct the required phase portrait: " +\
                   "its width need to have " + str(float(width)) + " pixels..., " +\
                   "which is not an integer number of pixels!"
            self.data_logger.error(text)
            return
        # Computation of the required values
        re_min = self.center_position.real - self.img_width / 2
        re_max = self.center_position.real + self.img_width / 2
        im_min = self.center_position.imaginary - self.img_height / 2
        im_max = self.center_position.imaginary + self.img_height / 2
        a = RiemannSphere(re_min, im_min)
        b = RiemannSphere(re_max, im_max)
        with self.output.out:
            self.data_logger.info('"Compute" button pushed ')
            if self.database_name == ".sqlite":
                database_name = ""
            else:
                database_name = self.database_name
            self.phase_portrait = PhasePortrait(self.function, a, b,
                                                self.precision,
                                                information=self.infos,
                                                database=database_name,
                                                data_logger=self.data_logger
                                                )

    def show(self, button):
        """ Event handler for the "Show the phase portrait" button
        which encapsulates the draw method of the phase portrait attribute

        :param button: Button Jupyter Widget
        """
        with self.output.out:
            self.data_logger.info('"Show" button pushed ')
            # Draw the image in memory
            self.phase_portrait.draw(information=self.infos)
            # Image centering
            img = display_preparing_of_img(self.phase_portrait.img,
                                           self.img_size
                                           )
            self.img_to_display = img
            # Image insertion in the Image widget
            self.get_image_zone().set_image(self.img_to_display)
            if not self.infos:
                self.data_logger.info("Image displayed ")

    def save(self, button):
        """ Event handler for the "Save the phase portrait" button
        which encapsulates the save method of the phase portrait attribute

        :param button: Button Jupyter Widget
        """
        a = RiemannSphere(self.center_position.real - self.img_width / 2,
                          self.center_position.imaginary - self.img_height / 2)
        b = RiemannSphere(self.center_position.real + self.img_width / 2,
                          self.center_position.imaginary + self.img_height / 2)
        if self.saved_file_name == "image (no extension needed)":
            saved_file_name = "image"
        else:
            saved_file_name = self.saved_file_name
        end_name = "_on_" + str(int(a.real * 100) / 100) + '_' + str(int(b.real * 100) / 100) + \
                   '_times_' + \
                   str(int(a.imaginary * 100) / 100) + '_' + str(int(b.imaginary * 100) / 100)
        complete_name = saved_file_name + end_name + '.png'
        with self.output.out:
            self.data_logger.info('"Save" button pushed ')
            self.phase_portrait.save('./', complete_name,
                                     information=self.infos)
            self.data_logger.info("Phase portrait saved in file:\n\n" +
                                  ' ' * 34 + complete_name.center(50) + '\n\n')


class TwoDimensionalPhasePortraitGUI(PhasePortraitApp):
    """ Class that extends the PhasePortraitApp class in order to have
    a two dimensionnal GUI to draw phase portrait of function defined
    over (a part of) C x C, and valued in the complex plane C

    The GUI contains four zone:
    * a name (the header of the GUI)
    * a control zone (the left sidebar of the GUI)
    * an image zone with beside it, action buttons
    * a log zone (the footer of the GUI)

    :attribute function: function, which represents the function whose partial
                         function phase portraits are required
    :attribute z_one: RiemannSphere complex number, which represents
                      the center of the phase portrait of the first partial
                      function
    :attribute z_two: RiemannSphere complex number, which represents
                      the center of the phase portrait of the second partial
                      function
    :attribute phase_portrait_one: PhasePortrait, which contains the datas of
                                   the phase portrait of the first partial
                                   function
    :attribute phase_portrait_two: PhasePortrait, which contains the datas of
                                   the phase portrait of the second partial
                                   function
    :attribute img_to_display_one: PIL image, which represents the displayed
                                   image of the phase portrait of the first
                                   phase portrait
    :attribute img_to_display_two: PIL image, which represents the displayed
                                   image of the phase portrait of the second
                                   phase portrait
    :attribute img_size: int, which represents in pixel the size of
                         the displayed image
    :attribute img_width: int
    :attribute img_height: int
    :attribute precision: int
    :attribute saved_file_name: String
    :attribute database_name: String
    :attribute infos: bool
    :attribute output: Output Jupyter Widget
    """
    def __init__(self, function,
                 z_one=RiemannSphere(0, 0), z_two=RiemannSphere(0, 0),
                 min_max_step=10,
                 min_width=1, max_width=10,
                 min_height=1, max_height=10,
                 default_precision=5, max_precision=100):
        """ Constructor of the class

        :param function: function, which represents the function whose partial
                         phase portraits are required
        :param z_one: RiemannSphere complex number, which represents
                      the center of the phase portrait of the first
                      phase portrait
        :param z_two: RiemannSphere complex number, which represents
                      the center of the phase portrait of the second
                      phase portrait
        :param min_max_step: int, optional parameter which encodes the minimal
                             and maximal possible value for the step of
                             the width and height sliders, as well as the step
                             of moving buttons. The step of these
                             sliders are integers or inverse of integers
                             contained in the following set:
                             {1 / min_max_step, 1 / (min_max_step - 1), ..., 1/2}
                             U {1, 2, ..., min_max_step}
        :param width_min: int, optional parameter which represents the minimal
                          value of the width slider
        :param width_max: int, optional parameter which represents the maximal
                          value of the width slider
        :param height_min: int, optional parameter which represents the minimal
                           value of the height slider
        :param height_max: int, optional parameter which represents the maximal
                           value of the height slider
        :param default_precision: int, optional parameter which represents
                                  the number of pixels per unit in the required
                                  phase portrait
        :param max_precision: int, optional parameter which represents
                              the maximal value of the precision slider, i.e.
                              the number of pixels per unit in the required
                              phase portrait
        """
        # Initialization
        super().__init__('Two dimensional phase portrait visualization tool', 'LOGS_2D',
                         min_max_step=min_max_step,
                         min_width=min_width, max_width=max_width,
                         min_height=min_height, max_height=max_height,
                         default_precision=default_precision, max_precision=max_precision)
        self.img_size = 575
        self.function = function
        self.z_one = z_one
        self.z_two = z_two
        self.phase_portrait_one = None  # defined by clicking on 'Compute'
        self.phase_portrait_two = None  # defined by clicking on 'Compute'
        self.img_to_display_one = None  # defined by clicking on 'Draw'
        self.img_to_display_two = None  # defined by clicking on 'Draw'

        # Main Zone
        width = self.img_width * self.precision + 1
        height = self.img_height * self.precision + 1
        generic_name = "Position of the center of the phase portrait"
        img_one = Image.new('RGB', (width, height), "white")
        name = 'Phase portrait of the 1st partial function'
        image_zone_one = ImageZone(img_one, 385, self.z_one, generic_name,
                                   step=1, name=name
                                   )
        img_two = Image.new('RGB', (width, height), "white")
        name = 'Phase portrait of the 1st partial function'
        image_zone_two = ImageZone(img_two, 385, self.z_two, generic_name,
                                   step=1, name=name
                                   )
        image_zone = widgets.HBox([image_zone_one, image_zone_two])
        self.set_image_zone(image_zone)

        # Add listeners
        self.add_listeners(self.compute, self.show, self.save)

    def compute(self, button):
        """ Event handler for the "Compute the phase portrait" button
        which encapsulates the initialization of the phase portrait attribute

        :param button: Button Jupyter Widget
        """
        # Computation of the required values
        re_min_one = int(self.z_one.real - self.img_width / 2)
        re_max_one = int(self.z_one.real + self.img_width / 2)
        im_min_one = int(self.z_one.imaginary - self.img_height / 2)
        im_max_one = int(self.z_one.imaginary + self.img_height / 2)
        a = RiemannSphere(re_min_one, im_min_one)
        b = RiemannSphere(re_max_one, im_max_one)

        re_min_two = int(self.z_two.real - self.img_width / 2)
        re_max_two = int(self.z_two.real + self.img_width / 2)
        im_min_two = int(self.z_two.imaginary - self.img_height / 2)
        im_max_two = int(self.z_two.imaginary + self.img_height / 2)
        c = RiemannSphere(re_min_two, im_min_two)
        d = RiemannSphere(re_max_two, im_max_two)
        with self.output.out:
            self.data_logger.info('"Compute" button pushed')
            if self.database_name == ".sqlite":
                database_name = ""
            else:
                database_name = self.database_name
            self.data_logger.info("First phase portrait computations started")
            def partial_one(z):
                return self.function(z, self.z_two)
            self.phase_portrait_one = PhasePortrait(partial_one,
                                                    a, b,
                                                    self.precision,
                                                    information=self.infos,
                                                    database=database_name,
                                                    data_logger=self.data_logger
                                                    )
            self.data_logger.info("Second phase portrait computations started")
            def partial_two(z):
                return self.function(self.z_one, z)
            self.phase_portrait_two = PhasePortrait(partial_two,
                                                    c, d,
                                                    self.precision,
                                                    information=self.infos,
                                                    database=database_name,
                                                    data_logger=self.data_logger
                                                    )
            if not self.infos:
                self.data_logger.info("Computations finished")

    def show(self, button):
        """ Event handler for the "Show the phase portrait" button
        which encapsulates the draw method of the phase portrait attribute

        :param button: Button Jupyter Widget
        """
        with self.output.out:
            self.data_logger.info('"Show" button pushed')
            # Draw the image in memory
            self.data_logger.info("First phase portrait drawing started")
            self.phase_portrait_one.draw(information=self.infos)
            self.data_logger.info("Second phase portrait drawing started")
            self.phase_portrait_two.draw(information=self.infos)
            # Image centering
            img_one = display_preparing_of_img(self.phase_portrait_one.img,
                                               self.img_size
                                               )
            self.img_to_display_one = img_one
            img_two = display_preparing_of_img(self.phase_portrait_two.img,
                                               self.img_size
                                               )
            self.img_to_display_two = img_two
            # Image insertion in the Image widget
            images_zone = self.get_image_zone().children
            images_zone[0].set_image(self.img_to_display_one)
            images_zone[1].set_image(self.img_to_display_two)
            if not self.infos:
                self.data_logger.info("Images displayed")

    def save(self, button):
        """ Event handler for the "Save the phase portrait" button
        which encapsulates the save method of the phase portrait attribute

        :param button: Button Jupyter Widget
        """
        # Computation of the required values
        re_min_one = self.z_one.real - self.img_width / 2
        re_max_one = self.z_one.real + self.img_width / 2
        im_min_one = self.z_one.imaginary - self.img_height / 2
        im_max_one = self.z_one.imaginary + self.img_height / 2
        a = RiemannSphere(re_min_one, im_min_one)
        b = RiemannSphere(re_max_one, im_max_one)

        re_min_two = self.z_two.real - self.img_width / 2
        re_max_two = self.z_two.real + self.img_width / 2
        im_min_two = self.z_two.imaginary - self.img_height / 2
        im_max_two = self.z_two.imaginary + self.img_height / 2
        c = RiemannSphere(re_min_two, im_min_two)
        d = RiemannSphere(re_max_two, im_max_two)
        # Names of the saved files
        if self.saved_file_name == "image (no extension needed)":
            saved_file_name = "image"
        else:
            saved_file_name = self.saved_file_name
        end_name_one = "_-_1st_partial_function_-_on_" +\
                       str(int(a.real * 100) / 100) + '_' + str(int(b.real * 100) / 100) + \
                       "_times_" + \
                       str(int(a.imaginary * 100) / 100) + '_' + str(int(b.imaginary * 100) / 100)
        complete_name_one = saved_file_name + end_name_one + '.png'
        end_name_two = "_-_2st_partial_function_-_on_" +\
                       str(int(c.real * 100) / 100) + '_' + str(int(d.real * 100) / 100) + \
                       "_times_" + \
                       str(int(c.imaginary * 100) / 100) + '_' + str(int(d.imaginary * 100) / 100)
        complete_name_two = saved_file_name + end_name_two + '.png'
        with self.output.out:
            self.data_logger.info('"Save" button pushed')
            self.phase_portrait_one.save('./', complete_name_one,
                                         information=self.infos)
            self.phase_portrait_two.save('./', complete_name_two,
                                         information=self.infos)
            self.data_logger.info("Phase portrait of the first partial " +
                                  "function saved in file:\n\n" + " " * 34 +
                                  complete_name_one.center(50) + '\n')
            self.data_logger.info("Phase portrait of the second partial " +
                                  "function saved in file:\n\n" + " " * 34 +
                                  complete_name_two.center(50) + '\n')


if __name__ == '__main__':
    from doctest import testmod
    testmod()
