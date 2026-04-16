/**
 * Abstract Asteroids — Leaderboard backend
 * =========================================
 * Paste this entire file into Google Apps Script, then deploy as a Web App.
 *
 * SETUP STEPS
 * -----------
 * 1. Open your Google Sheet (create one if needed — any name is fine).
 * 2. Click  Extensions > Apps Script.
 * 3. Delete any existing code and paste this file.
 * 4. Click  Deploy > New deployment.
 *      • Type: Web app
 *      • Execute as: Me
 *      • Who has access: Anyone
 * 5. Click Deploy, authorise when prompted.
 * 6. Copy the Web app URL  (looks like https://script.google.com/macros/s/.../exec)
 * 7. In Streamlit Cloud → your app → Settings → Secrets, add:
 *        APPS_SCRIPT_URL = "https://script.google.com/macros/s/.../exec"
 *
 * ENDPOINTS  (all plain GET — CORS-safe)
 * ----------------------------------------
 *   ?action=post&name=PILOT&score=150   →  saves one row
 *   ?action=get                         →  returns top-10 JSON (best per player)
 */

function doGet(e) {
  const p = e.parameter || {};

  // ── Get or create the Scores sheet ──────────────────────
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Scores');
  if (!sheet) {
    sheet = ss.insertSheet('Scores');
    sheet.appendRow(['Name', 'Score', 'Timestamp']);
    sheet.setFrozenRows(1);
  }

  // ── Write a score ────────────────────────────────────────
  if (p.action === 'post') {
    const name  = String(p.name  || 'PILOT').substring(0, 20).toUpperCase();
    const score = Math.max(0, parseInt(p.score) || 0);
    sheet.appendRow([name, score, new Date().toISOString()]);
    return json({ ok: true });
  }

  // ── Read top scores ──────────────────────────────────────
  const data = sheet.getDataRange().getValues();
  const rows = data.slice(1).filter(r => r[0] && Number(r[1]) >= 0);

  // Keep only the best score per player, then sort descending
  const best = {};
  rows.forEach(r => {
    const name  = String(r[0]);
    const score = Number(r[1]);
    if (!best[name] || score > best[name]) best[name] = score;
  });

  const top = Object.entries(best)
    .map(([name, score]) => ({ name, score }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);

  return json(top);
}

function json(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
