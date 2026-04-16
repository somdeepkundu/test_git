# Abstract Asteroids

A browser-based shoot'em'up game built with **vanilla HTML, CSS, and JavaScript** — no canvas, no frameworks, no dependencies. Dodge and destroy oncoming asteroids before they drain your health!

<p align="center">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
</p>

---

## Gameplay

<table>
  <tr>
    <td width="50%">
      <h3>Controls</h3>
      <table>
        <tr><td><kbd>W</kbd> / <kbd>Arrow Up</kbd></td><td>Move up</td></tr>
        <tr><td><kbd>S</kbd> / <kbd>Arrow Down</kbd></td><td>Move down</td></tr>
        <tr><td><kbd>A</kbd> / <kbd>Arrow Left</kbd></td><td>Move left</td></tr>
        <tr><td><kbd>D</kbd> / <kbd>Arrow Right</kbd></td><td>Move right</td></tr>
        <tr><td><kbd>Space</kbd></td><td>Fire shot</td></tr>
      </table>
    </td>
    <td width="50%">
      <h3>Objective</h3>
      <ul>
        <li>Pilot your spaceship to dodge incoming asteroids</li>
        <li>Shoot asteroids to destroy them and earn <strong>+10 points</strong> each</li>
        <li>Survive as long as possible — collisions drain your health bar</li>
        <li>Game ends when health reaches zero</li>
      </ul>
    </td>
  </tr>
</table>

---

## Features

- **Neon arcade theme** — synthwave-inspired CSS with glowing effects, animated starfield background, and tumbling asteroids
- **Smooth movement** — delta-time based physics for consistent speed across frame rates
- **Shooting mechanics** — fire green plasma bolts to destroy asteroids before they hit you
- **Collision detection** — circle-based distance calculations for spaceship-asteroid and shot-asteroid interactions
- **Health & scoring system** — gradient health bar and zero-padded score display
- **Game over screen** — dramatic overlay with final score and credits

---

## How to Run

No build tools or servers needed — just open `index.html` in your browser.

```bash
# Clone this repo
git clone https://github.com/somdeepkundu/test_git.git
cd test_git/abstract-asteroids

# Option 1: Open directly
open index.html          # macOS
start index.html         # Windows

# Option 2: Local server (optional)
python -m http.server 8000
# Then visit http://localhost:8000
```

---

## Project Structure

```
abstract-asteroids/
├── index.html                  # Game markup — gamefield, health bar, score
├── script.js                   # Game logic — movement, shooting, collisions, game loop
├── style.css                   # Neon arcade theme — starfield, glow effects, animations
└── assets/
    └── graphics/
        ├── spaceship_full.svg  # Player ship sprite
        ├── asteroid1.svg       # Asteroid variant 1
        ├── asteroid2.svg       # Asteroid variant 2
        ├── green_projectile.svg # Shot/laser sprite
        └── explosion.svg       # Explosion effect sprite
```

---

## Learning Journey

This project was built as a hands-on learning exercise following the **"Problem Solving with Abstraction"** tutorial series by [Programming 2.0](https://github.com/programming2point0/asteroids) on YouTube.

### Key concepts practiced:

| Concept | How it's applied |
|---|---|
| **Abstraction** | Game logic split into focused functions (`moveSpaceship`, `moveAsteroids`, `fireShot`, etc.) |
| **Game loop pattern** | `requestAnimationFrame` + delta-time for smooth, frame-rate-independent updates |
| **DOM manipulation** | Dynamic element creation/removal for shots and asteroids |
| **Collision detection** | Euclidean distance vs. combined radii for circle-based hit testing |
| **Event handling** | Keyboard input with keydown/keyup tracking and auto-repeat prevention |
| **Problem solving** | Implementing shooting mechanics — from firing to movement to collision response |

### Tutorial references:

- **Video**: [Problem Solving with Abstraction — Programming 2.0](https://youtu.be/nuRbPv6q2CI?si=9ytwtUVATuX2fqIh)
- **Source repo**: [programming2point0/asteroids](https://github.com/programming2point0/asteroids)

---

## Credits

- **Developed by**: Somdeep Kundu · [@RuDRA Lab](https://github.com/somdeepkundu), C-TARA, IIT Bombay
- **Tutorial by**: [Programming 2.0](https://www.youtube.com/@programming2point0) (YouTube)
- **Graphics**: Free assets from [FreePik](https://www.freepik.com/)
  - [Asteroids](https://www.freepik.com/free-vector/asteroid-space-scene-background_5184427.htm)
  - [Spaceship](https://www.freepik.com/free-vector/futuristic-spaceship-collection-with-flat-design_2898815.htm)
  - [Shots](https://www.freepik.com/free-vector/game-handgun-blaster-shoot-light-effect_133958192.htm) by upklyak
  - [Explosion](https://www.freepik.com/free-vector/cartoon-bomb-explosion-storyboard-animation_20902933.htm) by upklyak

---

<p align="center">
  <sub>Built with curiosity and code</sub>
</p>
