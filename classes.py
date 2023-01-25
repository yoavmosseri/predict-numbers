from ast import arg
import random
import socket
import pickle
import pygame
import threading
import time
from keras.datasets import mnist
from network import Network
import numpy as np
import cv2

SIZE_OF_SIZE = 8
SHOW_DIGIT_AREA_TOP = (67, 168)
SHOW_DIGIT_AREA_SIZE = (336, 336)
NAME_TOP = (140, 10)
MACHINE_GUESS_AREA_TOP = (565, 578)
MACHINE_GUESS_DIGIT_TOP = (595, 588)
BLACK = (0, 0, 0)
GRAY = (195, 195, 195)
YELLOW = (255, 201, 14)
GOLD = (239, 228, 176)
BROWN = (185, 122, 87)
MACHINE_SCORE_TOP = (545, 260)
PLAYER_SCORE_TOP_SIZE_Y = 65
SCORE_TOP = (524, 173)


port = 9999


class Button:
    def __init__(self, pos, size, function) -> None:
        self.pos = pos
        self.size = size
        self.func = function

    def is_clicked(self, pos):
        x, y = pos[0], pos[1]
        if x >= self.pos[0] and x < self.pos[0]+self.size[0]:
            if y >= self.pos[1] and y < self.pos[1] + self.size[1]:
                return True
        return False

    def click(self, args: tuple = None):
        if args == None:
            return self.func()
        return self.func(args)


class Player:
    def __init__(self, name) -> None:
        self.name = name
        self.score = 0


received_data = {}


class NetS:
    def __init__(self, port) -> None:
        self.server_sock = socket.socket()
        self.server_sock.bind(('0.0.0.0', port))
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.listen(20)
        self.sock = []
        self.clients_connected = 0

    def accept(self) -> bool:
        try:
            sock, addr = self.server_sock.accept()
            self.sock.append(sock)
            print(f"client {addr} has just connected!")
            self.clients_connected += 1
            return True
        except:
            return False

    def accept_all(self, clients_amount):

        while self.clients_connected < clients_amount:
            accepted = False
            while not accepted:
                accepted = self.accept()

        self.connected = True

    def connect(self) -> bool:
        try:
            self.sock.connect(self.ip_port)
            return True
        except:
            return False

    def recv(self, sock_i) -> object:
        global received_data
        global threads_done
        recieved = False
        while not recieved:
            try:
                size = int(self.sock[sock_i].recv(SIZE_OF_SIZE).decode())
                data = b''
                while len(data) < size:
                    data += self.sock[sock_i].recv(1)
                lock.acquire()
                received_data[sock_i] = pickle.loads(data)
                threads_done += 1
                lock.release()
                recieved = True
            except Exception as err:
                return

    def recv_from_all(self):
        global threads_done
        global received_data
        threads_done = 0
        threads = []
        for i in range(self.clients_connected):
            t = threading.Thread(target=self.recv, args=(i,))
            t.start()
            threads.append(t)

        while threads_done < self.clients_connected:
            pass

        for t in threads:
            t.join()

        return list(received_data.values())

    def send(self, data, sock_i):
        global threads_done
        data = pickle.dumps(data)
        data = str(len(data)).zfill(8).encode() + data
        self.sock[sock_i].send(data)

        lock.acquire()
        threads_done += 1
        lock.release()

    def send_to_all(self, data):
        global threads_done
        threads = []
        threads_done = 0
        for i in range(len(self.sock)):
            t = threading.Thread(target=self.send, args=(data, i))
            t.start()
            threads.append(t)

        while threads_done < len(self.sock):
            pass
        for t in threads:
            t.join()

    def close(self):
        for sock in self.sock:
            sock.close()
        self.server_sock.close()


class NetC:
    def __init__(self, port, ip='0.0.0.0') -> None:
        self.sock = socket.socket()
        self.sock.settimeout(1)
        self.ip_port = (ip, port)

    def connect(self) -> bool:
        try:
            self.sock.connect(self.ip_port)
            return True
        except:
            return False

    def recv(self) -> object:
        try:
            size = int(self.sock.recv(SIZE_OF_SIZE).decode())
            data = b''
            while len(data) < size:
                data += self.sock.recv(1)
            return pickle.loads(data)
        except Exception as err:
            return

    def send(self, data):
        data = pickle.dumps(data)
        data = str(len(data)).zfill(8).encode() + data
        self.sock.send(data)

    def close(self):
        self.sock.close()


threads_done = 0
lock = threading.Lock()


class HandleGame:
    def __init__(self, screen: pygame.display, players_amount=2) -> None:
        self.my = Player('Machine')
        self.screen = screen
        self.net = NetS(port)
        self.neural_network = self._load_network()
        self._show_name()
        self.done = True
        self.players_amount = players_amount - 1
        self.players = []
        self.connected = False

    def connect(self):
        self.net.accept_all(self.players_amount)
        self._handle_new_clients()
        self.connected = True

    def _handle_new_clients(self):
        self.net.send_to_all(self.my)
        self.players = self.net.recv_from_all()

    def _load_network(self) -> Network:
        with open('below3.txt', 'rb') as f:
            return pickle.load(f)

    def end(self):
        self.net.close()

    def start(self):
        self.done = False
        self._clear_machine_guess_area()
        self.digit, self.image = self._random_digit()
        machine_guess = self._guess()
        self._show_image()
        self.net.send_to_all(self.image)
        human_guesses = self._wait_for_respond()
        self._show_guess(machine_guess)
        score = self._update_score(machine_guess, human_guesses)
        self._show_score(score)
        self._send_scores(score)
        self.done = True

    def _send_scores(self, scores):
        self.net.send_to_all(scores)

    def _clear_machine_guess_area(self):
        image = pygame.image.load('machine_guess.png')
        self.screen.blit(image, MACHINE_GUESS_AREA_TOP)

    def _show_guess(self, machine_guess):
        font = pygame.font.Font('freesansbold.ttf', 80)
        text = font.render(str(machine_guess), True, BLACK, YELLOW)
        textRect = text.get_rect()
        textRect.topleft = MACHINE_GUESS_DIGIT_TOP
        self.screen.blit(text, textRect)
        pygame.display.flip()

    def _show_name(self):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(self.my.name, True, BLACK, GRAY)
        textRect = text.get_rect()
        textRect.topleft = NAME_TOP
        self.screen.blit(text, textRect)
        pygame.display.flip()

    def _show_image(self):
        image = cv2.resize(self.image, SHOW_DIGIT_AREA_SIZE)
        image = np.stack((image,)*3, axis=-1)
        cv2.imwrite('digit.png', image)
        image = pygame.image.load('digit.png')
        self.screen.blit(image, SHOW_DIGIT_AREA_TOP)
        pygame.display.flip()

    def _show_score(self, score):
        # clear
        image = pygame.image.load('score.png')
        self.screen.blit(image, SCORE_TOP)
        font = pygame.font.Font('freesansbold.ttf', 32)
        # players
        for i, player in enumerate(score):
            text = font.render(
                f'{player.name}: {player.score}', True, BROWN, GOLD)
            textRect = text.get_rect()
            textRect.topleft = (
                MACHINE_SCORE_TOP[0], MACHINE_SCORE_TOP[1] + PLAYER_SCORE_TOP_SIZE_Y*i)
            self.screen.blit(text, textRect)
        pygame.display.flip()

    def _update_score(self, machine_guess, human_guesses):
        if machine_guess == self.digit:
            self.my.score += 1
        for i, human_guess in enumerate(human_guesses):
            if human_guess == self.digit:
                self.players[i].score += 1

        all_players = self.players[:]
        all_players.append(self.my)
        return all_players

    def _wait_for_respond(self):
        return self.net.recv_from_all()

    def _random_digit(self):
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        rnd = random.randint(0, len(x_train))
        return y_train[rnd], x_train[rnd]

    def _guess(self):
        input_array = self.image.reshape(1, 784)
        guess_array = self.neural_network.predict(input_array)
        return np.argmax(guess_array)


class Play:
    def __init__(self, screen, name, ip='127.0.0.1') -> None:
        self.net = NetC(port, ip)
        self.my = Player(name)
        self.guess = -1
        self.screen = screen
        self.got_image = False
        self._show_name()

    def end(self):
        self.net.close()

    def connect(self):
        connected = False
        while not connected:
            connected = self.net.connect()
        self.net.send(self.my)
        self.player = self.net.recv()

    def get_image(self):
        try:
            self.guess = -1
            self.image = self.net.recv()
            if type(self.image) == type(None):
                self.got_image = False
                return
            self._show_image()
            self.got_image = True
        except Exception as err:
            self.got_image = False

    def send_player_guess(self, guess):
        self.net.send(guess)

    def get_score(self):
        got = False
        while not got:
            try:
                score = self.net.recv()
                if score != None:
                    got = True
            except:
                pass
        self._show_score(score)

    def _show_image(self):
        image = cv2.resize(self.image, SHOW_DIGIT_AREA_SIZE)
        image = np.stack((image,)*3, axis=-1)
        cv2.imwrite('digit.png', image)
        image = pygame.image.load('digit.png')
        self.screen.blit(image, SHOW_DIGIT_AREA_TOP)
        pygame.display.flip()

    def _show_name(self):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(self.my.name, True, BLACK, GRAY)
        textRect = text.get_rect()
        textRect.topleft = NAME_TOP
        self.screen.blit(text, textRect)
        pygame.display.flip()

    def _show_score(self, score):
        # clear
        image = pygame.image.load('score.png')
        self.screen.blit(image, SCORE_TOP)
        font = pygame.font.Font('freesansbold.ttf', 32)
        # players
        for i, player in enumerate(score):
            text = font.render(
                f'{player.name}: {player.score}', True, BROWN, GOLD)
            textRect = text.get_rect()
            textRect.topleft = (
                MACHINE_SCORE_TOP[0], MACHINE_SCORE_TOP[1] + PLAYER_SCORE_TOP_SIZE_Y*i)
            self.screen.blit(text, textRect)
        pygame.display.flip()
