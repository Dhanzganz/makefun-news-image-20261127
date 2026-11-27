[![make.fun](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/Dhanzganz/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/Dhanzganz/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

# The World Today — Friday 27 November 2026

A program that draws a newspaper front page summing up the world news of
Friday 27 November 2026 and writes it to `/output/entry.png`.

## The day's news

- **Lead — Kuwait:** Two Italian technicians were killed when a drone hit a
  facility in Kuwait. Rome blamed Iran; Tehran denied any role.
- **United States:** A nor'easter battered the East Coast on Thanksgiving,
  leaving 800,000 without power. The 100th Macy's Thanksgiving Day Parade
  was moved to Saturday — the first postponement in its 100-year history.
- **Europe:** EU leaders in Brussels stayed divided over a €45bn loan for
  Ukraine in 2027. Four states resist paying; Germany wants all 27 to
  share the cost.
- **Middle East:** Hamas weighed its response after Israeli strikes killed
  10 people in Gaza.
- **Also today:** UK net migration at its lowest since 1997; Gukesh draws
  Game 3 of the World Chess Championship; a refinery blast in Bangkok hurts
  nine; a tanker sinks off Spain, one dead.

Sources: BBC, Reuters, The New York Times, USA TODAY — 27 November 2026.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no network.
It draws the whole front page itself: its own 5×7 bitmap font, its own
vector shapes (rects, circles, lines, polygons, stars) and its own PNG
encoder (zlib + struct). All content is baked in as literals. The program
is deterministic: two runs write byte-identical output.

## Run

```sh
python3 main.py
# writes /output/entry.png (1024x1024, ~23 KB)
```

## License

MIT — see [LICENSE](LICENSE).
