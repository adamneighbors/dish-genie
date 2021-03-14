# TODO: Fill out header
# TODO: Update images to be cleaner.
# TODO: Add documentation
# TODO: Possibly change font
# TODO: Display time left on cleaning page
import time
import displayio
import terminalio
from adafruit_magtag.magtag import MagTag
import storage
import board
import alarm

# Try to mount root if USB is not connected.
try:
    storage.remount('/', False)
except:
    pass

# set up pin alarms
buttons = (board.BUTTON_A, board.BUTTON_B)
pin_alarms = [alarm.pin.PinAlarm(pin=pin, value=False, pull=True) for pin in buttons]

# toggle saved state
alarm.sleep_memory[0] = not alarm.sleep_memory[0]

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


class Timer():
    def __init__(self):
        self.default_timer = 3600
        self.amount = self.read()

    def read(self):
        try:
            with open('timer.txt', 'r') as timer_file:
                file_time = timer_file.read()
                self.default_timer = file_time
                return float(file_time)
        except:
            return self.default_timer

    def write(self):
        try:
            with open('timer.txt', 'w') as timer_file:
                timer_file.write(str(self.amount))
        except:
            pass

    def update(self, time):
        self.amount += time
        settings_screen.title = f'Timer: {display_time(self.amount)}'
        settings_screen.change_screen()

    def set(self, time):
        self.amount = time
        settings_screen.title = f'Timer: {display_time(self.amount)}'
        settings_screen.change_screen()

    def begin(self):
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() +
        self.amount)

        # Sleep for time set in settings
        alarm.light_sleep_until_alarms(time_alarm)
        clean_screen.change_screen()
        magtag.peripherals.play_tone(880, 0.15)

        # go to sleep until awaken by button
        alarm.exit_and_deep_sleep_until_alarms(*pin_alarms)

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

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds):
    seconds = float(seconds) % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d" % (hour, minutes)

# Main initialization
magtag = MagTag()
cleaning_timer = Timer()

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

settings_screen = Screen(f'Timer: {display_time(cleaning_timer.amount)}', WHITE, 6, 10, 3)
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
    # Button A
    if magtag.peripherals.button_a_pressed:
        if Screen.current_screen == settings_screen.index:
            cleaning_timer.write()
            main_screen.change_screen()
        else:
            dirty_screen.change_screen()

    # Button B
    if magtag.peripherals.button_b_pressed:
        if Screen.current_screen == settings_screen.index:
            cleaning_timer.update(3600)
        else:
            settings_screen.change_screen()

    # Button C
    if magtag.peripherals.button_c_pressed:
        if Screen.current_screen == settings_screen.index:
            cleaning_timer.update(1800)
        else:
            clean_screen.change_screen()

            # go to sleep until awaken by button
            alarm.exit_and_deep_sleep_until_alarms(*pin_alarms)

    # Button D
    if magtag.peripherals.button_d_pressed:
        if Screen.current_screen == settings_screen.index:
            cleaning_timer.set(3600)
        else:
            cleaning_screen.change_screen()
            cleaning_timer.begin()
