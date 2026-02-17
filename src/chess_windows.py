import pygame
import chess.svg
import cairosvg
import io
import math

# Color
LIGHT_SQUARE_COLOR = (238, 238, 210)
DARK_SQUARE_COLOR = (118, 150, 86)

def load_svg(svg_code, size):
    """Rendu d'un code XML SVG vers une Surface Pygame."""
    # On convertit le code texte du SVG en PNG (en mémoire)
    # On utilise 'bytestring' car on lui passe le contenu du SVG, pas un fichier
    png_data = cairosvg.svg2png(bytestring=svg_code, output_width=size, output_height=size)
    
    # On charge les données binaires dans Pygame via un buffer
    image_file = io.BytesIO(png_data)
    return pygame.image.load(image_file)

class ChessWindows:
    def __init__(self, WIDTH=800, HEIGHT=800):
        self.width = WIDTH
        self.height = HEIGHT
        self.board_size = 8
        self.square_size = self.width // self.board_size
        self._convert_svg()
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Échiquier Pygame")

        # Header 
        self.header_height = 100
        self.screen = pygame.display.set_mode((800, 800 + self.header_height))
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)

    def draw_arrow(self, surface, start_coord, end_coord, color=(255, 165, 0), width=10):
        start = pygame.Vector2(start_coord)
        end = pygame.Vector2(end_coord)
        
        # 1. Vecteur directionnel (du départ vers l'arrivée)
        direction = end - start
        if direction.length() == 0:
            return
        
        # On normalise pour avoir une unité de mesure
        unit_dir = direction.normalize()
        # Vecteur perpendiculaire pour la largeur de la tête
        perpendicular = pygame.Vector2(-unit_dir.y, unit_dir.x)

        # 2. Ajuster l'extrémité du corps (pour ne pas dépasser de la pointe)
        head_size = width * 3
        line_end = end - (unit_dir * (head_size * 0.5)) 
        
        # Dessiner le corps
        pygame.draw.line(surface, color, start, line_end, width)

        # 3. Calculer les 3 points du triangle de la tête
        # La pointe (le sommet)
        point_top = end
        # Les deux points de la base, en reculant par rapport à la pointe
        base_center = end - (unit_dir * head_size)
        point_left = base_center + (perpendicular * (head_size / 1.5))
        point_right = base_center - (perpendicular * (head_size / 1.5))

        # Dessiner la tête
        pygame.draw.polygon(surface, color, [point_top, point_left, point_right])

    def draw_move_arrow(self, move, white_pov):
        # 1. Récupérer les indices (col, row)
        from_sq = move.from_square
        to_sq = move.to_square
        
        def get_pixel_coords(square):
            col = chess.square_file(square)
            row = chess.square_rank(square)
            
            if not white_pov:
                col = 7 - col
                row = 7 - row
            
            # Centrer la coordonnée dans la case (+ OFFSET du header)
            x = col * self.square_size + self.square_size // 2
            y = (7 - row) * self.square_size + self.square_size // 2 + self.header_height
            return (x, y)

        start_pix = get_pixel_coords(from_sq)
        end_pix = get_pixel_coords(to_sq)
        
        # Dessiner la flèche (ici en rouge translucide)
        self.draw_arrow(self.screen, start_pix, end_pix, color=(255, 165, 0)) # Orange

    def draw_header(self, info):
        # Fond du header (un gris foncé élégant)
        header_rect = pygame.Rect(0, 0, 800, self.header_height)
        pygame.draw.rect(self.screen, (44, 44, 44), header_rect)
        
        # Séparateur
        pygame.draw.line(self.screen, (100, 100, 100), (0, self.header_height-2), (800, self.header_height-2), 2)

        # Texte : Blancs
        w_text = self.font.render(f"White : {info['white']} ({info['w_elo']})", True, (255, 255, 255))
        self.screen.blit(w_text, (20, 20))
        
        # Texte : Noirs
        b_text = self.font.render(f"Black : {info['black']} ({info['b_elo']})", True, (255, 255, 255))
        self.screen.blit(b_text, (20, 55))

        # Résultat au centre
        res_text = self.font.render(info['result'], True, (255, 215, 0)) # Doré
        res_rect = res_text.get_rect(center=(400, 50))
        self.screen.blit(res_text, res_rect)

        # avantage
        score_pos = self.font_small.render(f"Eval = {info["score"]}", True, (255, 255, 255))
        self.screen.blit(score_pos, (400, 80))
        
        # Aide à droite
        help_text = self.font_small.render("<- : Précédent | Suivant : ->", True, (180, 180, 180))
        key_text = self.font_small.render("f : flip board | q : quit", True, (180, 180, 180))
        self.screen.blit(help_text, (500, 10))
        self.screen.blit(key_text, (500, 40))

    def _convert_svg(self):
        # Dictionnaire des symboles de pièces
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        
        self.piece_images = {}
        for symbol in pieces:
            # 1. Obtenir l'objet Piece
            piece = chess.Piece.from_symbol(symbol)
            # 2. Obtenir le code XML du SVG via la lib python-chess
            svg_code = chess.svg.piece(piece)
            # 3. Transformer en Surface Pygame
            self.piece_images[symbol] = load_svg(svg_code, self.square_size)
    
    def draw_board(self, white_pov, board, best_move):
        y_offset = self.header_height
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Dessiner les cases
                color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
                pygame.draw.rect(self.screen, color, (col * self.square_size, (row * self.square_size) + y_offset, self.square_size, self.square_size))

                if white_pov:
                    # Vue classique (Blancs en bas)
                    square = chess.square(col, 7 - row)
                else:
                    # Vue inversée (Noirs en bas)
                    # Col 0 devient Col 7, Row 0 devient Row 7
                    square = chess.square(7 - col, row)

                piece = board.piece_at(square)
                if piece:
                    # La représentation textuelle de la pièce (ex: 'p', 'K')
                    piece_char = piece.symbol() 
                    
                    # Récupérer l'image correspondante et la dessiner
                    if piece_char in self.piece_images:
                        self.screen.blit(self.piece_images[piece_char], (col * self.square_size, (row * self.square_size) + y_offset))
        if best_move:
            self.draw_move_arrow(best_move, white_pov)