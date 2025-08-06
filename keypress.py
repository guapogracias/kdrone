import pygame

def init():
    pygame.init()
    pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Drone Control")  # Optional: gives window title

def getKey(keyName):
    ans = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, f'K_{keyName}')
    if keyInput[myKey]:
        print(f"{keyName} pressed")  # ← helpful feedback
        ans = True
    pygame.display.update()
    return ans


