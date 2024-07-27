import copy
import sys
from constants import *

pygame.init()


# draw the board and show the bottom text indicating whose turn it is
def draw_board(turn, player1, player2):
    for i in range(32):
        column = i % 4
        row = i // 4
        # draw the actual board and layout
        if row % 2 == 0:
            pygame.draw.rect(screen, 'light gray', [600 - column * 200, row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, 'light gray', [700 - column * 200, row * 100, 100, 100])
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
        pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
        pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT - 196], 5)

        # player1 and 2 are None when pawn promotion is happening
        if player1 is not None and player2 is not None:
            # show the turn and corresponding player at the bottom as a text
            player_name = player1.name if turn == 'white' else player2.name
            screen.blit(big_font.render(f'Turn: {turn} ({player_name})', True, 'black'), (20, 820))

        for i in range(9):
            # horizontal lines
            pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
            # vertical lines
            pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
        screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))
        screen.blit(medium_font.render('OFFER', True, 'black'), (810, 715))
        screen.blit(medium_font.render('DRAW', True, 'black'), (810, 755))


# draw pieces in their respective locations
def draw_pieces(pieces):
    for piece, data in pieces.items():
        pos = data['pos']
        if 'p' in piece:  # if the piece is a pawn
            screen.blit(PIECES[piece[:2]], (pos[1] * 100 + 18, pos[0] * 100 + 26))
        else:
            screen.blit(PIECES[piece[:2]], (pos[1] * 100 + 10, pos[0] * 100 + 10))


# check if the king is under attack at a given position
def is_king_scoped(pos, pieces, opponent_color):
    for p, data in pieces.items():
        if p[0] == opponent_color:
            # check_under_attack = False allows the calculation of the opponent king's movements
            opponent_moves = get_moves(p, data['pos'], pieces, check_under_attack=False)
            if pos in opponent_moves:
                return True
    return False


# get the possible moves for all pieces
def get_moves(piece, pos, pieces, check_under_attack=True):
    row, col = pos
    moves = []
    opponent_positions = {data['pos']: p for p, data in pieces.items() if p[0] != piece[0]}
    own_positions = {data['pos']: p for p, data in pieces.items() if p[0] == piece[0]}

    # given a direction, keep checking for valid moves in that line of sight
    def check_move_in_direction(row_dir, col_dir, color):
        r, c = row, col
        while True:
            r += row_dir
            c += col_dir
            if 0 <= r < 8 and 0 <= c < 8:
                if (r, c) in own_positions:
                    break
                moves.append((r, c))
                if (r, c) in opponent_positions:
                    # this is the opponent's king
                    king = 'wK' if color == 'b' else 'bK'
                    # this is to make sure the king cannot move into the opponent's line of sight
                    # when it is already in check by said piece (i.e. a bishop)
                    if not check_under_attack and pieces[king]['pos'] == (r, c):
                        r += row_dir
                        c += col_dir
                        moves.append((r, c))
                    break
            else:
                break

    if piece[1] == 'p':  # Pawn
        if piece[0] == 'w':
            direction = -1
        else:
            direction = 1
        # Move forward
        if (row + direction, col) not in own_positions and (row + direction, col) not in opponent_positions \
                and check_under_attack:
            moves.append((row + direction, col))
            if not pieces[piece]['moved'] and (row + 2 * direction, col) not in own_positions and \
                    (row + 2 * direction, col) not in opponent_positions:
                moves.append((row + 2 * direction, col))
        # Capturing diagonally
        if not check_under_attack or (row + direction, col - 1) in opponent_positions:
            moves.append((row + direction, col - 1))
        if not check_under_attack or (row + direction, col + 1) in opponent_positions:
            moves.append((row + direction, col + 1))
        # En passant
        # check left capture
        if col > 0:
            left_piece_pos = (row, col - 1)
            if left_piece_pos in opponent_positions:
                left_piece = opponent_positions[left_piece_pos]
                if left_piece[1] == 'p' and pieces[opponent_positions[left_piece_pos]]['e_p']:
                    moves.append((row + direction, col - 1))
        # check right capture
        if col < 7:
            right_piece_pos = (row, col + 1)
            if right_piece_pos in opponent_positions:
                right_piece = opponent_positions[right_piece_pos]
                if right_piece[1] == 'p' and pieces[opponent_positions[right_piece_pos]]['e_p']:
                    moves.append((row + direction, col + 1))

    elif piece[1] == 'R':  # Rook
        # check all moves in four straight directions
        check_move_in_direction(1, 0, piece[0])
        check_move_in_direction(-1, 0, piece[0])
        check_move_in_direction(0, 1, piece[0])
        check_move_in_direction(0, -1, piece[0])

    elif piece[1] == 'N':  # Knight
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for move in knight_moves:
            new_row, new_col = row + move[0], col + move[1]
            if 0 <= new_row < 8 and 0 <= new_col < 8 and (new_row, new_col) not in own_positions:
                moves.append((new_row, new_col))

    elif piece[1] == 'B':  # Bishop
        # check all four diagonals
        check_move_in_direction(1, 1, piece[0])
        check_move_in_direction(1, -1, piece[0])
        check_move_in_direction(-1, 1, piece[0])
        check_move_in_direction(-1, -1, piece[0])

    elif piece[1] == 'Q':  # Queen
        # check all eight directions
        check_move_in_direction(1, 0, piece[0])
        check_move_in_direction(-1, 0, piece[0])
        check_move_in_direction(0, 1, piece[0])
        check_move_in_direction(0, -1, piece[0])
        check_move_in_direction(1, 1, piece[0])
        check_move_in_direction(1, -1, piece[0])
        check_move_in_direction(-1, 1, piece[0])
        check_move_in_direction(-1, -1, piece[0])

    elif piece[1] == 'K':  # King
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for move in king_moves:
            new_row, new_col = row + move[0], col + move[1]
            if 0 <= new_row < 8 and 0 <= new_col < 8 and (new_row, new_col) not in own_positions:
                # only append move if either checking for opponent king moves, or
                # if the king is not under attack by the opponent after the move
                if not check_under_attack or not \
                        is_king_scoped((new_row, new_col), pieces, 'b' if piece[0] == 'w' else 'w'):
                    moves.append((new_row, new_col))

    return moves


# check for castling moves
def check_castling(piece, pos, pieces, turn, check_under_attack=True):
    row, col = pos
    moves = []
    opponent_positions = [(data['pos'][0], data['pos'][1]) for p, data in pieces.items() if p[0] != piece[0]]
    own_positions = [(data['pos'][0], data['pos'][1]) for p, data in pieces.items() if p[0] == piece[0]]
    rook_to_move = ''

    if piece[1] == 'K':
        # check for castling
        if not pieces[piece]['moved'] and not is_king_in_check(turn, pieces):
            # define the rooks as white or black (same as king)
            R1 = 'wR1' if piece[0] == 'w' else 'bR1'
            R2 = 'wR2' if piece[0] == 'w' else 'bR2'
            t = 'b' if piece[0] == 'w' else 'w'
            # if the rook is not taken and hasn't moved
            if R1 in pieces and not pieces[R1]['moved'] and pieces[R1]['pos'] == (row, 0):
                # check if all three squares between are empty
                if all([(row, col) not in own_positions and (row, col) not in opponent_positions
                        for col in range(1, 4)]):
                    if check_under_attack and not is_king_scoped((row, 2), pieces, t) and not \
                            is_king_scoped((row, 3), pieces, t) and not is_king_scoped((row, 4), pieces, t):
                        moves.append((row, 2))  # Queen-side castling
                        rook_to_move = R1
            if R2 in pieces and not pieces[R2]['moved'] and pieces[R2]['pos'] == (row, 7):
                # check if both squares between are empty
                if all([(row, col) not in own_positions and (row, col) not in opponent_positions
                        for col in range(5, 7)]):
                    if check_under_attack and not is_king_scoped((row, 5), pieces, t) and not \
                            is_king_scoped((row, 6), pieces, t) and not is_king_scoped((row, 7), pieces, t):
                        moves.append((row, 6))  # King-side castling
                        rook_to_move = R2
    return moves, rook_to_move


# draw captured pieces to the right of the board
def draw_captured_pieces(white_captured, black_captured):
    # draw captured white pieces
    for i in range(len(white_captured)):
        piece = white_captured[i]
        screen.blit(PIECES_SMALL[piece[:2]], (925, 5 + 45 * i))
    # draw captured black pieces
    for i in range(len(black_captured)):
        piece = black_captured[i]
        screen.blit(PIECES_SMALL[piece[:2]], (825, 5 + 45 * i))


# check if a pawn can be promoted
def promote_pawn(pieces, piece, new_piece_type):
    pos = pieces[piece]['pos']
    color = piece[0]

    # Find the highest suffix for the new piece type (this is to differentiate from existing pieces)
    max_suffix = 0
    for existing_piece in pieces:
        # if there already is a promoted piece of the same type,
        if existing_piece.startswith(color + new_piece_type):
            # define the suffix as that piece's suffix
            suffix = existing_piece[len(color + new_piece_type):]
            if suffix.isdigit():
                max_suffix = max(max_suffix, int(suffix))
    new_piece = f'{color}{new_piece_type}{max_suffix + 1}'
    # delete the pawn
    del pieces[piece]
    # replace it with the selected promotion piece
    pieces[new_piece] = {'pos': pos, 'moved': True}


# draw the promotion options on the right side of the screen
def draw_promotion(turn):
    pygame.draw.rect(screen, 'dark gray', [800, 0, 200, 420])
    for i in range(len(promotion_list)):
        piece = turn[0] + promotion_list[i]
        screen.blit(PIECES.get(piece), (900, 5 + 100 * i))
        screen.blit(medium_font.render(f'{i + 1}.', True, 'black'), (840, 5 + 100 * i))
    pygame.draw.rect(screen, turn, [800, 0, 200, 420], 8)


# checks if the king is in check
def is_king_in_check(turn, pieces):
    # find the position of the king
    king_pos = None
    for p, data in pieces.items():
        if p[0] == turn[0] and p[1] == 'K':
            king_pos = data['pos']
            break
    if not king_pos:
        return False

    # consider all opponent moves
    opponent_turn = 'b' if turn == 'white' else 'w'
    opponent_moves = []
    for p, data in pieces.items():
        if p[0] == opponent_turn[0]:
            moves = get_moves(p, data['pos'], pieces, check_under_attack=False)
            opponent_moves.extend(moves)

    # Check if the king is in the opponent's moves
    if king_pos in opponent_moves:
        return True
    return False


# draws a flashing red border around king when checked
def draw_check(turn, pieces):
    king = 'wK' if turn == 'white' else 'bK'
    for p, data in pieces.items():
        if p == king:
            pos = data['pos']
            if counter < 15:
                pygame.draw.rect(screen, 'dark red', [pos[1] * 100 + 1,
                                                      pos[0] * 100 + 1, 100, 100], 5)


# draw valid moves on screen
def draw_valid(selected_piece, pieces, turn):
    piece_name = selected_piece
    original_pos = pieces[piece_name]['pos']
    possible_moves = get_moves(piece_name, original_pos, pieces)
    castling_moves = check_castling(piece_name, original_pos, pieces, turn)[0]
    # draw red dots at valid move squares
    for move in possible_moves:
        pygame.draw.circle(screen, 'red', (move[1] * 100 + 50, move[0] * 100 + 50), 5)
    # draw blue dots at valid castling move squares
    for move in castling_moves:
        pygame.draw.circle(screen, 'blue', (move[1] * 100 + 50, move[0] * 100 + 50), 5)
    # draw red border for the selected piece
    pygame.draw.rect(screen, 'red', [original_pos[1] * 100 + 1,
                                     original_pos[0] * 100 + 1, 100, 100], 2)


# if either side offers a draw, write a text on screen
def offer_draw(color):
    pygame.draw.rect(screen, 'black', [200, 200, 400, 100])
    screen.blit(font.render(f'player {color} is offering a draw.', True, 'white'), (210, 210))
    screen.blit(font.render(f'Will you accept? Press Y or N', True, 'white'), (210, 240))


# checks if the game is over either by stalemate or if a king is taken
def is_game_over(pieces, turn):
    game_over = False
    winner = ''
    all_moves = []
    # check for stalemate
    if not is_king_in_check(turn, pieces):
        for p, data in pieces.items():
            # check all moves of our pieces
            if p[0] == turn[0]:
                moves = get_moves(p, data['pos'], pieces)
                all_moves.extend(moves)
        # if there are no moves, it's a stalemate
        if len(all_moves) == 0:
            game_over = True
            winner = 'draw'

    # check if king is taken
    king_pos = None
    for p, data in pieces.items():
        if p[0] == turn[0] and p[1] == 'K':
            king_pos = data['pos']
            break
    if not king_pos:
        game_over = True
        winner = 'black' if turn == 'white' else 'white'

    return game_over, winner


# game over screen
def draw_game_over():
    if winner == 'draw':
        pygame.draw.rect(screen, 'black', [200, 200, 500, 70])
        screen.blit(font.render(f'It\'s a draw!', True, 'white'), (210, 210))
    else:
        pygame.draw.rect(screen, 'black', [200, 200, 500, 70])
        screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press TAB to look at tournament standings', True, 'white'), (210, 240))


# handle user clicks and game states
def handle_click(pos, selected_piece, pieces, turn):
    global is_checked
    global winner
    global game_over
    game_over = False
    x, y = pos
    row, col = y // 100, x // 100
    # if player forfeits
    if (row, col) == (8, 8) or (row, col) == (9, 8):
        winner = 'black' if turn == 'white' else 'white'
        game_over = True
    # if player offers a draw
    if (row, col) == (7, 8) or (row, col) == (7, 9):
        winner = 'offer'
        game_over = True
    if selected_piece:  # if the player already chose a piece
        piece_name = selected_piece
        original_pos = pieces[piece_name]['pos']
        possible_moves = get_moves(piece_name, original_pos, pieces)
        castling_moves = check_castling(piece_name, original_pos, pieces, turn)[0]

        # handle castling
        if piece_name[1] == 'K':
            if (row, col) in castling_moves:
                rook_to_move = check_castling(piece_name, original_pos, pieces, turn)[1]
                if rook_to_move[1:] == 'R1':
                    pieces[rook_to_move]['pos'] = (row, 3)
                else:
                    pieces[rook_to_move]['pos'] = (row, 5)
                pieces[piece_name]['pos'] = (row, col)
                pieces[piece_name]['moved'] = True
                # reset selected piece to none
                selected_piece = None
                # change turns
                turn = 'black' if turn == 'white' else 'white'
            else:
                selected_piece = None
        # handle normal moves
        if (row, col) in possible_moves:
            # check if capturing a piece
            for opponent_piece in pieces:
                if pieces[opponent_piece]['pos'] == (row, col) and opponent_piece[0] != piece_name[0]:
                    # append the captured pieces to their list
                    if opponent_piece[0] == 'b':
                        black_captured.append(opponent_piece)
                    else:
                        white_captured.append(opponent_piece)
                    del pieces[opponent_piece]
                    break
                # en passant capture
                if piece_name[1] == 'p':
                    if pieces[opponent_piece]['pos'] == (original_pos[0], col) and \
                            pieces[opponent_piece].get('e_p', False):
                        if abs(original_pos[1] - col) == 1 and abs(original_pos[0] - row) == 1:
                            # append the captured pieces to their list
                            if opponent_piece[0] == 'b':
                                black_captured.append(opponent_piece)
                            else:
                                white_captured.append(opponent_piece)
                            del pieces[opponent_piece]
                            break
            pieces[piece_name]['pos'] = (row, col)
            pieces[piece_name]['moved'] = True
            # reset selected piece to none
            selected_piece = None

            # handle pawn promotion
            if piece_name[1] == 'p' and (row == 0 or row == 7):
                promoting = True
                while promoting:
                    draw_board(turn, None, None)
                    draw_pieces(pieces)
                    draw_captured_pieces(white_captured, black_captured)
                    draw_promotion(turn)
                    # Write a text to prompt user to promote
                    screen.blit(big_font.render(f'Press 1, 2, 3 or 4 to promote pawn', True, 'black'), (20, 820))
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                promote_pawn(pieces, piece_name, 'Q')
                                promoting = False
                            elif event.key == pygame.K_2:
                                promote_pawn(pieces, piece_name, 'R')
                                promoting = False
                            elif event.key == pygame.K_3:
                                promote_pawn(pieces, piece_name, 'B')
                                promoting = False
                            elif event.key == pygame.K_4:
                                promote_pawn(pieces, piece_name, 'N')
                                promoting = False

            # change turns
            turn = 'black' if turn == 'white' else 'white'

            # determine if the king is in check
            is_checked = is_king_in_check(turn, pieces)
            # reset en passant availability
            for p, data in pieces.items():
                if p[0] != piece_name[0] and p[1] == 'p':
                    pieces[p]['e_p'] = False

            # allow en passant
            if piece_name[1] == 'p' and abs(original_pos[0] - row) == 2:
                pieces[piece_name]['e_p'] = True
        else:
            selected_piece = None
    else:  # otherwise make that piece the selected piece
        for piece, data in pieces.items():
            if data['pos'] == (row, col) and piece.startswith(turn[0]):
                selected_piece = piece
                break
    return selected_piece, turn, game_over, winner


# main game function that returns the winner
def main(player1, player2):
    global counter
    global is_checked
    global winner
    run = True
    game_over = False
    is_checked = False
    selected_piece = None
    # make a copy of pieces so the board can reset after each game
    board_pieces = copy.deepcopy(pieces)
    turn = 'white'
    winner = ''

    while run:
        timer.tick(fps)
        if counter < 30:
            counter += 1
        else:
            counter = 0
        screen.fill('dark gray')

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # handle click
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                selected_piece, turn, game_over, winner = handle_click(pos, selected_piece, board_pieces, turn)
            # if a player offers to draw
            elif event.type == pygame.KEYDOWN and game_over and winner == 'offer':
                # if the other player does not accept the draw, the game continues
                if event.key == pygame.K_n:
                    game_over = False
                    winner = ''
                # if the other player accepts the draw, the game ends
                elif event.key == pygame.K_y:
                    winner = 'draw'

        draw_board(turn, player1, player2)
        draw_pieces(board_pieces)
        draw_captured_pieces(white_captured, black_captured)

        # draw move options as red dots
        if selected_piece:
            draw_valid(selected_piece, board_pieces, turn)
        # check if game is over
        if not game_over:
            game_over = is_game_over(board_pieces, turn)[0]
            winner = is_game_over(board_pieces, turn)[1]
        # draw king in check when checked
        if is_checked:
            draw_check(turn, board_pieces)

        # draw the game over screen
        if game_over:
            if winner == 'offer':
                offer_draw(turn)
            else:
                draw_game_over()

        pygame.display.flip()

        # only return the winner when the winner is decided and player presses TAB
        while game_over and winner != 'offer':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        return winner
