from play_game import GameLive
import json
import chess

def load_lines(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    game_live = GameLive("Hadriwer", "/usr/games/stockfish")
    lines_path = "data/oppening_failed.json"

    # Load oppenings that you've failed
    oppenings_failed = load_lines(lines_path)

    for line in oppenings_failed:
        header = line["header"]
        print(header)
        line = [chess.Move.from_uci(m) for m in line["moves"]]
        game_live.play_custom_line(line, header)

    game_live.engine.quit()

if __name__ == "__main__":
    main()