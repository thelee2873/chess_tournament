import sys
import chess_game
from constants import *

pygame.init()


# the Player class keeps track of each player's name, score, and whether they have just played
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.played = False  # track if the player has just played

    def __str__(self):
        return self.name


# the Tournament class models the actual tournament and keeps track of the schedule and the players' standings
class Tournament:
    def __init__(self):
        self.players = []
        self.results = []
        self.schedule = []

    # adds the player
    def add_player(self, name):
        self.players.append(Player(name))

    # asks for the players' names and returns a list of names
    def get_player_names(self):
        player_names = []
        user_input = ''
        player_num = 1
        too_few_names = False
        same_name = False
        run = True
        while run:
            screen.fill('gray')
            for i in range(150):
                column = i % 8
                row = i // 8
                # draw the actual board and layout
                if row % 2 == 0:
                    pygame.draw.rect(screen, 'white', [1000 - column * 200, row * 100, 100, 100])
                else:
                    pygame.draw.rect(screen, 'white', [900 - column * 200, row * 100, 100, 100])
            pygame.draw.rect(screen, 'snow', [100, 70, 800, 760])
            pygame.draw.rect(screen, 'gold', [100, 70, 800, 760], 5)
            # while there are less than 50 registered players
            if player_num < 101:
                screen.blit(medium_font.render(f'Type the name for Player {player_num}:', True, 'black'), (210, 210))
            # after 100 players
            else:
                screen.blit(medium_font.render(f'You\'ve reached the player limit!',True, 'black'), (210, 210))

            screen.blit(font.render(f'(Name must be less than 13 characters)', True, 'black'), (210, 400))
            screen.blit(font.render(f'Press ENTER to submit a name', True, 'black'), (210, 450))
            screen.blit(font.render(f'Type \'done\' when finished', True, 'black'), (210, 500))

            # if there are less than two names
            if too_few_names:
                screen.blit(font.render(f'There must be at least two names to start!', True, 'black'), (210, 540))
            # if the user types in an existing name
            if same_name:
                screen.blit(font.render(f'Name already exists!', True, 'black'), (210, 570))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # delete a letter by backspace button
                    if event.key == pygame.K_BACKSPACE:
                        if user_input != '':
                            user_input = user_input[:-1]
                    # if player presses ENTER, the name is registered
                    elif event.key == pygame.K_RETURN and user_input != '':
                        # when the user types 'done', finish collecting names
                        if user_input == 'done':
                            # if there are less than two players
                            if len(player_names) < 2:
                                too_few_names = True
                                user_input = ''
                            else: # otherwise start the tournament
                                run = False
                        else: # if the user enters a name
                            if player_num < 101:
                                # if the username already exists
                                if user_input in player_names:
                                    same_name = True
                                    user_input = ''
                                else: # register the name
                                    player_names.append(user_input)
                                    user_input = ''
                                    player_num += 1
                                    if too_few_names: too_few_names = False
                                    if same_name: same_name = False
                    else:
                        user_input += event.unicode
            # if the name is too long
            if len(user_input) > 13:
                user_input = user_input[:-1]

            # show the name as user types on screen
            screen.blit(medium_font.render(user_input, True, 'black'), (210, 280))
            pygame.display.flip()

        return player_names

    # schedules the matches based on a round-robin style match-up, where no one plays twice
    def schedule_matches(self):
        n = len(self.players)
        players = self.players[:]

        if n % 2 == 1:
            players.append(Player("Bye"))  # Add a dummy player for odd number of players
            n += 1
        # there will be n - 1 rounds if there are even number of players
        # there will be n rounds if there are odd number of players (n-1 since we added a dummy)
        rounds = n - 1

        for round_num in range(rounds):
            matches = []  # list that will contain tuples of matched players
            for i in range(n // 2):
                if players[i].name != "Bye" and players[-i - 1].name != "Bye":
                    # match two players at the ends of the list, then match the next players that
                    # are closer to the middle (sort of like pairing onion layers)
                    matches.append((players[i], players[-i - 1]))

            players.insert(1, players.pop())  # move the last player to first and repeat
            self.schedule.append(matches)

    # show a vs screen before a match
    def vs_screen(self, player1, player2):
        run = True
        # if one of the players is the dummy, don't show this screen
        if player1.name == 'Bye' or player2.name == 'Bye':
            run = False
        while run:
            screen.fill('light yellow')
            screen.blit(medium_font.render(f'Black: {player2.name}', True, 'black'), (210, 210))
            screen.blit(medium_font.render(f'VS.', True, 'black'), (300, 400))
            screen.blit(medium_font.render(f'White: {player1.name}', True, 'black'), (210, 590))
            screen.blit(font.render(f'Press ENTER to play', True, 'black'), (450, 700))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        run = False
            pygame.display.flip()

    # calls on the chess game to be played between two players and adjusts their respective scores
    def play_game(self, player1, player2):

        self.vs_screen(player1, player2)

        # if matched with the dummy player, they pass the round
        if player1.name == 'Bye' or player2.name == 'Bye':
            return

        # Play the game
        winner = chess_game.main(player1,player2)
        if winner == 'white':  # white won
            player1.score += 1.0
        elif winner == 'black':  # black won
            player2.score += 1.0
        else:  # draw
            player1.score += 0.5
            player2.score += 0.5

        self.results.append((player1, player2, winner))
        player1.played = True
        player2.played = True

    # have everyone play the game with respective schedules
    def play_tournament(self, expand):
        self.schedule_matches()
        for round_matches in self.schedule:
            # iterate over each match in the round
            for player1, player2 in round_matches:
                # don't let players play again if they played just now
                if player1.played or player2.played:
                    continue
                if player1.name == 'Bye' or player2.name == 'Bye':
                    continue
                self.play_game(player1, player2)
                self.show_standings(expand)
            # reset played status
            for player1, player2 in round_matches:
                player1.played = False
                player2.played = False

    # screen with standings of players in terms of points
    def show_standings(self, expand_page, tournament_over=False):
        run = True
        page = 1
        while run:
            screen.fill('sandybrown')
            pygame.draw.rect(screen, 'light yellow', [100, 70, 800, 760])
            if not tournament_over:
                screen.blit(medium_font.render(f'Standings:', True, 'black'), (210, 20))
                screen.blit(medium_font.render(f'Press ENTER to play', True, 'black'), (120, 780))
            num = 1 if page == 1 else 51
            # sort players based on score (highest score on top)
            self.players.sort(key=lambda x: x.score, reverse=True)
            for player in self.players:
                if page == 1:
                    # first column for players 1 - 25
                    if player.name != 'Bye' and num <= 25:
                        screen.blit(font.render(f'{num}. {player.name}: {player.score} points', True, 'black'),
                                    (120, 100 + 25 * num))
                        num += 1
                    # second column for players 26 - 50
                    elif player.name != 'Bye' and 26 <= num <= 50:
                        screen.blit(font.render(f'{num}. {player.name}: {player.score} points', True, 'black'),
                                    (550, 100 + 25 * (num - 25)))
                        num += 1
                elif page == 2:
                    # first column for players 51 - 75
                    if player.name != 'Bye' and 51 <= num <= 75:
                        screen.blit(font.render(f'{num}. {player.name}: {player.score} points', True, 'black'),
                                    (120, 100 + 25 * (num - 50)))
                        num += 1
                    # second column for players 76 - 100
                    elif player.name != 'Bye' and 76 <= num <= 100:
                        screen.blit(font.render(f'{num}. {player.name}: {player.score} points', True, 'black'),
                                    (550, 100 + 25 * (num - 75)))
                        num += 1
            # if there are more than 50 players, show the option to switch pages
            if expand_page:
                if page == 1:
                    screen.blit(font.render(f'Press RIGHT to show more', True, 'black'), (580, 810))
                else:
                    screen.blit(font.render(f'Press LEFT to show first page', True, 'black'), (580, 810))
            # if the tournament is over, show the winner
            if tournament_over:
                if self.players[0].score > self.players[1].score:
                    screen.blit(big_font.render(f'{self.players[0].name} wins!', True, 'black'), (210, 20))
                else:
                    screen.blit(big_font.render(f'It\'s a tie!', True, 'black'), (210, 20))
                screen.blit(medium_font.render(f'Press ENTER to exit', True, 'black'), (210, 780))

            # event handling for standings screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # switch pages of standings if there are more than 50 players
                    if event.key == pygame.K_RIGHT and page == 1 and expand_page:
                        page = 2
                    if event.key == pygame.K_LEFT and page == 2 and expand_page:
                        page = 1
                    # ENTER takes user out of the standings screen
                    if event.key == pygame.K_RETURN:
                        run = False
            pygame.display.flip()


if __name__ == '__main__':
    tournament = Tournament()
    # get the player names and add each player to tournament
    player_names = tournament.get_player_names()
    expand = True if len(player_names) > 50 else False
    for name in player_names:
        tournament.add_player(name)

    tournament.play_tournament(expand)
    # show the winner
    tournament.show_standings(expand, tournament_over=True)