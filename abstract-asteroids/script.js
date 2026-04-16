window.addEventListener("load", start);

function start() {
  console.log("JavaScript is running");
  document.addEventListener("keydown", keypressHandler);
  document.addEventListener("keyup", keypressHandler);

  createAsteroids();

  requestAnimationFrame(tick);
}

function keypressHandler(event) {
  const value = event.type === "keydown";
  const key = event.key;
  if (key === "a" || key === "ArrowLeft") controls.left = value;
  if (key === "w" || key === "ArrowUp") controls.up = value;
  if (key === "s" || key === "ArrowDown") controls.down = value;
  if (key === "d" || key === "ArrowRight") controls.right = value;
  if (key === " " && event.type === "keydown" && !controls.spaceHeld) {
    fireShot();
    controls.spaceHeld = true;  // FIX 4: prevent auto-repeat firing while held
  }
  if (key === " " && event.type === "keyup") {
    controls.spaceHeld = false;
  }
}

const controls = {
  up: false,
  down: false,
  left: false,
  right: false,
  spaceHeld: false,
};

let points = 0;
let gameOver = false;

// ========== SHOTS ==========

const shots = [];

function fireShot() {
  const div = document.createElement("div");
  div.classList.add("shot");
  document.querySelector("#gamefield").insertAdjacentElement("beforeend", div);

  const obj = {
    x: spaceship.x,
    y: spaceship.y - spaceship.h / 2,
    w: 20,
    h: 30,
    s: 400,
    visual: div,
  };
  shots.push(obj);
}

function moveShots(delta) {
  for (let i = shots.length - 1; i >= 0; i--) {
    const shot = shots[i];
    shot.y -= shot.s * delta;
    if (shot.y < 0) {
      removeShot(shot);
    }
  }
}

function removeShot(shot) {
  shot.visual.remove();
  const index = shots.indexOf(shot);
  if (index !== -1) shots.splice(index, 1);
}

// ========== ASTEROIDS ==========

const asteroids = [];

function createAsteroids() {
  for (let i = 0; i < 10; i++) {
    const div = document.createElement("div");
    div.classList.add("asteroid");
    document.querySelector("#gamefield").insertAdjacentElement("beforeend", div);

    const obj = {
      x: Math.floor(Math.random() * 750),
      y: -30,
      w: 50,
      h: 50,
      s: Math.random() * 100 + 50,
      visual: div,
    };
    asteroids.push(obj);
  }
}

function moveAsteroids(delta) {
  for (const asteroid of asteroids) {
    asteroid.y += asteroid.s * delta;
    if (asteroid.y > 450) {
      resetAsteroid(asteroid);
    }
  }
}

function resetAsteroid(asteroid) {
  asteroid.y = -30;
  asteroid.x = Math.floor(Math.random() * 750);
  asteroid.s = Math.random() * 100 + 50;
}

// ========== SPACESHIP ==========

const spaceship = {
  x: 380,
  y: 370,
  s: 300,
  w: 60,
  h: 80,
  hl: 100,
};

function moveSpaceship(delta) {
  if (controls.left && spaceship.x > spaceship.w / 2) {
    spaceship.x -= spaceship.s * delta;
  } else if (controls.right && spaceship.x < 770) {
    spaceship.x += spaceship.s * delta;
  }

  if (controls.up && spaceship.y > spaceship.h / 2) {
    spaceship.y -= spaceship.s * delta;
  } else if (controls.down && spaceship.y < 410) {
    spaceship.y += spaceship.s * delta;
  }
}

// ========== COLLISION HELPERS ==========

function distance(objA, objB) {
  return Math.sqrt(Math.pow(objA.x - objB.x, 2) + Math.pow(objA.y - objB.y, 2));
}

function combinedSize(objA, objB) {
  return objA.w / 2 + objB.w / 2;
}

function isColliding(objA, objB) {
  return distance(objA, objB) < combinedSize(objA, objB);
}

// ========== GAME LOOP ==========

let lastTime = 0;

function tick(timestamp) {
  if (gameOver) return;
  requestAnimationFrame(tick);

  // FIX 1: skip the first frame to avoid the huge initial delta spike
  if (lastTime === 0) {
    lastTime = timestamp;
    return;
  }

  const delta = (timestamp - lastTime) / 1000;
  lastTime = timestamp;

  moveSpaceship(delta);
  moveAsteroids(delta);
  moveShots(delta);

  // Asteroid vs spaceship
  for (const asteroid of asteroids) {
    if (isColliding(asteroid, spaceship)) {
      asteroid.s *= 0.95;
      spaceship.hl -= 20 * delta;  // FIX 3: delta-based damage (20 HP/sec) instead of per-frame
      if (spaceship.hl <= 0) {
        endGame();
        return;
      }
    }
  }

  // Shot vs asteroid
  for (let i = shots.length - 1; i >= 0; i--) {
    const shot = shots[i];
    for (const asteroid of asteroids) {
      if (isColliding(shot, asteroid)) {
        points += 10;
        resetAsteroid(asteroid);
        removeShot(shot);
        break;
      }
    }
  }

  render();
}

function render() {
  // FIX 2: null-check so a missing .spaceship element doesn't silently crash the loop
  const visualSpaceShip = document.querySelector(".spaceship");
  if (!visualSpaceShip) {
    console.error("No element with class 'spaceship' found in the DOM!");
    return;
  }
  visualSpaceShip.style.translate =
    `${spaceship.x - spaceship.w / 2}px ${spaceship.y - spaceship.h / 2}px`;

  for (const asteroid of asteroids) {
    asteroid.visual.style.translate =
      `${asteroid.x - asteroid.w / 2}px ${asteroid.y - asteroid.h / 2}px`;
  }

  for (const shot of shots) {
    shot.visual.style.translate =
      `${shot.x - shot.w / 2}px ${shot.y - shot.h / 2}px`;
  }

  document.querySelector("#score #number").textContent =
    String(points).padStart(3, "0");
  document.querySelector("#healthbar").style.width =
    `${Math.max(spaceship.hl, 0)}%`;
}

function endGame() {
  gameOver = true;
  const banner = document.createElement("div");
  banner.id = "gameover";
  banner.innerHTML = `
    <div class="gameover-title">GAME OVER — ${points} points</div>
    <div class="gameover-credit">Developed by Somdeep Kundu · @RuDRA Lab, C-TARA, IITB</div>
    <div class="gameover-source">learned from "Problem Solving with Abstraction" by Programming 2.0 (YouTube)</div>
  `;
  document.querySelector("#gamefield").appendChild(banner);
}