import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json

class TemplateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Template Area Creator (Drag to Select)")

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.tk_image = None
        self.rectangles = []
        self.start_x = None
        self.start_y = None

        # Buttons
        frame = tk.Frame(root)
        frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(frame, text="Open Image", command=self.open_image).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Save Template", command=self.save_template).pack(side=tk.LEFT, padx=5)

        # Events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.current_rect = None

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.png;*.jpg;*.jpeg")
        ])
        if not path:
            return

        self.image = Image.open(path)
        self.tk_image = ImageTk.PhotoImage(self.image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.rectangles = []

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2
        )

    def on_mouse_drag(self, event):
        if self.current_rect:
            self.canvas.coords(self.current_rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        if self.current_rect:
            x1, y1, x2, y2 = self.canvas.coords(self.current_rect)
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)

            field_name = f"field_{len(self.rectangles)+1}"
            self.rectangles.append({
                "name": field_name,
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            })

            print("Added:", self.rectangles[-1])
            self.current_rect = None

    def save_template(self):
        if not self.rectangles:
            print("No areas selected.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not save_path:
            return

        with open(save_path, "w") as f:
            json.dump({"fields": self.rectangles}, f, indent=4)

        print("Template saved to:", save_path)


if __name__ == "__main__":
    root = tk.Tk()
    gui = TemplateGUI(root)
    root.mainloop()
