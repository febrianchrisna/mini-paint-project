import tkinter as tk
from tkinter import simpledialog
import math
from typing import Optional, Tuple, List
from shapes import Shape, Line, Circle, Rectangle, Polygon, Ellipse, Triangle, Pentagon, Hexagon

class DrawingCanvas(tk.Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white", cursor="crosshair")
        self.app = app
        self.current_tool = "pointer"
        self.transform_mode = None
        
        # Drawing state
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.temp_shape = None
        self.polygon_points = []
        
        # Move state
        self.moving = False
        self.move_start_x = 0
        self.move_start_y = 0
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<Motion>", self.on_mouse_move)
        
        self.redraw()
        
    def on_click(self, event):
        x, y = event.x, event.y
        
        if self.transform_mode == "move":
            self.handle_move_start(x, y)
        elif self.transform_mode in ["scale", "rotate"]:
            self.handle_transform_click(x, y)
        else:
            self.handle_drawing_click(x, y)
            
    def handle_move_start(self, x, y):
        if self.app.selected_shape:
            self.moving = True
            self.move_start_x = x
            self.move_start_y = y
            self.config(cursor="fleur")  # Move cursor
            
    def handle_drawing_click(self, x, y):
        if self.current_tool == "pointer":
            # Selection mode
            clicked_shape = self.find_shape_at_point(x, y)
            
            # Deselect all shapes first
            for shape in self.app.shapes:
                shape.selected = False
                
            if clicked_shape:
                clicked_shape.selected = True
                self.app.selected_shape = clicked_shape
            else:
                self.app.selected_shape = None
                
            self.redraw()
            return
            
        # Check if clicking on existing shape for selection
        if not self.drawing:
            clicked_shape = self.find_shape_at_point(x, y)
            if clicked_shape:
                for shape in self.app.shapes:
                    shape.selected = False
                clicked_shape.selected = True
                self.app.selected_shape = clicked_shape
                self.redraw()
                return
        
        # Deselect all shapes if starting new drawing
        for shape in self.app.shapes:
            shape.selected = False
        self.app.selected_shape = None
        
        # Handle drawing based on current tool
        if self.current_tool == "polygon":
            self.polygon_points.append((x, y))
            self.redraw()
            self.draw_polygon_preview()
        else:
            self.drawing = True
            self.start_x, self.start_y = x, y
            
    def handle_transform_click(self, x, y):
        if not self.app.selected_shape:
            return
            
        if self.transform_mode == "rotate":
            angle_deg = simpledialog.askfloat("Rotate", "Enter rotation angle (degrees):", 
                                            initialvalue=0, minvalue=-360, maxvalue=360)
            if angle_deg is not None:
                angle_rad = math.radians(angle_deg)
                bounds = self.app.selected_shape.get_bounds()
                center_x = (bounds[0] + bounds[2]) / 2
                center_y = (bounds[1] + bounds[3]) / 2
                self.app.selected_shape.rotate(angle_rad, center_x, center_y)
                self.redraw()
        elif self.transform_mode == "scale":
            factor = simpledialog.askfloat("Scale", "Enter scale factor:", 
                                         initialvalue=1.0, minvalue=0.1, maxvalue=5.0)
            if factor is not None:
                bounds = self.app.selected_shape.get_bounds()
                center_x = (bounds[0] + bounds[2]) / 2
                center_y = (bounds[1] + bounds[3]) / 2
                self.app.selected_shape.scale(factor, center_x, center_y)
                self.redraw()
                
        self.transform_mode = None
        self.config(cursor="crosshair")
        
    def on_drag(self, event):
        x, y = event.x, event.y
        
        if self.moving and self.app.selected_shape:
            dx = x - self.move_start_x
            dy = y - self.move_start_y
            self.app.selected_shape.translate(dx, dy)
            self.move_start_x = x
            self.move_start_y = y
            self.redraw()
        elif self.drawing:
            self.redraw()
            self.draw_preview_shape(self.start_x, self.start_y, x, y)
            
    def on_release(self, event):
        if self.moving:
            self.moving = False
            self.transform_mode = None
            self.config(cursor="crosshair")
            return
            
        if not self.drawing:
            return
            
        x, y = event.x, event.y
        self.drawing = False
        
        # Create the actual shape with current properties
        shape = self.create_shape(self.start_x, self.start_y, x, y)
        if shape:
            # Apply current drawing properties
            shape.line_color = self.app.line_color
            shape.fill_color = self.app.fill_color
            shape.line_width = self.app.line_width
            shape.line_style = self.app.line_style
            
            self.app.shapes.append(shape)
            self.redraw()
            
    def create_shape(self, x1, y1, x2, y2):
        if self.current_tool == "line":
            return Line(x1, y1, x2, y2)
        elif self.current_tool == "circle":
            radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            return Circle(x1, y1, radius)
        elif self.current_tool == "rectangle":
            return Rectangle(x1, y1, x2, y2)
        elif self.current_tool == "ellipse":
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            return Ellipse(center_x, center_y, width, height)
        elif self.current_tool == "triangle":
            return Triangle(x1, y1, x2, y2)
        elif self.current_tool == "pentagon":
            radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            return Pentagon(x1, y1, radius)
        elif self.current_tool == "hexagon":
            radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            return Hexagon(x1, y1, radius)
        return None
        
    def on_right_click(self, event):
        if self.current_tool == "polygon" and len(self.polygon_points) >= 3:
            shape = Polygon(self.polygon_points)
            shape.line_color = self.app.line_color
            shape.fill_color = self.app.fill_color
            shape.line_width = self.app.line_width
            shape.line_style = self.app.line_style
            self.app.shapes.append(shape)
            self.polygon_points = []
            self.redraw()
            
    def on_mouse_move(self, event):
        # Update cursor based on mode
        if self.transform_mode == "move" and self.app.selected_shape:
            self.config(cursor="fleur")
        elif self.current_tool == "pointer":
            shape_under_cursor = self.find_shape_at_point(event.x, event.y)
            if shape_under_cursor:
                self.config(cursor="hand2")
            else:
                self.config(cursor="arrow")
        else:
            self.config(cursor="crosshair")
            
        if self.current_tool == "polygon" and self.polygon_points:
            self.redraw()
            self.draw_polygon_preview()
            if self.polygon_points:
                last_point = self.polygon_points[-1]
                self.create_line(last_point[0], last_point[1], event.x, event.y, 
                               fill="gray", dash=(2, 2), tags="preview")
                               
    def draw_preview_shape(self, x1, y1, x2, y2):
        if self.current_tool == "line":
            self.create_line(x1, y1, x2, y2, fill="gray", dash=(2, 2), tags="preview")
        elif self.current_tool == "circle":
            radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.create_oval(x1 - radius, y1 - radius, x1 + radius, y1 + radius, 
                           outline="gray", dash=(2, 2), tags="preview")
        elif self.current_tool == "rectangle":
            self.create_rectangle(x1, y1, x2, y2, outline="gray", dash=(2, 2), tags="preview")
        elif self.current_tool == "ellipse":
            self.create_oval(x1, y1, x2, y2, outline="gray", dash=(2, 2), tags="preview")
        elif self.current_tool in ["triangle", "pentagon", "hexagon"]:
            # Simple preview as circle for regular polygons
            radius = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.create_oval(x1 - radius, y1 - radius, x1 + radius, y1 + radius, 
                           outline="gray", dash=(2, 2), tags="preview")
            
    def draw_polygon_preview(self):
        if len(self.polygon_points) < 2:
            return
            
        # Draw lines between existing points
        for i in range(len(self.polygon_points) - 1):
            x1, y1 = self.polygon_points[i]
            x2, y2 = self.polygon_points[i + 1]
            self.create_line(x1, y1, x2, y2, fill="gray", dash=(2, 2), tags="preview")
            
        # Draw points
        for x, y in self.polygon_points:
            self.create_oval(x-3, y-3, x+3, y+3, fill="red", tags="preview")
            
    def find_shape_at_point(self, x, y) -> Optional[Shape]:
        # Search from top to bottom (last drawn first)
        for shape in reversed(self.app.shapes):
            if shape.contains_point(x, y):
                return shape
        return None
        
    def redraw(self):
        self.delete("all")
        
        # Draw all shapes
        for shape in self.app.shapes:
            shape.draw(self)
            
        # Draw polygon points if in polygon mode
        if self.current_tool == "polygon":
            self.draw_polygon_preview()
            
        # Show instructions
        self.create_text(10, 10, anchor="nw", 
                        text=f"Tool: {self.current_tool.title()}" + 
                             (f" | Transform: {self.transform_mode}" if self.transform_mode else "") +
                             (f" | Selected: {type(self.app.selected_shape).__name__}" if self.app.selected_shape else ""),
                        fill="blue", tags="info")
                        
        if self.current_tool == "polygon":
            self.create_text(10, 30, anchor="nw", 
                           text="Click to add points, Right-click to complete polygon",
                           fill="blue", tags="info")
