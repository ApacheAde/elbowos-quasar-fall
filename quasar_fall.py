#!/usr/bin/env python3
"""Quasar Fall — neon gravity-pachinko arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/QUASAR_FALL_ElbowOS.mp4")
TITLE, HANDLE = "QUASAR FALL", "x.com/ElbowOS"

BG = (6, 18, 14)
INK = (10, 36, 28)
GOLD = (255, 196, 48)
WHITE = (246, 255, 240)
EMERALD = (40, 255, 150)
MAG = (255, 55, 140)
ORANGE = (255, 120, 36)
TEAL = (20, 230, 210)
LIME = (180, 255, 70)
WELL_COLS = [EMERALD, GOLD, MAG, ORANGE, TEAL, LIME, GOLD]
WELL_PTS = [10, 30, 80, 160, 80, 30, 10]


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font_lg = pygame.font.SysFont("DejaVu Sans", 58, bold=True)
        self.font = pygame.font.SysFont("DejaVu Sans", 38, bold=True)
        self.font_sm = pygame.font.SysFont("DejaVu Sans", 24)
        self.clock = pygame.time.Clock()
        self.score = self.t = self.combo = self.flash = 0
        self.orbs, self.sparks, self.rings, self.motes = [], [], [], []
        self.pegs = []
        self.aim = 0.0
        self.aim_v = 0.0
        self.drop_cd = 12
        self.left = 240
        self.right = W - 240
        self.top = 280
        self.bot = 1580
        self._build_pegs()
        self._build_wells()
        for _ in range(90):
            self.motes.append([
                random.randint(0, W), random.randint(0, H),
                random.uniform(0.3, 1.8), random.choice([EMERALD, TEAL, GOLD, MAG])
            ])

    def _build_pegs(self):
        self.pegs.clear()
        rows, cols0 = 9, 7
        gap_x, gap_y = 108, 118
        y0 = 430
        for r in range(rows):
            n = cols0 if r % 2 == 0 else cols0 - 1
            span = (n - 1) * gap_x
            x0 = W // 2 - span // 2
            for c in range(n):
                self.pegs.append([x0 + c * gap_x, y0 + r * gap_y, 16, random.choice(WELL_COLS)])

    def _build_wells(self):
        n = len(WELL_PTS)
        self.wells = []
        margin = 90
        ww = (W - 2 * margin) / n
        for i, pts in enumerate(WELL_PTS):
            x = margin + i * ww
            self.wells.append([x, self.bot, ww, 90, pts, WELL_COLS[i % len(WELL_COLS)]])

    def burst(self, x, y, col, n=8):
        for _ in range(n):
            a = random.uniform(0, 6.2832)
            sp = random.uniform(1.6, 9)
            self.sparks.append([x, y, math.cos(a) * sp, math.sin(a) * sp, 16, col])

    def spawn_orb(self, ang=None):
        if ang is None:
            ang = self.aim
        x = W // 2 + math.sin(ang) * 210
        y = self.top + 20
        spd = 11.5
        vx = math.sin(ang) * spd * 0.55
        vy = 6.2
        col = random.choice([GOLD, EMERALD, MAG, TEAL])
        self.orbs.append([x, y, vx, vy, 15, col])

    def autoplay(self):
        target = math.sin(self.t * 0.07) * 0.55 + math.sin(self.t * 0.031) * 0.25
        err = target - self.aim
        self.aim_v += err * 0.08
        self.aim_v *= 0.78
        self.aim = max(-0.85, min(0.85, self.aim + self.aim_v))

    def tick(self):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        self.drop_cd -= 1
        if self.drop_cd <= 0 and len(self.orbs) < 6:
            self.spawn_orb()
            self.drop_cd = 22 if self.t < 120 else 16
        g = 0.38
        keep = []
        for o in self.orbs:
            o[2] *= 0.999
            o[3] += g
            o[3] = min(o[3], 16)
            o[0] += o[2]
            o[1] += o[3]
            if o[0] < 70:
                o[0], o[2] = 70, abs(o[2]) * 0.86
            elif o[0] > W - 70:
                o[0], o[2] = W - 70, -abs(o[2]) * 0.86
            for p in self.pegs:
                dx, dy = o[0] - p[0], o[1] - p[1]
                d = math.hypot(dx, dy) or 1
                min_d = o[4] + p[2]
                if d < min_d:
                    nx, ny = dx / d, dy / d
                    o[0] = p[0] + nx * min_d
                    o[1] = p[1] + ny * min_d
                    vn = o[2] * nx + o[3] * ny
                    if vn < 0:
                        o[2] -= 1.72 * vn * nx
                        o[3] -= 1.72 * vn * ny
                    o[2] += random.uniform(-0.6, 0.6)
                    self.burst(o[0], o[1], p[3], 5)
                    self.combo += 1
                    self.score += 2
            scored = False
            if o[1] >= self.bot:
                for w in self.wells:
                    if w[0] <= o[0] <= w[0] + w[2]:
                        self.score += w[4] + self.combo * 2
                        self.flash = 8
                        self.burst(o[0], self.bot, w[5], 16)
                        self.rings.append([o[0], self.bot, 10, w[5]])
                        self.combo = 0
                        scored = True
                        break
                if not scored:
                    self.combo = 0
                continue
            if o[1] > H + 40:
                continue
            keep.append(o)
        self.orbs = keep
        for p in self.sparks:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.18
            p[4] -= 1
        self.sparks = [p for p in self.sparks if p[4] > 0]
        for r in self.rings:
            r[2] += 8
        self.rings = [r for r in self.rings if r[2] < 140]
        for m in self.motes:
            m[1] += m[2]
            if m[1] > H + 4:
                m[1] = -4
                m[0] = random.randint(0, W)

    def draw(self, surf):
        surf.fill(BG)
        for m in self.motes:
            pygame.draw.circle(surf, m[3], (int(m[0]), int(m[1])), 2)
        pygame.draw.rect(surf, INK, (40, 210, W - 80, self.bot - 180), border_radius=28)
        pygame.draw.rect(surf, (20, 70, 52), (40, 210, W - 80, self.bot - 180), 3, border_radius=28)
        lx = W // 2 + math.sin(self.aim) * 210
        ly = self.top
        pygame.draw.circle(surf, (30, 80, 60), (W // 2, ly), 48)
        pygame.draw.line(surf, GOLD, (W // 2, ly), (lx, ly + 70), 8)
        pygame.draw.circle(surf, ORANGE, (int(lx), int(ly + 70)), 16)
        pygame.draw.circle(surf, WHITE, (int(lx) - 4, int(ly + 64)), 5)
        pulse = 1.0 + 0.12 * math.sin(self.t * 0.16)
        for i, p in enumerate(self.pegs):
            pr = int(p[2] * pulse) if i % 3 == self.t // 8 % 3 else p[2]
            pygame.draw.circle(surf, p[3], (int(p[0]), int(p[1])), pr)
            pygame.draw.circle(surf, WHITE, (int(p[0] - 4), int(p[1] - 5)), 4)
        for w in self.wells:
            pygame.draw.rect(surf, w[5], (int(w[0]) + 4, int(w[1]), int(w[2]) - 8, int(w[3])), border_radius=10)
            pygame.draw.rect(surf, WHITE, (int(w[0]) + 4, int(w[1]), int(w[2]) - 8, int(w[3])), 2, border_radius=10)
            lab = self.font_sm.render(str(w[4]), True, BG)
            surf.blit(lab, lab.get_rect(center=(w[0] + w[2] / 2, w[1] + 44)))
        for o in self.orbs:
            pygame.draw.circle(surf, o[5], (int(o[0]), int(o[1])), int(o[4]))
            pygame.draw.circle(surf, WHITE, (int(o[0] - 4), int(o[1] - 5)), 5)
        for r in self.rings:
            pygame.draw.circle(surf, r[3], (int(r[0]), int(r[1])), int(r[2]), 3)
        for p in self.sparks:
            pygame.draw.circle(surf, p[5], (int(p[0]), int(p[1])), max(2, p[4] // 4))
        if self.flash:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((255, 210, 40, 36))
            surf.blit(ov, (0, 0))
        title = self.font_lg.render(TITLE, True, EMERALD)
        surf.blit(title, title.get_rect(center=(W // 2, 78)))
        sub = self.font_sm.render(HANDLE, True, MAG)
        surf.blit(sub, sub.get_rect(center=(W // 2, 136)))
        sc = self.font.render(f"SCORE  {self.score}", True, WHITE)
        cb = self.font_sm.render(f"CHAIN  x{self.combo}", True, GOLD)
        hint = self.font_sm.render("A / D aim   SPACE drop   R reset", True, TEAL)
        surf.blit(sc, sc.get_rect(center=(W // 2, H - 150)))
        surf.blit(cb, cb.get_rect(center=(W // 2, H - 96)))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 48)))

    def play_interactive(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        self.spawn_orb()
                    elif ev.key == pygame.K_r:
                        self.score = self.combo = 0
                        self.orbs.clear()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.aim = max(-0.85, self.aim - 0.05)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.aim = min(0.85, self.aim + 0.05)
            self.tick()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        canvas = pygame.Surface((W, H))
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(canvas)
                proc.stdin.write(pygame.image.tostring(canvas, "RGB"))
                if i % 30 == 0:
                    print(f"frame {i}/{frames}", flush=True)
        finally:
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "ignore")
            rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
