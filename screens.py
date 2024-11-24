import pygame
import sys

# Constants
WIDTH, HEIGHT = 800, 600
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
TOGGLE_WIDTH, TOGGLE_HEIGHT = 50, 50

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, (186, 135, 89), self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main_menu(screen):
    def start_game():
        return True
    
    pygame.display.set_caption("Chess Game - Main Menu")
    font = pygame.font.Font(None, 36)

    pawn_image = pygame.image.load("assets/3d-pawn.png")
    pawn_image = pygame.transform.smoothscale(pawn_image, (250, 250))  # Assign back to pawn_image

    button_1v1 = Button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 - BUTTON_HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT, "1v1 Mode", start_game)
    number_value = 0
    number_display = font.render("Infinite time 8", True, (255, 255, 255))

    plus_button = Button(WIDTH // 2 + BUTTON_WIDTH // 2 + 20, HEIGHT // 2 - BUTTON_HEIGHT // 2, TOGGLE_WIDTH, TOGGLE_HEIGHT, "+")
    minus_button = Button(WIDTH // 2 - BUTTON_WIDTH // 2 - TOGGLE_WIDTH - 20, HEIGHT // 2 - BUTTON_HEIGHT // 2, TOGGLE_WIDTH, TOGGLE_HEIGHT, "-")

    button_AI = Button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + BUTTON_HEIGHT // 2 + 70, BUTTON_WIDTH, BUTTON_HEIGHT, "Versus AI", start_game)

    button_quit = Button(WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + BUTTON_HEIGHT // 2 + 140, BUTTON_WIDTH, BUTTON_HEIGHT, "Quit")

    running = True
    while running:
        screen.fill((30, 30, 30))

        # Draw the pawn image at the top center
        screen.blit(pawn_image, (WIDTH // 2 - pawn_image.get_width() // 2, 20))

        # Draw buttons and number display
        button_1v1.draw(screen)
        plus_button.draw(screen)
        minus_button.draw(screen)
        screen.blit(number_display, (WIDTH // 2 - number_display.get_width() // 2, HEIGHT // 2 + BUTTON_HEIGHT // 2 + 20))
        button_AI.draw(screen)
        button_quit.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_1v1.is_clicked(event.pos):
                    return number_value  # Return the timer value
                if plus_button.is_clicked(event.pos) and number_value < 120:
                    number_value += 1
                    number_display = font.render(
                        "Infinite time." if number_value == 0 else f"{number_value}min.", 
                        True, 
                        (255, 255, 255)
                    )
                if minus_button.is_clicked(event.pos) and number_value > 0:
                    number_value -= 1
                    number_display = font.render(
                        "Infinite time." if number_value == 0 else f"{number_value}min.", 
                        True, 
                        (255, 255, 255)
                    )

                if button_quit.is_clicked(event.pos):
                    pygame.quit()
                    sys.exit()
                
        pygame.display.flip()


def promotion_choice(WIDTH, HEIGH):
    font = pygame.font.Font(None, 80)
    text = "Promotion! Choose with what promoting your pawn.\n~~Press:"
    screen = pygame.display.get_surface()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Promotion text
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(text_surface, text_rect)

    # Options
    option_font = pygame.font.Font(None, 50)
    queen_text = "1-> Queen"
    rook_text = "2-> Rook"

    queen_surface = option_font.render(queen_text, True, (255, 255, 255))
    rook_surface = option_font.render(rook_text, True, (255, 255, 255))

    queen_rect = queen_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    rook_rect = rook_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

    screen.blit(queen_surface, queen_rect)
    screen.blit(rook_surface, rook_rect)

    pygame.display.flip()

def game_over(winner: str, WIDTH, HEIGHT):
    """
    Display a game-over screen.
    """
    font = pygame.font.Font(None, 80)
    text = f"{winner} wins!"
    screen = pygame.display.get_surface()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # GameOver text
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(text_surface, text_rect)

    # Options
    option_font = pygame.font.Font(None, 50)
    restart_text = "Press R to Restart"
    quit_text = "Press Esc to Quit"

    restart_surface = option_font.render(restart_text, True, (255, 255, 255))
    quit_surface = option_font.render(quit_text, True, (255, 255, 255))

    restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    quit_rect = quit_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

    screen.blit(restart_surface, restart_rect)
    screen.blit(quit_surface, quit_rect)

    pygame.display.flip()

    # Quit or restart
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pass  # Restart the game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
