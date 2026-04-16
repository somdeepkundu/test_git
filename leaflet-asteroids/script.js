// ─────────────────────────────────────────────────────
//  Leaflet Asteroids
//  Game logic runs in viewport pixels; each frame the
//  pixel positions are converted to LatLng so Leaflet
//  markers track the objects on the locked dark map.
// ─────────────────────────────────────────────────────

const VERSION = "v1.1.13";

const ASTEROID_IMGS = [
  '../abstract-asteroids/assets/graphics/asteroid1.svg',
  '../abstract-asteroids/assets/graphics/asteroid2.svg',
];

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
    keyboard: false,            // let our handler own the keyboard
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
      html: '<div class="spaceship-icon"></div>',
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
  const img = ASTEROID_IMGS[Math.floor(Math.random() * ASTEROID_IMGS.length)];
  const obj = {
    x: Math.random() * W,
    y: -30,
    w: 50, h: 50,
    s: Math.random() * 100 + 50,
  };
  obj.marker = L.marker(px(obj.x, obj.y), {
    icon: L.divIcon({
      className: '',
      html: `<div class="asteroid-icon" style="background-image:url('${img}')"></div>`,
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
  const obj = {
    x: Math.random() * W,
    y: -30,
    w: 30, h: 30,
    s: 80 // Falls a bit slower so the player has time to catch it
  };
  obj.marker = L.marker(px(obj.x, obj.y), {
    icon: L.divIcon({
      className: '',
      html: '<div class="health-icon"></div>',
      iconSize: [30, 30],
      iconAnchor: [15, 15],
    }),
    interactive: false,
    zIndexOffset: 400,
  }).addTo(map);
  powerups.push(obj);
}

function movePowerups(dt) {
  for (let i = powerups.length - 1; i >= 0; i--) {
    powerups[i].y += powerups[i].s * dt;
    // Remove if it falls off the screen
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
      html: '<div class="shot-icon"></div>',
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
      html: '<div class="explosion-icon"></div>',
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
// function render() {
//   shipMarker.setLatLng(px(ship.x, ship.y));
//   for (const a of asteroids) a.marker.setLatLng(px(a.x, a.y));
//   for (const s of shots)     s.marker.setLatLng(px(s.x, s.y));

//   document.getElementById('number').textContent = String(points).padStart(3, '0');
//   document.getElementById('healthbar').style.width = `${Math.max(ship.hl, 0)}%`;
// }

// ── 
function render() {
  shipMarker.setLatLng(px(ship.x, ship.y));
  for (const a of asteroids) a.marker.setLatLng(px(a.x, a.y));
  for (const s of shots)     s.marker.setLatLng(px(s.x, s.y));
  for (const p of powerups)  p.marker.setLatLng(px(p.x, p.y)); // <-- Health powerup rendered here

  document.getElementById('number').textContent = String(points).padStart(3, '0');
  document.getElementById('healthbar').style.width = `${Math.max(ship.hl, 0)}%`;
}

// ── Game loop ────────────────────────────────────────
// ── Game loop ────────────────────────────────────────
let points = 0, gameOver = false, lastTime = 0;

function tick(ts) {
  if (gameOver) return;
  requestAnimationFrame(tick);

  if (lastTime === 0) { lastTime = ts; return; }  // skip first frame
  const dt = Math.min((ts - lastTime) / 1000, 0.1);
  lastTime = ts;

  moveShip(dt);
  moveAsteroids(dt);
  moveShots(dt);
  movePowerups(dt); // <-- Move the health powerups

  // Powerup ↔ ship collision check
  for (let i = powerups.length - 1; i >= 0; i--) {
    const p = powerups[i];
    if (isColliding(p, ship)) {
      ship.hl = Math.min(100, ship.hl * 2); // Doubles life, caps at 100 max
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
    <div class="gameover-title">GAME OVER &mdash; ${points} points</div>
    <div class="gameover-credit">Developed by Somdeep Kundu &middot; @RuDRA Lab, C-TARA, IITB</div>
    <div class="gameover-source">learned from &ldquo;Problem Solving with Abstraction&rdquo; by Programming 2.0 (YouTube)</div>
  `;
  document.body.appendChild(div);
}

// ── Entry point ──────────────────────────────────────
// ── Entry point ──────────────────────────────────────
// window.addEventListener('load', () => {
//   document.addEventListener('keydown', keypressHandler);
//   document.addEventListener('keyup',   keypressHandler);

//   // Add the resize listener right here:
//   window.addEventListener('resize', () => {
//     W = window.innerWidth;
//     H = window.innerHeight;
//     map.invalidateSize(); 
//   });

//   initMap();
//   map.whenReady(() => {
//     initShip();
//     for (let i = 0; i < 10; i++) spawnAsteroid();
//     requestAnimationFrame(tick);
//   });
// });

// ── Entry point ──────────────────────────────────────
window.addEventListener('load', () => {
  document.addEventListener('keydown', keypressHandler);
  document.addEventListener('keyup',   keypressHandler);

  // Keeps the map sized correctly if the window changes
  window.addEventListener('resize', () => {
    W = window.innerWidth;
    H = window.innerHeight;
    map.invalidateSize(); 
  });

  initMap();
  map.whenReady(() => {
    initShip();
    for (let i = 0; i < 10; i++) spawnAsteroid();
    
    // Spawn a health pack every 15 seconds!
    setInterval(spawnHealth, 15000); 

    requestAnimationFrame(tick);
  });
});
