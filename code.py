# TODO: Fill out header
# TODO: Add option to input time for cleaning process which will then switch to
# Clean when done.
# TODO: Update images to be cleaner.
# TODO: Add documentation
# TODO: Add sound when cleaning is done
# TODO: Possibly change font
# TODO: Display time left on cleaning page
import time
import displayio
import terminalio
from adafruit_magtag.magtag import MagTag
import storage
from supervisor import runtime

# Try to mount root if USB is not connected.
try:
    storage.remount('/', False)
except:
    pass


# Define classes
class Button:
    def __init__(self, label, pos, index):
        self.label = label
        self.pos = pos
        self.index = index
        self.set_label()

    def set_label(self):
        magtag.add_text(
            text_font = terminalio.FONT,
            text_position = (self.pos, 120),
            text_scale = 1,
            )
        magtag.set_text(self.label, self.index, False)

    def change_label(self, label):
        magtag.set_text(label, self.index, False)


class Screen:
    current_screen = None
    def __init__(self, title, image, index, title_pos, title_scale):
        self.title = title
        self.index = index
        self.title_pos = title_pos
        self.title_scale = title_scale
        self.image = image
        current_screen = index
        self.button_a_label = ''
        self.button_b_label = ''
        self.button_c_label = ''
        self.button_d_label = ''

        self.set_title()

    def set_buttons(self, button_a_label, button_b_label, button_c_label,
    button_d_label):
        self.button_a_label = button_a_label
        self.button_b_label = button_b_label
        self.button_c_label = button_c_label
        self.button_d_label = button_d_label

    def change_screen(self):
        Screen.current_screen = self.index
        self.change_image()
        self.set_title()
        self.change_buttons()
        magtag.refresh()
        blink(self.blink_color, self.blink_count)

    def change_image(self):
        magtag.graphics.set_background(self.image)


    def change_buttons(self):
        button_a.change_label(self.button_a_label)
        button_b.change_label(self.button_b_label)
        button_c.change_label(self.button_c_label)
        button_d.change_label(self.button_d_label)

    def set_title(self):
        magtag.add_text(
            text_font = terminalio.FONT,
            text_position = (self.title_pos, (magtag.graphics.display.height // 2) - 1),
            text_scale = self.title_scale,
        )
        magtag.set_text(self.title, self.index, False)

        # Clears all other titles except for the one for the current screen.
        try:
            for i in range(50):
                if i != self.index:
                    magtag.set_text('', i, False)
        except:
            pass

    def set_blink(self, color, count):
        self.blink_color = color
        self.blink_count = count


# Define functions
def blink(color, count):
    """
    Blinks the LEDs for on the Magtag for the given color and number of times.

    ;param color: Color that the LED will blink.
    ;type color: str
    ;param count: Number of times you want the LEDs to blink.
    ;type count: int
    """
    for i in range(count):
        magtag.peripherals.neopixel_disable = False
        magtag.peripherals.neopixels.fill(color)
        time.sleep(0.5)
        magtag.peripherals.neopixel_disable = True
        time.sleep(0.5)

def timer_read():
    try:
        with open('timer.txt', 'r') as timer_file:
            timer_amount = timer_file.read()
    except:
        timer_amount = default_timer

    return timer_amount

def timer_write():
    with open('timer.txt', 'x') as timer_file:
            timer_file.write(timer_amount)

# Main initialization
magtag = MagTag()
default_timer = 3600
timer_amount = timer_read()

# Color codes
RED = 0x880000
GREEN = 0x00FF00
BLUE = 0x000088
YELLOW = 0x884400
CYAN = 0x0088BB
MAGENTA = 0x9900BB
WHITE = 0xFFFFFF

# Set image paths
Genie_image = './bmps/Dish_Genie.bmp'
dirty_dishes_image = './bmps/DirtyDishes.bmp'
clean_dishes_image = './bmps/CleanDishes.bmp'

# Create buttons
button_a = Button('', 5, 0)
button_b = Button('', 75, 1)
button_c = Button('', 155, 2)
button_d = Button('', 225, 3)

# Create screens
main_screen = Screen('Dish Genie', Genie_image, 4, 100, 3)
main_screen.set_buttons('Dirty', 'Settings', 'Clean', 'Cleaning')
main_screen.set_blink(BLUE, 1)

dirty_screen = Screen('Dirty', dirty_dishes_image, 5, 125, 5)
dirty_screen.set_buttons('Dirty', 'Settings', 'Clean', 'Cleaning')
dirty_screen.set_blink(RED, 2)

settings_screen = Screen('Timer:', WHITE, 6, 10, 3)
settings_screen.set_buttons('Home', '+1 hr', '+30 Min', 'Reset')
settings_screen.set_blink(MAGENTA, 1)

cleaning_screen = Screen('Cleaning', clean_dishes_image, 7, 5, 4)
cleaning_screen.set_buttons('Dirty', 'Settings', 'Clean', 'Cleaning')
cleaning_screen.set_blink(YELLOW, 3)

clean_screen = Screen('Clean', clean_dishes_image, 8, 5, 5)
clean_screen.set_buttons('Dirty', 'Settings', 'Clean', 'Cleaning')
clean_screen.set_blink(GREEN, 5)

main_screen.change_screen()

# Main loop
while True:
    if magtag.peripherals.button_a_pressed and Screen.current_screen != settings_screen.index:
        dirty_screen.change_screen()

    if magtag.peripherals.button_a_pressed and Screen.current_screen == settings_screen.index:
        main_screen.change_screen()

    if magtag.peripherals.button_b_pressed and Screen.current_screen != settings_screen.index:
        settings_screen.change_screen()

    if magtag.peripherals.button_c_pressed and Screen.current_screen != settings_screen.index:
        clean_screen.change_screen()

    if magtag.peripherals.button_d_pressed and Screen.current_screen != settings_screen.index:
        Screen.current_screen = cleaning_screen.index
        cleaning_screen.change_screen()
