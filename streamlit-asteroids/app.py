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

# ── HTML template ──────────────────────────────────────────────────────────────
# Use __PLACEHOLDERS__ for SVG data URIs (avoids Python f-string brace conflicts).
# All ${...} inside <script> are plain JS template literals, not Python.
# ──────────────────────────────────────────────────────────────────────────────
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

    /* ── Game field ─────────────────────────────────────── */
    #gamefield {
      position: relative;
      width: 810px; height: 480px;
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

    /* ── Start screen ───────────────────────────────────── */
    #start-screen {
      position: absolute; inset: 0; z-index: 500;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 18px;
      background: radial-gradient(ellipse at center,
        rgba(26,0,51,.97) 0%, rgba(0,0,0,.98) 100%);
    }
    .ss-title {
      font-size: 40px; font-weight: 900; letter-spacing: 8px;
      text-align: center; line-height: 1.15;
      color: var(--neon-cyan);
      text-shadow: 0 0 18px var(--neon-cyan), 0 0 36px var(--neon-cyan);
      animation: title-pulse 2.2s ease-in-out infinite alternate;
    }
    @keyframes title-pulse {
      from { text-shadow: 0 0 18px var(--neon-cyan); }
      to   { text-shadow: 0 0 36px var(--neon-cyan), 0 0 70px var(--neon-pink); }
    }
    .ss-sub {
      font-size: 12px; letter-spacing: 3px; color: rgba(255,255,255,.5);
      text-transform: uppercase;
    }
    #name-input {
      width: 280px; padding: 12px 20px;
      background: rgba(0,255,245,.07);
      border: 2px solid rgba(0,255,245,.5); border-radius: 8px;
      color: white; font-family: 'Orbitron', monospace;
      font-size: 17px; font-weight: 700; letter-spacing: 3px;
      text-align: center; text-transform: uppercase; outline: none;
      box-shadow: 0 0 12px rgba(0,255,245,.2);
      transition: border-color .15s, box-shadow .15s;
    }
    #name-input::placeholder { color: rgba(0,255,245,.3); }
    #name-input:focus {
      border-color: var(--neon-cyan);
      box-shadow: 0 0 22px rgba(0,255,245,.45);
    }
    #launch-btn {
      padding: 13px 42px;
      background: rgba(0,255,245,.1);
      border: 2px solid var(--neon-cyan); border-radius: 10px;
      color: var(--neon-cyan); font-family: 'Orbitron', monospace;
      font-size: 17px; font-weight: 900; letter-spacing: 4px;
      text-shadow: 0 0 8px var(--neon-cyan);
      box-shadow: 0 0 18px rgba(0,255,245,.25);
      cursor: pointer; -webkit-tap-highlight-color: transparent;
      transition: background .15s, box-shadow .15s, transform .1s;
    }
    #launch-btn:hover  { background: rgba(0,255,245,.22); box-shadow: 0 0 28px rgba(0,255,245,.5); }
    #launch-btn:active { transform: scale(.97); }
    .ss-hint {
      font-size: 10px; letter-spacing: 2px;
      color: rgba(255,255,255,.25); text-transform: uppercase;
    }

    /* ── Game objects ───────────────────────────────────── */
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

    /* ── HUD ────────────────────────────────────────────── */
    #health {
      position: absolute; top: 18px; left: 50%; transform: translateX(-50%);
      width: 300px; height: 22px;
      background: rgba(0,0,0,.7); border: 2px solid var(--neon-cyan); border-radius: 12px;
      overflow: hidden; padding: 2px; z-index: 100;
      box-shadow: 0 0 12px rgba(0,255,245,.6), inset 0 0 8px rgba(0,0,0,.8);
    }
    #healthbar {
      height: 100%;
      background: linear-gradient(90deg,
        var(--neon-pink) 0%, #ff7b00 40%, var(--neon-yellow) 70%, var(--neon-green) 100%);
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

    /* ── Game over ──────────────────────────────────────── */
    #gameover {
      position: absolute; inset: 0; z-index: 1000;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 12px; padding: 20px;
      background: radial-gradient(ellipse at center,
        rgba(255,0,110,.25) 0%, rgba(0,0,0,.92) 70%);
      text-align: center; backdrop-filter: blur(2px);
    }
    .gameover-title {
      color: var(--neon-pink); font-size: 46px; font-weight: 900;
      letter-spacing: 6px; text-transform: uppercase;
      text-shadow: 0 0 12px var(--neon-pink),0 0 30px var(--neon-pink),0 0 60px white;
      animation: go-pulse 1.6s ease-in-out infinite;
    }
    .gameover-pilot {
      color: white; font-size: 20px; font-weight: 700; letter-spacing: 3px;
      text-shadow: 0 0 10px white, 0 0 22px var(--neon-cyan);
    }
    .gameover-credit {
      color: rgba(255,255,255,.85); font-size: 12px; font-weight: 700;
      letter-spacing: 1.5px; text-transform: uppercase;
      text-shadow: 0 0 8px rgba(0,255,245,.6);
    }
    .gameover-source {
      color: rgba(255,255,255,.45); font-size: 10px;
      font-style: italic; letter-spacing: 1px; max-width: 540px;
    }
    .play-again-btn {
      margin-top: 6px; padding: 10px 30px;
      background: rgba(0,255,245,.1);
      border: 2px solid var(--neon-cyan); border-radius: 8px;
      color: var(--neon-cyan); font-family: 'Orbitron', monospace;
      font-size: 13px; font-weight: 700; letter-spacing: 2px;
      cursor: pointer; -webkit-tap-highlight-color: transparent;
      transition: background .15s;
    }
    .play-again-btn:hover, .play-again-btn:active { background: rgba(0,255,245,.26); }
    @keyframes go-pulse {
      0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.75;transform:scale(1.04)}
    }

    /* ── Mobile controls ────────────────────────────────── */
    #mobile-controls {
      display: none;
      position: absolute; bottom: 14px; left: 0; right: 0;
      justify-content: space-between; align-items: flex-end;
      padding: 0 18px; z-index: 200;
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
      background: rgba(0,255,245,.12); border: 2px solid rgba(0,255,245,.45);
      border-radius: 10px; color: var(--neon-cyan); font-size: 20px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; -webkit-tap-highlight-color: transparent;
      user-select: none; touch-action: none; transition: background .08s;
    }
    .ctrl-btn:active { background: rgba(0,255,245,.38); }
    #btn-fire {
      width: 74px; height: 74px; border-radius: 50%;
      font-size: 12px; font-weight: 900; letter-spacing: 1px;
      background: rgba(255,0,110,.15); border: 2px solid rgba(255,0,110,.6);
      color: var(--neon-pink); font-family: 'Orbitron', monospace;
      text-shadow: 0 0 8px var(--neon-pink);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; -webkit-tap-highlight-color: transparent;
      user-select: none; touch-action: none;
      margin-bottom: 14px; transition: background .08s;
    }
    #btn-fire:active { background: rgba(255,0,110,.42); }

    footer {
      font-size: 11px; color: rgba(255,255,255,.3);
      text-align: center; max-width: 810px;
    }
    footer a { color: rgba(0,255,245,.5); text-decoration: none; }
  </style>
</head>
<body>
  <div id="gamefield">

    <!-- ① Start screen -->
    <div id="start-screen">
      <h1 class="ss-title">ABSTRACT<br>ASTEROIDS</h1>
      <p class="ss-sub">Enter your callsign</p>
      <input id="name-input" type="text" placeholder="PILOT NAME"
             maxlength="16" autocomplete="off" spellcheck="false">
      <button id="launch-btn">&#9654; LAUNCH</button>
      <p class="ss-hint">WASD / Arrows &middot; Space to fire</p>
    </div>

    <!-- ② HUD (rendered under start screen, visible after launch) -->
    <div id="health"><div id="healthbar"></div></div>
    <div id="score"><span id="number">000</span> pts</div>
    <div class="spaceship"></div>

    <!-- ③ Mobile controls (injected after launch on touch devices) -->
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
    &mdash; by upklyak:
    <a href="https://www.freepik.com/free-vector/game-handgun-blaster-shoot-light-effect_133958192.htm">shots</a>,
    <a href="https://www.freepik.com/free-vector/cartoon-bomb-explosion-storyboard-animation_20902933.htm">explosion</a>
  </footer>

  <script>
    const ASTEROID_IMGS = ['__AST1__', '__AST2__'];

    // ── Player state ──────────────────────────────────────
    let playerName = '';

    // ── Difficulty / pressure system ──────────────────────
    // pressure: 0-100 drives all difficulty parameters.
    // It rises slowly over time, but faster when the player is
    // killing asteroids quickly (rolling 5-second kill rate).
    let pressure    = 0;
    let recentKills = [];   // timestamps (ms) of recent kills
    let lastSpawnTs = 0;    // throttle new-asteroid spawning

    function killRate() {
      const now = performance.now();
      recentKills = recentKills.filter(t => now - t < 5000);
      return recentKills.length / 5;   // kills per second
    }

    function updatePressure(dt) {
      // base 0.5 /s  +  up to ~4 /s when killing fast
      pressure = Math.min(pressure + (0.5 + killRate() * 2) * dt, 100);
    }

    function targetCount() {
      // 3 asteroids at pressure=0 → 12 at pressure=100
      return Math.floor(3 + (pressure / 100) * 9);
    }

    function freshSpeed() {
      // 50 px/s at pressure=0 → 160 px/s at pressure=100, ±25% variance
      const base = 50 + (pressure / 100) * 110;
      return base * (0.75 + Math.random() * 0.5);
    }

    // ── Controls ──────────────────────────────────────────
    const controls = { up:false, down:false, left:false, right:false, spaceHeld:false };

    function keypressHandler(e) {
      const v = e.type === 'keydown';
      if (e.key === 'a' || e.key === 'ArrowLeft')  { controls.left  = v; e.preventDefault(); }
      if (e.key === 'w' || e.key === 'ArrowUp')    { controls.up    = v; e.preventDefault(); }
      if (e.key === 's' || e.key === 'ArrowDown')  { controls.down  = v; e.preventDefault(); }
      if (e.key === 'd' || e.key === 'ArrowRight') { controls.right = v; e.preventDefault(); }
      if (e.key === ' ') {
        e.preventDefault();
        if (v && !controls.spaceHeld) { fireShot(); controls.spaceHeld = true; }
        if (!v) controls.spaceHeld = false;
      }
    }

    function setupMobileControls() {
      document.getElementById('mobile-controls').style.display = 'flex';
      const dirs = { 'btn-up':'up', 'btn-down':'down', 'btn-left':'left', 'btn-right':'right' };
      for (const [id, dir] of Object.entries(dirs)) {
        const btn = document.getElementById(id);
        btn.addEventListener('touchstart', e => { e.preventDefault(); controls[dir] = true;  }, { passive:false });
        btn.addEventListener('touchend',   e => { e.preventDefault(); controls[dir] = false; }, { passive:false });
        btn.addEventListener('touchcancel',() => { controls[dir] = false; });
        btn.addEventListener('mousedown',  () => controls[dir] = true);
        btn.addEventListener('mouseup',    () => controls[dir] = false);
        btn.addEventListener('mouseleave', () => controls[dir] = false);
      }
      const fire = document.getElementById('btn-fire');
      fire.addEventListener('touchstart', e => {
        e.preventDefault();
        if (!controls.spaceHeld) { fireShot(); controls.spaceHeld = true; }
      }, { passive:false });
      fire.addEventListener('touchend',    e => { e.preventDefault(); controls.spaceHeld = false; }, { passive:false });
      fire.addEventListener('touchcancel', () => { controls.spaceHeld = false; });
      fire.addEventListener('mousedown',   () => { if (!controls.spaceHeld) { fireShot(); controls.spaceHeld = true; } });
      fire.addEventListener('mouseup',     () => { controls.spaceHeld = false; });
    }

    // ── Shots ─────────────────────────────────────────────
    const shots = [];

    function fireShot() {
      const div = document.createElement('div');
      div.classList.add('shot');
      document.getElementById('gamefield').appendChild(div);
      shots.push({ x: ship.x, y: ship.y - ship.h/2, w:20, h:30, s:420, visual:div });
    }
    function moveShots(dt) {
      for (let i = shots.length-1; i >= 0; i--) {
        shots[i].y -= shots[i].s * dt;
        if (shots[i].y < -30) removeShot(shots[i]);
      }
    }
    function removeShot(shot) {
      shot.visual.remove();
      shots.splice(shots.indexOf(shot), 1);
    }

    // ── Asteroids ─────────────────────────────────────────
    const asteroids = [];

    function addAsteroid() {
      const img = ASTEROID_IMGS[Math.floor(Math.random() * ASTEROID_IMGS.length)];
      const div = document.createElement('div');
      div.classList.add('asteroid');
      div.style.backgroundImage = `url('${img}')`;
      document.getElementById('gamefield').appendChild(div);
      asteroids.push({
        x: Math.random() * 750, y: -30,
        w: 50, h: 50, s: freshSpeed(), visual: div
      });
    }

    function moveAsteroids(dt) {
      for (const a of asteroids) {
        a.y += a.s * dt;
        if (a.y > 480) resetAsteroid(a);
      }
    }

    function resetAsteroid(a) {
      a.y = -30;
      a.x = Math.random() * 750;
      a.s = freshSpeed();   // picks up current difficulty
    }

    // ── Spaceship ─────────────────────────────────────────
    const ship = { x:380, y:370, s:300, w:60, h:80, hl:100 };

    function moveShip(dt) {
      if (controls.left  && ship.x > ship.w/2)       ship.x -= ship.s * dt;
      else if (controls.right && ship.x < 770)        ship.x += ship.s * dt;
      if (controls.up    && ship.y > ship.h/2)        ship.y -= ship.s * dt;
      else if (controls.down  && ship.y < 420)        ship.y += ship.s * dt;
    }

    // ── Collision ─────────────────────────────────────────
    function isColliding(a, b) {
      const dx = a.x - b.x, dy = a.y - b.y;
      return Math.sqrt(dx*dx + dy*dy) < (a.w/2 + b.w/2);
    }

    // ── Render ────────────────────────────────────────────
    function render() {
      const shipEl = document.querySelector('.spaceship');
      if (!shipEl) return;
      shipEl.style.translate = `${ship.x - ship.w/2}px ${ship.y - ship.h/2}px`;
      for (const a of asteroids)
        a.visual.style.translate = `${a.x - a.w/2}px ${a.y - a.h/2}px`;
      for (const s of shots)
        s.visual.style.translate = `${s.x - s.w/2}px ${s.y - s.h/2}px`;
      document.getElementById('number').textContent = String(points).padStart(3, '0');
      document.getElementById('healthbar').style.width = `${Math.max(ship.hl, 0)}%`;
    }

    // ── Game loop ─────────────────────────────────────────
    let points = 0, gameOver = false, lastTime = 0;

    function tick(ts) {
      if (gameOver) return;
      requestAnimationFrame(tick);
      if (lastTime === 0) { lastTime = ts; return; }
      const dt = Math.min((ts - lastTime) / 1000, 0.1);
      lastTime = ts;

      // Difficulty: grow pressure, then maybe add a new asteroid
      updatePressure(dt);
      if (asteroids.length < targetCount() && ts - lastSpawnTs > 900) {
        addAsteroid();
        lastSpawnTs = ts;
      }

      moveShip(dt);
      moveAsteroids(dt);
      moveShots(dt);

      // Asteroid ↔ ship
      for (const a of asteroids) {
        if (isColliding(a, ship)) {
          a.s *= 0.95;
          ship.hl -= 20 * dt;
          if (ship.hl <= 0) { endGame(); return; }
        }
      }

      // Shot ↔ asteroid
      for (let i = shots.length - 1; i >= 0; i--) {
        const shot = shots[i];
        for (const a of asteroids) {
          if (isColliding(shot, a)) {
            points += 10;
            recentKills.push(ts);   // register kill for pressure calc
            resetAsteroid(a);
            removeShot(shot);
            break;
          }
        }
      }

      render();
    }

    // ── Game over ─────────────────────────────────────────
    function endGame() {
      gameOver = true;
      const div = document.createElement('div');
      div.id = 'gameover';
      div.innerHTML =
        '<div class="gameover-title">GAME OVER</div>' +
        '<div class="gameover-pilot">' + playerName + ' &mdash; ' + points + ' PTS</div>' +
        '<div class="gameover-credit">Developed by Somdeep Kundu &middot; @RuDRA Lab, C-TARA, IITB</div>' +
        '<div class="gameover-source">learned from &ldquo;Problem Solving with Abstraction&rdquo; by Programming 2.0 (YouTube)</div>' +
        '<button class="play-again-btn" onclick="location.reload()">&#8635; PLAY AGAIN</button>';
      document.getElementById('gamefield').appendChild(div);
    }

    // ── Start screen logic ────────────────────────────────
    function launchGame() {
      const input = document.getElementById('name-input');
      playerName = input.value.trim().toUpperCase() || 'PILOT';
      try { localStorage.setItem('aa-player', playerName); } catch(e) {}

      document.getElementById('start-screen').style.display = 'none';

      if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        setupMobileControls();
      }

      // Seed 3 asteroids at low speed to ease the player in
      for (let i = 0; i < 3; i++) addAsteroid();
      requestAnimationFrame(tick);
    }

    window.addEventListener('load', () => {
      // Pre-fill name from last session
      try {
        const saved = localStorage.getItem('aa-player');
        if (saved) document.getElementById('name-input').value = saved;
      } catch(e) {}

      document.getElementById('launch-btn').addEventListener('click', launchGame);
      document.getElementById('name-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') launchGame();
      });

      document.body.setAttribute('tabindex', '0');
      document.addEventListener('keydown', keypressHandler);
      document.addEventListener('keyup',   keypressHandler);
      document.addEventListener('click',   () => document.body.focus());
    });
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
