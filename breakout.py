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

class Brick(GameObject):
    # --- MODIFIKASI: Penggunaan palet warna Flat UI modern ---
    COLORS = {1: "#e74c3c", 2: "#3498db", 3: "#2ecc71"}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=color,
            outline="#ffffff",
            width=1,
            tags="brick",
        )
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        # --- MODIFIKASI (BARU): Memicu pembuatan ledakan partikel saat terkena pukulan ---
        coords = self.get_position()
        center_x = (coords[0] + coords[2]) * 0.5
        center_y = (coords[1] + coords[3]) * 0.5
        color = Brick.COLORS[self.hits]

        game_instance = self.canvas.master
        if hasattr(game_instance, "create_explosion"):
            game_instance.create_explosion(center_x, center_y, color)

        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])

class Game(tk.Frame):

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        # --- MODIFIKASI: Warna latar canvas diubah ke Dark Slate (#2c3e50) ---
        self.canvas = tk.Canvas(
            self, bg="#2c3e50", width=self.width, height=self.height
        )
        self.canvas.pack()
        self.pack()

        self.items = {}
        # --- MODIFIKASI (BARU): List penampung objek partikel ---
        self.particles = []
        self.ball = None
        # --- MODIFIKASI: Penyesuaian posisi Y paddle agar lebih presisi ---
        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 75, 2)
            self.add_brick(x + 37.5, 100, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        # --- MODIFIKASI: Kecepatan gerakan paddle dinaikkan dari 10 ke 15 ---
        self.canvas.bind("<Left>", lambda _: self.paddle.move(-15))
        self.canvas.bind("<Right>", lambda _: self.paddle.move(15))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, "Press Space to start")
        self.canvas.bind("<space>", lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            # --- MODIFIKASI: Clear trails sebelum menghapus objek bola lama ---
            self.ball.clear_trails()
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        # --- MODIFIKASI: Penyesuaian posisi awal bola mengikuti tinggi paddle baru ---
        self.ball = Ball(self.canvas, x, 334)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size=30):
        # --- MODIFIKASI: Font standar Helvetica bold dengan warna terang (#ecf0f1) ---
        font = ("Helvetica", size, "bold")
        return self.canvas.create_text(
            x, y, text=text, font=font, fill="#ecf0f1"
        )

    def update_lives_text(self):
        text = "Lives: %s" % self.lives
        if self.hud is None:
            self.hud = self.draw_text(60, 20, text, 14)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    # --- MODIFIKASI (BARU): Fungsi pemicu pembuatan 12 partikel ledakan ---
    def create_explosion(self, x, y, color):
        for _ in range(12):
            self.particles.append(Particle(self.canvas, x, y, color))

    # --- MODIFIKASI (BARU): Fungsi pembaruan siklus hidup partikel ---
    def update_particles(self):
        active_particles = []
        for p in self.particles:
            if p.update():
                active_particles.append(p)
        self.particles = active_particles

    def start_game(self):
        self.canvas.unbind("<space>")
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        # --- MODIFIKASI (BARU): Update animasi partikel di setiap frame loop ---
        self.update_particles()

        num_bricks = len(self.canvas.find_withtag("brick"))
        if num_bricks == 0:
            self.draw_text(300, 200, "YOU WIN!")
        elif self.ball.get_position()[3] >= self.height:
            # --- MODIFIKASI: Membersihkan jejak bola saat kalah/mati ---
            self.ball.clear_trails()
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, "GAME OVER!")
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            # --- MODIFIKASI: Penyesuaian frame rate dari 50 ms ke 30 ms (~33 FPS) ---
            self.after(30, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)

        destroyed_items = [
            item_id
            for item_id in self.items
            if item_id not in self.canvas.find_all()
        ]
        for item_id in destroyed_items:
            del self.items[item_id]

        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Breakout FX - Tkinter Edition")
    game = Game(root)
    game.mainloop()