import pygame
pygame.init()

WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Welcome to the Chess Tournament!')
font = pygame.font.Font('freesansbold.ttf', 20)
medium_font = pygame.font.Font('freesansbold.ttf', 40)
big_font = pygame.font.Font('freesansbold.ttf', 47)
timer = pygame.time.Clock()
fps = 60
counter = 0
white_captured = []
black_captured = []
promotion_list = ['Q', 'R', 'B', 'N']

# Load images
PIECES = {
    'bK': pygame.transform.scale(pygame.image.load('images/black king.png'), (80, 80)),
    'bQ': pygame.transform.scale(pygame.image.load('images/black queen.png'), (80, 80)),
    'bR': pygame.transform.scale(pygame.image.load('images/black rook.png'), (80, 80)),
    'bN': pygame.transform.scale(pygame.image.load('images/black knight.png'), (80, 80)),
    'bB': pygame.transform.scale(pygame.image.load('images/black bishop.png'), (80, 80)),
    'bp': pygame.transform.scale(pygame.image.load('images/black pawn.png'), (65, 65)),
    'wK': pygame.transform.scale(pygame.image.load('images/white king.png'), (80, 80)),
    'wQ': pygame.transform.scale(pygame.image.load('images/white queen.png'), (80, 80)),
    'wR': pygame.transform.scale(pygame.image.load('images/white rook.png'), (80, 80)),
    'wN': pygame.transform.scale(pygame.image.load('images/white knight.png'), (80, 80)),
    'wB': pygame.transform.scale(pygame.image.load('images/white bishop.png'), (80, 80)),
    'wp': pygame.transform.scale(pygame.image.load('images/white pawn.png'), (65, 65)),
}

# Load small images
PIECES_SMALL = {
    'bK': pygame.transform.scale(pygame.image.load('images/black king.png'), (40, 40)),
    'bQ': pygame.transform.scale(pygame.image.load('images/black queen.png'), (40, 40)),
    'bR': pygame.transform.scale(pygame.image.load('images/black rook.png'), (40, 40)),
    'bN': pygame.transform.scale(pygame.image.load('images/black knight.png'), (40, 40)),
    'bB': pygame.transform.scale(pygame.image.load('images/black bishop.png'), (40, 40)),
    'bp': pygame.transform.scale(pygame.image.load('images/black pawn.png'), (40, 40)),
    'wK': pygame.transform.scale(pygame.image.load('images/white king.png'), (40, 40)),
    'wQ': pygame.transform.scale(pygame.image.load('images/white queen.png'), (40, 40)),
    'wR': pygame.transform.scale(pygame.image.load('images/white rook.png'), (40, 40)),
    'wN': pygame.transform.scale(pygame.image.load('images/white knight.png'), (40, 40)),
    'wB': pygame.transform.scale(pygame.image.load('images/white bishop.png'), (40, 40)),
    'wp': pygame.transform.scale(pygame.image.load('images/white pawn.png'), (40, 40)),
}

# dict containing the piece position and whether it moved
# 'e_p' for tracking en passant possibility
pieces = {
    'bK': {'pos': (0, 4), 'moved': False},
    'bQ': {'pos': (0, 3), 'moved': False},
    'bR1': {'pos': (0, 0), 'moved': False},
    'bR2': {'pos': (0, 7), 'moved': False},
    'bN1': {'pos': (0, 1), 'moved': False},
    'bN2': {'pos': (0, 6), 'moved': False},
    'bB1': {'pos': (0, 2), 'moved': False},
    'bB2': {'pos': (0, 5), 'moved': False},
    'bp1': {'pos': (1, 0), 'moved': False, 'e_p': False},
    'bp2': {'pos': (1, 1), 'moved': False, 'e_p': False},
    'bp3': {'pos': (1, 2), 'moved': False, 'e_p': False},
    'bp4': {'pos': (1, 3), 'moved': False, 'e_p': False},
    'bp5': {'pos': (1, 4), 'moved': False, 'e_p': False},
    'bp6': {'pos': (1, 5), 'moved': False, 'e_p': False},
    'bp7': {'pos': (1, 6), 'moved': False, 'e_p': False},
    'bp8': {'pos': (1, 7), 'moved': False, 'e_p': False},
    'wK': {'pos': (7, 4), 'moved': False},
    'wQ': {'pos': (7, 3), 'moved': False},
    'wR1': {'pos': (7, 0), 'moved': False},
    'wR2': {'pos': (7, 7), 'moved': False},
    'wN1': {'pos': (7, 1), 'moved': False},
    'wN2': {'pos': (7, 6), 'moved': False},
    'wB1': {'pos': (7, 2), 'moved': False},
    'wB2': {'pos': (7, 5), 'moved': False},
    'wp1': {'pos': (6, 0), 'moved': False, 'e_p': False},
    'wp2': {'pos': (6, 1), 'moved': False, 'e_p': False},
    'wp3': {'pos': (6, 2), 'moved': False, 'e_p': False},
    'wp4': {'pos': (6, 3), 'moved': False, 'e_p': False},
    'wp5': {'pos': (6, 4), 'moved': False, 'e_p': False},
    'wp6': {'pos': (6, 5), 'moved': False, 'e_p': False},
    'wp7': {'pos': (6, 6), 'moved': False, 'e_p': False},
    'wp8': {'pos': (6, 7), 'moved': False, 'e_p': False},
}