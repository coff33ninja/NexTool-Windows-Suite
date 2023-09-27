import tkinter as tk
from tkinter import messagebox
import random
from tkinter import PhotoImage
import os

class CombinedGame:
    # Define allowed paths
    ALLOWED_IMAGES = {
        "cat_image": "cat_image.png",
        "mouse_image": "mouse_image.png",
        "background_image": "background_image.png"
    }

    def __init__(self, root):
        self.root = root

        # Load images
        script_directory = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
        self.cat_image = self.load_image("cat_image", script_directory)
        self.mouse_image = self.load_image("mouse_image", script_directory)
        self.background_image = self.load_image("background_image", script_directory)

        self.setup_menu()

    def load_image(self, image_id, base_dir):
        """Loads an image from the ALLOWED_IMAGES mapping"""
        if image_id in self.ALLOWED_IMAGES:
            image_path = os.path.join(base_dir, self.ALLOWED_IMAGES[image_id])
            absolute_image_path = os.path.abspath(image_path)
            if not absolute_image_path.startswith(base_dir):
                raise ValueError(f"Unauthorized file path detected: {absolute_image_path}")
            if os.path.exists(absolute_image_path):
                return PhotoImage(file=absolute_image_path)
            else:
                raise ValueError(f"Image path {absolute_image_path} does not exist!")
        else:
            raise ValueError(f"Image ID {image_id} not recognized!")

    def setup_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=100)
        root.geometry('600x500')  # Adjust dimensions as needed

        self.blockrun_button = tk.Button(self.menu_frame, text="Block Run (AI)", command=self.start_block_run_mode)
        self.blockrun_button.pack(pady=20)

        self.catmouse_single_button = tk.Button(self.menu_frame, text="Cat & Mouse (Single Player)", command=self.start_catmouse_single)
        self.catmouse_single_button.pack(pady=20)

        self.rules_button = tk.Button(self.menu_frame, text="Game Rules & Controls", command=self.show_rules)
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
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if not clicked or "block" not in self.canvas.gettags(clicked[0]):
            self.score -= 1
            self.score_label.config(text=f"Score: {self.score}")

    def generate_block_ai(self):
        x = random.randint(10, 380)
        y = random.randint(10, 380)
        self.canvas.create_rectangle(x, y, x+20, y+20, fill='blue', tags="block")
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
        self.canvas.pack()

        self.score = 0
        self.hits = 0  # Initialize hits counter
        self.misses = 0  # Initialize misses counter
        self.score_label = tk.Label(self.root, text=f"Score: {self.score} - Hits: {self.hits} Misses: {self.misses}")
        self.score_label.pack(pady=5)

        self.root.after(1000, self.generate_cat_ai)

        # Comment out or remove this line to prevent the global binding
        # self.canvas.bind('<Button-1>', self.mis_click_cat)

    def mis_click_cat(self, event):
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if not clicked or "cat" not in self.canvas.gettags(clicked[0]):
            self.score -= 1
            self.misses += 1  # Increment misses counter
            self.score_label.config(text=f"Score: {self.score} - Missed! Hits: {self.hits} Misses: {self.misses}")

    def generate_cat_ai(self):
        x = random.randint(10, 380)
        y = random.randint(10, 380)
        self.canvas.create_image(x, y, image=self.cat_image, tags="cat")
        self.canvas.tag_bind("cat", '<Button-1>', self.cat_clicked_ai)
        # Setting the multiplier initially to 1
        self.multiplier = 1
        self.move_task = self.root.after(1000, self.move_cat_ai)
        # This task checks for quick clicks
        self.multiplier_task = self.root.after(3000, self.reset_multiplier)

    def cat_clicked_ai(self, event):
        clicked = self.canvas.find_withtag(tk.CURRENT)
        if "cat" in self.canvas.gettags(clicked[0]):
            self.hits += 1  # Increment hit counter
            self.score += (1 * self.multiplier)
            if self.multiplier_task:
                self.multiplier = 2
            self.score_label.config(text=f"Score: {self.score} - Correct x{self.multiplier}! Hits: {self.hits} Misses: {self.misses}")
            self.canvas.delete("cat")
            if self.move_task:
                self.root.after_cancel(self.move_task)
                self.move_task = None
            if self.multiplier_task:
                self.root.after_cancel(self.multiplier_task)
                self.multiplier_task = None
            self.root.after(1000, self.generate_cat_ai)
        else:
            self.score -= 1
            self.misses += 1  # Increment misses counter
            self.score_label.config(text=f"Score: {self.score} - Missed! Hits: {self.hits} Misses: {self.misses}")

    def move_cat_ai(self):
        # If there's no cat on the canvas, just return
        if not self.canvas.find_withtag("cat"):
            return

        directions = [(-10, 0), (10, 0), (0, -10), (0, 10)]
        x, y = random.choice(directions)
        speed = random.randint(500, 1500)  # Speed is random between 0.5 to 1.5 seconds

        # Get the current position of the cat
        try:
            current_x, current_y = self.canvas.coords("cat")
        except ValueError:
            return  # The cat doesn't exist, so just exit the function

        # Ensure the cat stays inside the canvas boundaries
        if (current_x + x < 20 or current_x + x > 380) or (current_y + y < 20 or current_y + y > 380):
            return

        self.canvas.move("cat", x, y)
        self.move_task = self.root.after(speed, self.move_cat_ai)

    def reset_multiplier(self):
        self.multiplier = 1
        self.move_task = self.root.after(1000, self.move_cat_ai)
        self.multiplier_task = self.root.after(3000, self.reset_multiplier)
    def show_rules(self):
        rules = ("Block Run Rules & Controls: \n\n"
                 "Player vs. AI:\n"
                 "- Click the block before it disappears.\n\n"
                 "Cat & Mouse Rules & Controls:\n\n"
                 "Single Player:\n"
                 "- Click the cat before it reaches the bottom.")
        messagebox.showinfo("Rules & Controls", rules)


root = tk.Tk()
game = CombinedGame(root)
root.mainloop()
