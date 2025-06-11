import math
from typing import List, Tuple
from abc import ABC, abstractmethod
import copy

class Shape(ABC):
    def __init__(self):
        self.selected = False
        self.line_color = "black"
        self.fill_color = ""
        self.line_width = 2
        self.line_style = "solid"
        
    @abstractmethod
    def draw(self, canvas):
        pass
        
    @abstractmethod
    def contains_point(self, x, y) -> bool:
        pass
        
    @abstractmethod
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y)"""
        pass
        
    @abstractmethod
    def translate(self, dx, dy):
        pass
        
    @abstractmethod
    def scale(self, factor, center_x=None, center_y=None):
        pass
        
    @abstractmethod
    def rotate(self, angle, center_x=None, center_y=None):
        pass
        
    @abstractmethod
    def copy(self):
        pass
        
    def shear(self, shear_x, shear_y):
        """Default shear implementation - can be overridden by subclasses"""
        pass
        
    def get_dash_pattern(self):
        if self.line_style == "dashed":
            return (5, 5)
        elif self.line_style == "dotted":
            return (2, 2)
        return None

class Line(Shape):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        
    def draw(self, canvas):
        color = "red" if self.selected else self.line_color
        dash = self.get_dash_pattern()
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, 
                          fill=color, width=self.line_width, dash=dash, tags="shape")
                          
    def contains_point(self, x, y) -> bool:
        # Check if point is near the line
        A = self.y2 - self.y1
        B = self.x1 - self.x2
        C = self.x2 * self.y1 - self.x1 * self.y2
        
        # Check for zero-length line (both points are the same)
        denominator = math.sqrt(A * A + B * B)
        if denominator == 0:
            # Line has zero length, check if point is near either endpoint
            distance_to_point = math.sqrt((x - self.x1)**2 + (y - self.y1)**2)
            return distance_to_point < 5
        
        distance = abs(A * x + B * y + C) / denominator
        
        # Also check if point is within the line segment bounds
        min_x, max_x = min(self.x1, self.x2), max(self.x1, self.x2)
        min_y, max_y = min(self.y1, self.y2), max(self.y1, self.y2)
        
        return (distance < 5 and min_x - 5 <= x <= max_x + 5 and min_y - 5 <= y <= max_y + 5)
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (min(self.x1, self.x2), min(self.y1, self.y2), 
                max(self.x1, self.x2), max(self.y1, self.y2))
                
    def translate(self, dx, dy):
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x = (self.x1 + self.x2) / 2
            center_y = (self.y1 + self.y2) / 2
            
        self.x1 = center_x + (self.x1 - center_x) * factor
        self.y1 = center_y + (self.y1 - center_y) * factor
        self.x2 = center_x + (self.x2 - center_x) * factor
        self.y2 = center_y + (self.y2 - center_y) * factor
        
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x = (self.x1 + self.x2) / 2
            center_y = (self.y1 + self.y2) / 2
            
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Rotate point 1
        dx1 = self.x1 - center_x
        dy1 = self.y1 - center_y
        self.x1 = center_x + dx1 * cos_a - dy1 * sin_a
        self.y1 = center_y + dx1 * sin_a + dy1 * cos_a
        
        # Rotate point 2
        dx2 = self.x2 - center_x
        dy2 = self.y2 - center_y
        self.x2 = center_x + dx2 * cos_a - dy2 * sin_a
        self.y2 = center_y + dx2 * sin_a + dy2 * cos_a
        
    def copy(self):
        new_line = Line(self.x1, self.y1, self.x2, self.y2)
        new_line.line_color = self.line_color
        new_line.line_width = self.line_width
        new_line.line_style = self.line_style
        return new_line
        
    def shear(self, shear_x, shear_y):
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        new_x1 = x1 + shear_x * y1
        new_y1 = y1 + shear_y * x1
        new_x2 = x2 + shear_x * y2
        new_y2 = y2 + shear_y * x2
        self.x1, self.y1, self.x2, self.y2 = new_x1, new_y1, new_x2, new_y2

class Circle(Shape):
    def __init__(self, center_x, center_y, radius):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        
    def draw(self, canvas):
        outline_color = "red" if self.selected else self.line_color
        fill_color = self.fill_color if self.fill_color else ""
        dash = self.get_dash_pattern()
        
        x1 = self.center_x - self.radius
        y1 = self.center_y - self.radius
        x2 = self.center_x + self.radius
        y2 = self.center_y + self.radius
        canvas.create_oval(x1, y1, x2, y2, outline=outline_color, fill=fill_color,
                          width=self.line_width, dash=dash, tags="shape")
        
    def contains_point(self, x, y) -> bool:
        distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        return abs(distance - self.radius) < 5  # Near the circumference
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (self.center_x - self.radius, self.center_y - self.radius,
                self.center_x + self.radius, self.center_y + self.radius)
                
    def translate(self, dx, dy):
        self.center_x += dx
        self.center_y += dy
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x, center_y = self.center_x, self.center_y
        else:
            # Scale position relative to external center
            self.center_x = center_x + (self.center_x - center_x) * factor
            self.center_y = center_y + (self.center_y - center_y) * factor
        self.radius *= factor
        
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            return  # Circle doesn't change when rotated around its center
            
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        dx = self.center_x - center_x
        dy = self.center_y - center_y
        self.center_x = center_x + dx * cos_a - dy * sin_a
        self.center_y = center_y + dx * sin_a + dy * cos_a
        
    def copy(self):
        new_circle = Circle(self.center_x, self.center_y, self.radius)
        new_circle.line_color = self.line_color
        new_circle.fill_color = self.fill_color
        new_circle.line_width = self.line_width
        new_circle.line_style = self.line_style
        return new_circle

    def shear(self, shear_x, shear_y):
        # Approximate circle as polygon, shear all points, then convert to Polygon
        cx, cy, r = self.center_x, self.center_y, self.radius
        num_points = 36
        points = []
        for i in range(num_points):
            theta = 2 * math.pi * i / num_points
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            points.append((new_x, new_y))
        self.points = points
        self.__class__ = Polygon

class Rectangle(Shape):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self.x1, self.y1 = min(x1, x2), min(y1, y2)
        self.x2, self.y2 = max(x1, x2), max(y1, y2)
        
    def draw(self, canvas):
        outline_color = "red" if self.selected else self.line_color
        fill_color = self.fill_color if self.fill_color else ""
        dash = self.get_dash_pattern()
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, 
                              outline=outline_color, fill=fill_color,
                              width=self.line_width, dash=dash, tags="shape")
                              
    def contains_point(self, x, y) -> bool:
        # Check if point is on the border
        margin = 5
        return ((self.x1 - margin <= x <= self.x2 + margin and 
                 self.y1 - margin <= y <= self.y1 + margin) or
                (self.x1 - margin <= x <= self.x2 + margin and 
                 self.y2 - margin <= y <= self.y2 + margin) or
                (self.x1 - margin <= x <= self.x1 + margin and 
                 self.y1 - margin <= y <= self.y2 + margin) or
                (self.x2 - margin <= x <= self.x2 + margin and 
                 self.y1 - margin <= y <= self.y2 + margin))
                 
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)
        
    def translate(self, dx, dy):
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x = (self.x1 + self.x2) / 2
            center_y = (self.y1 + self.y2) / 2
            
        self.x1 = center_x + (self.x1 - center_x) * factor
        self.y1 = center_y + (self.y1 - center_y) * factor
        self.x2 = center_x + (self.x2 - center_x) * factor
        self.y2 = center_y + (self.y2 - center_y) * factor
        
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x = (self.x1 + self.x2) / 2
            center_y = (self.y1 + self.y2) / 2
            
        # Convert rectangle to 4 points, rotate them, then find new bounds
        points = [(self.x1, self.y1), (self.x2, self.y1), 
                  (self.x2, self.y2), (self.x1, self.y2)]
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        rotated_points = []
        for px, py in points:
            dx = px - center_x
            dy = py - center_y
            new_x = center_x + dx * cos_a - dy * sin_a
            new_y = center_y + dx * sin_a + dy * cos_a
            rotated_points.append((new_x, new_y))
            
        # Find new bounds
        xs = [p[0] for p in rotated_points]
        ys = [p[1] for p in rotated_points]
        self.x1, self.y1 = min(xs), min(ys)
        self.x2, self.y2 = max(xs), max(ys)

    def copy(self):
        new_rect = Rectangle(self.x1, self.y1, self.x2, self.y2)
        new_rect.line_color = self.line_color
        new_rect.fill_color = self.fill_color
        new_rect.line_width = self.line_width
        new_rect.line_style = self.line_style
        return new_rect
        
    def shear(self, shear_x, shear_y):
        # Shear keempat titik sudut rectangle, lalu simpan sebagai polygon
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        points = [
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2)
        ]
        sheared = []
        for x, y in points:
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            sheared.append((new_x, new_y))
        self.points = sheared
        self.__class__ = Polygon  # Ubah menjadi Polygon agar bisa digambar sebagai poligon

class Ellipse(Shape):
    def __init__(self, center_x, center_y, width, height):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        
    def draw(self, canvas):
        outline_color = "red" if self.selected else self.line_color
        fill_color = self.fill_color if self.fill_color else ""
        dash = self.get_dash_pattern()
        
        x1 = self.center_x - self.width / 2
        y1 = self.center_y - self.height / 2
        x2 = self.center_x + self.width / 2
        y2 = self.center_y + self.height / 2
        canvas.create_oval(x1, y1, x2, y2, outline=outline_color, fill=fill_color,
                          width=self.line_width, dash=dash, tags="shape")
                          
    def contains_point(self, x, y) -> bool:
        # Safety check to prevent division by zero
        if self.width <= 0 or self.height <= 0:
            return False
            
        dx = (x - self.center_x) / (self.width / 2)
        dy = (y - self.center_y) / (self.height / 2)
        return dx * dx + dy * dy <= 1
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (self.center_x - self.width/2, self.center_y - self.height/2,
                self.center_x + self.width/2, self.center_y + self.height/2)
                
    def translate(self, dx, dy):
        self.center_x += dx
        self.center_y += dy
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x, center_y = self.center_x, self.center_y
        else:
            self.center_x = center_x + (self.center_x - center_x) * factor
            self.center_y = center_y + (self.center_y - center_y) * factor
        self.width *= factor
        self.height *= factor
        
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            return
            
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        dx = self.center_x - center_x
        dy = self.center_y - center_y
        self.center_x = center_x + dx * cos_a - dy * sin_a
        self.center_y = center_y + dx * sin_a + dy * cos_a
        
    def copy(self):
        new_ellipse = Ellipse(self.center_x, self.center_y, self.width, self.height)
        new_ellipse.line_color = self.line_color
        new_ellipse.fill_color = self.fill_color
        new_ellipse.line_width = self.line_width
        new_ellipse.line_style = self.line_style
        return new_ellipse

    def shear(self, shear_x, shear_y):
        # Approximate ellipse as polygon, shear all points, then convert to Polygon
        cx, cy, rx, ry = self.center_x, self.center_y, self.width / 2, self.height / 2
        num_points = 36
        points = []
        for i in range(num_points):
            theta = 2 * math.pi * i / num_points
            x = cx + rx * math.cos(theta)
            y = cy + ry * math.sin(theta)
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            points.append((new_x, new_y))
        self.points = points
        self.__class__ = Polygon

class Triangle(Shape):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        # Create equilateral triangle
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        size = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 2
        
        self.points = [
            (center_x, center_y - size),  # Top
            (center_x - size * 0.866, center_y + size * 0.5),  # Bottom left
            (center_x + size * 0.866, center_y + size * 0.5)   # Bottom right
        ]
        
    def draw(self, canvas):
        outline_color = "red" if self.selected else self.line_color
        fill_color = self.fill_color if self.fill_color else ""
        dash = self.get_dash_pattern()
        
        flat_points = [coord for point in self.points for coord in point]
        canvas.create_polygon(flat_points, outline=outline_color, fill=fill_color,
                            width=self.line_width, dash=dash, tags="shape")
                            
    def contains_point(self, x, y) -> bool:
        # Simple bounding box check for now
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return (min(xs) - 5 <= x <= max(xs) + 5 and 
                min(ys) - 5 <= y <= max(ys) + 5)
                
    def get_bounds(self) -> Tuple[float, float, float, float]:
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))
        
    def translate(self, dx, dy):
        self.points = [(x + dx, y + dy) for x, y in self.points]
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)
            
        self.points = [(center_x + (x - center_x) * factor, 
                        center_y + (y - center_y) * factor) 
                       for x, y in self.points]
                       
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)
            
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        new_points = []
        for x, y in self.points:
            dx = x - center_x
            dy = y - center_y
            new_x = center_x + dx * cos_a - dy * sin_a
            new_y = center_y + dx * sin_a + dy * cos_a
            new_points.append((new_x, new_y))
            
        self.points = new_points
        
    def copy(self):
        new_triangle = Triangle(0, 0, 0, 0)  # Dummy values
        new_triangle.points = self.points[:]
        new_triangle.line_color = self.line_color
        new_triangle.fill_color = self.fill_color
        new_triangle.line_width = self.line_width
        new_triangle.line_style = self.line_style
        return new_triangle

    def shear(self, shear_x, shear_y):
        new_points = []
        for x, y in self.points:
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            new_points.append((new_x, new_y))
        self.points = new_points

class Pentagon(Shape):
    def __init__(self, center_x, center_y, radius):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.points = self._generate_pentagon_points()
        
    def _generate_pentagon_points(self):
        points = []
        for i in range(5):
            angle = i * 2 * math.pi / 5 - math.pi / 2  # Start from top
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            points.append((x, y))
        return points
        
    def draw(self, canvas):
        outline_color = "red" if self.selected else self.line_color
        fill_color = self.fill_color if self.fill_color else ""
        dash = self.get_dash_pattern()
        
        flat_points = [coord for point in self.points for coord in point]
        canvas.create_polygon(flat_points, outline=outline_color, fill=fill_color,
                            width=self.line_width, dash=dash, tags="shape")
                            
    def contains_point(self, x, y) -> bool:
        distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        return abs(distance - self.radius) < 10
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (self.center_x - self.radius, self.center_y - self.radius,
                self.center_x + self.radius, self.center_y + self.radius)
                
    def translate(self, dx, dy):
        self.center_x += dx
        self.center_y += dy
        self.points = [(x + dx, y + dy) for x, y in self.points]
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x, center_y = self.center_x, self.center_y
        else:
            self.center_x = center_x + (self.center_x - center_x) * factor
            self.center_y = center_y + (self.center_y - center_y) * factor
        self.radius *= factor
        self.points = self._generate_pentagon_points()
        
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x, center_y = self.center_x, self.center_y
        else:
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            dx = self.center_x - center_x
            dy = self.center_y - center_y
            self.center_x = center_x + dx * cos_a - dy * sin_a
            self.center_y = center_y + dx * sin_a + dy * cos_a
            
        self.points = self._generate_pentagon_points()
        
    def copy(self):
        new_pentagon = Pentagon(self.center_x, self.center_y, self.radius)
        new_pentagon.line_color = self.line_color
        new_pentagon.fill_color = self.fill_color
        new_pentagon.line_width = self.line_width
        new_pentagon.line_style = self.line_style
        return new_pentagon

    def shear(self, shear_x, shear_y):
        new_points = []
        for x, y in self.points:
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            new_points.append((new_x, new_y))
        self.points = new_points

class Hexagon(Shape):
    def __init__(self, center_x, center_y, radius):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.points = self._generate_hexagon_points()
        
    def _generate_hexagon_points(self):
        points = []
        for i in range(6):
            angle = i * 2 * math.pi / 6
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            points.append((x, y))
        return points
        
    def draw(self, canvas):
        outline_color = "red" if self.selected else self.line_color
        fill_color = self.fill_color if self.fill_color else ""
        dash = self.get_dash_pattern()
        
        flat_points = [coord for point in self.points for coord in point]
        canvas.create_polygon(flat_points, outline=outline_color, fill=fill_color,
                            width=self.line_width, dash=dash, tags="shape")
                            
    def contains_point(self, x, y) -> bool:
        distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        return abs(distance - self.radius) < 10
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        return (self.center_x - self.radius, self.center_y - self.radius,
                self.center_x + self.radius, self.center_y + self.radius)
                
    def translate(self, dx, dy):
        self.center_x += dx
        self.center_y += dy
        self.points = [(x + dx, y + dy) for x, y in self.points]
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x, center_y = self.center_x, self.center_y
        else:
            self.center_x = center_x + (self.center_x - center_x) * factor
            self.center_y = center_y + (self.center_y - center_y) * factor
        self.radius *= factor
        self.points = self._generate_hexagon_points()
        
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            center_x, center_y = self.center_x, self.center_y
        else:
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            dx = self.center_x - center_x
            dy = self.center_y - center_y
            self.center_x = center_x + dx * cos_a - dy * sin_a
            self.center_y = center_y + dx * sin_a + dy * cos_a
            
        self.points = self._generate_hexagon_points()
        
    def copy(self):
        new_hexagon = Hexagon(self.center_x, self.center_y, self.radius)
        new_hexagon.line_color = self.line_color
        new_hexagon.fill_color = self.fill_color
        new_hexagon.line_width = self.line_width
        new_hexagon.line_style = self.line_style
        return new_hexagon

    def shear(self, shear_x, shear_y):
        new_points = []
        for x, y in self.points:
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            new_points.append((new_x, new_y))
        self.points = new_points

class Polygon(Shape):
    def __init__(self, points: List[Tuple[float, float]]):
        super().__init__()
        self.points = points[:]
        
    def draw(self, canvas):
        if len(self.points) < 2:
            return
            
        color = "red" if self.selected else self.line_color
        
        # Draw lines between consecutive points
        for i in range(len(self.points)):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % len(self.points)]
            canvas.create_line(x1, y1, x2, y2, fill=color, width=self.line_width, tags="shape")
            
    def contains_point(self, x, y) -> bool:
        # Check if point is near any edge
        for i in range(len(self.points)):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % len(self.points)]
            
            if x1 == x2 and y1 == y2:
                continue
                
            A = y2 - y1
            B = x1 - x2
            C = x2 * y1 - x1 * y2
            
            if A == 0 and B == 0:
                continue
                
            distance = abs(A * x + B * y + C) / math.sqrt(A * A + B * B)
            if distance < 5:
                return True
        return False
        
    def get_bounds(self) -> Tuple[float, float, float, float]:
        if not self.points:
            return (0, 0, 0, 0)
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))
        
    def translate(self, dx, dy):
        self.points = [(x + dx, y + dy) for x, y in self.points]
        
    def scale(self, factor, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)
            
        self.points = [(center_x + (x - center_x) * factor, 
                        center_y + (y - center_y) * factor) 
                       for x, y in self.points]
                       
    def rotate(self, angle, center_x=None, center_y=None):
        if center_x is None or center_y is None:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)
            
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        new_points = []
        for x, y in self.points:
            dx = x - center_x
            dy = y - center_y
            new_x = center_x + dx * cos_a - dy * sin_a
            new_y = center_y + dx * sin_a + dy * cos_a
            new_points.append((new_x, new_y))
            
        self.points = new_points
        
    def copy(self):
        new_polygon = Polygon(self.points[:])
        new_polygon.line_color = self.line_color
        new_polygon.fill_color = self.fill_color
        new_polygon.line_width = self.line_width
        new_polygon.line_style = self.line_style
        return new_polygon
        
    def shear(self, shear_x, shear_y):
        new_points = []
        for x, y in self.points:
            new_x = x + shear_x * y
            new_y = y + shear_y * x
            new_points.append((new_x, new_y))
        self.points = new_points
