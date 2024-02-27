import requests
from streamlink import Streamlink
import time
import random
from random import shuffle
from fake_useragent import UserAgent
from threading import Thread

class TwitchBot:
    def __init__(self):
        self.channel_name = input("Enter Channel Nickname: ")
        self.proxies_file = "proxy.txt"
        self.max_nb_of_threads = 50
        self.session = Streamlink()
        self.usagt = UserAgent()
        self.all_proxies = self.load_proxies()
        self.channel_url = f"https://www.twitch.tv/{self.channel_name}"

    def load_proxies(self):
        try:
            with open(self.proxies_file, "r") as file:
                return [{"proxy": line.strip(), "time": time.time(), "url": ""} for line in file]
        except IOError as e:
            print(f"Unable to load proxies: {e}")
            return []

    def get_url(self):
        try:
            streams = self.session.streams(self.channel_url)
            return streams['audio_only'].url if 'audio_only' in streams else streams['worst'].url
        except Exception as e:
            print(f"Failed to get stream URL: {e}")
            return ""

    def open_url(self, proxy_data):
        headers = {'User-Agent': self.usagt.random}
        try:
            current_index = self.all_proxies.index(proxy_data)
            if time.time() - proxy_data['time'] >= random.randint(1, 5):
                current_proxy = {"http": proxy_data['proxy'], "https": proxy_data['proxy']}
                with requests.Session() as s:
                    response = s.head(proxy_data['url'], proxies=current_proxy, headers=headers)
                print(f"Success: {response.status_code}")
                proxy_data['time'] = time.time()
                self.all_proxies[current_index] = proxy_data
        except Exception as e:
            print(f"Failed request: {e}")

    def main(self):
        shuffle(self.all_proxies)
        while True:
            try:
                for i in range(min(self.max_nb_of_threads, len(self.all_proxies))):
                    proxy = random.choice(self.all_proxies)
                    t = Thread(target=self.open_url, args=(proxy,))
                    t.daemon = True
                    t.start()
                time.sleep(5)
            except KeyboardInterrupt:
                print("Exiting...")
                break

if __name__ == "__main__":
    bot = TwitchBot()
    bot.main()
