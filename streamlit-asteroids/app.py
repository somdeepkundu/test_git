import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Abstract Asteroids",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """<style>
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0 !important; }
    </style>""",
    unsafe_allow_html=True,
)

ASSETS = Path(__file__).parent.parent / "abstract-asteroids" / "assets" / "graphics"

def _b64(name: str) -> str:
    data = (ASSETS / name).read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(data).decode()

SHIP = _b64("spaceship_full.svg")
AST1 = _b64("asteroid1.svg")
AST2 = _b64("asteroid2.svg")
SHOT = _b64("green_projectile.svg")
EXPL = _b64("explosion.svg")

_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
  <style>
    :root {
      --neon-cyan: #00fff5; --neon-pink: #ff006e;
      --neon-yellow: #ffd60a; --neon-green: #39ff14;
      --gamefield-w: 810px; --gamefield-h: 480px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      min-height: 100vh;
      background:
        radial-gradient(ellipse at 20% 10%, rgba(255,0,110,.15) 0%, transparent 40%),
        radial-gradient(ellipse at 80% 90%, rgba(0,255,245,.15) 0%, transparent 40%),
        radial-gradient(ellipse at center, #1a0033 0%, #000 100%);
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      font-family: 'Orbitron','Courier New',monospace;
      color: white; overflow: hidden; padding: 20px; gap: 15px;
    }
    body::before {
      content: ''; position: fixed; inset: 0;
      background-image:
        radial-gradient(2px 2px at 20% 30%, white, transparent),
        radial-gradient(1px 1px at 60% 70%, white, transparent),
        radial-gradient(1.5px 1.5px at 80% 10%, var(--neon-cyan), transparent),
        radial-gradient(1px 1px at 30% 80%, white, transparent),
        radial-gradient(2px 2px at 90% 60%, var(--neon-pink), transparent);
      background-size: 200px 200px,150px 150px,250px 250px,180px 180px,220px 220px;
      animation: twinkle 4s ease-in-out infinite alternate;
      pointer-events: none; z-index: -1;
    }
    @keyframes twinkle { from{opacity:.4} to{opacity:1} }

    #gamefield {
      position: relative;
      width: var(--gamefield-w); height: var(--gamefield-h);
      background: linear-gradient(180deg,#0a0e27 0%,#1a0033 50%,#0a0e27 100%);
      border: 2px solid var(--neon-cyan); border-radius: 12px; overflow: hidden;
      box-shadow: 0 0 40px rgba(0,255,245,.4), 0 0 80px rgba(255,0,110,.2),
                  inset 0 0 100px rgba(0,0,0,.6);
    }
    #gamefield::before {
      content: ''; position: absolute; inset: 0;
      background-image:
        radial-gradient(1px 1px at 25% 15%,white,transparent),
        radial-gradient(1px 1px at 75% 85%,white,transparent),
        radial-gradient(2px 2px at 40% 50%,rgba(0,255,245,.6),transparent),
        radial-gradient(1px 1px at 90% 30%,white,transparent),
        radial-gradient(1.5px 1.5px at 10% 90%,rgba(255,0,110,.6),transparent);
      background-size: 300px 300px;
      animation: drift 15s linear infinite; pointer-events: none;
    }
    @keyframes drift { from{background-position:0 0} to{background-position:0 300px} }

    .spaceship {
      position: absolute; width: 60px; height: 80px;
      background-image: url('__SHIP__');
      background-size: contain; background-repeat: no-repeat; background-position: center;
      filter: drop-shadow(0 0 10px rgba(0,255,245,.7)) drop-shadow(0 0 20px rgba(0,255,245,.3));
      z-index: 10;
    }
    .asteroid {
      position: absolute; width: 50px; height: 50px;
      background-size: contain; background-repeat: no-repeat; background-position: center;
      filter: drop-shadow(0 0 6px rgba(255,80,80,.4));
      animation: tumble 10s linear infinite;
    }
    @keyframes tumble { from{rotate:0deg} to{rotate:360deg} }
    .shot {
      position: absolute; width: 20px; height: 30px;
      background-image: url('__SHOT__');
      background-size: contain; background-repeat: no-repeat; background-position: center;
      filter: drop-shadow(0 0 8px rgba(57,255,20,.9)) drop-shadow(0 0 16px rgba(57,255,20,.5));
      z-index: 5;
    }

    #health {
      position: absolute; top: 18px; left: 50%; transform: translateX(-50%);
      width: 300px; height: 22px;
      background: rgba(0,0,0,.7); border: 2px solid var(--neon-cyan); border-radius: 12px;
      overflow: hidden; padding: 2px; z-index: 100;
      box-shadow: 0 0 12px rgba(0,255,245,.6), inset 0 0 8px rgba(0,0,0,.8);
    }
    #healthbar {
      height: 100%;
      background: linear-gradient(90deg,var(--neon-pink) 0%,#ff7b00 40%,var(--neon-yellow) 70%,var(--neon-green) 100%);
      background-size: 300px 100%; background-position: right;
      border-radius: 8px; transition: width .25s ease-out;
    }
    #score {
      position: absolute; top: 18px; right: 24px;
      font-size: 26px; font-weight: 900; font-style: italic;
      color: var(--neon-cyan);
      text-shadow: 0 0 8px var(--neon-cyan),0 0 18px var(--neon-cyan);
      letter-spacing: 2px; z-index: 100; text-transform: uppercase;
    }
    #score #number {
      color: white; margin-right: 6px;
      text-shadow: 0 0 8px white,0 0 18px var(--neon-pink),0 0 28px var(--neon-pink);
    }
    #gameover {
      position: absolute; inset: 0;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      gap: 14px; padding: 20px;
      background: radial-gradient(ellipse at center,rgba(255,0,110,.25) 0%,rgba(0,0,0,.92) 70%);
      z-index: 1000; text-align: center; backdrop-filter: blur(2px);
    }
    .gameover-title {
      color: var(--neon-pink); font-size: 46px; font-weight: 900;
      letter-spacing: 6px; text-transform: uppercase;
      text-shadow: 0 0 12px var(--neon-pink),0 0 30px var(--neon-pink),0 0 60px white;
      animation: gameover-pulse 1.6s ease-in-out infinite;
    }
    .gameover-credit {
      color: rgba(255,255,255,.92); font-size: 13px; font-weight: 700;
      letter-spacing: 1.5px; text-transform: uppercase;
      text-shadow: 0 0 8px rgba(0,255,245,.6);
    }
    .gameover-source {
      color: rgba(255,255,255,.5); font-size: 10px;
      font-style: italic; letter-spacing: 1px; max-width: 560px;
    }
    @keyframes gameover-pulse {
      0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.75;transform:scale(1.04)}
    }
    footer {
      font-size: 11px; color: rgba(255,255,255,.3);
      text-align: center; max-width: 810px;
    }
    footer a { color: rgba(0,255,245,.5); text-decoration: none; }

    /* ── Mobile on-screen controls ─────────────────────── */
    #mobile-controls {
      display: none;                      /* revealed by JS on touch devices */
      position: absolute;
      bottom: 14px; left: 0; right: 0;
      justify-content: space-between;
      align-items: flex-end;
      padding: 0 18px;
      z-index: 200;
    }
    #dpad {
      display: grid;
      grid-template-columns: repeat(3, 52px);
      grid-template-rows: repeat(3, 52px);
      gap: 5px;
    }
    #btn-up    { grid-column: 2; grid-row: 1; }
    #btn-left  { grid-column: 1; grid-row: 2; }
    #btn-right { grid-column: 3; grid-row: 2; }
    #btn-down  { grid-column: 2; grid-row: 3; }
    .ctrl-btn {
      width: 52px; height: 52px;
      background: rgba(0,255,245,.12);
      border: 2px solid rgba(0,255,245,.45);
      border-radius: 10px;
      color: var(--neon-cyan); font-size: 20px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
      user-select: none; touch-action: none;
      transition: background .08s;
    }
    .ctrl-btn:active { background: rgba(0,255,245,.38); }
    #btn-fire {
      width: 74px; height: 74px;
      border-radius: 50%;
      font-size: 12px; font-weight: 900; letter-spacing: 1px;
      background: rgba(255,0,110,.15);
      border: 2px solid rgba(255,0,110,.6);
      color: var(--neon-pink);
      font-family: 'Orbitron', monospace;
      text-shadow: 0 0 8px var(--neon-pink);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
      user-select: none; touch-action: none;
      margin-bottom: 14px;
      transition: background .08s;
    }
    #btn-fire:active { background: rgba(255,0,110,.42); }
  </style>
</head>
<body>
  <div id="gamefield">
    <div id="health"><div id="healthbar"></div></div>
    <div id="score"><span id="number">0</span> points</div>
    <div class="spaceship"></div>

    <!-- On-screen controls: shown only on touch devices via JS -->
    <div id="mobile-controls">
      <div id="dpad">
        <button id="btn-up"    class="ctrl-btn">&#9650;</button>
        <button id="btn-left"  class="ctrl-btn">&#9664;</button>
        <button id="btn-right" class="ctrl-btn">&#9654;</button>
        <button id="btn-down"  class="ctrl-btn">&#9660;</button>
      </div>
      <button id="btn-fire">FIRE</button>
    </div>
  </div>

  <footer>
    Graphics from FreePik:
    <a href="https://www.freepik.com/free-vector/asteroid-space-scene-background_5184427.htm">asteroids</a>,
    <a href="https://www.freepik.com/free-vector/futuristic-spaceship-collection-with-flat-design_2898815.htm">spaceship</a>
    &mdash; by upklyak on FreePik:
    <a href="https://www.freepik.com/free-vector/game-handgun-blaster-shoot-light-effect_133958192.htm">shots</a>,
    <a href="https://www.freepik.com/free-vector/cartoon-bomb-explosion-storyboard-animation_20902933.htm">explosion</a>
  </footer>

  <script>
    const ASTEROID_IMGS = ['__AST1__', '__AST2__'];

    window.addEventListener('load', start);

    function start() {
      document.body.setAttribute('tabindex', '0');
      document.body.focus();
      document.addEventListener('keydown', keypressHandler);
      document.addEventListener('keyup',   keypressHandler);
      document.addEventListener('click', () => document.body.focus());

      // Show touch controls automatically on touch-capable devices
      if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        setupMobileControls();
      }

      createAsteroids();
      requestAnimationFrame(tick);
    }

    // ── Keyboard ─────────────────────────────────────────
    function keypressHandler(event) {
      const value = event.type === 'keydown';
      const key = event.key;
      if (key === 'a' || key === 'ArrowLeft')  { controls.left  = value; event.preventDefault(); }
      if (key === 'w' || key === 'ArrowUp')    { controls.up    = value; event.preventDefault(); }
      if (key === 's' || key === 'ArrowDown')  { controls.down  = value; event.preventDefault(); }
      if (key === 'd' || key === 'ArrowRight') { controls.right = value; event.preventDefault(); }
      if (key === ' ' && event.type === 'keydown' && !controls.spaceHeld) {
        fireShot(); controls.spaceHeld = true; event.preventDefault();
      }
      if (key === ' ' && event.type === 'keyup') controls.spaceHeld = false;
    }

    // ── Mobile touch controls ────────────────────────────
    function setupMobileControls() {
      document.getElementById('mobile-controls').style.display = 'flex';

      const dirs = { 'btn-up':'up', 'btn-down':'down', 'btn-left':'left', 'btn-right':'right' };
      for (const [id, dir] of Object.entries(dirs)) {
        const btn = document.getElementById(id);
        btn.addEventListener('touchstart', e => { e.preventDefault(); controls[dir] = true;  }, { passive: false });
        btn.addEventListener('touchend',   e => { e.preventDefault(); controls[dir] = false; }, { passive: false });
        btn.addEventListener('touchcancel',() => { controls[dir] = false; });
        btn.addEventListener('mousedown',  () => controls[dir] = true);
        btn.addEventListener('mouseup',    () => controls[dir] = false);
        btn.addEventListener('mouseleave', () => controls[dir] = false);
      }

      const fire = document.getElementById('btn-fire');
      fire.addEventListener('touchstart', e => {
        e.preventDefault();
        if (!controls.spaceHeld) { fireShot(); controls.spaceHeld = true; }
      }, { passive: false });
      fire.addEventListener('touchend',    e => { e.preventDefault(); controls.spaceHeld = false; }, { passive: false });
      fire.addEventListener('touchcancel', () => { controls.spaceHeld = false; });
      fire.addEventListener('mousedown',   () => { if (!controls.spaceHeld) { fireShot(); controls.spaceHeld = true; } });
      fire.addEventListener('mouseup',     () => { controls.spaceHeld = false; });
    }

    const controls = { up:false, down:false, left:false, right:false, spaceHeld:false };
    let points = 0, gameOver = false;

    // ── Shots ────────────────────────────────────────────
    const shots = [];
    function fireShot() {
      const div = document.createElement('div');
      div.classList.add('shot');
      document.querySelector('#gamefield').insertAdjacentElement('beforeend', div);
      shots.push({ x: spaceship.x, y: spaceship.y - spaceship.h/2, w:20, h:30, s:400, visual:div });
    }
    function moveShots(delta) {
      for (let i = shots.length-1; i >= 0; i--) {
        shots[i].y -= shots[i].s * delta;
        if (shots[i].y < 0) removeShot(shots[i]);
      }
    }
    function removeShot(shot) {
      shot.visual.remove();
      shots.splice(shots.indexOf(shot), 1);
    }

    // ── Asteroids ────────────────────────────────────────
    const asteroids = [];
    function createAsteroids() {
      for (let i = 0; i < 10; i++) {
        const div = document.createElement('div');
        div.classList.add('asteroid');
        div.style.backgroundImage = `url('${ASTEROID_IMGS[Math.floor(Math.random()*ASTEROID_IMGS.length)]}')`;
        document.querySelector('#gamefield').insertAdjacentElement('beforeend', div);
        asteroids.push({ x: Math.floor(Math.random()*750), y:-30, w:50, h:50,
                         s: Math.random()*100+50, visual:div });
      }
    }
    function moveAsteroids(delta) {
      for (const a of asteroids) {
        a.y += a.s * delta;
        if (a.y > 450) resetAsteroid(a);
      }
    }
    function resetAsteroid(a) {
      a.y = -30; a.x = Math.floor(Math.random()*750); a.s = Math.random()*100+50;
    }

    // ── Spaceship ────────────────────────────────────────
    const spaceship = { x:380, y:370, s:300, w:60, h:80, hl:100 };
    function moveSpaceship(delta) {
      if (controls.left  && spaceship.x > spaceship.w/2) spaceship.x -= spaceship.s*delta;
      else if (controls.right && spaceship.x < 770)      spaceship.x += spaceship.s*delta;
      if (controls.up    && spaceship.y > spaceship.h/2) spaceship.y -= spaceship.s*delta;
      else if (controls.down  && spaceship.y < 410)      spaceship.y += spaceship.s*delta;
    }

    // ── Collision ────────────────────────────────────────
    function isColliding(a, b) {
      const dx = a.x-b.x, dy = a.y-b.y;
      return Math.sqrt(dx*dx+dy*dy) < (a.w/2+b.w/2);
    }

    // ── Game loop ────────────────────────────────────────
    let lastTime = 0;
    function tick(timestamp) {
      if (gameOver) return;
      requestAnimationFrame(tick);
      if (lastTime === 0) { lastTime = timestamp; return; }
      const delta = (timestamp - lastTime) / 1000;
      lastTime = timestamp;

      moveSpaceship(delta);
      moveAsteroids(delta);
      moveShots(delta);

      for (const a of asteroids) {
        if (isColliding(a, spaceship)) {
          a.s *= 0.95;
          spaceship.hl -= 20 * delta;
          if (spaceship.hl <= 0) { endGame(); return; }
        }
      }
      for (let i = shots.length-1; i >= 0; i--) {
        const shot = shots[i];
        for (const a of asteroids) {
          if (isColliding(shot, a)) {
            points += 10;
            resetAsteroid(a);
            removeShot(shot);
            break;
          }
        }
      }
      render();
    }

    function render() {
      const ship = document.querySelector('.spaceship');
      if (!ship) return;
      ship.style.translate = `${spaceship.x - spaceship.w/2}px ${spaceship.y - spaceship.h/2}px`;
      for (const a of asteroids)
        a.visual.style.translate = `${a.x - a.w/2}px ${a.y - a.h/2}px`;
      for (const s of shots)
        s.visual.style.translate = `${s.x - s.w/2}px ${s.y - s.h/2}px`;
      document.querySelector('#score #number').textContent = String(points).padStart(3,'0');
      document.querySelector('#healthbar').style.width = `${Math.max(spaceship.hl,0)}%`;
    }

    function endGame() {
      gameOver = true;
      const banner = document.createElement('div');
      banner.id = 'gameover';
      banner.innerHTML = `
        <div class="gameover-title">GAME OVER \u2014 ${points} points</div>
        <div class="gameover-credit">Developed by Somdeep Kundu \u00b7 @RuDRA Lab, C-TARA, IITB</div>
        <div class="gameover-source">learned from \u201cProblem Solving with Abstraction\u201d by Programming 2.0 (YouTube)</div>
      `;
      document.querySelector('#gamefield').appendChild(banner);
    }
  </script>
</body>
</html>
"""

html = (
    _TEMPLATE
    .replace("__SHIP__", SHIP)
    .replace("__AST1__", AST1)
    .replace("__AST2__", AST2)
    .replace("__SHOT__", SHOT)
    .replace("__EXPL__", EXPL)
)

st.components.v1.html(html, height=580, scrolling=False)
