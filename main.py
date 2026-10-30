import pygame
import random

# Initialize Pygame
pygame.init()

# --- CONFIGURATION CONSTANTS ---
WIDTH, HEIGHT = 800, 800
FPS = 60
GRID_SIZE = 25  # Increased size for a better maze experience (25x25 grid)
CELL_SIZE = WIDTH // GRID_SIZE

# Colors
COLOR_BG = (22, 22, 29)         # Dark slate blue
COLOR_WALL = (145, 150, 163)     # Muted silver gray
COLOR_START = (39, 174, 96)      # Soft green
COLOR_GOAL = (192, 57, 43)       # Soft red
COLOR_PLAYER = (52, 152, 219)    # Bright blue
COLOR_VISITED = (44, 62, 80)     # Dark accent for carved rooms during generation
COLOR_CURRENT = (241, 196, 15)   # Gold marker for the generation head

COLOR_ENEMY = (219, 152, 52)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Maze: Watch Generation or Play with Arrows!")
clock = pygame.time.Clock()

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Walls ordered: [Top, Right, Bottom, Left] or NESW
        self.walls = [True, True, True, True]
        self.visited = False

    def draw(self, surface, is_generating=False):
        """Draws the background cell area and its walls."""
        x_pix = self.x * CELL_SIZE
        y_pix = self.y * CELL_SIZE

        # Draw backgrounds during the live generation phase
        if is_generating and self.visited:
            pygame.draw.rect(surface, COLOR_VISITED, (x_pix, y_pix, CELL_SIZE, CELL_SIZE))

        # Render walls as distinct lines
        if self.walls[0]: # Top
            pygame.draw.line(surface, COLOR_WALL, (x_pix, y_pix), (x_pix + CELL_SIZE, y_pix), 2)
        if self.walls[1]: # Right
            pygame.draw.line(surface, COLOR_WALL, (x_pix + CELL_SIZE, y_pix), (x_pix + CELL_SIZE, y_pix + CELL_SIZE), 2)
        if self.walls[2]: # Bottom
            pygame.draw.line(surface, COLOR_WALL, (x_pix + CELL_SIZE, y_pix + CELL_SIZE), (x_pix, y_pix + CELL_SIZE), 2)
        if self.walls[3]: # Left
            pygame.draw.line(surface, COLOR_WALL, (x_pix, y_pix + CELL_SIZE), (x_pix, y_pix), 2)


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dead = False
        self.past_time = 0

    def move(self, dx, dy, grid):
        """Moves the player safely by verifying if a wall is blockading them."""
        current_cell = grid[self.y][self.x]
        
        # Check boundaries and wall arrays before jumping positions
        if dx == 1 and not current_cell.walls[1]:    # Move Right
            self.x += 1
        elif dx == -1 and not current_cell.walls[3]:  # Move Left
            self.x -= 1
        elif dy == 1 and not current_cell.walls[2]:   # Move Down
            self.y += 1
        elif dy == -1 and not current_cell.walls[0]:  # Move Up
            self.y -= 1

    def draw(self, surface):
        """Draws the player node in the middle of their current tracking cell."""
        center_x = (self.x * CELL_SIZE) + (CELL_SIZE // 2)
        center_y = (self.y * CELL_SIZE) + (CELL_SIZE // 2)
        radius = CELL_SIZE // 3
        pygame.draw.circle(surface, COLOR_PLAYER, (center_x, center_y), radius)

class Enemy:
    def __init__(self):
        self.x = random.randint(5, 25)
        self.y = random.randint(5, 25)
    def move(self, dx, dy, grid):
        cell = grid[self.y][self.x]
        if dx == 1 and not cell.walls[1]:
            self.x += 1
        elif dx == -1 and not cell.walls[3]:
            self.x -= 1
        elif dy == 1 and not cell.walls[2]:
            self.y += 1
        elif dy == -1 and not cell.walls[0]:
            self.y -= 1
    def track(self, player, grid):
        goal = (player.x, player.y)
    def wander(self, grid):
        cell = grid[self.y][self.x]
        y_diff = random.randint(-1, 1)
        match y_diff:
            case -1:
                if not cell.walls[2]:
                    self.y -= 1
            case 0:
                pass
            case 1:
                if not cell.walls[0]:
                    self.y += 1
        x_diff = random.randint(-1, 1)
        match x_diff:
            case -1:
                if not cell.walls[3]:
                    self.x -= 1
            case 0:
                pass
            case 1:
                if not cell.walls[1]:
                    self.x += 1

    def draw(self, surface):
        center_x = (self.x * CELL_SIZE) + (CELL_SIZE // 2)
        center_y = (self.y * CELL_SIZE) + (CELL_SIZE // 2)
        radius = CELL_SIZE // 3
        pygame.draw.circle(surface, COLOR_ENEMY, (center_x, center_y), radius)


def get_neighbors(cell, grid):
    """Gathers all unvisited neighbors adjacent to the cell."""
    neighbors = []
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] # Top, Right, Bottom, Left
    
    for dx, dy in directions:
        nx, ny = cell.x + dx, cell.y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            neighbor = grid[ny][nx]
            if not neighbor.visited:
                neighbors.append(neighbor)
    return neighbors


def remove_walls(current, next_cell):
    """Safely tears down the matching wall variables between two neighboring cells."""
    dx = current.x - next_cell.x
    dy = current.y - next_cell.y

    if dx == -1: # Next is right
        current.walls[1] = False
        next_cell.walls[3] = False
    elif dx == 1: # Next is left
        current.walls[3] = False
        next_cell.walls[1] = False
        
    if dy == -1: # Next is down
        current.walls[2] = False
        next_cell.walls[0] = False
    elif dy == 1: # Next is up
        current.walls[0] = False
        next_cell.walls[2] = False


def reset_generation_state():
    """Initializes a new grid template, structural generation trackers, and stack chains."""
    grid = [[Cell(x, y) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
    stack = []
    current = grid[0][0]
    current.visited = True
    generating = True
    return grid, stack, current, generating


def main():
    grid, stack, current, generating = reset_generation_state()
    player = Player()
    enemy = Enemy()
    running = True

    while running:
        screen.fill(COLOR_BG)

        # --- EVENT MANAGER SYSTEM ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Manual Generation Trigger
                if event.key == pygame.K_SPACE:
                    grid, stack, current, generating = reset_generation_state()
                    player.x, player.y = 0, 0 # Snap player back to start area
                
                # Active Gameplay Controls (Ignored while maze is animating)
                elif not generating:
                    if event.key == pygame.K_UP:
                        player.move(0, -1, grid)
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1, grid)
                    elif event.key == pygame.K_LEFT:
                        player.move(-1, 0, grid)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0, grid)

        # --- ANIMATED GENERATION MACHINE ---
        if generating:
            # Execute one step of the DFS algorithm per frame
            neighbors = get_neighbors(current, grid)
            if neighbors:
                next_cell = random.choice(neighbors)
                stack.append(current)
                remove_walls(current, next_cell)
                next_cell.visited = True
                current = next_cell
            elif stack:
                current = stack.pop()
            else:
                # Stack is empty: Maze generation is fully finished!
                generating = False

        # --- DRAWING SYSTEM ---
        # 1. Base Grid Layer
        for row in grid:
            for cell in row:
                cell.draw(screen, is_generating=generating)

        # 2. Draw Start and End Markers (When generation finishes)
        if not generating:
            pygame.draw.rect(screen, COLOR_START, (2, 2, CELL_SIZE - 2, CELL_SIZE - 2))
            pygame.draw.rect(screen, COLOR_GOAL, ((GRID_SIZE - 1) * CELL_SIZE + 2, (GRID_SIZE - 1) * CELL_SIZE + 2, CELL_SIZE - 2, CELL_SIZE - 2))
            # Draw the playable element overlay
            player.draw(screen)
            #enemy.track(player, grid)
            enemy.draw(screen)
            if pygame.time.get_ticks() - player.past_time >= 500:
                player.past_time = pygame.time.get_ticks()
                enemy.wander(grid)
        else:
            # Draw visual tracking box over the current algorithm generation head
            pygame.draw.rect(screen, COLOR_CURRENT, (current.x * CELL_SIZE + 3, current.y * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6))

        pygame.display.flip()
        
        # Speed multiplier setup: run faster during generation to reduce wait time
        clock.tick(120 if generating else FPS)

    pygame.quit()

if __name__ == "__main__":
    main()