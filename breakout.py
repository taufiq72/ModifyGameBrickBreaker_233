import math  # --- MODIFIKASI: Import math untuk kalkulasi sudut & partikel ---
import random  # --- MODIFIKASI: Import random untuk variasi gerakan partikel ---
import tkinter as tk

class GameObject(object):

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

# --- MODIFIKASI (BARU): Kelas Particle untuk efek ledakan bata ---
class Particle(GameObject):

    def __init__(self, canvas, x, y, color):
        self.radius = random.randint(2, 4)
        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill=color,
            outline="",
        )
        super(Particle, self).__init__(canvas, item)
        # Menghitung arah gerak partikel secara acak ke segala arah
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(8, 15)  # Umur hidup partikel dalam frame

    def update(self):
        self.move(self.vx, self.vy)
        self.life -= 1
        if self.life <= 0:
            self.delete()
            return False
        return True