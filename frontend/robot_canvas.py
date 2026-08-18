"""
robot_canvas.py  --  Animated Robot Canvas
==========================================
Draws and animates the robot on a tkinter Canvas widget.

The RobotCanvas class:
  - Renders a geometric robot (head, body, arms, tracks, antenna)
  - Maintains robot world position (x, y) and heading angle
  - Executes a queue of parsed commands one by one, animating each
  - Provides visual effects for: shield, laser, stop, pulse
  - Draws a grid background and a motion trail
"""

import tkinter as tk
import math


# ── Color palette ─────────────────────────────────────────────────────────────
C = {
    "bg"          : "#0d1117",
    "grid"        : "#1e2d40",
    "origin"      : "#30363d",
    "trail"       : "#388bfd",
    "body"        : "#1f6feb",
    "body_hi"     : "#388bfd",
    "head"        : "#58a6ff",
    "eye"         : "#79c0ff",
    "eye_hi"      : "#cae8ff",
    "arm"         : "#2d76d2",
    "track"       : "#1158c7",
    "joint"       : "#388bfd",
    "chest"       : "#f0883e",
    "chest_hi"    : "#ffa657",
    "antenna"     : "#f0883e",
    "stop_flash"  : "#f85149",
    "shield"      : "#39d353",
    "laser"       : "#f85149",
    "text"        : "#8b949e",
    "speed_fill"  : "#1f6feb",
}

CELL = 40       # grid cell size in pixels (1 step = 40 px)


class RobotCanvas:
    """Handles all robot rendering and sequential command animation."""

    def __init__(self, parent: tk.Widget):
        self.parent = parent

        # tkinter Canvas
        self.canvas = tk.Canvas(
            parent,
            bg=C["bg"],
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ── Robot world state ──
        self.rx      = 0.0   # world x-position (pixels from origin)
        self.ry      = 0.0   # world y-position (pixels from origin)
        self.angle   = 0.0   # heading angle in degrees (0 = up, +ve = CW)
        self.speed   = 5     # animation speed 1-10

        # ── Animation queue ──
        self._queue     : list[dict] = []
        self._busy      : bool       = False
        self._on_done   = None

        # ── Trail history ──
        self._trail     : list[tuple[float, float]] = []  # world coords

        # Initial draw
        self._full_redraw()
        self.canvas.bind("<Configure>", lambda _e: self._full_redraw())

    # ══════════════════════════════════════════════════════════════════════════
    #  Public API
    # ══════════════════════════════════════════════════════════════════════════

    def execute_commands(self, commands: list[dict], on_done=None):
        """Queue commands for sequential animation."""
        self._on_done = on_done
        self._queue.extend(commands)
        if not self._busy:
            self._next()

    def reset(self):
        """Return robot to origin, clear trail, flush queue."""
        self._queue  = []
        self._busy   = False
        self.rx, self.ry, self.angle, self.speed = 0.0, 0.0, 0.0, 5
        self._trail  = []
        self._full_redraw()

    # ══════════════════════════════════════════════════════════════════════════
    #  Internal: animation queue driver
    # ══════════════════════════════════════════════════════════════════════════

    def _next(self):
        """Pick the next command and start its animation."""
        if not self._queue:
            self._busy = False
            if self._on_done:
                self._on_done()
            return

        self._busy = True
        cmd = self._queue.pop(0)

        dispatch = {
            "move"   : self._anim_move,
            "turn"   : self._anim_turn,
            "speed"  : self._do_speed,
            "stop"   : self._anim_stop,
            "ability": self._anim_ability,
        }
        handler = dispatch.get(cmd.get("type", ""))
        if handler:
            handler(cmd)
        else:
            self._next()

    def _after_cmd(self, delay: int = 200):
        """Called at the end of every command animation."""
        self.parent.after(delay, self._next)

    # ══════════════════════════════════════════════════════════════════════════
    #  Command handlers
    # ══════════════════════════════════════════════════════════════════════════

    # ── MOVE ──────────────────────────────────────────────────────────────────
    def _anim_move(self, cmd: dict):
        direction = cmd.get("direction", "forward")
        steps     = float(cmd.get("value", 1))
        pixels    = steps * CELL

        rad = math.radians(self.angle)

        # Direction vector in screen space (y-axis is flipped)
        vectors = {
            "forward"  : ( math.sin(rad), -math.cos(rad)),
            "backward" : (-math.sin(rad),  math.cos(rad)),
            "left"     : (-math.cos(rad), -math.sin(rad)),
            "right"    : ( math.cos(rad),  math.sin(rad)),
        }
        dx, dy = vectors.get(direction, (0, 0))

        sx, sy   = self.rx, self.ry          # start
        tx, ty   = sx + dx * pixels, sy + dy * pixels  # target
        frames   = max(1, int(pixels / 3))  # 3 px per frame
        delay_ms = self._frame_ms()

        def step(f: int):
            if f > frames:
                self.rx, self.ry = tx, ty
                self._trail.append((self.rx, self.ry))
                self._full_redraw()
                self._after_cmd(120)
                return
            t          = f / frames
            t_ease     = t * t * (3 - 2 * t)   # smooth-step
            self.rx    = sx + (tx - sx) * t_ease
            self.ry    = sy + (ty - sy) * t_ease
            self._full_redraw()
            self.parent.after(delay_ms, lambda: step(f + 1))

        step(1)

    # ── TURN ──────────────────────────────────────────────────────────────────
    def _anim_turn(self, cmd: dict):
        direction = cmd.get("direction", "right")
        degrees   = float(cmd.get("value", 90))
        sign      = -1 if direction == "left" else 1
        target    = self.angle + sign * degrees
        start     = self.angle
        frames    = max(1, int(abs(degrees) / 3))   # 3° per frame
        delay_ms  = self._frame_ms()

        def step(f: int):
            if f > frames:
                self.angle = target
                self._full_redraw()
                self._after_cmd(120)
                return
            t          = f / frames
            t_ease     = t * t * (3 - 2 * t)
            self.angle = start + (target - start) * t_ease
            self._full_redraw()
            self.parent.after(delay_ms, lambda: step(f + 1))

        step(1)

    # ── SPEED ─────────────────────────────────────────────────────────────────
    def _do_speed(self, cmd: dict):
        self.speed = max(1, min(10, int(cmd.get("value", 5))))
        self._full_redraw()
        self._after_cmd(150)

    # ── STOP ──────────────────────────────────────────────────────────────────
    def _anim_stop(self, cmd: dict = None):
        """Flash the robot body between stop-red and normal blue."""
        count = [0]

        def flash():
            count[0] += 1
            if count[0] > 7:
                self._full_redraw()
                self._after_cmd(200)
                return
            # Draw robot with alternating color
            override = C["stop_flash"] if count[0] % 2 == 1 else C["body"]
            self._full_redraw(body_override=override)
            self.parent.after(120, flash)

        flash()

    # ── ABILITY ───────────────────────────────────────────────────────────────
    def _anim_ability(self, cmd: dict):
        name = cmd.get("extra", "").lower()
        if   "shield" in name: self._fx_shield()
        elif "laser"  in name: self._fx_laser()
        elif "boost"  in name: self._fx_boost()
        else                 : self._fx_pulse(C["eye"])

    # ── Shield effect: expanding green concentric rings ───────────────────────
    def _fx_shield(self):
        sx, sy = self._w2s(self.rx, self.ry)
        step   = [0]

        def frame():
            step[0] += 1
            if step[0] > 14:
                self._full_redraw()
                self._after_cmd(250)
                return
            self._full_redraw()
            for i in range(step[0]):
                r     = (step[0] - i) * 9 + 25
                alpha = max(0, 200 - i * 22)
                col   = f"#00{alpha:02x}53" if alpha > 15 else C["bg"]
                self.canvas.create_oval(
                    sx - r, sy - r, sx + r, sy + r,
                    outline=col, width=2, tags="fx"
                )
            # Solid ring
            self.canvas.create_oval(
                sx - 40, sy - 40, sx + 40, sy + 40,
                outline=C["shield"], fill="", width=3, tags="fx"
            )
            self.parent.after(55, frame)

        frame()

    # ── Laser effect: beam shoots forward ─────────────────────────────────────
    def _fx_laser(self):
        sx, sy    = self._w2s(self.rx, self.ry)
        rad       = math.radians(self.angle)
        MAX_LEN   = 350
        step      = [0]

        def frame():
            step[0] += 1
            if step[0] > 14:
                self._full_redraw()
                self._after_cmd(250)
                return
            self._full_redraw()
            length = min(MAX_LEN, step[0] * 28)
            ex = sx + math.sin(rad) * length
            ey = sy - math.cos(rad) * length
            # Glow layers
            for w, col in [(14, "#0d1117"), (7, "#8a2b28"),
                           (3, C["laser"]), (1, "#ffffff")]:
                self.canvas.create_line(
                    sx, sy, ex, ey, fill=col, width=w,
                    capstyle=tk.ROUND, tags="fx"
                )
            # Impact burst (last few frames)
            if step[0] > 9:
                r = (step[0] - 9) * 7
                self.canvas.create_oval(
                    ex - r, ey - r, ex + r, ey + r,
                    fill=C["laser"], outline="#ffffff", width=1, tags="fx"
                )
            self.parent.after(50, frame)

        frame()

    # ── Boost effect: speed lines ─────────────────────────────────────────────
    def _fx_boost(self):
        import random
        sx, sy  = self._w2s(self.rx, self.ry)
        rad     = math.radians(self.angle + 180)
        step    = [0]

        def frame():
            step[0] += 1
            if step[0] > 10:
                self._full_redraw()
                self._after_cmd(200)
                return
            self._full_redraw()
            for _ in range(6):
                spread = random.uniform(-0.5, 0.5)
                ang    = rad + spread
                length = random.randint(30, 80) * step[0] // 5 + 10
                ex = sx + math.sin(ang) * length
                ey = sy - math.cos(ang) * length
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=C["chest"], width=2, tags="fx"
                )
            self.parent.after(60, frame)

        frame()

    # ── Generic pulse ─────────────────────────────────────────────────────────
    def _fx_pulse(self, color: str):
        sx, sy = self._w2s(self.rx, self.ry)
        step   = [0]

        def frame():
            step[0] += 1
            if step[0] > 10:
                self._full_redraw()
                self._after_cmd(200)
                return
            self._full_redraw()
            r = step[0] * 11
            self.canvas.create_oval(
                sx - r, sy - r, sx + r, sy + r,
                outline=color, width=2, tags="fx"
            )
            self.parent.after(55, frame)

        frame()

    # ══════════════════════════════════════════════════════════════════════════
    #  Drawing helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _full_redraw(self, body_override: str | None = None):
        """Delete everything and redraw from scratch."""
        self.canvas.delete("all")
        self._draw_grid()
        self._draw_trail()
        self._draw_robot(body_override)
        self._draw_hud()

    # ── Grid ──────────────────────────────────────────────────────────────────
    def _draw_grid(self):
        w = self.canvas.winfo_width()  or 800
        h = self.canvas.winfo_height() or 600

        # Vertical lines
        for x in range(0, w + CELL, CELL):
            self.canvas.create_line(x, 0, x, h, fill=C["grid"], width=1)
        # Horizontal lines
        for y in range(0, h + CELL, CELL):
            self.canvas.create_line(0, y, w, y, fill=C["grid"], width=1)

        # Origin marker
        ox, oy = self._w2s(0, 0)
        self.canvas.create_line(ox - 10, oy, ox + 10, oy, fill=C["origin"], width=2)
        self.canvas.create_line(ox, oy - 10, ox, oy + 10, fill=C["origin"], width=2)
        self.canvas.create_oval(ox-3, oy-3, ox+3, oy+3,
                                fill=C["origin"], outline="")

    # ── Trail ─────────────────────────────────────────────────────────────────
    def _draw_trail(self):
        pts = [(0.0, 0.0)] + self._trail + [(self.rx, self.ry)]
        if len(pts) < 2:
            return
        for i in range(len(pts) - 1):
            x1, y1 = self._w2s(*pts[i])
            x2, y2 = self._w2s(*pts[i + 1])
            alpha   = int(255 * (i + 1) / len(pts))
            # Dashed trail line
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="#388bfd", width=2,
                dash=(5, 5)
            )
        # Dot at each waypoint
        for wp in self._trail:
            px, py = self._w2s(*wp)
            self.canvas.create_oval(px-3, py-3, px+3, py+3,
                                    fill="#388bfd", outline="")

    # ── Robot ─────────────────────────────────────────────────────────────────
    def _draw_robot(self, body_override: str | None = None):
        """Render the robot at (self.rx, self.ry) rotated by self.angle."""
        cx, cy = self._w2s(self.rx, self.ry)
        a      = self.angle
        bc     = body_override or C["body"]   # body color (overrideable)

        def rot(dx: float, dy: float) -> tuple[float, float]:
            """Rotate point (dx, dy) around robot center by angle a."""
            rad = math.radians(a)
            rx  = dx * math.cos(rad) - dy * math.sin(rad)
            ry  = dx * math.sin(rad) + dy * math.cos(rad)
            return cx + rx, cy + ry

        def poly(*pts) -> list[float]:
            """Flatten a list of (x,y) tuples for canvas polygon."""
            return [v for p in pts for v in p]

        # ── Tracks (left and right) ──────────────────────────────────────────
        for sx in (-20, 20):
            pts = [rot(sx - 9, 18), rot(sx + 9, 18),
                   rot(sx + 9, 33), rot(sx - 9, 33)]
            self.canvas.create_polygon(
                poly(*pts), fill=C["track"], outline=C["joint"], width=1)
            # Tread lines
            for t in range(20, 32, 4):
                self.canvas.create_line(*rot(sx-9, t), *rot(sx+9, t),
                                        fill=C["joint"], width=1)

        # ── Main body ────────────────────────────────────────────────────────
        body_pts = [rot(-18, -12), rot(18, -12), rot(18, 18), rot(-18, 18)]
        self.canvas.create_polygon(poly(*body_pts), fill=bc,
                                   outline=C["joint"], width=1)

        # Panel divider
        self.canvas.create_line(*rot(-18, 4), *rot(18, 4),
                                fill=C["joint"], width=1)

        # Chest light (always same color for visibility)
        lc = rot(0, 11)
        self.canvas.create_oval(lc[0]-6, lc[1]-6, lc[0]+6, lc[1]+6,
                                fill=C["chest"], outline=C["joint"], width=1)
        self.canvas.create_oval(lc[0]-2, lc[1]-2, lc[0]+2, lc[1]+2,
                                fill=C["chest_hi"], outline="")

        # Side vents
        for vx in (-14, 14):
            for vy in (-6, -2, 2):
                self.canvas.create_line(
                    *rot(vx, vy), *rot(vx - 4 * (1 if vx < 0 else -1), vy),
                    fill=C["joint"], width=1
                )

        # ── Arms ─────────────────────────────────────────────────────────────
        for sx in (-1, 1):
            arm_pts = [rot(sx*18, -8), rot(sx*27, -8),
                       rot(sx*27, 14),  rot(sx*18, 14)]
            self.canvas.create_polygon(
                poly(*arm_pts), fill=C["arm"], outline=C["joint"], width=1)
            # Hand knuckle
            hc = rot(sx * 27, 5)
            self.canvas.create_oval(hc[0]-4, hc[1]-6, hc[0]+4, hc[1]+6,
                                    fill=C["joint"], outline="")

        # ── Head ─────────────────────────────────────────────────────────────
        head_pts = [rot(-15, -12), rot(15, -12), rot(15, -30), rot(-15, -30)]
        self.canvas.create_polygon(poly(*head_pts), fill=C["head"],
                                   outline=C["joint"], width=1)

        # Visor band (between eyes)
        self.canvas.create_line(*rot(-13, -21), *rot(13, -21),
                                fill="#1e3555", width=9)

        # Eyes (left and right)
        for ex in (-6, 6):
            ec = rot(ex, -21)
            # Outer glow
            self.canvas.create_oval(ec[0]-7, ec[1]-5, ec[0]+7, ec[1]+5,
                                    fill="#1b2d42", outline="")
            # Iris
            self.canvas.create_oval(ec[0]-5, ec[1]-4, ec[0]+5, ec[1]+4,
                                    fill=C["eye"], outline=C["eye_hi"], width=1)
            # Pupil
            self.canvas.create_oval(ec[0]-2, ec[1]-2, ec[0]+2, ec[1]+2,
                                    fill=C["eye_hi"], outline="")

        # Mouth (3 dots)
        for mx in (-5, 0, 5):
            mc = rot(mx, -14)
            self.canvas.create_oval(mc[0]-1, mc[1]-1, mc[0]+1, mc[1]+1,
                                    fill=C["joint"], outline="")

        # ── Antenna ──────────────────────────────────────────────────────────
        base = rot(0, -30)
        tip  = rot(0, -45)
        self.canvas.create_line(*base, *tip, fill=C["antenna"], width=2)
        ball = rot(0, -48)
        # Glow
        self.canvas.create_oval(ball[0]-7, ball[1]-7, ball[0]+7, ball[1]+7,
                                fill="#1f1a0d", outline="")
        # Ball
        self.canvas.create_oval(ball[0]-4, ball[1]-4, ball[0]+4, ball[1]+4,
                                fill=C["antenna"], outline=C["chest_hi"], width=1)

    # ── HUD (heads-up display) ────────────────────────────────────────────────
    def _draw_hud(self):
        w = self.canvas.winfo_width()  or 800
        h = self.canvas.winfo_height() or 600

        # Position / angle info (bottom-left)
        sx = self.rx / CELL
        sy = -self.ry / CELL
        info = (
            f"  Position: ({sx:.1f}, {sy:.1f}) steps  |"
            f"  Heading: {self.angle % 360:.0f}°  |"
            f"  Speed: {self.speed}/10"
        )
        self.canvas.create_text(
            8, h - 10, text=info, anchor="sw",
            fill=C["text"], font=("Consolas", 9)
        )

        # Speed bar (bottom-right)
        bar_w  = 90
        bar_x  = w - bar_w - 10
        bar_y  = h - 22
        fill_w = int(bar_w * self.speed / 10)

        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_w, bar_y + 8,
            fill="#1a2030", outline=C["origin"], width=1
        )
        if fill_w > 0:
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + fill_w, bar_y + 8,
                fill=C["speed_fill"], outline=""
            )
        self.canvas.create_text(
            bar_x + bar_w // 2, bar_y - 7,
            text="SPEED", fill=C["text"], font=("Consolas", 7)
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  Utility
    # ══════════════════════════════════════════════════════════════════════════

    def _w2s(self, wx: float, wy: float) -> tuple[float, float]:
        """World coordinates → screen coordinates (origin = canvas center)."""
        w = self.canvas.winfo_width()  or 800
        h = self.canvas.winfo_height() or 600
        return w / 2 + wx, h / 2 + wy

    def _frame_ms(self) -> int:
        """Per-frame delay in milliseconds based on speed (1=slow, 10=fast)."""
        return max(8, int(90 / self.speed))
