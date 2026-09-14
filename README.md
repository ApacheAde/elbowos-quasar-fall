# Quasar Fall

Full-colour Python 3 neon gravity-pachinko arcade for **ElbowOS**.

Aim the launcher, drop glowing orbs, bounce them through a field of neon pegs, and land in the high-value wells.

- Featured: https://x.com/ElbowOS
- Reel (9:16 MP4): https://drive.google.com/file/d/1E6UADJvHmUR0zTwgmjXfWaEPY4fGv8AY/view?usp=drivesdk

## Play

```bash
python3 -m pip install -r requirements.txt
python3 quasar_fall.py --play
```

Controls: **A / D** or arrows aim · **SPACE** drop · **R** reset · **ESC** quit

## Record a 15s 1080×1920 reel

```bash
python3 quasar_fall.py --record
```

Writes `QUASAR_FALL_ElbowOS.mp4` (override with `ELBOWOS_MP4`). Uses a dummy SDL driver so it works headless.
