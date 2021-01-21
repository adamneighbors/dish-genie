# TODO: Fill out header
# TODO: Add option to input time for cleaning process which will then switch to
# Clean when done.
# TODO: Update images to be cleaner.
import time
import displayio
import terminalio
from adafruit_magtag.magtag import MagTag

magtag = MagTag()

# Color Codes
RED = 0x880000
GREEN = 0x00FF00
BLUE = 0x000088
YELLOW = 0x884400
CYAN = 0x0088BB
MAGENTA = 0x9900BB
WHITE = 0xFFFFFF

# Set Image Paths
dishes_image = './bmps/Dishes.bmp'
dirty_dishes_image = './bmps/DirtyDishes.bmp'
clean_dishes_image = './bmps/CleanDishes.bmp'

# Screen Variables
main_screen = 0
dirty_screen = 1
settings_screen = 2
cleaning_screen = 3
clean_screen = 4
current_screen = main_screen

# Define Functions
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


def set_title(label, pos, scale):
    magtag.add_text(
        text_font = terminalio.FONT,
        text_position = (pos, (magtag.graphics.display.height // 2) - 1),
        text_scale = scale,
    )
    magtag.set_text(label, 4, False)


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

# Create buttons
button_a = Button('', 5, 0)
button_b = Button('', 75, 1)
button_c = Button('', 160, 2)
button_d = Button('', 220, 3)

def main():
    current_screen = main_screen
    # Add Title
    set_title('Dish Genie', 5, 3)
    magtag.graphics.set_background(dishes_image)
    button_a.change_label('Dirty')
    button_b.change_label('Settings')
    button_c.change_label('')
    button_d.change_label('Cleaning')
    magtag.refresh()


main()

while True:
    if magtag.peripherals.button_a_pressed and current_screen != settings_screen:
        current_screen = dirty_screen
        magtag.graphics.set_background(dirty_dishes_image)
        set_title('Dirty', 1, 3)
        blink(RED, 2)
        magtag.refresh()

    if magtag.peripherals.button_a_pressed and current_screen == settings_screen:
        main()

    if magtag.peripherals.button_b_pressed and current_screen != settings_screen:
        current_screen = settings_screen
        button_a.change_label('Back')
        button_b.change_label('')
        button_c.change_label('')
        button_d.change_label('')
        magtag.set_background(WHITE)
        magtag.refresh()

    if magtag.peripherals.button_c_pressed and current_screen != settings_screen:
        pass

    if magtag.peripherals.button_d_pressed and current_screen != settings_screen:
        current_screen = cleaning_screen
        magtag.graphics.set_background(clean_dishes_image)
        set_title('Cleaning', 5, 3)
        blink(GREEN, 3)
        magtag.refresh()
