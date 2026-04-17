// ─────────────────────────────────────────────────────
//  Leaflet Asteroids  —  fully self-contained build
//  All graphics are inline SVG data-URIs; no external
//  asset folder required. Drop the three files into any
//  GitHub Pages repo and it works immediately.
// ─────────────────────────────────────────────────────

const VERSION = "v1.1.13";

// ── Inline SVG assets (no external files needed) ─────
const SPACESHIP_SVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 80'><defs><radialGradient id='eng' cx='50%25' cy='80%25' r='50%25'><stop offset='0%25' stop-color='%23ffd60a'/><stop offset='100%25' stop-color='%23ff7b00' stop-opacity='0'/></radialGradient></defs><polygon points='30,4 8,62 30,50 52,62' fill='%2300fff5' opacity='0.95'/><polygon points='8,62 0,76 20,58' fill='%23ff006e'/><polygon points='52,62 60,76 40,58' fill='%23ff006e'/><ellipse cx='30' cy='64' rx='12' ry='8' fill='url(%23eng)'/><circle cx='30' cy='28' r='6' fill='%23ffffff' opacity='0.18'/><line x1='30' y1='8' x2='30' y2='50' stroke='%23ffffff' stroke-width='1' opacity='0.25'/></svg>`;

const ASTEROID_SVGS = [
  `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 50 50'><polygon points='25,2 40,7 48,20 44,38 28,48 10,46 2,30 6,12 18,4' fill='%23796045' stroke='%23b08a55' stroke-width='1.5'/><circle cx='16' cy='15' r='4.5' fill='%234a3520' opacity='0.75'/><circle cx='34' cy='28' r='3' fill='%234a3520' opacity='0.75'/><circle cx='22' cy='36' r='2' fill='%234a3520' opacity='0.6'/><circle cx='38' cy='14' r='2.5' fill='%234a3520' opacity='0.5'/></svg>`,
  `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 50 50'><polygon points='26,2 44,10 48,28 38,46 18,48 4,36 4,18 16,6' fill='%23625040' stroke='%23988060' stroke-width='1.5'/><circle cx='20' cy='18' r='5' fill='%23382810' opacity='0.7'/><circle cx='34' cy='22' r='3.5' fill='%23382810' opacity='0.65'/><circle cx='26' cy='38' r='2.5' fill='%23382810' opacity='0.6'/><circle cx='12' cy='32' r='2' fill='%23382810' opacity='0.5'/></svg>`,
];

const SHOT_SVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 30'><defs><radialGradient id='sg' cx='50%25' cy='40%25' r='60%25'><stop offset='0%25' stop-color='%23ffffff'/><stop offset='40%25' stop-color='%2339ff14'/><stop offset='100%25' stop-color='%2339ff14' stop-opacity='0.2'/></radialGradient></defs><ellipse cx='10' cy='15' rx='5' ry='13' fill='url(%23sg)'/></svg>`;

const EXPLOSION_SVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><circle cx='30' cy='30' r='28' fill='%23ff7b00' opacity='0.7'/><circle cx='30' cy='30' r='18' fill='%23ffd60a' opacity='0.9'/><circle cx='30' cy='30' r='9' fill='%23ffffff' opacity='0.95'/><polygon points='30,0 34,24 58,30 34,36 30,60 26,36 2,30 26,24' fill='%23ff006e' opacity='0.55'/></svg>`;

const HEALTH_SVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect width='24' height='24' rx='5' fill='%23001a00' opacity='0.7'/><path d='M19 10.5H13.5V5H10.5V10.5H5V13.5H10.5V19H13.5V13.5H19V10.5Z' fill='%2339ff14'/></svg>`;

let map, W, H;

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
      html: `<img src="${SPACESHIP_SVG}" width="60" height="80" style="display:block;filter:drop-shadow(0 0 10px rgba(0,255,245,0.8)) drop-shadow(0 0 22px rgba(0,255,245,0.4))">`,
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
  const svgSrc = ASTEROID_SVGS[Math.floor(Math.random() * ASTEROID_SVGS.length)];
  const obj = {
    x: Math.random() * W,
    y: -30,
    w: 50, h: 50,
    s: Math.random() * 100 + 50,
  };
  obj.marker = L.marker(px(obj.x, obj.y), {
    icon: L.divIcon({
      className: '',
      html: `<img src="${svgSrc}" width="50" height="50" class="asteroid-spin" style="display:block;filter:drop-shadow(0 0 6px rgba(255,80,80,0.5))">`,
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
  a.s = Math.random() * 100 + 50;
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
      html: `<img src="${SHOT_SVG}" width="20" height="30" style="display:block;filter:drop-shadow(0 0 8px rgba(57,255,20,0.95)) drop-shadow(0 0 18px rgba(57,255,20,0.5))">`,
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
      html: `<img src="${EXPLOSION_SVG}" width="60" height="60" class="explode-anim" style="display:block">`,
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
    <div class="gameover-title">GAME OVER &mdash; ${points} pts</div>
    <div class="gameover-credit">Developed by Somdeep Kundu &middot; @RuDRA Lab, C-TARA, IITB</div>
    <div class="gameover-source">learned from &ldquo;Problem Solving with Abstraction&rdquo; by Programming 2.0 (YouTube)</div>
    <button class="restart-btn" onclick="location.reload()">PLAY AGAIN</button>
  `;
  document.body.appendChild(div);
}

// ── Entry point ──────────────────────────────────────
window.addEventListener('load', () => {
  document.addEventListener('keydown', keypressHandler);
  document.addEventListener('keyup',   keypressHandler);
  document.getElementById('version').textContent = VERSION;

  window.addEventListener('resize', () => {
    W = window.innerWidth;
    H = window.innerHeight;
    map.invalidateSize();
  });

  initMap();
  map.whenReady(() => {
    initShip();
    for (let i = 0; i < 10; i++) spawnAsteroid();
    setInterval(spawnHealth, 15000);
    requestAnimationFrame(tick);
  });
});
