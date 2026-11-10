<img width="469" height="332" alt="Screenshot 2026-11-10 105224" src="https://github.com/user-attachments/assets/755f7801-d1b9-4e1d-b1b2-90fcd6c54cd4" />

Modifikasi yang tambahkan
### 1. Perbaikan Bug & Optimasi Memori
* **Penjelasan:** 
  1. Mengganti seluruh format *smart quotes* (`''`) pada string awal menjadi petik tunggal standar (`'`) untuk mengeliminasi `SyntaxError`.
  2. Menambahkan pembersihan referensi objek bata yang telah hancur dari kamus `self.items` agar tidak memicu `KeyError` saat deteksi benturan.
* **Cuplikan Kode:**
```python
def check_collisions(self):
    ball_coords = self.ball.get_position()
    items = self.canvas.find_overlapping(*ball_coords)

    # Membersihkan referensi item yang sudah terhapus dari canvas
    destroyed_items = [
        item_id for item_id in self.items
        if item_id not in self.canvas.find_all()
    ]
    for item_id in destroyed_items:
        del self.items[item_id]

    objects = [self.items[x] for x in items if x in self.items]
    self.ball.collide(objects)
```

---

### 2. Fisika Pantulan & Vektor Kecepatan Bola Dinamis
* **Penjelasan:** Mengubah sistem pantulan statis kaku `direction = [1, -1]` menjadi vektor trigonometri dinamis (`self.vx`, `self.vy`). Sudut pantul bola kini bergantung pada titik benturan bola terhadap paddle (pantulan bisa mencapai sudut tajam hingga 60 derajat).
* **Cuplikan Kode:**
```python
def collide(self, game_objects):
    coords = self.get_position()
    ball_center_x = (coords[0] + coords[2]) * 0.5

    for game_object in game_objects:
        if isinstance(game_object, Paddle):
            paddle_coords = game_object.get_position()
            paddle_center_x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            paddle_width = paddle_coords[2] - paddle_coords[0]

            # Menghitung titik jatuh bola relatif terhadap tengah paddle [-1.0, 1.0]
            hit_pos = (ball_center_x - paddle_center_x) / (paddle_width / 2.0)
            hit_pos = max(-1.0, min(1.0, hit_pos))

            # Menghitung sudut pantul maksimal 60 derajat
            max_angle = math.radians(60)
            bounce_angle = hit_pos * max_angle

            self.vx = math.sin(bounce_angle)
            self.vy = -math.cos(bounce_angle)
```

---

### 3. Efek Visual Partikel Ledakan (Explosion FX)
* **Penjelasan:** Menambahkan kelas `Particle` baru untuk menciptakan efek ledakan pecahan bata saat bola berhasil menghancurkannya. Setiap partikel menyebar secara acak ke segala arah dan menghapus dirinya sendiri dari memori canvas setelah durasi hidupnya habis.
* **Cuplikan Kode:**
```python
class Particle(GameObject):
    def __init__(self, canvas, x, y, color):
        self.radius = random.randint(2, 4)
        item = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill=color, outline=""
        )
        super(Particle, self).__init__(canvas, item)
        
        # Menghitung arah gerak acak partikel (360 derajat)
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
```

---

### 4. Efek Jejak Pergerakan Bola (Motion Trail FX)
* **Penjelasan:** Setiap kali bola bergerak, sistem akan menggambar bayangan transparan di posisi bola sebelumnya. Bayangan ini akan menghilang secara otomatis setelah 4 frame untuk menghasilkan efek gerakan cepat (*motion blur*).
* **Cuplikan Kode:**
```python
def update(self):
    coords = self.get_position()

    # Membuat objek bayangan bola di posisi saat ini
    trail = self.canvas.create_oval(
        coords[0], coords[1], coords[2], coords[3],
        fill="#dcdde1", outline=""
    )
    self.trail_items.append((trail, 4))
    self.update_trails()
    ...

def update_trails(self):
    new_trails = []
    for trail, life in self.trail_items:
        life -= 1
        if life <= 0:
            self.canvas.delete(trail)
        else:
            new_trails.append((trail, life))
    self.trail_items = new_trails
```

---
