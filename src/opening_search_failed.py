import chess.pgn
import os
import json

def export_line(path, moves, header):
    # 1. Préparer l'objet à enregistrer
    # On convertit les moves en UCI et on garde le header tel quel
    new_entry = {
        "header": dict(header),
        "moves": [m.uci() for m in moves]
    }
    
    # 2. Charger les données existantes
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                data = json.load(f)
                # On s'assure que data est bien une liste
                if not isinstance(data, list): 
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # 3. Ajouter la nouvelle entrée (header + moves)
    data.append(new_entry)

    # 4. Sauvegarder avec une indentation pour que ce soit lisible
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    # seuil max quand on sort de l'ouverture si l'adversaire a un avantage de 1 (ou -1)
    seuil_max = 1.2
    # profondeur de l'ouverture
    deep_oppening = 20
    name = "Hadriwer"
    engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
    game_cnt = 0

    export_path = "data/oppening_failed.json"

    with open("data/chess_com_games_2026-02-17.pgn") as pgn:

        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            game_cnt += 1
            print(f"Game n° = {game_cnt}")
            is_white = game.headers["White"] == name
            # beg = 0 if is_white else 1

            moves = list(game.mainline_moves())
            # my_moves = moves[beg:deep_oppening:2]
            # oponent_moves = moves[abs(beg-1):deep_oppening:2]

            board = game.board()

            for move in moves[:deep_oppening]:
                board.push(move)
                score_engine = engine.analyse(board, chess.engine.Limit(time=0.1))
                score = score_engine["score"].white().score()
                if score is None:
                    raise ValueError("wtf")
                score /= 100
                
                if is_white and score <= -seuil_max:
                    print(f"score = {score}")
                    print(board.move_stack)
                    export_line(export_path, board.move_stack, game.headers)
                    break
                    
                if (not is_white) and score >= seuil_max:
                    print(f"score = {score}")
                    print(board.move_stack)
                    export_line(export_path, board.move_stack, game.headers)
                    break
        
    engine.quit()