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


class Screen:
    current_screen = None
    def __init__(self, title, image, index, title_pos, title_scale):
        self.title = title
        self.index = index
        self.title_pos = title_pos
        self.title_scale = title_scale
        self.image = image
        current_screen = index

        self.set_title()

    def change_screen(self):
        self.current_screen = self.index
        self.change_image()
        self.set_title()

    def change_image(self):
        magtag.graphics.set_background(self.image)


    def change_buttons(self, button_a_label, button_b_label, button_c_label, button_d_label):
        button_a.change_label(button_a_label)
        button_b.change_label(button_b_label)
        button_c.change_label(button_c_label)
        button_d.change_label(button_d_label)


    def set_title(self):
        magtag.add_text(
            text_font = terminalio.FONT,
            text_position = (self.title_pos, (magtag.graphics.display.height // 2) - 1),
            text_scale = self.title_scale,
        )
        magtag.set_text(self.title, 4, False)


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

# Create screens
main_screen = Screen('Dish Genie', dishes_image, 0, 5, 3)
dirty_screen = Screen('Dirty', dirty_dishes_image, 1, 500, 5)
settings_screen = Screen('Settings', None, 2, 5, 5)
cleaning_screen = Screen('Cleaning', clean_dishes_image, 3, 5, 5)
clean_screen = Screen('Clean', clean_dishes_image, 4, 5, 5)

def main():
    main_screen.change_screen()
    # Add Title
    magtag.graphics.set_background(dishes_image)
    button_a.change_label('Dirty')
    button_b.change_label('Settings')
    button_c.change_label('')
    button_d.change_label('Cleaning')
    magtag.refresh()
    print(Screen.current_screen)

main()

while True:
    if magtag.peripherals.button_a_pressed and Screen.current_screen != settings_screen.index:
        dirty_screen.change_screen()
        blink(RED, 2)
        magtag.refresh()

    if magtag.peripherals.button_a_pressed and Screen.current_screen == settings_screen.index:
        main()

    if magtag.peripherals.button_b_pressed and Screen.current_screen != settings_screen.index:
        Screen.current_screen = settings_screen.index
        settings_screen.change_buttons('Home', '', '', '')
        magtag.set_background(WHITE)
        magtag.refresh()

    if magtag.peripherals.button_c_pressed and Screen.current_screen != settings_screen.index:
        pass

    if magtag.peripherals.button_d_pressed and Screen.current_screen != settings_screen.index:
        Screen.current_screen = cleaning_screen.index
        magtag.graphics.set_background(clean_dishes_image)
        set_title('Cleaning', 5, 3)
        blink(GREEN, 3)
        magtag.refresh()
