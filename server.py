
import pygame,threading,sys

from classes import HandleGame
from classes import Button


SHOW_DIGIT_AREA_TOP = (67,168)
SHOW_DIGIT_AREA_SIZE = (336,336)
NAME_TOP = (35,20)
FIRST_DIGIT_GUESS_TOP = ()
MACHINE_GUESS_AREA_TOP = (565,578)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
BACKGROUND = 's_background.png'
LEFT = 1
START_BUTTOM_TOP = (776,589)
START_BUTTOM_SIZE = (164,65)

def create_buttoms(game: HandleGame):
    buttoms = []
    buttoms.append(Button(START_BUTTOM_TOP,START_BUTTOM_SIZE,game.start))
    return buttoms
    

def main(players_number):
   
    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('machine VS human')

    img = pygame.image.load(BACKGROUND)
    screen.blit(img, (0, 0))
    pygame.display.flip()

    game = HandleGame(screen,players_number)
    connect = threading.Thread(target=game.connect)
    connect.start()

    buttoms = create_buttoms(game)

    played_once = False
    finish = False
    while not finish:
        if game.connected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == LEFT:
                        pos = pygame.mouse.get_pos()
                        for buttom in buttoms:
                            
                            if buttom.is_clicked(pos):
                                if game.done:
                                    played_once =True
                                    t =threading.Thread(target=buttom.click)
                                    t.start()
                                break
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
        if game.done and played_once:
            t.join()

           

        pygame.display.flip()

    connect.join()
    game.end()


def help():
    print("""
    Hello!\n
    To launch the server you should deliver the number of participants.\n
    Example: py server.py <players amount>\n
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'help':
            help()
        else:
            players_number = sys.argv[1]
            main(int(players_number))
    else:
        help()