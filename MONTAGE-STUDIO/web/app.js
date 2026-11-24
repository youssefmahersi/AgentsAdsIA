/* Studio Ads : outils communs (requêtes, onglets, bulles d'aide, guide, toasts). */
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const enc = encodeURIComponent;
const media = c => "/media?chemin=" + enc(c);
const vign = (c, t = 0.5, l = 240) => `/vignette?chemin=${enc(c)}&t=${t}&l=${l}`;
const fmtTc = s => { s = Math.max(0, s || 0); const m = Math.floor(s / 60); return `${String(m).padStart(2,"0")}:${(s - m * 60).toFixed(2).padStart(5,"0")}`; };
const fmtNb = (n, d = 2) => Number(n).toLocaleString("fr-FR", {maximumFractionDigits: d});
const nomFichier = c => (c || "").split("/").pop();

async function api(url, opts = {}) {
  const o = {...opts};
  if (o.json !== undefined) { o.method = o.method || "POST"; o.headers = {"Content-Type": "application/json"}; o.body = JSON.stringify(o.json); delete o.json; }
  const r = await fetch(url, o);
  if (r.status === 401) { location.href = "/code"; throw new Error("code"); }
  const t = await r.text();
  let d; try { d = t ? JSON.parse(t) : null; } catch { d = t; }
  if (!r.ok) throw new Error((d && d.detail) || (d && d.erreur) || `Erreur ${r.status}`);
  return d;
}

let toastMinuteur;
function toast(msg, ms = 2600) {
  const t = $("#toast"); t.innerHTML = msg; t.hidden = false;
  clearTimeout(toastMinuteur); toastMinuteur = setTimeout(() => t.hidden = true, ms);
}

function modale(html, auOuvrir) {
  $("#modale-corps").innerHTML = html; $("#modale").hidden = false;
  if (auOuvrir) auOuvrir($("#modale-corps"));
}
function fermerModale() { $("#modale").hidden = true; $("#modale-corps").innerHTML = ""; }
$("#modale-fermer").onclick = fermerModale;
$("#modale").addEventListener("click", e => { if (e.target.id === "modale") fermerModale(); });

/* ---------- bulles « ? » : data-aide="Titre|À quoi ça sert|Exemple" */
function aide(titre, texte, exemple) { return `<button type="button" class="aide" data-aide="${esc(titre)}|${esc(texte)}|${esc(exemple || "")}">?</button>`; }
document.addEventListener("click", e => {
  const b = e.target.closest(".aide");
  const bulle = $("#bulle");
  if (!b) { bulle.hidden = true; return; }
  e.stopPropagation(); e.preventDefault();
  const [t, x, ex] = b.dataset.aide.split("|");
  bulle.innerHTML = `<b>${t}</b>${x}${ex ? `<i>Exemple : ${ex}</i>` : ""}`;
  bulle.hidden = false;
  const r = b.getBoundingClientRect();
  const l = Math.min(innerWidth - 290, Math.max(8, r.left - 130));
  bulle.style.left = l + "px";
  bulle.style.top = (r.bottom + 8 + 120 > innerHeight ? r.top - bulle.offsetHeight - 8 : r.bottom + 8) + "px";
}, true);

/* ---------- onglets */
const Onglets = {
  actif: "montage", auChangement: {},
  aller(nom) {
    this.actif = nom;
    $$("#onglets button").forEach(b => b.classList.toggle("actif", b.dataset.onglet === nom));
    $$(".vue").forEach(v => v.classList.toggle("actif", v.id === "vue-" + nom));
    try { localStorage.setItem("studio-onglet", nom); } catch {}
    (this.auChangement[nom] || (() => {}))();
  },
};
$$("#onglets button").forEach(b => b.onclick = () => Onglets.aller(b.dataset.onglet));

/* ---------- mode simple / avancé */
const caseAvance = $("#mode-avance");
try { caseAvance.checked = localStorage.getItem("studio-mode") === "avance"; } catch {}
const appliquerMode = () => { document.body.dataset.mode = caseAvance.checked ? "avance" : "simple"; try { localStorage.setItem("studio-mode", caseAvance.checked ? "avance" : "simple"); } catch {} };
caseAvance.onchange = appliquerMode; appliquerMode();

/* ---------- guide « Première fois ? » */
const ETAPES = [
  ["Ouvrir un projet", "En haut à gauche, choisis un projet. Le remake B0002 est déjà prêt pour t'entraîner. Pour en créer un, va dans Bibliothèque, coche des créas et clique « Nouveau projet »."],
  ["Regarder", "Appuie sur ▶ (ou la barre Espace). Fais glisser la timeline du bas : la ligne blanche au centre est la tête de lecture. Pour zoomer : pince avec deux doigts, ou Ctrl + molette."],
  ["Poser un repère", "Là où ça ne va pas, arrête la lecture et touche ⚑ Marqueur. Écris ton commentaire (« le texte arrive trop tôt »). Le repère part aussi chez Claude."],
  ["Donner un ordre", "Dans l'onglet Claude, écris ce que tu veux. Le projet et le timecode sont joints tout seuls. Les réponses arrivent dans le même fil."],
  ["Exporter", "Touche ⇪ Exporter et choisis « Reels / Stories 9:16 ». Le fichier est vérifié automatiquement (taille, images/s, son à −14 LUFS)."],
];
function guide(i = 0) {
  try { localStorage.setItem("studio-guide", "vu"); } catch {}
  const [t, x] = ETAPES[i];
  modale(`<div class="etapes">${ETAPES.map((_, k) => `<i class="${k <= i ? "fait" : ""}"></i>`).join("")}</div>
    <p class="note">Étape ${i + 1} sur 5</p><h2>${t}</h2><p>${x}</p>
    <div class="rangee" style="justify-content:flex-end">${i > 0 ? `<button class="btn" id="g-prec">Précédent</button>` : ""}
    <button class="btn btn-accent" id="g-suiv">${i < 4 ? "Suivant" : "C'est parti"}</button></div>`, c => {
    if (i > 0) $("#g-prec", c).onclick = () => guide(i - 1);
    $("#g-suiv", c).onclick = () => { if (i < 4) guide(i + 1); else { fermerModale(); try { localStorage.setItem("studio-guide", "vu"); } catch {} } };
  });
}
$("#btn-guide").onclick = () => guide(0);

/* ---------- catalogue partagé */
let CATALOGUE = null, ETAT = {};
async function chargerCatalogue() {
  if (!CATALOGUE) CATALOGUE = await api("/api/catalogue");
  return CATALOGUE;
}

/* ---------- glisser-déposer universel (souris + appui long 0,3 s au doigt) */
function rendreGlissable(el, donnees, apercuHtml) {
  let minuteur = null, actif = false, fantome = null, depart = null, cible = null;
  const debut = e => {
    if (e.button && e.button !== 0) return;
    depart = {x: e.clientX, y: e.clientY, t: e.pointerType};
    const lancer = () => {
      actif = true; try { el.setPointerCapture(e.pointerId); } catch {}
      fantome = document.createElement("div"); fantome.className = "fantome-glisse"; fantome.innerHTML = apercuHtml;
      document.body.appendChild(fantome); bouger(e);
      document.dispatchEvent(new CustomEvent("glisse-debut", {detail: donnees}));
      if (navigator.vibrate) navigator.vibrate(15);
    };
    if (e.pointerType === "mouse") { el._lancer = lancer; try { el.setPointerCapture(e.pointerId); } catch {} } else { minuteur = setTimeout(lancer, 300); }
  };
  const bouger = e => {
    if (!depart) return;
    if (!actif) {
      const d = Math.hypot(e.clientX - depart.x, e.clientY - depart.y);
      if (depart.t === "mouse" && d > 6 && el._lancer) { el._lancer(); el._lancer = null; }
      else if (depart.t !== "mouse" && d > 10) { clearTimeout(minuteur); depart = null; }
      if (!actif) return;
    }
    e.preventDefault();
    fantome.style.left = e.clientX + "px"; fantome.style.top = e.clientY + "px";
    const ev = new CustomEvent("glisse-bouge", {detail: {x: e.clientX, y: e.clientY, donnees}});
    document.dispatchEvent(ev);
  };
  const fin = e => {
    clearTimeout(minuteur); el._lancer = null;
    if (actif) {
      e.preventDefault(); e.stopPropagation();
      document.dispatchEvent(new CustomEvent("glisse-fin", {detail: {x: e.clientX, y: e.clientY, donnees}}));
      fantome?.remove(); fantome = null; actif = false;
      el._vientDeGlisser = true; setTimeout(() => el._vientDeGlisser = false, 50);
    }
    depart = null;
  };
  el.addEventListener("pointerdown", debut);
  el.addEventListener("pointermove", bouger);
  el.addEventListener("pointerup", fin);
  el.addEventListener("pointercancel", fin);
  el.addEventListener("contextmenu", e => e.preventDefault());
}

/* ---------- démarrage */
window.addEventListener("load", async () => {
  try { ETAT = await api("/api/etat"); } catch {}
  await chargerCatalogue();
  let o = "montage"; try { o = localStorage.getItem("studio-onglet") || "montage"; } catch {}
  Onglets.aller(o);
  let vu = null; try { vu = localStorage.getItem("studio-guide"); } catch {}
  if (!vu) guide(0);
});
