import threading, time, requests

class ESP32:
    def __init__(self, esp32_api: str, update_interval: float):
        self.__esp32_api = esp32_api
        self.__update_interval = update_interval

        self.__locks = {
            'current_temperature': threading.Lock(),
            'current_humidity': threading.Lock(),
            'running_time': threading.Lock(),
            'target_temperature': threading.Lock()
        }
        self.__running = threading.Event()

        self.__current_temperature = None
        self.__current_humidity = None
        self.__current_running_time = None
        self.__current_target_temperature = None

        if not self.__api_up():
            raise Exception(f'Failed to connect to ESP32 at {esp32_api}')

        self.__running.set()
        threading.Thread(target=self.__update_periodically, daemon=True).start()

    def __api_up(self):
        req = requests.get(f'{self.__esp32_api}/api/fetch_data',
                           headers={'Content-Type': 'application/json'},
                           timeout=2)
        return req.status_code == 200

    def __update(self):
        try:
            res = requests.get(f'{self.__esp32_api}/api/fetch_data',
                               headers={'Content-Type': 'application/json'})
            res.raise_for_status()
            data = res.json()

            with self.__locks['current_temperature']:
                self.__current_temperature = data.get('currentTemperature', None)
            with self.__locks['current_humidity']:
                self.__current_humidity = data.get('currentHumidity', None)
            with self.__locks['running_time']:
                self.__current_running_time = data.get('runningTime', None)
            with self.__locks['target_temperature']:
                self.__current_target_temperature = data.get('targetTemperature', None)

        except requests.exceptions.RequestException as e:
            print(f'Failed to fetch data from ESP32 at {self.__esp32_api}: {e}')
        except ValueError as e:
            print(f'Failed parsing response from ESP32: {e}')

    def __update_periodically(self):
        while self.__running.is_set():
            self.__update()
            time.sleep(self.__update_interval)

    def kill(self):
        self.__running.clear()

    def increase_target_temperature(self):
        try:
            res = requests.post(f'{self.__esp32_api}/api/increase-target-temperature',
                                headers={'Content-Type': 'application/json'})
            res.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f'Failed to post data to ESP32 at {self.__esp32_api}: {e}')

    def decrease_target_temperature(self):
        try:
            res = requests.post(f'{self.__esp32_api}/api/decrease-target-temperature',
                                headers={'Content-Type': 'application/json'})
            res.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f'Failed to post data to ESP32 at {self.__esp32_api}: {e}')

    def increase_running_time(self):
        try:
            res = requests.post(f'{self.__esp32_api}/api/increase-running-time',
                                headers={'Content-Type': 'application/json'})
            res.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f'Failed to post data to ESP32 at {self.__esp32_api}: {e}')

    def decrease_running_time(self):
        try:
            res = requests.post(f'{self.__esp32_api}/api/decrease-running-time',
                                headers={'Content-Type': 'application/json'})
            res.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f'Failed to post data to ESP32 at {self.__esp32_api}: {e}')

    def get_current_temperature(self):
        with self.__locks['current_temperature']:
            return self.__current_temperature

    def get_current_humidity(self):
        with self.__locks['current_humidity']:
            return self.__current_humidity

    def get_current_running_time(self):
        with self.__locks['running_time']:
            return self.__current_running_time

    def get_current_target_temperature(self):
        with self.__locks['target_temperature']:
            return self.__current_target_temperature