import socket
from spotifyAPI import *
import tkinter as tk
import threading


class GestureContainer:
    def __init__(self):
        self.gestures = {
            "starting_position": 0,
            "snap": 1,
            "gap_between_pointer_and_thumb": 2,
            "swing": 3,
            "swing_left": 4,
            "swing_right": 5,
            "one_up" : 6,
            "two_up" : 7,
            "three_up" : 8
        }

        self.spotify_actions = {
            "nothing": "starting_position",
            "play/pause": "snap",
            "volume": "gap_between_pointer_and_thumb",
            "shuffle": "swing",
            "next_track": "swing_left",
            "previous_track": "swing_right"
        }

    def get_gesture_value(self, gesture):
        return self.gestures.get(gesture)

    def set_gesture_value(self, gesture, value):
        self.gestures[gesture] = value

    def get_spotify_action_gesture(self, action):
        return self.spotify_actions.get(action)

    def set_set_spotify_action_gesture(self, action, gesture):
        self.gestures[action] = gesture


def handle_api(server_socket, spotify, device_id, gestures):
    while True:
        server_socket.listen(5)
        client, address = server_socket.accept()
        print(f"Connection ok - {address[0]}:{address[1]}")
        client_string = client.recv(20)
        client_string = client_string.decode("utf-8")
        client_string = eval(client_string)
        print
        if type(client_string) is int:
            client_gesture = client_string
        elif type(client_string) is tuple:
            client_gesture = client_string[0]
            gesture_value = client_string[1]
        print(client_gesture)
        if client_gesture == gestures.get_gesture_value(gestures.get_spotify_action_gesture("play/pause")):
            try:
                spotify.pause_playback(device_id=device_id)
            except spotipy.exceptions.SpotifyException:
                spotify.start_playback(device_id=device_id)
        elif client_gesture == gestures.get_gesture_value(gestures.get_spotify_action_gesture("volume")):
            volume = gesture_value - 20
            if volume > 100:
                volume = 100
            elif volume < 0:
                volume = 0
            spotify.volume(device_id=device_id, volume_percent=volume)
        elif client_gesture == gestures.get_gesture_value(gestures.get_spotify_action_gesture("shuffle")):
            if spotify.current_playback()["shuffle_state"]:
                spotify.shuffle(device_id=device_id, state=False)
            else:
                spotify.shuffle(device_id=device_id, state=True)
        elif client_gesture == gestures.get_gesture_value(gestures.get_spotify_action_gesture("next_track")):
            spotify.next_track()
        elif client_gesture == gestures.get_gesture_value(gestures.get_spotify_action_gesture("previous_track")):
            spotify.previous_track(device_id=device_id)

        client.close()


def main():
    host_name = socket.gethostname()
    ip = socket.gethostbyname(host_name)
    port = 5050
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    sp = SpotifyApi()
    scope = "user-modify-playback-state user-read-playback-state"

    sp2 = spotipy.Spotify(
        auth_manager=SpotifyOAuth(sp.client_id, sp.client_secret, redirect_uri='https://example.com', scope=scope))
    gestures = GestureContainer()
    device_id = ''
    for device in sp2.devices().get('devices'):
        if device.get('is_active'):
            device_id = device.get('id')

    # handle_api(server_socket, sp2, device_id)
    api_thread = threading.Thread(target=handle_api, args=[server_socket, sp2, device_id, gestures])
    api_thread.start()


if __name__ == '__main__':
    main()
