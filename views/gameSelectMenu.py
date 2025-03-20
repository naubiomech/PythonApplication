import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

async def select_game(self):
    """Select a game to play."""
    # Create a new window
    game_window = tk.Toplevel(self)
    game_window.title("Select a Game")
    game_window.geometry("400x400")

    # Create a canvas
    canvas = tk.Canvas(game_window, width=400, height=400)
    
    # Create a frame to hold the widgets
    frame = tk.Frame(canvas)
    vsb = tk.Scrollbar(game_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4,4), window=frame, anchor="nw")

    # Create a label
    game_label = tk.Label(frame, text="Select a Game", font=("Arial", 20))
    game_label.grid(row=0, column=0, columnspan=3, pady=10)

    # Scan for each game folder within the Games folder
    games_folder = os.path.join(os.getcwd(), "Games")

    # gets all the games in the games folder, and avoids any hidden folders such as __pycache__
    games = [f for f in os.listdir(games_folder) if os.path.isdir(os.path.join(games_folder, f)) and not f.startswith("__")]

    def select_and_close(game):
        self.selected_game = game
        game_window.destroy()
        self.launchGameButton.config(state="normal")

    row, col = 1, 0
    for game in games:
        game_path = os.path.join(games_folder, game)
        image_path = os.path.join(game_path, "icon.png")
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize((50, 50), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        else:
            photo = None

        game_button = tk.Button(
            frame,
            text=game,
            image=photo,
            # set the button size
            width=100,
            height=100,
            compound="top",
            command=lambda g=game: select_and_close(g)
        )
        game_button.image = photo  # Keep a reference to avoid garbage collection
        game_button.grid(row=row, column=col, padx=10, pady=10)

        col += 1
        if col > 2:
            col = 0
            row += 1

    # Create a button to save the selected game
    exit_button = tk.Button(
        frame,
        text="Exit",
        command=game_window.destroy
    )
    exit_button.grid(row=row + 1, column=0, columnspan=3, pady=10)

    # allow for scrolling
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # allow scrolling using the scroll wheel
    def on_mousewheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)


    