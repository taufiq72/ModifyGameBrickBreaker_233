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

class Ball(GameObject):

    def __init__(self, canvas, x, y):
        self.radius = 10
        self.speed = 10
        # --- MODIFIKASI: Mengganti self.direction = [1, -1] dengan vektor kecepatan (vx, vy) ---
        self.vx = 0.707
        self.vy = -0.707

        # --- MODIFIKASI: Mengubah warna & border bola agar lebih menarik ---
        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill="#ffffff",
            outline="#cccccc",
            width=2,
        )
        super(Ball, self).__init__(canvas, item)
        # --- MODIFIKASI (BARU): List untuk menyimpan objek efek jejak bola (trail) ---
        self.trail_items = []

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # --- MODIFIKASI (BARU): Efek jejak pergerakan bola (Trail FX) ---
        trail = self.canvas.create_oval(
            coords[0],
            coords[1],
            coords[2],
            coords[3],
            fill="#dcdde1",
            outline="",
        )
        self.trail_items.append((trail, 4))
        self.update_trails()

        # --- MODIFIKASI: Penyesuaian pantulan dinding menggunakan vx dan vy ---
        if coords[0] <= 0:
            self.vx = abs(self.vx)
        elif coords[2] >= width:
            self.vx = -abs(self.vx)

        if coords[1] <= 0:
            self.vy = abs(self.vy)

        x = self.vx * self.speed
        y = self.vy * self.speed
        self.move(x, y)

    # --- MODIFIKASI (BARU): Metode untuk meng-update dan menghapus efek jejak bola ---
    def update_trails(self):
        new_trails = []
        for trail, life in self.trail_items:
            life -= 1
            if life <= 0:
                self.canvas.delete(trail)
            else:
                new_trails.append((trail, life))
        self.trail_items = new_trails

    def collide(self, game_objects):
        coords = self.get_position()
        ball_center_x = (coords[0] + coords[2]) * 0.5
        ball_center_y = (coords[1] + coords[3]) * 0.5

        for game_object in game_objects:
            if isinstance(game_object, Paddle):
                # --- MODIFIKASI: Fisika pantulan paddle dinamis berdasarkan titik kontak ---
                paddle_coords = game_object.get_position()
                paddle_center_x = (paddle_coords[0] + paddle_coords[2]) * 0.5
                paddle_width = paddle_coords[2] - paddle_coords[0]

                # Menghitung posisi relatif benturan terhadap pusat paddle [-1, 1]
                hit_pos = (ball_center_x - paddle_center_x) / (
                    paddle_width / 2.0
                )
                hit_pos = max(-1.0, min(1.0, hit_pos))

                # Menentukan sudut pantul maksimum (60 derajat)
                max_angle = math.radians(60)
                bounce_angle = hit_pos * max_angle

                self.vx = math.sin(bounce_angle)
                self.vy = -math.cos(bounce_angle)

            elif isinstance(game_object, Brick):
                # --- MODIFIKASI: Penentuan arah pantulan bata berdasarkan sumbu X/Y ---
                b_coords = game_object.get_position()
                if (
                    ball_center_x < b_coords[0]
                    or ball_center_x > b_coords[2]
                ):
                    self.vx *= -1
                else:
                    self.vy *= -1

                game_object.hit()

    # --- MODIFIKASI (BARU): Membersihkan sisa efek jejak saat bola reset ---
    def clear_trails(self):
        for trail, _ in self.trail_items:
            self.canvas.delete(trail)
        self.trail_items = []


class Paddle(GameObject):

    def __init__(self, canvas, x, y):
        # --- MODIFIKASI: Penyesuaian ukuran lebar & tinggi paddle ---
        self.width = 100
        self.height = 12
        self.ball = None
        # --- MODIFIKASI: Desain visual paddle modern (kuning keemasan dengan border) ---
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill="#f1c40f",
            outline="#f39c12",
            width=2,
        )
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)