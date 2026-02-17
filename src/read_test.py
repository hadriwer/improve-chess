import chess.pgn
import chess.svg # Utile si vous préférez générer des images
import time

def play_game_live(pgn_file):
    with open(pgn_file) as pgn:
        game = chess.pgn.read_game(pgn)
        if not game:
            return

        board = game.board()
        
        print("Début de la partie...")
        for move in game.mainline_moves():
            board.push(move)
            
            # 1. Affichage console (rapide pour tester)
            # On efface la console pour l'effet "animation"
            print("\033c", end="") 
            print(board)
            print(f"\nDernier coup : {move}")
            
            # 2. Pause pour simuler le direct (0.5 seconde entre chaque coup)
            time.sleep(0.5)

if __name__ == "__main__":
    play_game_live("data/chess_com_games_2026-02-16.pgn")