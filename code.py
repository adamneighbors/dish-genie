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
start_screen = 0
dirty_screen = 1
settings_screen = 2
cleaning_screen = 3
clean_screen = 4

# Add Title
magtag.graphics.set_background(dishes_image)
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(
        5,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=2,
)
magtag.set_text("Dish Bish")
current_screen = start_screen

# Add Button Labels
magtag.add_text(
    text_font=terminalio.FONT,
    text_position=(3, 120),
    text_scale=1,
)
magtag.set_text(" Dirty      Settings                  Clean", 1)


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

while True:
    if magtag.peripherals.button_a_pressed:
        magtag.graphics.set_background(dirty_dishes_image)
        magtag.add_text(
            text_font=terminalio.FONT,
            text_position=(
                5,
                (magtag.graphics.display.height // 2) - 1,
            ),
            # TODO: Find out why this text scalling isn't working
            text_scale=3,
        )
        magtag.set_text("               Dirty")
        blink(RED, 2)
        current_screen = dirty_screen

    if magtag.peripherals.button_b_pressed:
        magtag.set_background(WHITE)
        magtag.set_text("")
        current_screen = settings_screen


    if magtag.peripherals.button_c_pressed:
        pass

    if magtag.peripherals.button_d_pressed:
        magtag.graphics.set_background(clean_dishes_image)
        magtag.add_text(
            text_font=terminalio.FONT,
            text_position=(
                5,
                (magtag.graphics.display.height // 2) - 1,
            ),
            # TODO: same here too for text scalling
            text_scale=3,
        )
        magtag.set_text("   Cleaning")
        blink(GREEN, 3)
        current_screen = cleaning_screen
