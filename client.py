
from ast import arg
import sys
import pygame,threading

from classes import Play
from classes import Button


SHOW_DIGIT_AREA_TOP = (67,168)
SHOW_DIGIT_AREA_SIZE = (336,336)
NAME_TOP = (35,20)
FIRST_DIGIT_GUESS_TOP = (72,542)
DIGIT_GUESS_SIZE_X = 60
DIGIT_GUESS_SIZE = (50,65)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
BACKGROUND = 'c_background.png'
LEFT = 1

finish_t = True

def create_buttoms(game: Play):
    buttoms = []
    for i in range(10):
        buttoms.append(Button((FIRST_DIGIT_GUESS_TOP[0]+i*DIGIT_GUESS_SIZE_X,FIRST_DIGIT_GUESS_TOP[1]),DIGIT_GUESS_SIZE,game.send_player_guess))
    
    return buttoms
    

def main(ip):
    global finish_t
    name = input('Please enter your name: ')
    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('human VS machine')

    img = pygame.image.load(BACKGROUND)
    screen.blit(img, (0, 0))
    pygame.display.flip()
    game = Play(screen,name,ip)
    game.connect()
    print('connected')

    buttoms = create_buttoms(game)

    finish = False
    clicked = False
    while not finish:
        threads = []
        
        if game.got_image and finish_t:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == LEFT:
                        pos = pygame.mouse.get_pos()
                        for i,buttom in enumerate(buttoms):
                            if buttom.is_clicked(pos):
                                clicked = True
                                t1 = threading.Thread(target=buttom.click,args=(i,))
                                t1.start()
                                threads.append(t1)
                                break
                        if clicked:
                            t2 = threading.Thread(target=game.get_score)
                            t2.start()
                            game.got_image = False
                            threads.append(t2)
                            clicked = False
                            t1.join()
                            t2.join()
        else:
            t = threading.Thread(target=game.get_image)
            t.start()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
           
        pygame.display.flip()
        t.join()
        
    game.end()




def activate_pygame_screen(threads):
    global finish_t
    for t in threads:
        t.join()

    finish_t = True


def help():
    print("""
    Hello!\n
    To start the game you should enter the host's IP address\n
    Example: py client.py <IP>\n
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        main(ip)
    else:
        help()
