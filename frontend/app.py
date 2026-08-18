"""
app.py  --  Robot Command Simulator  (Main Window)
===================================================
Entry point for the Python frontend.

Layout:
  ┌────────────────────────────────────────────────────┐
  │  🤖  Header  (title + compiler-mode status bar)    │
  ├──────────────────────┬─────────────────────────────┤
  │  📝  Code Editor     │   🤖  Robot Canvas           │
  │      (syntax hi.)    │       (animated robot)       │
  │      line numbers    │       grid + trail           │
  ├──────────────────────┴─────────────────────────────┤
  │  🖥  Output Console  (scrollable, color-coded)      │
  ├────────────────────────────────────────────────────┤
  │  [▶ Run] [⟳ Reset] [✕ Clear] [📋 Example]  [ℹ About]│
  └────────────────────────────────────────────────────┘

Author : Md. Zihad Hosain Siyam
Course : Compiler Design
"""

import tkinter as tk
import os
import sys
import re

# Add the frontend directory to import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from robot_canvas   import RobotCanvas
from command_runner import CommandRunner


# ── Color theme (GitHub Dark-inspired) ───────────────────────────────────────
T = {
    "bg_dark"    : "#0d1117",
    "bg_mid"     : "#161b22",
    "bg_light"   : "#21262d",
    "border"     : "#30363d",
    "accent"     : "#1f6feb",
    "accent_hi"  : "#388bfd",
    "green"      : "#39d353",
    "orange"     : "#f0883e",
    "red"        : "#f85149",
    "text"       : "#e6edf3",
    "text_muted" : "#8b949e",
    "text_dim"   : "#484f58",
    # Syntax highlight colors
    "syn_kw"     : "#ff7b72",   # keywords  (move, turn, stop …)
    "syn_dir"    : "#7ee787",   # directions (forward, left …)
    "syn_num"    : "#79c0ff",   # numbers
    "syn_str"    : "#a5d6ff",   # strings
    "syn_cmt"    : "#6e7681",   # comments
    "syn_unit"   : "#d2a8ff",   # units (steps, degrees)
}

# ── Syntax token groups (for highlighting) ────────────────────────────────────
SYN_KEYWORDS   = ["move","go","turn","rotate","stop","halt","ability","skill","speed"]
SYN_DIRECTIONS = ["forward","backward","back","left","right"]
SYN_UNITS      = ["steps","step","degrees","degree","deg"]

# ── Starter example code ──────────────────────────────────────────────────────
EXAMPLE = """\
# ════════════════════════════════════════
#   Robot Command Language  (RCL)
#   Type commands below and press ▶ Run
# ════════════════════════════════════════

# Set speed first (1 = slow, 10 = fast)
speed 6

# Move the robot
move forward 4 steps
move right 2 steps

# Turn the robot
turn left 90 degrees
move forward 3 steps

turn right 45 degrees
move forward 2 steps

# Special abilities
ability "shield"
ability "laser"

# Reset position (go back)
turn left 135 degrees
move forward 4 steps

# Stop!
stop
"""


# ═════════════════════════════════════════════════════════════════════════════
#  Main Application
# ═════════════════════════════════════════════════════════════════════════════

class App:
    """Builds and runs the Robot Command Simulator window."""

    def __init__(self):
        # ── Root window ──────────────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("🤖  Robot Command Simulator  ·  Compiler Design")
        self.root.geometry("1300x780")
        self.root.minsize(900, 620)
        self.root.configure(bg=T["bg_dark"])

        # ── Compiler backend ─────────────────────────────────────────────────
        self.runner = CommandRunner()

        # ── Build UI ─────────────────────────────────────────────────────────
        self._fonts()
        self._build_header()
        self._build_body()
        self._build_console()
        self._build_footer()

        # ── Load example ─────────────────────────────────────────────────────
        self._editor_set(EXAMPLE)
        self._highlight()

        # ── Status ───────────────────────────────────────────────────────────
        mode = self.runner.get_mode()
        self._status(f"Ready  ·  {mode}", "info")
        self._log(f"  Compiler mode: {mode}", "info")
        self._log("  Type RCL commands in the editor and press ▶ Run.\n", "muted")

        self.root.mainloop()

    # ══════════════════════════════════════════════════════════════════════════
    #  Fonts
    # ══════════════════════════════════════════════════════════════════════════

    def _fonts(self):
        self.F_CODE  = ("Consolas", 12)
        self.F_UI    = ("Segoe UI", 10)
        self.F_UI_B  = ("Segoe UI", 10, "bold")
        self.F_TITLE = ("Segoe UI", 17, "bold")
        self.F_SMALL = ("Segoe UI",  9)
        self.F_MONO  = ("Consolas",  9)

    # ══════════════════════════════════════════════════════════════════════════
    #  Header
    # ══════════════════════════════════════════════════════════════════════════

    def _build_header(self):
        # ── Main header bar ──
        hdr = tk.Frame(self.root, bg=T["bg_mid"], height=58)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=T["bg_mid"])
        left.pack(side=tk.LEFT, padx=16, pady=10)

        tk.Label(left, text="🤖", bg=T["bg_mid"],
                 font=("Segoe UI Emoji", 24)).pack(side=tk.LEFT)

        tk.Label(left, text=" Robot Command Simulator",
                 bg=T["bg_mid"], fg=T["text"],
                 font=self.F_TITLE).pack(side=tk.LEFT)

        tk.Label(left,
                 text="   Compiler Design  ·  Flex  ·  Bison  ·  Python",
                 bg=T["bg_mid"], fg=T["text_muted"],
                 font=self.F_SMALL).pack(side=tk.LEFT, pady=2)

        # ── Separator ──
        tk.Frame(self.root, bg=T["border"], height=1).pack(fill=tk.X)

        # ── Status bar ──
        self._status_bar = tk.Frame(self.root, bg=T["bg_mid"], height=26)
        self._status_bar.pack(fill=tk.X)
        self._status_bar.pack_propagate(False)

        self._dot = tk.Label(self._status_bar, text="●",
                             bg=T["bg_mid"], fg=T["green"], font=self.F_SMALL)
        self._dot.pack(side=tk.LEFT, padx=(10, 4))

        self._status_lbl = tk.Label(self._status_bar, text="",
                                    bg=T["bg_mid"], fg=T["text_muted"],
                                    font=self.F_SMALL)
        self._status_lbl.pack(side=tk.LEFT)

        tk.Frame(self.root, bg=T["border"], height=1).pack(fill=tk.X)

    # ══════════════════════════════════════════════════════════════════════════
    #  Body (editor + canvas)
    # ══════════════════════════════════════════════════════════════════════════

    def _build_body(self):
        pane = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL,
            bg=T["border"], sashwidth=4, sashrelief=tk.FLAT
        )
        pane.pack(fill=tk.BOTH, expand=True)

        # ── LEFT: Code editor ──────────────────────────────────────────────
        ef = tk.Frame(pane, bg=T["bg_mid"])
        pane.add(ef, width=430, minsize=280)

        self._panel_title(ef, "📝  Code Editor  —  Robot Command Language (.rcl)")

        # Editor inner layout: line-numbers | scrollbar | text
        inner = tk.Frame(ef, bg=T["bg_dark"])
        inner.pack(fill=tk.BOTH, expand=True)

        self._lnum = tk.Text(
            inner, width=4, state=tk.DISABLED,
            bg=T["bg_mid"], fg=T["text_dim"],
            font=self.F_CODE, relief=tk.FLAT, bd=0,
            selectbackground=T["bg_mid"],
            padx=4, pady=6
        )
        self._lnum.pack(side=tk.LEFT, fill=tk.Y)

        sb = tk.Scrollbar(inner, orient=tk.VERTICAL,
                          bg=T["bg_mid"], troughcolor=T["bg_dark"])
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor = tk.Text(
            inner,
            bg=T["bg_dark"], fg=T["text"],
            insertbackground=T["accent_hi"],
            font=self.F_CODE, relief=tk.FLAT, bd=0,
            padx=10, pady=6, undo=True,
            yscrollcommand=sb.set,
            wrap=tk.NONE,
            selectbackground=T["bg_light"],
            selectforeground=T["text"]
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.editor.yview)

        # ── Syntax highlight tags ──
        self.editor.tag_config("kw",   foreground=T["syn_kw"])
        self.editor.tag_config("dir",  foreground=T["syn_dir"])
        self.editor.tag_config("num",  foreground=T["syn_num"])
        self.editor.tag_config("str",  foreground=T["syn_str"])
        self.editor.tag_config("cmt",  foreground=T["syn_cmt"],
                               font=("Consolas", 12, "italic"))
        self.editor.tag_config("unit", foreground=T["syn_unit"])

        # ── Bindings ──
        self.editor.bind("<KeyRelease>", lambda _: (self._highlight(),
                                                     self._update_lnums()))
        self.editor.bind("<MouseWheel>",
                         lambda _: self._lnum.yview_moveto(
                             self.editor.yview()[0]))

        # ── RIGHT: Robot canvas ────────────────────────────────────────────
        cf = tk.Frame(pane, bg=T["bg_dark"])
        pane.add(cf, minsize=300)

        self._panel_title(cf, "🤖  Robot Simulator  —  Real-time Animation View")
        self.robot_canvas = RobotCanvas(cf)

    def _panel_title(self, parent, text: str):
        bar = tk.Frame(parent, bg=T["bg_light"], height=30)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text=f"  {text}",
                 bg=T["bg_light"], fg=T["text_muted"],
                 font=self.F_SMALL).pack(side=tk.LEFT, pady=5)

    # ══════════════════════════════════════════════════════════════════════════
    #  Console
    # ══════════════════════════════════════════════════════════════════════════

    def _build_console(self):
        tk.Frame(self.root, bg=T["border"], height=1).pack(fill=tk.X)

        cf = tk.Frame(self.root, bg=T["bg_mid"], height=145)
        cf.pack(fill=tk.X)
        cf.pack_propagate(False)

        # Title bar
        bar = tk.Frame(cf, bg=T["bg_light"], height=28)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text="  🖥  Output Console",
                 bg=T["bg_light"], fg=T["text_muted"],
                 font=self.F_SMALL).pack(side=tk.LEFT, pady=5)
        tk.Button(bar, text="Clear", bg=T["bg_light"], fg=T["text_muted"],
                  font=self.F_SMALL, relief=tk.FLAT, bd=0, padx=8,
                  cursor="hand2",
                  activebackground=T["bg_mid"], activeforeground=T["text"],
                  command=self._clear_console).pack(side=tk.RIGHT, pady=3, padx=4)

        # Console text area
        area = tk.Frame(cf, bg=T["bg_dark"])
        area.pack(fill=tk.BOTH, expand=True)

        csb = tk.Scrollbar(area, orient=tk.VERTICAL,
                           bg=T["bg_mid"], troughcolor=T["bg_dark"])
        csb.pack(side=tk.RIGHT, fill=tk.Y)

        self.console = tk.Text(
            area, bg=T["bg_dark"], fg=T["green"],
            insertbackground=T["green"],
            font=self.F_MONO, relief=tk.FLAT, bd=0,
            padx=10, pady=4, state=tk.DISABLED,
            yscrollcommand=csb.set, wrap=tk.WORD
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        csb.config(command=self.console.yview)

        # Console color tags
        self.console.tag_config("info",    foreground=T["text_muted"])
        self.console.tag_config("muted",   foreground=T["text_dim"])
        self.console.tag_config("success", foreground=T["green"])
        self.console.tag_config("error",   foreground=T["red"])
        self.console.tag_config("warn",    foreground=T["orange"])
        self.console.tag_config("cmd",     foreground=T["accent_hi"])
        self.console.tag_config("sep",     foreground=T["text_dim"])

    # ══════════════════════════════════════════════════════════════════════════
    #  Footer / toolbar
    # ══════════════════════════════════════════════════════════════════════════

    def _build_footer(self):
        tk.Frame(self.root, bg=T["border"], height=1).pack(fill=tk.X)

        foot = tk.Frame(self.root, bg=T["bg_mid"], height=52)
        foot.pack(fill=tk.X)
        foot.pack_propagate(False)

        # ── Left buttons ──────────────────────────────────────────────────
        lf = tk.Frame(foot, bg=T["bg_mid"])
        lf.pack(side=tk.LEFT, padx=14, pady=10)

        self.btn_run = self._btn(lf, "▶  Run",      T["accent"],    self._run)
        self.btn_run.pack(side=tk.LEFT, padx=3)

        self._btn(lf, "⟳  Reset",   T["bg_light"],  self._reset
                  ).pack(side=tk.LEFT, padx=3)

        self._btn(lf, "✕  Clear",   T["bg_light"],  self._clear_editor,
                  fg=T["text_muted"]).pack(side=tk.LEFT, padx=3)

        self.btn_example = self._btn(lf, "📋  Example", T["bg_light"],  self._load_example,
                                     fg=T["text_muted"])
        self.btn_example.pack(side=tk.LEFT, padx=3)

        # ── Right: About Us (bottom-right corner) ─────────────────────────
        rf = tk.Frame(foot, bg=T["bg_mid"])
        rf.pack(side=tk.RIGHT, padx=14, pady=10)

        about = tk.Button(
            rf, text="ℹ  About Us",
            bg=T["bg_light"], fg=T["text_muted"],
            font=self.F_SMALL, relief=tk.FLAT, bd=0,
            padx=14, pady=6, cursor="hand2",
            activebackground=T["border"],
            activeforeground=T["text"],
            command=self._show_about
        )
        about.pack()
        about.bind("<Enter>", lambda _: about.config(fg=T["accent_hi"]))
        about.bind("<Leave>", lambda _: about.config(fg=T["text_muted"]))

    def _btn(self, parent, text, bg, cmd, fg=None):
        """Create a flat, hover-aware button."""
        b = tk.Button(
            parent, text=text, bg=bg,
            fg=fg or T["text"],
            font=self.F_UI_B, relief=tk.FLAT, bd=0,
            padx=12, pady=5, cursor="hand2",
            activebackground=T["accent"],
            activeforeground="#ffffff",
            command=cmd
        )
        b.bind("<Enter>", lambda _: b.config(bg=T["accent_hi"]))
        b.bind("<Leave>", lambda _: b.config(bg=bg))
        return b

    # ══════════════════════════════════════════════════════════════════════════
    #  Actions
    # ══════════════════════════════════════════════════════════════════════════

    def _run(self):
        src = self.editor.get("1.0", tk.END).strip()
        if not src:
            self._log("  No code to run.", "warn")
            return

        # Clear old error highlights
        self.editor.tag_remove("err_line", "1.0", tk.END)

        self._log("─" * 50, "sep")
        self._log(f"  Compiler : {self.runner.get_mode()}", "info")

        commands, errors = self.runner.run(src)

        # Highlight error lines in editor and print in console
        if errors:
            self._log(f"\n  ❌ Compilation Errors ({len(errors)} found):", "error")
            for e in errors:
                self._log(f"    • {e}", "error")
                
                # Extract line number from "Line X" or "line X"
                m = re.search(r'line\s+(\d+)', e, re.IGNORECASE)
                if m:
                    err_lineno = m.group(1)
                    self.editor.tag_add("err_line", f"{err_lineno}.0", f"{err_lineno}.end")
            
            self.editor.tag_config("err_line", background="#3d1618")

        if not commands:
            self._log("\n  ❌ Compilation FAILED: No valid commands to execute.", "error")
            self._log("  Please correct the error(s) above and try again.\n", "warn")
            self._status(f"Compilation Failed ({len(errors)} error(s))", "error")
            return

        if errors:
            self._log(f"\n  ⚠  Parsed {len(commands)} valid command(s) with warnings.\n", "warn")
        else:
            self._log(f"  ✓  {len(commands)} command(s) successfully compiled.\n", "success")

        # Print command table
        for i, c in enumerate(commands, 1):
            t = c.get("type", "?")
            if t == "move":
                line = (f"  [{i:02d}]  move {c.get('direction'):8s} "
                        f"{c.get('value'):.0f} steps")
            elif t == "turn":
                line = (f"  [{i:02d}]  turn {c.get('direction'):5s} "
                        f"{c.get('value'):.0f}°")
            elif t == "speed":
                line = f"  [{i:02d}]  speed → {c.get('value'):.0f}"
            elif t == "stop":
                line = f"  [{i:02d}]  STOP"
            elif t == "ability":
                line = f"  [{i:02d}]  ability \"{c.get('extra')}\""
            else:
                line = f"  [{i:02d}]  {t}"
            self._log(line, "cmd")

        self._log("\n  Executing animation…", "info")
        self._status("Running animation…", "running")
        self.btn_run.config(state=tk.DISABLED)
        self.robot_canvas.execute_commands(commands, on_done=self._done)

    def _done(self):
        self._log("  ✓  Animation complete.\n", "success")
        self._status("Animation complete", "success")
        self.btn_run.config(state=tk.NORMAL)

    def _reset(self):
        self.robot_canvas.reset()
        self._log("─" * 50, "sep")
        self._log("  Robot reset to origin.\n", "info")
        self._status("Reset complete", "info")
        self.btn_run.config(state=tk.NORMAL)

    def _clear_editor(self):
        self.editor.delete("1.0", tk.END)
        self._update_lnums()

    def _load_example(self):
        examples_dir = os.path.join(_PROJ_ROOT, "examples")
        
        menu = tk.Menu(self.root, tearoff=0, bg=T["bg_mid"], fg=T["text"],
                       activebackground=T["accent"], activeforeground="#ffffff",
                       font=self.F_UI)
        
        examples_list = [
            ("🛡  1. Patrol Loop", "demo_patrol.rcl"),
            ("⚔  2. Combat Simulation", "combat_simulation.rcl"),
            ("🧩  3. Maze Navigator", "maze_navigator.rcl"),
            ("✨  4. Full Language & Aliases", "full_showcase.rcl"),
            ("⚠️  5. Error Handling Test", "error_demo.rcl"),
        ]

        def load_file(fname):
            fpath = os.path.join(examples_dir, fname)
            if os.path.isfile(fpath):
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
                self._editor_set(content)
                self._highlight()
                self._status(f"Loaded {fname}", "info")
                self._log(f"  Loaded example file: {fname}", "info")
            else:
                self._editor_set(EXAMPLE)
                self._highlight()

        for label, fname in examples_list:
            menu.add_command(label=label, command=lambda fn=fname: load_file(fn))

        # Popup menu under the button position
        try:
            x = self.btn_example.winfo_rootx()
            y = self.btn_example.winfo_rooty() - 130
            menu.tk_popup(x, y)
        except Exception:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _clear_console(self):
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)

    # ══════════════════════════════════════════════════════════════════════════
    #  About Us dialog
    # ══════════════════════════════════════════════════════════════════════════

    def _show_about(self):
        pop = tk.Toplevel(self.root)
        pop.title("About")
        pop.geometry("460x360")
        pop.resizable(False, False)
        pop.configure(bg=T["bg_mid"])
        pop.transient(self.root)
        pop.grab_set()

        # Center on parent
        self.root.update_idletasks()
        rx = self.root.winfo_x() + self.root.winfo_width()  // 2 - 230
        ry = self.root.winfo_y() + self.root.winfo_height() // 2 - 180
        pop.geometry(f"460x360+{rx}+{ry}")

        # Accent stripe
        tk.Frame(pop, bg=T["accent"], height=5).pack(fill=tk.X)

        body = tk.Frame(pop, bg=T["bg_mid"])
        body.pack(fill=tk.BOTH, expand=True, padx=36, pady=20)

        # Robot emoji
        tk.Label(body, text="🤖", bg=T["bg_mid"],
                 font=("Segoe UI Emoji", 44)).pack()

        # Project title
        tk.Label(body, text="Robot Command Simulator",
                 bg=T["bg_mid"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(8, 2))

        tk.Label(body, text="Compiler Design Course Project",
                 bg=T["bg_mid"], fg=T["text_muted"],
                 font=("Segoe UI", 10)).pack()

        # Separator
        tk.Frame(body, bg=T["border"], height=1).pack(fill=tk.X, pady=18)

        tk.Label(body, text="Developed by",
                 bg=T["bg_mid"], fg=T["text_muted"],
                 font=("Segoe UI", 9)).pack()

        # ── Developer name ──────────────────────────────────────────────────
        tk.Label(body,
                 text="Md. Zihad Hosain Siyam",
                 bg=T["bg_mid"], fg=T["accent_hi"],
                 font=("Segoe UI", 17, "bold")).pack(pady=6)

        # Tech stack badges
        badge_row = tk.Frame(body, bg=T["bg_mid"])
        badge_row.pack()
        for tech, color in [("Flex", T["green"]),
                             ("Bison", T["orange"]),
                             ("Python", T["accent_hi"]),
                             ("Tkinter", T["syn_unit"])]:
            tk.Label(badge_row, text=f" {tech} ",
                     bg=color + "22", fg=color,
                     font=("Segoe UI", 9, "bold"),
                     padx=6, pady=2,
                     relief=tk.FLAT, bd=0).pack(side=tk.LEFT, padx=3)

        # Close button
        close = tk.Button(
            body, text="  Close  ",
            bg=T["accent"], fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, bd=0, padx=24, pady=7,
            cursor="hand2",
            activebackground=T["accent_hi"],
            activeforeground="#ffffff",
            command=pop.destroy
        )
        close.pack(pady=(18, 0))

    # ══════════════════════════════════════════════════════════════════════════
    #  Syntax highlighting
    # ══════════════════════════════════════════════════════════════════════════

    def _highlight(self):
        content = self.editor.get("1.0", tk.END)

        # Remove all tags first
        for tag in ("kw", "dir", "num", "str", "cmt", "unit"):
            self.editor.tag_remove(tag, "1.0", tk.END)

        for lineno, line in enumerate(content.split("\n"), 1):
            # ── Comments (#...) — must be first to avoid highlighting inside them
            m = re.search(r'#.*$', line)
            if m:
                self.editor.tag_add("cmt",
                    f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")
                # Don't highlight anything inside a comment
                continue

            # ── String literals
            for m in re.finditer(r'"[^"]*"', line):
                self.editor.tag_add("str",
                    f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # ── Numbers
            for m in re.finditer(r'\b\d+(\.\d+)?\b', line):
                self.editor.tag_add("num",
                    f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # ── Units (before keywords so "steps" doesn't get re-colored)
            for u in SYN_UNITS:
                for m in re.finditer(rf'\b{u}\b', line, re.I):
                    self.editor.tag_add("unit",
                        f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # ── Keywords
            for kw in SYN_KEYWORDS:
                for m in re.finditer(rf'\b{kw}\b', line, re.I):
                    self.editor.tag_add("kw",
                        f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # ── Directions
            for d in SYN_DIRECTIONS:
                for m in re.finditer(rf'\b{d}\b', line, re.I):
                    self.editor.tag_add("dir",
                        f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

    # ══════════════════════════════════════════════════════════════════════════
    #  Editor utilities
    # ══════════════════════════════════════════════════════════════════════════

    def _editor_set(self, text: str):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", text)
        self._update_lnums()

    def _update_lnums(self):
        lines = self.editor.get("1.0", tk.END).count("\n")
        self._lnum.config(state=tk.NORMAL)
        self._lnum.delete("1.0", tk.END)
        for i in range(1, lines + 1):
            self._lnum.insert(tk.END, f"{i:>3}\n")
        self._lnum.config(state=tk.DISABLED)
        # Sync scroll
        self._lnum.yview_moveto(self.editor.yview()[0])

    # ══════════════════════════════════════════════════════════════════════════
    #  Console / status helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _log(self, msg: str, tag: str = "info"):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, msg + "\n", tag)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def _status(self, msg: str, level: str = "info"):
        colors = {
            "info"   : (T["text_muted"], T["accent"]),
            "success": (T["green"],      T["green"]),
            "error"  : (T["red"],        T["red"]),
            "running": (T["orange"],     T["orange"]),
        }
        fg_lbl, fg_dot = colors.get(level, (T["text_muted"], T["accent"]))
        self._status_lbl.config(text=msg, fg=fg_lbl)
        self._dot.config(fg=fg_dot)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App()
