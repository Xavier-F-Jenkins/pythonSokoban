import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable
from model import SokobanModel, Tile, Entity
from a2_support import *
from a3_support import *

COIN = '$'

def get_image_path(item) -> str:
    """
    Returns the file path for the selected image via dictionary.
    """
    image_paths = {
        FLOOR: "images/Floor.png",
        COIN: "images/$.png",
        CRATE: "images/C.png",
        GOAL: "images/G.png",
        FILLED_GOAL: "images/X.png",
        WALL: "images/W.png",
        PLAYER: "images/P.png",
        MOVE_POTION: "images/M.png",
        STRENGTH_POTION: "images/S.png",
        FANCY_POTION: "images/F.png"
    }
    return image_paths.get(item)

class FancyGameView(AbstractGrid):
    """
    Game view of Sokoban MVC. Inherits from AbstractGrid to place images
    on a grid in a GUI Window.
    """

    def __init__(self, master: tk.Frame | tk.Tk, dimensions: tuple[int, int],
                 size: tuple[int, int], **kwargs) -> None:
        """
        Sets up FancyGameView to inherit appropriate size and dimensions from
        abstract_grid. Also creates an image cache with a dictionary.
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._image_storage_cache = {}

    def display(self, maze: Grid,
                entities: Entities, player_position: Position):
        """
        Clears game view, then places images for tiles and instances.
        Floor tiles are assumed to be underneath all entities.
        """
        self.clear()  # Clears View for image placement

        for y, row in enumerate(maze):
            for x, item in enumerate(row):
                y_x = (y, x)

                if isinstance(item, Tile):
                    path = get_image_path(item.get_type())
                    tile_image = get_image(path, self.get_cell_size(),
                                           self._image_storage_cache)

                    self.create_image(self.get_midpoint(y_x),
                                      image = tile_image)

                if isinstance(item, Entity):
                    path = get_image_path(item.get_type())
                    entity_image = get_image(path, self.get_cell_size(),
                                             self._image_storage_cache)

                    self.create_image(self.get_midpoint(y_x),
                                      image=entity_image)
                    
                if y_x in entities:
                    e = entities[y_x]
                    path = get_image_path(e.get_type())
                    ent_image = get_image(path, self.get_cell_size(),
                                          self._image_storage_cache)

                    self.create_image(self.get_midpoint(y_x),
                                      image = ent_image)
                    if e.get_type() == CRATE:
                        crate_strength = str(e.get_strength())
                        self.annotate_position(y_x, # Put strength num on crate
                                               crate_strength, CRATE_FONT)

                if y_x == player_position:
                    path = get_image_path(PLAYER)
                    player_image = get_image(path, self.get_cell_size(),
                                             self._image_storage_cache)

                    self.create_image(self.get_midpoint(y_x),
                                      image = player_image)


class FancyStatsView(AbstractGrid):
    """
    Viewer for player stats that are placed by Abstract Grid.
    Title at the top row, middle col, Stat names in middle row across 3 col,
    stat values underneath stat names in bottom row.
    """
    
    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """
        Sets up this FancyStatsView to be an AbstractGrid with the appropriate
        number of rows and columns, and the appropriate width and height.
        """
        size = (MAZE_SIZE + SHOP_WIDTH, STATS_HEIGHT)
        super().__init__(master, dimensions = (3, 3), size=size)

    def draw_stats(self, moves_remaining: int,
                   strength: int, money: int) -> None:
        """
        Clears the FancyStatsView and redraws it to display the provided
        moves remaining, strength, and money.
        """
        self.clear()
        stat_names = ["Moves remaining:", "Strength:", "Money:"]
        stat_nums = [moves_remaining, strength, money]

        # Title
        self.annotate_position((0, 1), "Player Stats", font = TITLE_FONT)

        # Stat Names
        for col, name in enumerate(stat_names):
            name_pos = (1, col)
            self.annotate_position(name_pos, name)

        # Stat Values
        for col, num in enumerate(stat_nums):
            if col == 2:
                self.annotate_position((2, 2), "$" + str(num))
            else:
                num_pos = (2, col)
                self.annotate_position(num_pos, str(num))

                                       
class Shop(tk.Frame):
    """Shop class for viewer that acts like tk.Frame."""
    
    def __init__(self, master: tk.Frame) -> None:
        """Creates the Shop Frame title, at centre top."""
        super().__init__(master)
        self.shop_title = tk.Label(self, text = "Shop",
                                   font = TITLE_FONT)
        self.shop_title.pack(side = tk.TOP, anchor = tk.N)

    def create_buyable_item(self, item: str, amount: int,
                            callback: Callable[[], None]) -> None:
        """
        Creates the shops buyable items for the three potions and puts the
        item names and prices next to a button that can buy the item
        via lambda callback
        """
        POTION_NAME = {
            "S": "Strength Potion",
            "M": "Move Potion",
            "F": "Fancy Potion",
        }
        ITEM_COSTS = {
            STRENGTH_POTION: 5,
            MOVE_POTION: 5,
            FANCY_POTION: 10,
        }
        
        # Create a frame for the buyable item
        self.new_item_frame = tk.Frame(self)
        self.new_item_frame.pack(side = tk.TOP, fill = tk.X)

        # Create a label for the item name and cost
        self.new_item_label = tk.Label(
            self.new_item_frame,
            text = f"{POTION_NAME.get(item)}: ${amount}",
        )
        self.new_item_label.pack(side = tk.LEFT, fill = tk.BOTH,
                                 expand = tk.TRUE)

        # Create a button for buying the item via lambda callback
        self.buy_item_button = tk.Button(self.new_item_frame,
                                         text = "Buy",
                                         command = lambda: callback(item))
        self.buy_item_button.pack(side = tk.RIGHT, anchor = tk.E)
        

class FancySokobanView:
    """
    Main view class that puts smaller GUI components into one window.
    """
    def __init__(self, master: tk.Tk,
                 dimensions: tuple[int, int], size: tuple[int, int]) -> None:
        """Initialise frames and views to be utilised in controller."""
        self.root = master
        self.dimensions = dimensions
        self.size = size

        # Create frame for game and shop to sit side by side
        self.game_shop_frame = tk.Frame(self.root)
        self.game_shop_frame.pack(side = tk.TOP, anchor = tk.NW)
        
        # Put game frame in game_shop_frame
        self._game_frame = tk.Frame(self.game_shop_frame)
        self._game_frame.pack(side = tk.LEFT,
                              anchor = tk.W, fill = tk.BOTH, expand = True)
        self._game_view = FancyGameView(self._game_frame,
                                        dimensions = self.dimensions,
                                        size = (450, 450))
        self._game_view.config(width = 450, height = 450)
        self._game_view.pack(fill = tk.BOTH, expand = True)
        
        # Put stats_view in its own frame at bottom of window
        self.stats_view = FancyStatsView(self.root)
        self.stats_view.pack(side = tk.BOTTOM, anchor = tk.NW,
                             fill = tk.BOTH, expand = True)

    def display_game(self, maze: Grid, entities: Entities,
                     player_position: Position) -> None:
        """Clears and displays game view with current maze configuration."""
        self._game_view.clear()
        self._game_view.display(maze, entities, player_position)

    def display_shop(self) -> None:
        """Makes shop frame to sit next to Game, and displays Shop."""
        self._shop_frame = tk.Frame(self.game_shop_frame,
                                    width = 200, height = 450)
        self._shop_frame.pack(side = tk.RIGHT, anchor = tk.NE,
                              fill = tk.BOTH, expand = True)
        self._shop_view = Shop(self._shop_frame)
        self._shop_view.pack(side = tk.TOP, anchor = tk.NE,
                             fill = tk.BOTH, expand = True)

    def display_stats(self, moves: int, strength: int, money: int):
        """Clears and displays current player stats."""
        self.stats_view.clear()
        self.stats_view.draw_stats(moves, strength, money)

    def create_shop_items(self, shop_items: dict[str, int],
                          button_callback: Callable[[str], None] = None):
        """
        Creates items that can be purchased in shop by
        calling create_buyable_item
        """
        for item_id, amount in shop_items.items():
            self._shop_view.create_buyable_item(item_id,
                                                amount, button_callback)


class ExtraFancySokoban:
    """Controller class for Sokoban MVC"""
    def __init__(self, root: tk.Tk, maze_file: str) -> None:
        """
        Initialise root, model, and views to communicate the models gameplay
        to the players view.
        """
        # Create Model Instance
        self._root = root
        self._maze_file = maze_file
        self._model = SokobanModel(self._maze_file)

        # Size and Dimension
        rows, cols = self._model.get_dimensions()
        width, height = (MAZE_SIZE + SHOP_WIDTH,
                         MAZE_SIZE + BANNER_HEIGHT + STATS_HEIGHT)
        self._dimension = (rows, cols)
        self._size = (width, height)

        # Game grid variables
        self.game_maze = self._model.get_maze()
        self.game_entity = self._model.get_entities()
        self.game_player_position = self._model.get_player_position()

        # Game player variables
        self.player_moves = self._model.get_player_moves_remaining()
        self.player_strength = self._model.get_player_strength()
        self.player_money = self._model.get_player_money()

        # Shop Variables
        self._shop_items = self._model.get_shop_items()

        # Create View Instance to display the current game
        self._view = FancySokobanView(self._root,
                                      self._dimension, self._size)
        self._view.display_shop()
        self._view.create_shop_items(self._shop_items,
                                     self.handle_button_callback)
        self.display_game_and_stats()

    def display_game_and_stats(self) -> None:
        """
        Display game and stats. seperate function for refreshing
        game view and player stats after successfull attempt move.
        """
        self.game_maze = self._model.get_maze()
        self.game_entity = self._model.get_entities()
        self.game_player_position = self._model.get_player_position()

        self.player_moves = self._model.get_player_moves_remaining()
        self.player_strength = self._model.get_player_strength()
        self.player_money = self._model.get_player_money()

        self._view.display_game(self.game_maze, self.game_entity, self.game_player_position)
        self._view.display_stats(self.player_moves, self.player_strength, self.player_money)

    def handle_button_callback(self, item_id) -> None:
        """
        Callback handler for player purchasing item from shop. Uses attempt
        purchase from model to ensure player has enough money and passes over
        relevent stats.
        """
        ID_TO_NAME = {
            "S": STRENGTH_POTION,
            "M": MOVE_POTION,
            "F": FANCY_POTION,
        }
        item = ID_TO_NAME.get(item_id)
        self._model.attempt_purchase(item)
        self.redraw()

    def redraw(self) -> None:
        """Redraws gameplay for attempt move and resetting the game."""
        self.game_maze = self._model.get_maze()
        self.game_entity = self._model.get_entities()
        self.game_player_position = self._model.get_player_position()

        self.player_moves = self._model.get_player_moves_remaining()
        self.player_strength = self._model.get_player_strength()
        self.player_money = self._model.get_player_money()

        self.display_game_and_stats()

    def handle_keypress(self, event: tk.Event) -> None:
        """Converts players keypresses to models attempt move for gameplay."""
        move = event.keysym
        move = move.lower()
        move_to_wasd = {
            "up": "w",
            "down": "s",
            "left": "a",
            "right": "d",
        }
        if move in move_to_wasd:
            move = move_to_wasd[move]
            
        self._model.attempt_move(move)
        self.redraw() # Redraws game after move completed

        if self._model.has_won():
            yes_or_no = messagebox.askyesno(message = "You won! Play again?")
            if not yes_or_no:
                self._root.destroy() # Stops game in player says no
            else:
                self._model.reset()
                self.redraw()
                
        elif self._model.get_player_moves_remaining() <= 0:
            yes_or_no = messagebox.askyesno(message = "You lost! Play again?")
            if not yes_or_no:
                self._root.destroy()
            else:
                self._model.reset()
                self.redraw()

    
def place_banner(root, banner_cache) -> None:
    """Places banner at top of window when starting game."""
    banner_image = get_image("images/banner.png",
                             (MAZE_SIZE + SHOP_WIDTH, BANNER_HEIGHT),
                             banner_cache)
    banner_label = tk.Label(image = banner_image)
    banner_label.pack(side = tk.TOP, anchor = tk.NW)


def play_game(root: tk.Tk, maze_file: str) -> None:
    """Acts like main() for online testing."""
    root.title("Extra Fancy Sokoban")
    banner_cache = {}
    place_banner(root, banner_cache)
    controller = ExtraFancySokoban(root, maze_file)

    root.bind("<Up>", controller.handle_keypress)
    root.bind("<Down>", controller.handle_keypress)
    root.bind("<Left>", controller.handle_keypress)
    root.bind("<Right>", controller.handle_keypress)
    root.bind("w", controller.handle_keypress)
    root.bind("a", controller.handle_keypress)
    root.bind("s", controller.handle_keypress)
    root.bind("d", controller.handle_keypress)

    root.mainloop()


def main() -> None:
    """Initialise root and call play_game()."""
    root = tk.Tk()
    play_game(root, 'maze_files/coin_maze.txt')


if __name__ == "__main__":
    main()
