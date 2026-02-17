import chess.pgn
import pygame
import time
from chess_windows import ChessWindows

class GameLive:
    def __init__(self, user_name, engine_path):
        self.engine_path = engine_path
        self.user_name = user_name
        self.prev_score = 0.0
        # On ouvre le moteur ICI une seule fois
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.stats = {
            'white': "?", 'w_elo': "?",
            'black': "?", 'b_elo': "?",
            'result': "?", 'score': 0.0
        }
        self.white_pov = True
    
    def _read_game(self, game):
        self.white_pov = game.headers["White"] == self.user_name

        self.stats = {
            'white': game.headers["White"], 'w_elo': game.headers["WhiteElo"],
            'black': game.headers["Black"], 'b_elo': game.headers["BlackElo"],
            'result': game.headers["Result"], 'score': 0.0
        }

    def _read_headers(self, headers):
        self.white_pov = headers["White"] == self.user_name

        self.stats = {
            'white': headers["White"], 'w_elo': headers["WhiteElo"],
            'black': headers["Black"], 'b_elo': headers["BlackElo"],
            'result': headers["Result"], 'score': 0.0
        }

    def change_path(self, new_pgn_path):
        self.pgn_file = new_pgn_path

    def get_score_position(self, board):
        # On utilise le moteur déjà ouvert
        # 0.1s suffit pour une analyse fluide en direct
        info = self.engine.analyse(board, chess.engine.Limit(time=0.1))
        score = info["score"].white()
        
        if score.is_mate():
            return 99.0 if score.mate() >= 0 else -99.0
        return score.score() / 100
    
    def play_custom_line(self, move_list, header):
        self._read_headers(header)
        board = chess.Board()
        self._run_interface(move_list, board)

    def play_game(self):
        self._read_game(game)

        moves = list(game.mainline_moves())
        board = game.board()
        self._run_interface(moves, board)
    
    def _run_interface(self, moves, board):
        game_board = ChessWindows()
        best_move = None
        current_move_idx = 0  # Position actuelle dans la partie
        
        running = True
        while running:
            update_score = False
            # 2. Gestion des entrées clavier (Événements)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:  # Touche flèche DROITE
                        if current_move_idx < len(moves):
                            board.push(moves[current_move_idx])
                            current_move_idx += 1
                            update_score = True
                    
                    elif event.key == pygame.K_LEFT:  # Touche flèche GAUCHE
                        if current_move_idx > 0:
                            board.pop()  # Annule le dernier coup
                            current_move_idx -= 1
                            update_score = True

                    elif event.key == pygame.K_f:  # 'f' pour Flip
                        self.white_pov = not self.white_pov

                    elif event.key == pygame.K_q:
                        running = False

            if update_score:
                self.stats["score"] = self.get_score_position(board)
                best_move = self.engine.play(board, chess.engine.Limit(time=0.1)).move

            # 3. Dessin
            game_board.draw_header(self.stats)
            game_board.draw_board(self.white_pov, board, best_move)
            # self.get_score_position()
            # 4. Rafraîchissement
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game_live = GameLive("Hadriwer", "/usr/games/stockfish")
    game_to_watch_id = 8
    game_cnt = 0
    with open("data/chess_com_games_2026-02-17.pgn") as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            game_cnt += 1
            if game_cnt == game_to_watch_id:
                game_live.play_game(game)
            elif game_cnt > game_to_watch_id:
                break

        game_live.engine.quit()