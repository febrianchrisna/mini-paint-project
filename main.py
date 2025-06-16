import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, simpledialog
import math
from typing import List, Optional, Tuple
from shapes import Shape, Line, Circle, Rectangle, Polygon, Ellipse, Triangle, Pentagon, Hexagon, Sketch
from canvas import DrawingCanvas

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafika Paint - Advanced Drawing & Transformations")
        self.root.geometry("1200x800")
        
        self.current_tool = "pointer"
        self.selected_shape = None
        self.shapes = []
        
        # Drawing properties
        self.line_color = "black"
        self.fill_color = ""
        self.line_width = 2
        self.line_style = "solid"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header dengan informasi mahasiswa
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        header_label = ttk.Label(header_frame, 
                               text="Nama: Febrian Chrisna Ardianto | NIM: 123220051 | Kelas: IF-A", 
                               font=("Segoe UI", 10, "bold"),
                               foreground="blue")
        header_label.pack(pady=5)
        
        ttk.Separator(header_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(5, 10))
        
        # Sidebar (navbar kiri) untuk transform
        sidebar = ttk.Frame(main_frame)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=0)

        ttk.Label(sidebar, text="Transform:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        # Remove Move button - integrate directly into pointer tool
        ttk.Button(sidebar, text="Scale", command=self.enable_scale).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Rotate", command=self.enable_rotate).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Translate XY", command=self.translate_xy).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Shear", command=self.shear_transform).pack(fill=tk.X, pady=2)

        # Toolbar atas
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Tools section
        ttk.Label(toolbar, text="Tools:").pack(side=tk.LEFT, padx=5)
        
        self.tool_var = tk.StringVar(value="pointer")
        tools = [("Pointer", "pointer"), ("Draw", "draw"), ("Line", "line"), ("Circle", "circle"), 
                ("Rectangle", "rectangle"), ("Ellipse", "ellipse"), ("Triangle", "triangle"),
                ("Pentagon", "pentagon"), ("Hexagon", "hexagon"), ("Polygon", "polygon")]
        
        for text, value in tools:
            ttk.Radiobutton(toolbar, text=text, variable=self.tool_var, 
                          value=value, command=self.change_tool).pack(side=tk.LEFT, padx=1)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Line properties
        ttk.Label(toolbar, text="Line:").pack(side=tk.LEFT, padx=5)
        
        # Line width
        ttk.Label(toolbar, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=2)
        width_spinbox = ttk.Spinbox(toolbar, from_=1, to=10, width=3, textvariable=self.width_var,
                                   command=self.update_line_width)
        width_spinbox.pack(side=tk.LEFT, padx=2)
        
        # Line style
        ttk.Label(toolbar, text="Style:").pack(side=tk.LEFT, padx=(5,0))
        self.style_var = tk.StringVar(value="solid")
        style_combo = ttk.Combobox(toolbar, textvariable=self.style_var, width=8,
                                  values=["solid", "dashed", "dotted"], state="readonly")
        style_combo.pack(side=tk.LEFT, padx=2)
        style_combo.bind("<<ComboboxSelected>>", self.update_line_style)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Colors
        ttk.Label(toolbar, text="Colors:").pack(side=tk.LEFT, padx=5)
        
        # Line color
        self.line_color_btn = tk.Button(toolbar, text="Line", bg=self.line_color, width=6,
                                       command=self.choose_line_color)
        self.line_color_btn.pack(side=tk.LEFT, padx=2)
        
        # Fill color
        self.fill_color_btn = tk.Button(toolbar, text="Fill", bg="white", width=6,
                                       command=self.choose_fill_color)
        self.fill_color_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Second toolbar row
        toolbar2 = ttk.Frame(main_frame)
        toolbar2.pack(fill=tk.X, pady=(0, 5))
        
        # Utility buttons
        ttk.Label(toolbar2, text="Actions:").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar2, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar2, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar2, text="Duplicate", command=self.duplicate_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar2, text="Bring to Front", command=self.bring_to_front).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar2, text="Send to Back", command=self.send_to_back).pack(side=tk.LEFT, padx=2)
        
        # Canvas
        self.canvas = DrawingCanvas(main_frame, self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind right-click for moving objects when pointer tool is active
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right click
        self.canvas.bind("<B3-Motion>", self.on_right_drag)  # Right drag
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)  # Right release
        
        # Variables for drag operation
        self.drag_data = {"x": 0, "y": 0, "shape": None}
        
    def on_right_click(self, event):
        """Handle right click for starting move operation"""
        if self.current_tool != "pointer":
            return
            
        # Find shape at click position
        clicked_shape = self.canvas.find_shape_at_point(event.x, event.y)
        if clicked_shape:
            # Select the shape if not already selected
            if self.selected_shape != clicked_shape:
                if self.selected_shape:
                    self.selected_shape.selected = False
                clicked_shape.selected = True
                self.selected_shape = clicked_shape
                self.canvas.redraw()
            
            # Start drag operation
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["shape"] = clicked_shape
            
    def on_right_drag(self, event):
        """Handle right drag for moving object"""
        if self.current_tool != "pointer" or not self.drag_data["shape"]:
            return
            
        # Calculate movement delta
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Move the shape
        self.drag_data["shape"].translate(dx, dy)
        
        # Update drag position
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        # Redraw canvas
        self.canvas.redraw()
        
    def on_right_release(self, event):
        """Handle right click release to end move operation"""
        self.drag_data = {"x": 0, "y": 0, "shape": None}
        
    def change_tool(self):
        self.current_tool = self.tool_var.get()
        self.canvas.current_tool = self.current_tool
        
        # Clear transform mode - let pointer handle selection and movement directly
        self.canvas.transform_mode = None

    def update_line_width(self):
        self.line_width = self.width_var.get()
        
    def update_line_style(self, event=None):
        self.line_style = self.style_var.get()
        
    def choose_line_color(self):
        color = colorchooser.askcolor(title="Choose Line Color")[1]
        if color:
            self.line_color = color
            self.line_color_btn.config(bg=color)
            
    def choose_fill_color(self):
        result = colorchooser.askcolor(title="Choose Fill Color")
        if result[1]:
            self.fill_color = result[1]
            self.fill_color_btn.config(bg=result[1])
        else:
            # User might want no fill
            response = messagebox.askyesno("No Fill", "Do you want no fill color?")
            if response:
                self.fill_color = ""
                self.fill_color_btn.config(bg="white", text="No Fill")
            
    def enable_scale(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
        self.canvas.transform_mode = "scale"
        if self.current_tool != "pointer":
            self.tool_var.set("pointer")
            self.current_tool = "pointer"
            self.canvas.current_tool = "pointer"
        
    def enable_rotate(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
        self.canvas.transform_mode = "rotate"
        if self.current_tool != "pointer":
            self.tool_var.set("pointer")
            self.current_tool = "pointer"
            self.canvas.current_tool = "pointer"
        
    def translate_xy(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
            
        # Get translation values from user
        dx = simpledialog.askfloat("Translate X", "Enter X translation:", initialvalue=0)
        if dx is None:
            return
            
        dy = simpledialog.askfloat("Translate Y", "Enter Y translation:", initialvalue=0)
        if dy is None:
            return
            
        self.selected_shape.translate(dx, dy)
        self.canvas.redraw()
        
    def shear_transform(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
            
        # Get shear values from user
        shear_x = simpledialog.askfloat("Shear X", "Enter X shear factor (misal 0.5 untuk miring ke kanan):", initialvalue=0)
        if shear_x is None:
            return
            
        shear_y = simpledialog.askfloat("Shear Y", "Enter Y shear factor (misal 0.5 untuk miring ke atas):", initialvalue=0)
        if shear_y is None:
            return

        # Penjelasan: shear_x menggeser titik secara horizontal proporsional terhadap Y,
        # shear_y menggeser titik secara vertikal proporsional terhadap X.
        # Implementasi shear harus sesuai rumus:
        #   x' = x + shear_x * y
        #   y' = y + shear_y * x
        if hasattr(self.selected_shape, 'shear'):
            self.selected_shape.shear(shear_x, shear_y)
            self.canvas.redraw()
        else:
            messagebox.showinfo("Not Supported", "Shear transformation not supported for this shape type.")
            
    def duplicate_selected(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
            
        # Create a copy of the selected shape
        new_shape = self.selected_shape.copy()
        new_shape.translate(20, 20)  # Offset the duplicate
        new_shape.selected = False
        self.shapes.append(new_shape)
        self.canvas.redraw()
        
    def bring_to_front(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
            
        if self.selected_shape in self.shapes:
            self.shapes.remove(self.selected_shape)
            self.shapes.append(self.selected_shape)
            self.canvas.redraw()
            
    def send_to_back(self):
        if not self.selected_shape:
            messagebox.showwarning("No Selection", "Please select a shape first.")
            return
            
        if self.selected_shape in self.shapes:
            self.shapes.remove(self.selected_shape)
            self.shapes.insert(0, self.selected_shape)
            self.canvas.redraw()
            
    def clear_all(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all shapes?"):
            self.shapes.clear()
            self.selected_shape = None
            self.canvas.redraw()
            
    def delete_selected(self):
        if self.selected_shape and self.selected_shape in self.shapes:
            self.shapes.remove(self.selected_shape)
            self.selected_shape = None
            self.canvas.redraw()
        
    def enable_move(self):
        # Enable explicit move mode for drag operations
        self.canvas.transform_mode = "move"
        if self.current_tool != "pointer":
            self.tool_var.set("pointer")
            self.current_tool = "pointer"
            self.canvas.current_tool = "pointer"
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
