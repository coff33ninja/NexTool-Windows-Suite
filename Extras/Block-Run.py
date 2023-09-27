import tkinter as tk
from tkinter import messagebox
import random
from tkinter import PhotoImage
import os


class CombinedGame:
    def __init__(self, root):
        self.root = root

        # Load images
        script_directory = os.path.dirname(os.path.abspath(
            __file__))  # Get the directory of the script
        self.cat_image = PhotoImage(file=os.path.join(
            script_directory, "cat_image.png"))
        self.mouse_image = PhotoImage(file=os.path.join(
            script_directory, "mouse_image.png"))
        self.background_image = PhotoImage(file=os.path.join(
            script_directory, "background_image.png"))

        self.setup_menu()
        self.move_task = None

    def setup_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=100)

        self.blockrun_button = tk.Button(
            self.menu_frame, text="Block Run (AI)", command=self.start_block_run_mode)
        self.blockrun_button.pack(pady=20)

        self.catmouse_single_button = tk.Button(
            self.menu_frame, text="Cat & Mouse (Single Player)", command=self.start_catmouse_single)
        self.catmouse_single_button.pack(pady=20)

        self.catmouse_multi_button = tk.Button(
            self.menu_frame, text="Cat & Mouse (Multiplayer)", command=self.start_catmouse_multi)
        self.catmouse_multi_button.pack(pady=20)

        self.rules_button = tk.Button(
            self.menu_frame, text="Game Rules & Controls", command=self.show_rules)
        self.rules_button.pack(pady=20)

    def start_block_run_mode(self):
        self.menu_frame.destroy()
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='white')
        self.canvas.pack()

        self.score = 0
        self.score_label = tk.Label(self.root, text="Score: 0")
        self.score_label.pack(pady=5)
        self.canvas.bind('<Button-1>', self.mis_click)

        self.root.after(1000, self.generate_block_ai)

    def mis_click(self, event):
        # Check if clicked on block
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if not clicked or "block" not in self.canvas.gettags(clicked[0]):
            self.score -= 1
            self.score_label.config(text=f"Score: {self.score}")

    def generate_block_ai(self):
        x = random.randint(10, 380)
        y = random.randint(10, 380)
        self.canvas.create_rectangle(
            x, y, x+20, y+20, fill='blue', tags="block")
        self.canvas.tag_bind("block", '<Button-1>', self.block_clicked_ai)
        self.root.after(2000, self.clear_blocks_ai)
        self.root.after(3000, self.generate_block_ai)

    def block_clicked_ai(self, event):
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if "block" in self.canvas.gettags(clicked[0]):
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.canvas.delete("block")
        else:
            self.score -= 1
            self.score_label.config(text=f"Score: {self.score}")

    def clear_blocks_ai(self):
        self.canvas.delete("block")

    def start_catmouse_single(self):
        self.menu_frame.destroy()
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.create_image(200, 200, image=self.background_image)
        self.canvas.bind('<Button-1>', self.mis_click_cat)
        self.canvas.pack()

        self.score = 0
        self.score_label = tk.Label(self.root, text="Score: 0")
        self.score_label.pack(pady=5)

        self.root.after(1000, self.generate_cat_ai)

    def mis_click_cat(self, event):
        # Check if clicked on cat
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if not clicked or "cat" not in self.canvas.gettags(clicked[0]):
            self.score -= 1
            self.score_label.config(text=f"Score: {self.score}")

    def generate_cat_ai(self):
        x = random.randint(10, 380)
        y = random.randint(10, 380)
        self.canvas.create_image(x, y, image=self.cat_image, tags="cat")
        self.canvas.tag_bind("cat", '<Button-1>', self.cat_clicked_ai)
        self.root.after(1000, self.move_cat_ai)

    def cat_clicked_ai(self, event):
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if "cat" in self.canvas.gettags(clicked[0]):
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.canvas.delete("cat")
            # Cancel scheduled movements
            if self.move_task:
                self.root.after_cancel(self.move_task)
                self.move_task = None
            self.root.after(1000, self.generate_cat_ai)
        else:
            self.score -= 1
            self.score_label.config(text=f"Score: {self.score}")

    def move_cat_ai(self):
        # If there's no cat on the canvas, just return
        if not self.canvas.find_withtag("cat"):
            return

        directions = [(-10, 0), (10, 0), (0, -10), (0, 10)]
        x, y = random.choice(directions)

        # Get the current position of the cat
        try:
            current_x, current_y = self.canvas.coords("cat")
        except ValueError:
            return  # The cat doesn't exist, so just exit the function

        # Ensure the cat stays inside the canvas boundaries
        if (current_x + x < 20 or current_x + x > 380) or (current_y + y < 20 or current_y + y > 380):
            return

        self.canvas.move("cat", x, y)
        self.move_task = self.root.after(1000, self.move_cat_ai)

    def start_catmouse_multi(self):
        self.menu_frame.destroy()
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.create_image(200, 200, image=self.background_image)
        self.canvas.bind('<Button-1>', self.mis_click_cat_multi)
        self.canvas.pack()

        self.mouse_score = 0
        self.mouse_score_label = tk.Label(self.root, text="Mouse Score: 0")
        self.mouse_score_label.pack(pady=5)

        self.cat_score = 0
        self.cat_score_label = tk.Label(self.root, text="Cat Score: 0")
        self.cat_score_label.pack(pady=5)

        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Up>', self.move_up)
        self.root.bind('<Down>', self.move_down)

        self.generate_cat()

    def mis_click_cat_multi(self, event):
        # Check if clicked on cat
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if not clicked or "cat" not in self.canvas.gettags(clicked[0]):
            self.mouse_score -= 1
            self.mouse_score_label.config(
                text=f"Mouse Score: {self.mouse_score}")

    def generate_cat(self):
        x = random.randint(10, 380)
        y = random.randint(10, 380)
        self.canvas.create_image(x, y, image=self.cat_image, tags="cat")
        self.canvas.tag_bind("cat", '<Button-1>', self.cat_clicked)

    def cat_clicked(self, event):
        self.mouse_score += 1
        self.mouse_score_label.config(text=f"Mouse Score: {self.mouse_score}")
        self.canvas.delete("cat")
        self.generate_cat()

    def move_left(self, event):
        self.move_cat(-10, 0)

    def move_right(self, event):
        self.move_cat(10, 0)

    def move_up(self, event):
        self.move_cat(0, -10)

    def move_down(self, event):
        self.move_cat(0, 10)

    def move_cat_ai(self):
        directions = [(-10, 0), (10, 0), (0, -10), (0, 10)]
        x, y = random.choice(directions)

        # Get the current position of the cat
        current_x, current_y = self.canvas.coords("cat")

        # Ensure the cat stays inside the canvas boundaries
        if (current_x + x < 20 or current_x + x > 380) or (current_y + y < 20 or current_y + y > 380):
            return

        self.canvas.move("cat", x, y)
        self.root.after(1000, self.move_cat_ai)

    def show_rules(self):
        rules = ("Block Run Rules & Controls: \n\n"
                 "Player vs. AI:\n"
                 "- Click the block before it disappears.\n\n"
                 "Cat & Mouse Rules & Controls:\n\n"
                 "Single Player:\n"
                 "- Click the cat before it reaches the bottom.\n\n"
                 "Multiplayer:\n"
                 "- Player 1: Click the cat\n"
                 "- Player 2: Use arrow keys to move the cat. Try to reach the bottom!")
        messagebox.showinfo("Rules & Controls", rules)


root = tk.Tk()
game = CombinedGame(root)
root.mainloop()
