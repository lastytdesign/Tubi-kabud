"""
Гурез аз монеа — Бозии соддаи ҳаракат
Сохта шуда бо Kivy барои кор дар Pydroid 3 (Android)

Тарзи бозӣ:
- Тӯбчаи кабудро бо ангушт (кашидан ба чап/рост) ҳаракат деҳ
- Бастаҳои сурхро, ки аз боло меафтанд, гурез
- Ҳар қадар дертар зинда монӣ, холи бештар мегирӣ — суръат тадриҷан меафзояд
- Агар бархӯрд шавӣ — бозӣ тамом, бо ангушт "аз нав" пахш кун

Насб: Pydroid 3 -> Pip -> "kivy" (агар аллакай насб накарда бошӣ)
Иҷро: ин файлро Run кун
"""

import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

# ---------- Ранг (тарзи дизайн) ----------
BG_DARK = (0.07, 0.07, 0.10, 1)
PLAYER_COLOR = (0.36, 0.75, 0.98, 1)
OBSTACLE_COLOR = (0.95, 0.35, 0.40, 1)
TEXT_MAIN = (0.95, 0.95, 0.96, 1)
ACCENT = (0.36, 0.62, 0.98, 1)

Window.clearcolor = BG_DARK


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_size = dp(46)
        self.player_x = 0  # марказ, дар update_player_start муайян мешавад
        self.obstacles = []  # ҳар як: {"x":, "y":, "size":, "speed":}
        self.score = 0.0
        self.game_over = False
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.1

        self.score_label = Label(
            text="Хол: 0",
            color=TEXT_MAIN,
            font_size="20sp",
            size_hint=(None, None),
        )
        self.add_widget(self.score_label)

        self.info_label = Label(
            text="",
            color=TEXT_MAIN,
            font_size="26sp",
            halign="center",
            valign="middle",
            size_hint=(None, None),
        )
        self.add_widget(self.info_label)

        self.bind(size=self._on_resize, pos=self._on_resize)
        Clock.schedule_once(self._start_game, 0.1)

    def _on_resize(self, *_):
        self.score_label.pos = (self.x + dp(16), self.top - dp(40))
        self.info_label.size = (self.width, dp(120))
        self.info_label.text_size = self.info_label.size
        self.info_label.pos = (self.x, self.center_y - dp(60))
        if not hasattr(self, "_positioned"):
            self.player_x = self.center_x
            self._positioned = True

    def _start_game(self, *_):
        self.player_x = self.center_x
        self.obstacles = []
        self.score = 0.0
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.1
        self.game_over = False
        self.info_label.text = ""
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1 / 60)

    def on_touch_down(self, touch):
        if self.game_over:
            self._start_game()
            return True
        self.player_x = touch.x
        return True

    def on_touch_move(self, touch):
        if not self.game_over:
            self.player_x = touch.x
        return True

    def update(self, dt):
        if self.game_over:
            return

        self.elapsed += dt
        self.score_label.text = f"Хол: {int(self.score)}"

        # Маҳдуд кардани ҳаракати бозингар дар доираи экран
        half = self.player_size / 2
        self.player_x = max(self.x + half, min(self.right - half, self.player_x))

        # Суръати афтиш ва басомади пайдоиши монеаҳо тадриҷан меафзояд
        fall_speed = dp(160) + self.elapsed * dp(6)
        self.spawn_interval = max(0.45, 1.1 - self.elapsed * 0.01)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            size = random.uniform(dp(30), dp(56))
            x = random.uniform(self.x + size / 2, self.right - size / 2)
            self.obstacles.append({"x": x, "y": self.top, "size": size, "speed": fall_speed})

        # Ҳаракати монеаҳо
        for obs in self.obstacles:
            obs["y"] -= obs["speed"] * dt

        # Монеаҳое, ки бомуваффақият гузашта шудаанд — хол медиҳем
        passed = [o for o in self.obstacles if o["y"] + o["size"] <= self.y]
        if passed:
            self.score += 10 * len(passed)
            self.score_label.text = f"Хол: {int(self.score)}"

        # Тоза кардани монеаҳое, ки аз экран баромадаанд
        self.obstacles = [o for o in self.obstacles if o["y"] + o["size"] > self.y]

        # Санҷиши бархӯрд (доира бо квадрат — тахминӣ бо масофа)
        px, py = self.player_x, self.y + self.player_size
        for obs in self.obstacles:
            ox = obs["x"]
            oy = obs["y"]
            dist_x = abs(px - ox)
            dist_y = abs(py - oy)
            min_dist = (self.player_size + obs["size"]) / 2 * 0.82
            if dist_x < min_dist and dist_y < min_dist:
                self.end_game()
                break

        self.draw()

    def end_game(self):
        self.game_over = True
        Clock.unschedule(self.update)
        self.info_label.text = (
            f"Бозӣ тамом шуд!\nХоли ту: {int(self.score)}\n\nБарои аз нав сар кардан пахш кун"
        )
        self.draw()

    def draw(self):
        self.canvas.before.clear()
        with self.canvas.before:
            # Заминаи бозӣ
            Color(*BG_DARK)
            Rectangle(pos=self.pos, size=self.size)

            # Монеаҳо
            Color(*OBSTACLE_COLOR)
            for obs in self.obstacles:
                s = obs["size"]
                RoundedRectangle(
                    pos=(obs["x"] - s / 2, obs["y"] - s / 2),
                    size=(s, s),
                    radius=[dp(8)],
                )

            # Бозингар (агар бозӣ тамом нашуда бошад)
            if not self.game_over:
                Color(*PLAYER_COLOR)
                s = self.player_size
                Ellipse(
                    pos=(self.player_x - s / 2, self.y + self.player_size - s / 2),
                    size=(s, s),
                )


class DodgeGameApp(App):
    def build(self):
        self.title = "Гурез аз монеа"
        return GameWidget()


if __name__ == "__main__":
    DodgeGameApp().run()
