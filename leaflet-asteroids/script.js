// ─────────────────────────────────────────────────────
//  Leaflet Asteroids  —  fully self-contained build
//  All graphics are inline SVG data-URIs; no external
//  asset folder required. Drop the three files into any
//  GitHub Pages repo and it works immediately.
// ─────────────────────────────────────────────────────

const VERSION = "v2.0.0";

const HEALTH_SVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect width='24' height='24' rx='5' fill='%23001a00' opacity='0.7'/><path d='M19 10.5H13.5V5H10.5V10.5H5V13.5H10.5V19H13.5V13.5H19V10.5Z' fill='%2339ff14'/></svg>`;


// Asset paths (real SVG files from abstract-asteroids)
const ASSETS = {
  spaceship: 'assets/graphics/spaceship_full.svg',
  asteroid1: 'assets/graphics/asteroid1.svg',
  asteroid2: 'assets/graphics/asteroid2.svg',
  shot:      'assets/graphics/green_projectile.svg',
  explosion: 'assets/graphics/explosion.svg',
};

// Progressive difficulty levels
const LEVELS = [
  { minScore:   0, count:  3, speedMin:  50, speedMax: 100, label: 'LEVEL 1' },
  { minScore:  50, count:  5, speedMin:  65, speedMax: 130, label: 'LEVEL 2' },
  { minScore: 150, count:  7, speedMin:  80, speedMax: 160, label: 'LEVEL 3' },
  { minScore: 300, count:  9, speedMin:  95, speedMax: 195, label: 'LEVEL 4' },
  { minScore: 500, count: 12, speedMin: 115, speedMax: 225, label: 'LEVEL 5' },
  { minScore: 800, count: 15, speedMin: 135, speedMax: 260, label: 'LEVEL 6' },
];
let currentLevel = 0;
let map, W, H;
let playerName = "Player";

// ── Map initialisation ───────────────────────────────
function initMap() {
  W = window.innerWidth;
  H = window.innerHeight;

  map = L.map('map', {
    center: [19.133, 72.914],   // IIT Bombay, Mumbai
    zoom: 13,
    zoomControl: false,
    attributionControl: true,
    dragging: false,
    touchZoom: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution:
      '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> ' +
      '&copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20,
  }).addTo(map);
}

// Viewport pixel → Leaflet LatLng
function px(x, y) {
  return map.containerPointToLatLng(L.point(x, y));
}

// ── Keyboard controls ────────────────────────────────
const controls = { up: false, down: false, left: false, right: false, spaceHeld: false };

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

// ── Spaceship ────────────────────────────────────────
const ship = { x: 0, y: 0, s: 300, w: 60, h: 80, hl: 100 };
let shipMarker;

function initShip() {
  ship.x = W / 2;
  ship.y = H * 0.75;
  shipMarker = L.marker(px(ship.x, ship.y), {
    icon: L.divIcon({
      className: '',
      html: `<img src="${ASSETS.spaceship}" width="60" height="80" style="display:block;filter:drop-shadow(0 0 10px rgba(0,255,245,0.8)) drop-shadow(0 0 22px rgba(0,255,245,0.4))">`,
      iconSize: [60, 80],
      iconAnchor: [30, 40],
    }),
    interactive: false,
    zIndexOffset: 500,
  }).addTo(map);
}

function moveShip(dt) {
  if (controls.left  && ship.x > ship.w / 2)       ship.x -= ship.s * dt;
  if (controls.right && ship.x < W - ship.w / 2)   ship.x += ship.s * dt;
  if (controls.up    && ship.y > ship.h / 2)        ship.y -= ship.s * dt;
  if (controls.down  && ship.y < H - ship.h / 2)   ship.y += ship.s * dt;
}

// ── Asteroids ────────────────────────────────────────
const asteroids = [];

function spawnAsteroid() {
  const src = Math.random() < 0.5 ? ASSETS.asteroid1 : ASSETS.asteroid2;
  const lvl = LEVELS[currentLevel];
  const obj = {
    x: Math.random() * W,
    y: -30,
    w: 50, h: 50,
    s: Math.random() * (lvl.speedMax - lvl.speedMin) + lvl.speedMin,
  };
  obj.marker = L.marker(px(obj.x, obj.y), {
    icon: L.divIcon({
      className: '',
      html: `<img src="${src}" width="50" height="50" class="asteroid-spin" style="display:block;filter:drop-shadow(0 0 6px rgba(255,80,80,0.5))">`,
      iconSize: [50, 50],
      iconAnchor: [25, 25],
    }),
    interactive: false,
  }).addTo(map);
  asteroids.push(obj);
}

function moveAsteroids(dt) {
  for (const a of asteroids) {
    a.y += a.s * dt;
    if (a.y > H + 30) resetAsteroid(a);
  }
}

function resetAsteroid(a) {
  a.y = -30;
  a.x = Math.random() * W;
  const lvl = LEVELS[currentLevel];
  a.s = Math.random() * (lvl.speedMax - lvl.speedMin) + lvl.speedMin;
}

// ── Powerups ─────────────────────────────────────────
const powerups = [];

function spawnHealth() {
  if (gameOver) return;
  const obj = {
    x: Math.random() * (W - 60) + 30,
    y: -30,
    w: 34, h: 34,
    s: 80,
  };
  obj.marker = L.marker(px(obj.x, obj.y), {
    icon: L.divIcon({
      className: '',
      html: `<img src="${HEALTH_SVG}" width="34" height="34" class="health-pulse" style="display:block;filter:drop-shadow(0 0 10px rgba(57,255,20,0.9)) drop-shadow(0 0 20px rgba(57,255,20,0.5))">`,
      iconSize: [34, 34],
      iconAnchor: [17, 17],
    }),
    interactive: false,
    zIndexOffset: 400,
  }).addTo(map);
  powerups.push(obj);
}

function movePowerups(dt) {
  for (let i = powerups.length - 1; i >= 0; i--) {
    powerups[i].y += powerups[i].s * dt;
    if (powerups[i].y > H + 30) {
      map.removeLayer(powerups[i].marker);
      powerups.splice(i, 1);
    }
  }
}

// ── Shots ────────────────────────────────────────────
const shots = [];

function fireShot() {
  const obj = { x: ship.x, y: ship.y - ship.h / 2, w: 20, h: 30, s: 450 };
  obj.marker = L.marker(px(obj.x, obj.y), {
    icon: L.divIcon({
      className: '',
      html: `<img src="${ASSETS.shot}" width="20" height="30" style="display:block;filter:drop-shadow(0 0 8px rgba(57,255,20,0.95)) drop-shadow(0 0 18px rgba(57,255,20,0.5))">`,
      iconSize: [20, 30],
      iconAnchor: [10, 15],
    }),
    interactive: false,
    zIndexOffset: 200,
  }).addTo(map);
  shots.push(obj);
}

function moveShots(dt) {
  for (let i = shots.length - 1; i >= 0; i--) {
    shots[i].y -= shots[i].s * dt;
    if (shots[i].y < -30) removeShot(shots[i]);
  }
}

function removeShot(shot) {
  map.removeLayer(shot.marker);
  shots.splice(shots.indexOf(shot), 1);
}

// ── Explosion flash ──────────────────────────────────
function explodeAt(x, y) {
  const m = L.marker(px(x, y), {
    icon: L.divIcon({
      className: '',
      html: `<img src="${ASSETS.explosion}" width="60" height="60" class="explode-anim" style="display:block">`,
      iconSize: [60, 60],
      iconAnchor: [30, 30],
    }),
    interactive: false,
    zIndexOffset: 300,
  }).addTo(map);
  setTimeout(() => map.removeLayer(m), 500);
}

// ── Collision detection ──────────────────────────────
function isColliding(a, b) {
  const dx = a.x - b.x, dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy) < (a.w / 2 + b.w / 2);
}

// ── Render ───────────────────────────────────────────
function render() {
  shipMarker.setLatLng(px(ship.x, ship.y));
  for (const a of asteroids) a.marker.setLatLng(px(a.x, a.y));
  for (const s of shots)     s.marker.setLatLng(px(s.x, s.y));
  for (const p of powerups)  p.marker.setLatLng(px(p.x, p.y));

  document.getElementById('number').textContent = String(points).padStart(3, '0');
  document.getElementById('healthbar').style.width = `${Math.max(ship.hl, 0)}%`;
  document.getElementById('level-indicator').textContent = LEVELS[currentLevel].label;
}


// ── Difficulty progression ────────────────────────────
function getLevelIndex(score) {
  let idx = 0;
  for (let i = 0; i < LEVELS.length; i++) {
    if (score >= LEVELS[i].minScore) idx = i;
  }
  return idx;
}

function levelUp(newIdx) {
  currentLevel = newIdx;
  const lvl = LEVELS[currentLevel];
  while (asteroids.length < lvl.count) spawnAsteroid();
  showLevelBanner(lvl.label);
}

function showLevelBanner(label) {
  const el = document.createElement('div');
  el.className = 'level-banner';
  el.textContent = label;
  document.body.appendChild(el);
  setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 600);
  }, 1600);
}

// ── Game loop ────────────────────────────────────────
let points = 0, gameOver = false, lastTime = 0;

function tick(ts) {
  if (gameOver) return;
  requestAnimationFrame(tick);

  if (lastTime === 0) { lastTime = ts; return; }
  const dt = Math.min((ts - lastTime) / 1000, 0.1);
  lastTime = ts;

  moveShip(dt);
  moveAsteroids(dt);
  moveShots(dt);
  movePowerups(dt);

  // Check level up
  const newLevel = getLevelIndex(points);
  if (newLevel > currentLevel) levelUp(newLevel);

  // Powerup ↔ ship
  for (let i = powerups.length - 1; i >= 0; i--) {
    const p = powerups[i];
    if (isColliding(p, ship)) {
      ship.hl = Math.min(100, ship.hl + 40);   // restore 40 HP, cap at 100
      map.removeLayer(p.marker);
      powerups.splice(i, 1);
      break;
    }
  }

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
        explodeAt(a.x, a.y);
        resetAsteroid(a);
        removeShot(shot);
        break;
      }
    }
  }

  render();
}

// ── Game over ────────────────────────────────────────
function endGame() {
  gameOver = true;
  const div = document.createElement('div');
  div.id = 'gameover';
  div.innerHTML = `
    <div class="gameover-title">GAME OVER</div>
    <div class="gameover-player">${playerName} &mdash; ${points} pts</div>
    <div class="gameover-level">Reached ${LEVELS[currentLevel].label}</div>
    <div class="gameover-credit">Developed by Somdeep Kundu &middot; @RuDRA Lab, C-TARA, IITB</div>
    <div class="gameover-source">learned from &ldquo;Problem Solving with Abstraction&rdquo; by Programming 2.0 (YouTube)</div>
    <button class="restart-btn" onclick="location.reload()">PLAY AGAIN</button>
  `;
  document.body.appendChild(div);
}

// ── Entry point ──────────────────────────────────────
function startGame() {
  const input = document.getElementById('player-name');
  const name = input.value.trim();
  playerName = name.length > 0 ? name : "Player";

  const screen = document.getElementById('startscreen');
  screen.style.opacity = '0';
  screen.style.transition = 'opacity 0.4s ease';
  setTimeout(() => { screen.style.display = 'none'; }, 400);

  document.addEventListener('keydown', keypressHandler);
  document.addEventListener('keyup',   keypressHandler);

  initMap();
  map.whenReady(() => {
    initShip();
    for (let i = 0; i < LEVELS[0].count; i++) spawnAsteroid();
    setInterval(spawnHealth, 15000);
    requestAnimationFrame(tick);
  });
}

window.addEventListener('load', () => {
  document.getElementById('version').textContent = VERSION;
  document.getElementById('start-version').textContent = VERSION;

  const btn = document.getElementById('start-btn');
  const input = document.getElementById('player-name');

  btn.addEventListener('click', startGame);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') startGame();
  });

  input.focus();

  window.addEventListener('resize', () => {
    W = window.innerWidth;
    H = window.innerHeight;
    if (map) map.invalidateSize();
  });
});
