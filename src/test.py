import chess
import chess.engine

# Créer un plateau (position de départ par défaut)
board = chess.Board()

# Chemin vers l'exécutable Stockfish que vous avez téléchargé
engine_path = "/usr/games/stockfish"

with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
    # Analyser la position pendant 0.1 seconde
    info = engine.analyse(board, chess.engine.Limit(time=0.5))
    
    # Récupérer le score du point de vue des Blancs
    score = info["score"].white()
    
    if score.is_mate():
        print(f"Mat en {abs(score.mate())} coups")
    else:
        print(f"Estimation : {score.score() / 100} pions")