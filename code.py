import ssl
import time

import adafruit_requests
import alarm
import board
import displayio
import socketpool
import storage
import terminalio
import wifi
from adafruit_magtag.magtag import MagTag
from alarm.pin import PinAlarm
from alarm.time import TimeAlarm

try:
    storage.remount(
        mount_path='/',
        readonly=False,
        disable_concurrent_write_protection=True
    )
except:
    pass

# Color codes
RED = 0x880000
GREEN = 0x00FF00
BLUE = 0x000088
YELLOW = 0x884400
CYAN = 0x0088BB
MAGENTA = 0x9900BB
WHITE = 0xFFFFFF

# Set image paths
Genie_image = 'bmps/Dish_Genie.bmp'
dirty_dishes_image = 'bmps/DirtyDishes.bmp'
clean_dishes_image = 'bmps/CleanDishes.bmp'
bubbles_image = 'bmps/bubbles.bmp'

# Import secrets
try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')
    # Todo Log instead of print?
    raise

pin_alarm_a = PinAlarm(pin=board.BUTTON_A, value=False, pull=True)
alarm.sleep_memory[0] = not alarm.sleep_memory[0]


class Screen:
    def __init__(self, name: str, title: str, image: str | int, title_position: int, title_scale: int, button_labels: tuple[str, str, str, str], blink: tuple[int, int, float]):
        self.name = name
        self.title = title
        self.image = image
        self.title_position = title_position
        self.title_scale = title_scale
        self.buttons = button_labels
        self.blink_color = blink[0]
        self.blink_count = blink[1]
        self.blink_duration = blink[2]


class Timer:
    def __init__(self):
        self.default_timer = 3600
        self.amount = int(self.read_time())
        self.session = None
        self.format = self.read_format()

    def read_time(self):
        try:
            with open('timer.txt', 'r') as timer_file:
                file_time = timer_file.read()
                self.default_timer = file_time
                return float(file_time)
        except:
            return self.default_timer

    def write_time(self):
        try:
            with open('timer.txt', 'w') as timer_file:
                timer_file.write(str(self.amount))
        except:
            pass

    def read_format(self):
        try:
            file_format = '24'
            with open('format.txt', 'r') as format_file:
                file_format = format_file.read()
                self.format = file_format
            return file_format
        except:
            return self.default_timer

    def write_format(self):
        try:
            with open('format.txt', 'w') as format_file:
                format_file.write(str(self.format))
        except:
            pass

    def update(self, time: int):
        self.amount += time

    def set(self, time: int):
        self.amount = time

    def _connect_network(self):
        network = secrets['ssid']
        network_pass = secrets['password']

        wifi.radio.connect(network, network_pass)

        pool = socketpool.SocketPool(wifi.radio)
        return adafruit_requests.Session(pool, ssl.create_default_context())

    def _return_current_time(self) -> str | None:
        aio_username = secrets['aio_username']
        aio_key = secrets['aio_key']
        # time_url = 'https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z' % (aio_username, aio_key)
        time_url = f'https://io.adafruit.com/api/v2/{aio_username}/integrations/time/strftime?x-aio-key={aio_key}&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z'

        if not self.session:
            self.session = self._connect_network()
        response = self.session.get(time_url)
        current_time = response.text.split(' ')[1]
        return current_time

    def _format_time(self, hour: int, minute: int):
        minute_str = str(minute)
        hour_format = self.get_current_format()
        if len(minute_str) < 2:
            minute = int(f'0{minute_str}')

        if minute > 60:
            minute -= 60
            hour += 1

        if hour_format == '12':
            am_pm = 'AM'

            display_hour = hour
            if hour == 0:
                display_hour = 12
            elif hour > 12:
                am_pm = 'PM'
                display_hour = hour - 12

            return f'{display_hour}:{minute} {am_pm}'
        return f'{hour:02d}:{minute:02d}'

    def return_start_finish_time(self):
        """Calculates start/finsih time and returns in readable format

        Returns:
            str: When the timer is started
            str: When the timer will end
        """
        current_time = str(self._return_current_time())
        start_hour = int(current_time.split(":")[0])
        start_min = int(current_time.split(":")[1])
        current_time_formatted = self._format_time(start_hour, start_min)
        print(current_time_formatted)

        timer_time = self.convert_secs_to_hour_min()
        timer_hour = int(timer_time.split(":")[0])
        timer_min = int(timer_time.split(":")[1])
        finish_hour = start_hour + timer_hour
        finish_min = start_min + timer_min
        finish_time_formatted = self._format_time(finish_hour, finish_min)

        return current_time_formatted, finish_time_formatted

    def begin(self):
        time_alarm = TimeAlarm(monotonic_time=time.monotonic() + self.amount)

        # Sleep for time set in settings or awaken by button press
        alarm.exit_and_deep_sleep_until_alarms(pin_alarm_a, time_alarm)

    def convert_secs_to_hour_min(self):
        seconds = float(self.amount) % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60

        return '%d:%02d' % (hour, minutes)

    def get_current_format(self):
        return self.format

    def set_format(self, format: str):
        self.format = format


class DishGenie(MagTag):
    def __init__(self):
        super().__init__()
        self.cleaning_timer = Timer()
        self.screens = {}
        self.current_screen = None
        self.main_screen = None
        self._create_screens()
        self.main()

    def _create_screens(self):
        self.screens['Home'] = Screen(
            name='Home',
            title='Dish Genie',
            image=Genie_image,
            title_position=100,
            title_scale=3,
            button_labels=('Dirty', 'Settings', '', 'Cleaning'),
            blink=(BLUE, 1, 0.5)
        )
        self.screens['Dirty'] = Screen(
            name='Dirty',
            title='Dirty',
            image=dirty_dishes_image,
            title_position=125,
            title_scale=5,
            button_labels=('Dirty', 'Settings', '', 'Cleaning'),
            blink=(RED, 2, 0.5)
        )
        self.screens['Settings-time'] = Screen(
            name='Settings-time',
            title=f'Timer: {self.cleaning_timer.convert_secs_to_hour_min()}',
            image=WHITE,
            title_position=10,
            title_scale=3,
            button_labels=('Home', '+30 Min', 'Reset', 'Format'),
            blink=(MAGENTA, 1, 0.5)
        )
        self.screens['Settings-format'] = Screen(
            name='Settings-format',
            title=f'Format: {self.cleaning_timer.get_current_format()}hr',
            image=WHITE,
            title_position=10,
            title_scale=3,
            button_labels=('Home', '24 Hour', '12 Hour', 'Timer'),
            blink=(MAGENTA, 1, 0.5)
        )
        self.screens['Cleaning'] = Screen(
            name='Cleaning',
            title=f'Cleaning...',
            image=clean_dishes_image,
            title_position=5,
            title_scale=3,
            button_labels=('Cancel', '', '', ''),
            blink=(YELLOW, 3, 0.5)
        )
        self.screens['Cleaned'] = Screen(
            name='Cleaned',
            title=f'Clean!',
            image=bubbles_image,
            title_position=self.graphics.display.height // 2,
            title_scale=5,
            button_labels=('Home', '', '', ''),
            blink=(GREEN, 5, 0.5)
        )

    def _change_screen(self, screen: Screen):
        # Clear screen
        self.remove_all_text(auto_refresh=False)
        # Set image
        self.graphics.set_background(screen.image)
        # Set Button Labels
        
        bottom_buttons = [5, 75, 155, 225]
        for i, pos in enumerate(bottom_buttons):
            button_index = self.add_text(
                text_font = terminalio.FONT,
                text_position = (pos, 120),
                text_scale = 1,
            )
            self.set_text(screen.buttons[i], button_index, False)

        # Set Title
        title_index = self.add_text(
            text_font = terminalio.FONT,
            text_position = (screen.title_position, (self.graphics.display.height // 2) - 1),
            text_scale = screen.title_scale,
        )
        self.set_text(screen.title, title_index, True)
        # Blink LEDs
        self.blink(screen.blink_color, screen.blink_count, screen.blink_duration)
        self.current_screen = screen


    def blink(self, color: int, count: int, duration: float = 0.5):
        '''Blinks the LEDs for on the Magtag for the given color and number of times.

        Args:
            color (int): Color that the LED will blink.
            count (int): Number of times you want the LEDs to blink.
            duration (float): How long to leave the light on each 'blink'.
        '''
        for i in range(count):
            self.peripherals.neopixel_disable = False
            self.peripherals.neopixels.fill(color)
            time.sleep(duration)
            self.peripherals.neopixel_disable = True
            time.sleep(0.3)

    def _start_cleaning(self):
        if not self.main_screen:
            return

        current_time, finish_time = self.cleaning_timer.return_start_finish_time()
        self.screens.get('Cleaning', self.main_screen).buttons = ('Cancel',f'Started - {current_time} | Finish - {finish_time}','','')
        self._change_screen(self.screens.get('Cleaning', self.main_screen))
        self.cleaning_timer.begin()

    def main(self):
        self.main_screen = self.screens.get('Home', None)
        if not self.main_screen:
            return

        if str(alarm.wake_alarm) == '<TimeAlarm>':
            self._change_screen(self.screens.get('Cleaned', self.main_screen))
            jingle = [
                (659, 0.2),
                (784, 0.2),
                (880, 0.2),
                (988, 0.3),
                (880, 0.3),
                (784, 0.3),
                (988, 0.4),
                (1319, 0.6),
            ]
            # Play the jingle
            for freq, duration in jingle:
                self.peripherals.play_tone(freq, duration)
                time.sleep(0.05)  # tiny gap between notes

            alarm.exit_and_deep_sleep_until_alarms(pin_alarm_a)

        self._change_screen(self.main_screen)
        if not self.current_screen:
            self.current_screen = self.main_screen

        while True:
            if self.current_screen.name == 'Home':
                if self.peripherals.button_a_pressed:
                    self._change_screen(self.screens.get('Dirty', self.main_screen))
                elif self.peripherals.button_b_pressed:
                    self._change_screen(self.screens.get('Settings-time', self.main_screen))
                elif self.peripherals.button_c_pressed:
                    pass
                elif self.peripherals.button_d_pressed:
                    self._start_cleaning()

            elif self.current_screen.name == 'Dirty':
                if self.peripherals.button_a_pressed:
                    self._change_screen(self.screens.get('Home', self.main_screen))
                elif self.peripherals.button_b_pressed:
                    self._change_screen(self.screens.get('Settings-time', self.main_screen))
                elif self.peripherals.button_c_pressed:
                    pass
                elif self.peripherals.button_d_pressed:
                    self._start_cleaning()

            elif self.current_screen.name == 'Settings-time':
                if self.peripherals.button_a_pressed:
                    self.cleaning_timer.write_time()
                    self._change_screen(self.screens.get('Home', self.main_screen))
                elif self.peripherals.button_b_pressed:
                    self.cleaning_timer.update(1800)
                    self.current_screen.title=f'Timer: {self.cleaning_timer.convert_secs_to_hour_min()}'
                    self._change_screen(self.screens.get('Settings-time', self.main_screen))
                elif self.peripherals.button_c_pressed:
                    self.cleaning_timer.set(3600)
                    self.current_screen.title=f'Timer: {self.cleaning_timer.convert_secs_to_hour_min()}'
                    self._change_screen(self.screens.get('Settings-time', self.main_screen))
                elif self.peripherals.button_d_pressed:
                    self.cleaning_timer.write_time()
                    self._change_screen(self.screens.get('Settings-format', self.main_screen))

            elif self.current_screen.name == 'Settings-format':
                if self.peripherals.button_a_pressed:
                    self.cleaning_timer.write_format()
                    self._change_screen(self.screens.get('Home', self.main_screen))
                elif self.peripherals.button_b_pressed:
                    self.cleaning_timer.set_format('24')
                    self.screens.get('Settings-format', self.main_screen).title = f'Format: {self.cleaning_timer.get_current_format()}hr'
                    self._change_screen(self.screens.get('Settings-format', self.main_screen))
                elif self.peripherals.button_c_pressed:
                    self.cleaning_timer.set_format('12')
                    self.screens.get('Settings-format', self.main_screen).title = f'Format: {self.cleaning_timer.get_current_format()}hr'
                    self._change_screen(self.screens.get('Settings-format', self.main_screen))
                elif self.peripherals.button_d_pressed:
                    self.cleaning_timer.write_format()
                    self._change_screen(self.screens.get('Settings-time', self.main_screen))

            elif self.current_screen.name == 'Cleaning':
                if self.peripherals.button_a_pressed:
                    self._change_screen(self.screens.get('Home', self.main_screen))
                elif self.peripherals.button_b_pressed:
                    pass
                elif self.peripherals.button_c_pressed:
                    pass
                elif self.peripherals.button_d_pressed:
                    pass

            elif self.current_screen.name == 'Cleaned':
                if self.peripherals.button_a_pressed:
                    self._change_screen(self.screens.get('Home', self.main_screen))
                elif self.peripherals.button_b_pressed:
                    pass
                elif self.peripherals.button_c_pressed:
                    pass
                elif self.peripherals.button_d_pressed:
                    pass


if __name__ == '__main__':
    DishGenie()
