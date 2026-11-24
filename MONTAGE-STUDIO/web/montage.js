/* Studio Ads : onglet Montage (lecteur synchronisé, timeline type CapCut, outils). */
"use strict";
const M = {
  projet: null, reperes: [], choisi: null, T: 0, pps: 80, lecture: false,
  passe: [], futur: [], modifie: false, actifVideo: 0, planCourant: -1, sons: {}, horloge: 0,
};
const vids = [$("#video-a"), $("#video-b")];
const tl = $("#timeline");
const IPS = 30;

/* ============================================================ calculs de timeline (= serveur) */
const dureePlan = p => p.type === "image" ? Math.max(0.1, +p.duree || 2) : Math.max(0.05, (p.fin - p.debut) / Math.max(0.1, +p.vitesse || 1));
const transitionApres = cle => (M.projet.transitions || []).find(t => t.apres === cle && t.type && t.type !== "coupe") || null;
const DUREES_DEFAUT = {punch: 0.15};
function dureeTransition(t, d1, d2) {
  if (!t) return 0;
  const d = +t.duree || DUREES_DEFAUT[t.type] || 0.4;
  return Math.max(0.05, Math.min(d, d1 * 0.9, d2 * 0.9));
}
function dispo() {
  const plans = M.projet?.plans || [];
  const debuts = []; let t = 0;
  plans.forEach((p, i) => {
    const d = dureePlan(p);
    if (i > 0) t -= dureeTransition(transitionApres(plans[i - 1].id), dureePlan(plans[i - 1]), d);
    debuts.push(t); t += d;
  });
  return {debuts, total: Math.max(t, 0)};
}
let D = {debuts: [], total: 0};

/* ============================================================ historique */
function memoriser() {
  M.passe.push(JSON.stringify(M.projet)); if (M.passe.length > 80) M.passe.shift();
  M.futur = []; M.modifie = true; majBoutonsHisto();
}
function annuler() { if (!M.passe.length) return; M.futur.push(JSON.stringify(M.projet)); M.projet = JSON.parse(M.passe.pop()); apresChangement(); toast("Annulé"); }
function refaire() { if (!M.futur.length) return; M.passe.push(JSON.stringify(M.projet)); M.projet = JSON.parse(M.futur.pop()); apresChangement(); toast("Refait"); }
function majBoutonsHisto() { $("#btn-annuler").disabled = !M.passe.length; $("#btn-refaire").disabled = !M.futur.length; $("#btn-enregistrer").classList.toggle("btn-accent", M.modifie); }
$("#btn-annuler").onclick = annuler; $("#btn-refaire").onclick = refaire;
function apresChangement() { D = dispo(); preparerSons(); dessiner(); allerA(Math.min(M.T, D.total)); majBoutonsHisto(); if (!$("#panneau").hidden && Panneau.outil) Panneau.rafraichir(); }

/* ============================================================ chargement */
async function listerProjets(choix) {
  const liste = await api("/api/projets");
  const sel = $("#choix-projet");
  sel.innerHTML = liste.map(p => `<option value="${esc(p.id)}">${esc(p.nom)}</option>`).join("");
  let id = choix; try { id = id || localStorage.getItem("studio-projet"); } catch {}
  if (!liste.some(p => p.id === id)) id = liste[0]?.id;
  if (id) { sel.value = id; await ouvrirProjet(id); }
  return liste;
}
async function ouvrirProjet(id, version) {
  if (M.modifie && !confirm("Des changements ne sont pas enregistrés. Les abandonner ?")) { $("#choix-projet").value = M.projet.id; return; }
  const d = await api(`/api/projets/${enc(id)}` + (version ? `?version=${enc(version)}` : ""));
  M.projet = d.projet; M.reperes = d.reperes; M.passe = []; M.futur = []; M.modifie = false; M.choisi = null; M.planCourant = -1;
  try { localStorage.setItem("studio-projet", id); } catch {}
  $("#choix-version").innerHTML = M.projet.versions.slice().reverse().map(v => `<option ${v === M.projet.version ? "selected" : ""}>${v}</option>`).join("");
  $("#btn-script").hidden = !M.projet.script_rendu;
  const f = M.projet.format || {largeur: 1080, hauteur: 1920};
  $("#ecran").style.aspectRatio = `${f.largeur}/${f.hauteur}`;
  apresChangement(); M.modifie = false; majBoutonsHisto(); allerA(0);
}
$("#choix-projet").onchange = e => ouvrirProjet(e.target.value);
$("#choix-version").onchange = e => ouvrirProjet(M.projet.id, e.target.value);

$("#btn-enregistrer").onclick = async () => {
  const note = M.modifie ? "" : "copie";
  const r = await api(`/api/projets/${enc(M.projet.id)}/enregistrer`, {json: {projet: M.projet, note}});
  M.modifie = false; toast(`Enregistré en <b>${r.version}</b>. Les versions précédentes sont gardées.`);
  const pid = M.projet.id; M.modifie = false; await ouvrirProjet(pid, r.version);
};

$("#btn-nouveau-projet").onclick = () => { Onglets.aller("bibliotheque"); Biblio.aller("creas"); toast("Coche des créas, puis « Nouveau projet avec la sélection »."); };

/* ============================================================ dessin de la timeline */
function dessiner() {
  const p = M.projet; if (!p) return;
  const L = Math.max(D.total, 1) * M.pps;
  $$(".piste").forEach(pi => pi.style.width = L + "px");
  $("#vide-projet").hidden = p.plans.length > 0;
  $("#tc-total").textContent = fmtTc(D.total);
  $("#zoom-info").textContent = `${Math.round(M.pps)} px/s`;
  // règle
  const pas = M.pps > 160 ? 0.5 : M.pps > 60 ? 1 : M.pps > 25 ? 2 : 5;
  let r = ""; for (let t = 0; t <= D.total + 0.001; t += pas) r += `<i style="left:${t * M.pps}px"></i>` + (Math.round(t / pas) % 2 === 0 ? `<span style="left:${t * M.pps}px">${t < 60 ? fmtNb(t, 1) + " s" : fmtTc(t)}</span>` : "");
  $("#regle").style.width = L + "px"; $("#regle").innerHTML = r;
  // vidéo + son
  let hv = "", hs = "";
  p.plans.forEach((pl, i) => {
    const x = D.debuts[i] * M.pps, w = dureePlan(pl) * M.pps;
    const ch = M.choisi?.genre === "plan" && M.choisi.id === pl.id ? " choisi" : "";
    const n = Math.max(1, Math.min(12, Math.round(w / 42)));
    let tranches = "";
    for (let k = 0; k < n; k++) {
      const t = pl.type === "image" ? 0 : pl.debut + (k + 0.5) * (pl.fin - pl.debut) / n;
      tranches += `<span style="position:absolute;top:0;bottom:0;left:${k * 100 / n}%;width:${100 / n}%;background:url('${vign(pl.source, t.toFixed(2), 120)}') center/cover"></span>`;
    }
    const badges = [];
    if ((+pl.vitesse || 1) !== 1) badges.push(`${fmtNb(pl.vitesse)}x`);
    if (pl.look?.id) badges.push(CATALOGUE.looks[pl.look.id]?.nom.split(" ")[0] || pl.look.id);
    if (pl.effets?.length) badges.push("✦" + pl.effets.length);
    if (pl.masque) badges.push("masque");
    if (pl.voix_claire) badges.push("voix claire");
    hv += `<div class="clip clip-video${ch}" data-genre="plan" data-id="${pl.id}" style="left:${x}px;width:${w}px">${tranches}
      <span class="etiquette">${i + 1}. ${esc(nomFichier(pl.source))} · ${fmtNb(dureePlan(pl), 2)} s</span>
      <span class="badges">${badges.map(b => `<b>${esc(b)}</b>`).join("")}</span>
      <span class="bord g" data-bord="g"></span><span class="bord d" data-bord="d"></span></div>`;
    if (pl.type !== "image" && pl.a_son !== false) {
      const v = +pl.vitesse || 1, wsrc = (pl.duree_source || pl.fin) / v * M.pps;
      hs += `<div class="clip clip-son${(+pl.volume === 0) ? " muet" : ""}" data-genre="plan" data-id="${pl.id}" style="left:${x}px;width:${w}px;background-image:url('/onde?chemin=${enc(pl.source)}');background-size:${wsrc}px 100%;background-position:${-pl.debut / v * M.pps}px 0;opacity:${Math.min(1, .35 + (+pl.volume ?? 1) * .65)}"></div>`;
    } else {
      hs += `<div class="clip clip-son muet" data-genre="plan" data-id="${pl.id}" style="left:${x}px;width:${w}px"></div>`;
    }
  });
  // jointures (début, entre les plans, fin)
  const j = (cle, x, bout) => {
    const t = transitionApres(cle);
    const ch = M.choisi?.genre === "jointure" && M.choisi.id === cle ? " cible" : "";
    return `<button class="jointure${t ? " avec" : ""}${bout ? " bout" : ""}${ch}" data-jointure="${cle}" style="left:${x}px" title="${t ? esc(CATALOGUE.transitions[t.type]?.nom) : "Ajouter une transition"}">${t ? "⧉" : (bout ? "◆" : "+")}</button>`;
  };
  if (p.plans.length) {
    hv += j("debut", 0, true);
    p.plans.forEach((pl, i) => { if (i > 0) { const tr = transitionApres(p.plans[i - 1].id); const dt = dureeTransition(tr, dureePlan(p.plans[i - 1]), dureePlan(pl)); hv += j(p.plans[i - 1].id, (D.debuts[i] + dt / 2) * M.pps); } });
    hv += j("fin", D.total * M.pps, true);
  }
  $("#piste-video").innerHTML = hv; $("#piste-son").innerHTML = hs;
  // textes, sons, musique
  const clipLibre = (genre, it, debut, fin, classe, contenu) => {
    const ch = M.choisi?.genre === genre && M.choisi.id === it.id ? " choisi" : "";
    return `<div class="clip ${classe}${ch}" data-genre="${genre}" data-id="${it.id}" style="left:${debut * M.pps}px;width:${Math.max(8, (fin - debut) * M.pps)}px">${contenu}<span class="bord g" data-bord="g"></span><span class="bord d" data-bord="d"></span></div>`;
  };
  $("#piste-texte").innerHTML = (p.textes || []).map(t => clipLibre("texte", t, t.debut, t.fin, "clip-texte", t.image ? "🖼 " + esc(nomFichier(t.image)) : "T " + esc(t.texte))).join("");
  const sonsHtml = type => (p.sons || []).filter(s => type === "musique" ? s.type === "musique" : s.type !== "musique").map(s => {
    const d = s.duree || M.sons[s.id]?.duree || 5;
    return clipLibre("son", s, +s.debut || 0, (+s.debut || 0) + d, type === "musique" ? "clip-musique" : "clip-sons",
      `${type === "musique" ? "♪" : s.type === "voix" ? "🎙" : "🔔"} ${esc(nomFichier(s.source))} · ${Math.round((+s.volume ?? 1) * 100)} %`);
  }).join("");
  $("#piste-sons").innerHTML = sonsHtml("autres"); $("#piste-musique").innerHTML = sonsHtml("musique");
  // repères
  $("#piste-reperes").innerHTML = M.reperes.map(r => `<span class="repere" data-repere="${r.id}" style="left:${r.t * M.pps}px" title="${esc(r.texte)}">⚑</span>`).join("");
}

/* ============================================================ lecture */
function planA(T) {
  const pl = M.projet?.plans || [];
  for (let i = pl.length - 1; i >= 0; i--) if (T >= D.debuts[i] - 1e-6) return Math.min(i, pl.length - 1);
  return pl.length ? 0 : -1;
}
const CSS_LOOKS = {
  naturel: {contrast: 1.06, saturate: 1.05}, serie: {contrast: .95, saturate: .92, brightness: 1.02, sepia: .06},
  soleil: {sepia: .18, saturate: 1.15, brightness: 1.05}, frais: {brightness: 1.06, saturate: .98, "hue-rotate": -5},
  punchy: {contrast: 1.25, saturate: 1.25}, nuit: {brightness: .82, contrast: 1.08, saturate: .88, "hue-rotate": 6},
  nb: {grayscale: 1, contrast: 1.15}, vintage: {sepia: .25, contrast: .92, saturate: .85, brightness: 1.04}, auto: {},
};
const NEUTRE = {contrast: 1, saturate: 1, brightness: 1, sepia: 0, grayscale: 0, "hue-rotate": 0};
function filtreCss(pl) {
  const parts = [];
  const look = pl?.look; if (look?.id && CSS_LOOKS[look.id]) {
    const k = look.force ?? 1;
    for (const [f, v] of Object.entries(CSS_LOOKS[look.id])) { const val = NEUTRE[f] + (v - NEUTRE[f]) * k; parts.push(f === "hue-rotate" ? `${f}(${val}deg)` : `${f}(${val.toFixed(3)})`); }
  }
  for (const e of pl?.effets || []) if (e.type === "flou") parts.push(`blur(${(1 + 8 * e.force).toFixed(1)}px)`);
  return parts.join(" ") || "none";
}
function chargerDans(v, pl, t) {
  const src = media(pl.source);
  if (v.dataset.src !== src) { v.dataset.src = src; v.src = src; }
  const fixer = () => { try { v.currentTime = t; } catch {} };
  if (v.readyState >= 1) fixer(); else v.addEventListener("loadedmetadata", fixer, {once: true});
  v.playbackRate = +pl.vitesse || 1;
  v.volume = Math.max(0, Math.min(1, +pl.volume ?? 1)); v.muted = (+pl.volume === 0);
  v.style.filter = filtreCss(pl);
}
function montrerPlan(i, T, jouer) {
  const pl = M.projet.plans[i]; if (!pl) return;
  const img = $("#image-plan");
  if (pl.type === "image") {
    vids.forEach(v => { v.pause(); v.classList.remove("visible"); });
    img.src = media(pl.source); img.hidden = false; img.style.filter = filtreCss(pl);
  } else {
    img.hidden = true;
    let v = vids[M.actifVideo];
    if (i !== M.planCourant) {
      const autre = vids[1 - M.actifVideo];
      if (autre.dataset.src === media(pl.source) && autre.dataset.plan === pl.id) { M.actifVideo = 1 - M.actifVideo; v = autre; }
    }
    chargerDans(v, pl, pl.debut + (T - D.debuts[i]) * (+pl.vitesse || 1));
    v.dataset.plan = pl.id;
    v.classList.add("visible"); vids[1 - M.actifVideo].classList.remove("visible"); vids[1 - M.actifVideo].pause();
    if (jouer) v.play().catch(() => {}); else v.pause();
    // précharger le plan suivant dans l'autre lecteur
    const suiv = M.projet.plans[i + 1];
    if (suiv && suiv.type !== "image") { const o = vids[1 - M.actifVideo]; chargerDans(o, suiv, suiv.debut); o.dataset.plan = suiv.id; }
  }
  M.planCourant = i;
}
let scrollProgramme = false;
function allerA(T, depuisScroll) {
  if (!M.projet) return;
  M.T = Math.max(0, Math.min(T, D.total));
  const i = planA(M.T);
  if (i >= 0) montrerPlan(i, M.T, M.lecture);
  majTextes(); majTc();
  if (!depuisScroll) { scrollProgramme = true; tl.scrollLeft = M.T * M.pps; requestAnimationFrame(() => scrollProgramme = false); }
  if (M.lecture) synchroSons(true);
}
function majTc() { $("#tc").textContent = fmtTc(M.T); }
function majTextes() {
  const f = M.projet.format || {largeur: 1080, hauteur: 1920};
  const vis = (M.projet.textes || []).filter(t => M.T >= t.debut && M.T <= t.fin);
  const cle = vis.map(t => t.id + t.texte + t.style + (t.ancien || "")).join("|");
  const cal = $("#calque-textes");
  if (cal.dataset.cle === cle) return;
  cal.dataset.cle = cle;
  cal.innerHTML = vis.map(t => t.image ? `<img src="${media(t.image)}" alt="">` :
    `<img src="/apercu/texte?texte=${enc(t.texte)}&style=${enc(t.style)}&l=${f.largeur}&h=${f.hauteur}&ancien=${enc(t.ancien || "")}" alt="">`).join("");
}
function preparerSons() {
  for (const s of M.projet.sons || []) {
    if (!M.sons[s.id] || M.sons[s.id].src !== s.source) {
      const a = new Audio(media(s.source)); a.preload = "auto";
      M.sons[s.id] = {a, src: s.source, duree: null};
      a.addEventListener("loadedmetadata", () => { M.sons[s.id].duree = a.duration - (+s.coupe_debut || 0); dessiner(); });
    }
  }
}
function synchroSons(force) {
  for (const s of M.projet.sons || []) {
    const o = M.sons[s.id]; if (!o) continue;
    const local = M.T - (+s.debut || 0) + (+s.coupe_debut || 0);
    const dans = M.T >= (+s.debut || 0) && (!o.duree || M.T < (+s.debut || 0) + (s.duree || o.duree));
    o.a.volume = Math.max(0, Math.min(1, (+s.volume ?? 1) * (s.type === "musique" ? .6 : 1)));
    if (M.lecture && dans) {
      if (force || Math.abs(o.a.currentTime - local) > 0.25) o.a.currentTime = Math.max(0, local);
      if (o.a.paused) o.a.play().catch(() => {});
    } else o.a.pause();
  }
}
function lecture(on) {
  if (!M.projet?.plans.length) return;
  M.lecture = on ?? !M.lecture;
  $("#btn-lecture").textContent = M.lecture ? "❚❚" : "▶";
  if (M.lecture) { if (M.T >= D.total - 0.05) M.T = 0; M.horloge = performance.now(); allerA(M.T); requestAnimationFrame(boucle); }
  else { vids.forEach(v => v.pause()); synchroSons(); }
}
function boucle(now) {
  if (!M.lecture) return;
  const i = M.planCourant, pl = M.projet.plans[i];
  const dt = (now - M.horloge) / 1000; M.horloge = now;
  if (pl) {
    if (pl.type === "image") M.T += dt;
    else { const v = vids[M.actifVideo]; if (!v.seeking && v.readyState >= 2) M.T = D.debuts[i] + (v.currentTime - pl.debut) / (+pl.vitesse || 1); }
    const finPlan = D.debuts[i] + dureePlan(pl);
    const suiv = M.projet.plans[i + 1];
    const bascule = suiv ? D.debuts[i + 1] + dureeTransition(transitionApres(pl.id), dureePlan(pl), dureePlan(suiv)) / 2 : finPlan;
    if (M.T >= Math.min(finPlan, bascule) - 0.01) {
      if (suiv) { M.T = Math.max(M.T, D.debuts[i + 1] + (bascule - D.debuts[i + 1])); montrerPlan(i + 1, M.T, true); }
      else { M.T = D.total; lecture(false); }
    }
  }
  scrollProgramme = true; tl.scrollLeft = M.T * M.pps; requestAnimationFrame(() => scrollProgramme = false);
  majTextes(); majTc(); synchroSons();
  if (M.lecture) requestAnimationFrame(boucle);
}
$("#btn-lecture").onclick = () => lecture();
$("#btn-zone-sure").onclick = () => $("#zone-sure").hidden = !$("#zone-sure").hidden;
tl.addEventListener("scroll", () => {
  if (scrollProgramme || M.lecture || !M.projet) return;
  allerA(tl.scrollLeft / M.pps, true);
});

/* ============================================================ zoom (pincer, Ctrl + molette) */
function zoomer(f, centreT = M.T) {
  M.pps = Math.max(8, Math.min(600, M.pps * f));
  dessiner(); scrollProgramme = true; tl.scrollLeft = centreT * M.pps; requestAnimationFrame(() => scrollProgramme = false);
}
tl.addEventListener("wheel", e => { if (e.ctrlKey || e.metaKey) { e.preventDefault(); zoomer(e.deltaY < 0 ? 1.12 : 1 / 1.12); } }, {passive: false});
const pointeurs = new Map(); let distPince = 0;
tl.addEventListener("pointerdown", e => { if (e.pointerType === "touch") pointeurs.set(e.pointerId, e); });
tl.addEventListener("pointermove", e => {
  if (!pointeurs.has(e.pointerId)) return; pointeurs.set(e.pointerId, e);
  if (pointeurs.size === 2) {
    const [a, b] = [...pointeurs.values()]; const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    if (distPince) zoomer(d / distPince); distPince = d;
  }
});
const finPince = e => { pointeurs.delete(e.pointerId); if (pointeurs.size < 2) distPince = 0; };
tl.addEventListener("pointerup", finPince); tl.addEventListener("pointercancel", finPince);

/* ============================================================ sélection, glisser, couper les bords */
function choisir(genre, id) { M.choisi = genre ? {genre, id} : null; dessiner(); if (!$("#panneau").hidden && Panneau.outil) Panneau.rafraichir(); }
const trouver = (genre, id) => genre === "plan" ? M.projet.plans.find(p => p.id === id) : genre === "texte" ? (M.projet.textes || []).find(t => t.id === id) : (M.projet.sons || []).find(s => s.id === id);
function selection(genre) {
  if (M.choisi?.genre === genre) return trouver(genre, M.choisi.id);
  if (genre === "plan") { const i = planA(M.T); return i >= 0 ? M.projet.plans[i] : null; }
  return null;
}

let geste = null;
tl.addEventListener("pointerdown", e => {
  const j = e.target.closest(".jointure");
  if (j) { choisir("jointure", j.dataset.jointure); Panneau.ouvrir("transitions"); return; }
  const r = e.target.closest(".repere");
  if (r) { const rep = M.reperes.find(x => x.id === r.dataset.repere); if (rep) { allerA(rep.t); toast("⚑ " + esc(rep.texte)); } return; }
  const c = e.target.closest(".clip"); if (!c || pointeurs.size > 1) return;
  const genre = c.dataset.genre, id = c.dataset.id, bord = e.target.dataset.bord;
  const deja = M.choisi?.genre === genre && M.choisi.id === id;
  geste = {genre, id, bord, x0: e.clientX, actif: false, el: c, pointer: e.pointerType, idp: e.pointerId, deja,
           snapshot: JSON.stringify(M.projet), item: JSON.parse(JSON.stringify(trouver(genre, id)))};
  if (bord && deja) { geste.actif = true; geste.mode = "bord"; c.setPointerCapture(e.pointerId); e.preventDefault(); }
  else if (e.pointerType !== "mouse") geste.minuteur = setTimeout(() => { if (geste) { geste.actif = true; geste.mode = "deplacer"; c.classList.add("glisse"); c.setPointerCapture(geste.idp); if (navigator.vibrate) navigator.vibrate(15); } }, 300);
});
tl.addEventListener("pointermove", e => {
  if (!geste) return;
  const dx = e.clientX - geste.x0;
  if (!geste.actif) {
    if (geste.pointer === "mouse" && Math.abs(dx) > 6) { geste.actif = true; geste.mode = "deplacer"; geste.el.classList.add("glisse"); geste.el.setPointerCapture(geste.idp); }
    else if (geste.pointer !== "mouse" && Math.abs(dx) > 10) { clearTimeout(geste.minuteur); geste = null; return; }
    if (!geste?.actif) return;
  }
  e.preventDefault();
  const ds = dx / M.pps, it = trouver(geste.genre, geste.id), o = geste.item;
  if (geste.mode === "bord") {
    if (geste.genre === "plan") {
      const v = +o.vitesse || 1;
      if (o.type === "image") { if (geste.bord === "d") it.duree = Math.max(0.2, +(o.duree + ds).toFixed(3)); }
      else if (geste.bord === "g") it.debut = +Math.max(0, Math.min(o.fin - 0.1, o.debut + ds * v)).toFixed(3);
      else it.fin = +Math.max(o.debut + 0.1, Math.min(o.duree_source || o.fin + 999, o.fin + ds * v)).toFixed(3);
    } else if (geste.genre === "texte") {
      if (geste.bord === "g") it.debut = +Math.max(0, Math.min(o.fin - 0.2, o.debut + ds)).toFixed(3);
      else it.fin = +Math.max(o.debut + 0.2, o.fin + ds).toFixed(3);
    } else {
      const total = M.sons[o.id]?.duree || o.duree || 5;
      if (geste.bord === "g") { const d = Math.max(-(+o.coupe_debut || 0), Math.min(ds, (o.duree || total) - 0.2)); it.debut = +((+o.debut || 0) + d).toFixed(3); it.coupe_debut = +((+o.coupe_debut || 0) + d).toFixed(3); it.duree = +((o.duree || total) - d).toFixed(3); }
      else it.duree = +Math.max(0.2, (o.duree || total) + ds).toFixed(3);
    }
    D = dispo(); dessiner();
  } else {
    if (geste.genre === "plan") geste.el.style.transform = `translateX(${dx}px)`;
    else { const d = Math.max(-o.debut, ds); it.debut = +(o.debut + d).toFixed(3); if (geste.genre === "texte") it.fin = +(o.fin + d).toFixed(3); dessiner(); }
  }
});
const finGeste = e => {
  if (!geste) return;
  clearTimeout(geste.minuteur);
  const g = geste; geste = null;
  if (!g.actif) { // simple clic : sélection
    if (g.deja && g.genre === "plan") { /* rien */ }
    choisir(g.genre, g.id); return;
  }
  if (g.mode === "deplacer" && g.genre === "plan") {
    const pl = M.projet.plans, i = pl.findIndex(p => p.id === g.id);
    const centre = D.debuts[i] + dureePlan(pl[i]) / 2 + (e.clientX - g.x0) / M.pps;
    let n = 0; pl.forEach((p, k) => { if (k !== i && D.debuts[k] + dureePlan(p) / 2 < centre) n++; });
    if (n !== i) { M.passe.push(g.snapshot); M.futur = []; M.modifie = true; const [x] = pl.splice(i, 1); pl.splice(n, 0, x); toast(`Plan déplacé en position ${n + 1}`); }
  } else if (g.snapshot !== JSON.stringify(M.projet)) { M.passe.push(g.snapshot); M.futur = []; M.modifie = true; }
  choisir(g.genre, g.id); apresChangement();
};
tl.addEventListener("pointerup", finGeste); tl.addEventListener("pointercancel", finGeste);

/* ============================================================ dépôt des transitions / looks / effets glissés */
function jointureSous(x, y) {
  let meilleure = null, dist = 46;
  $$(".jointure").forEach(j => { const r = j.getBoundingClientRect(); const d = Math.hypot(r.left + r.width / 2 - x, r.top + r.height / 2 - y); if (d < dist) { dist = d; meilleure = j; } });
  return meilleure;
}
function planSous(x, y) { const el = document.elementFromPoint(x, y)?.closest(".clip-video,.clip-son"); return el?.dataset.id || null; }
document.addEventListener("glisse-bouge", e => {
  const {x, y, donnees} = e.detail;
  $$(".jointure.cible").forEach(j => j.classList.remove("cible"));
  $$(".clip.cible-plan").forEach(c => { c.classList.remove("cible-plan"); c.style.outline = ""; });
  if (donnees.genre === "transition") { const j = jointureSous(x, y); if (j) j.classList.add("cible"); }
  else { const id = planSous(x, y); if (id) $$(`.clip-video[data-id="${id}"]`).forEach(c => { c.classList.add("cible-plan"); c.style.outline = "3px solid var(--jaune)"; }); }
});
document.addEventListener("glisse-fin", e => {
  const {x, y, donnees} = e.detail;
  $$(".jointure.cible").forEach(j => j.classList.remove("cible"));
  if (donnees.genre === "transition") {
    const j = jointureSous(x, y); if (!j) return;
    appliquerTransition(j.dataset.jointure, donnees.type); choisir("jointure", j.dataset.jointure);
    Panneau.ouvrir("transitions");
  } else {
    const id = planSous(x, y); if (!id) return;
    const pl = M.projet.plans.find(p => p.id === id); memoriser();
    if (donnees.genre === "look") pl.look = {id: donnees.type, force: Panneau.forceLook ?? 1};
    if (donnees.genre === "effet") { pl.effets = (pl.effets || []).filter(f => f.type !== donnees.type); pl.effets.push({type: donnees.type, force: .5}); }
    choisir("plan", id); apresChangement(); toast(`Appliqué au plan ${M.projet.plans.indexOf(pl) + 1}`);
  }
});
function appliquerTransition(cle, type, duree) {
  memoriser();
  const tr = M.projet.transitions = (M.projet.transitions || []).filter(t => t.apres !== cle);
  if (type && type !== "coupe") tr.push({apres: cle, type, duree: duree || DUREES_DEFAUT[type] || (cle === "debut" || cle === "fin" ? .5 : .4)});
  apresChangement();
}

/* ============================================================ actions */
function couper() {
  const i = planA(M.T), pl = M.projet.plans[i];
  if (!pl) return toast("Aucun plan sous la tête de lecture.");
  const local = M.T - D.debuts[i];
  if (local < 0.1 || local > dureePlan(pl) - 0.1) return toast("Place la tête de lecture à l'intérieur du plan (pas sur un bord).");
  memoriser();
  const b = JSON.parse(JSON.stringify(pl)); b.id = "p" + Date.now().toString(36);
  if (pl.type === "image") { b.duree = +(pl.duree - local).toFixed(3); pl.duree = +local.toFixed(3); }
  else { const c = +(pl.debut + local * (+pl.vitesse || 1)).toFixed(3); b.debut = c; pl.fin = c; }
  M.projet.plans.splice(i + 1, 0, b);
  const tr = (M.projet.transitions || []).find(t => t.apres === pl.id); if (tr) tr.apres = b.id;
  choisir("plan", b.id); apresChangement(); toast("Plan coupé en deux.");
}
function supprimer() {
  const c = M.choisi;
  if (!c) return toast("Touche d'abord un élément de la timeline.");
  memoriser();
  if (c.genre === "plan") {
    const i = M.projet.plans.findIndex(p => p.id === c.id); M.projet.plans.splice(i, 1);
    M.projet.transitions = (M.projet.transitions || []).filter(t => t.apres !== c.id);
  } else if (c.genre === "texte") M.projet.textes = M.projet.textes.filter(t => t.id !== c.id);
  else if (c.genre === "son") M.projet.sons = M.projet.sons.filter(s => s.id !== c.id);
  else if (c.genre === "jointure") M.projet.transitions = (M.projet.transitions || []).filter(t => t.apres !== c.id);
  M.choisi = null; apresChangement(); toast("Supprimé. (↶ pour annuler)");
}
function dupliquer() {
  const pl = selection("plan"); if (!pl) return;
  memoriser(); const b = JSON.parse(JSON.stringify(pl)); b.id = "p" + Date.now().toString(36);
  M.projet.plans.splice(M.projet.plans.indexOf(pl) + 1, 0, b); choisir("plan", b.id); apresChangement(); toast("Plan dupliqué.");
}
async function rendre(preset) {
  $("#menu-rendre").hidden = true;
  if (preset === "script") { const t = await api(`/api/projets/${enc(M.projet.id)}/script`, {method: "POST"}); toast(t.etat === "échec" ? t.message : "Script lancé."); Onglets.aller("exporter"); return; }
  await api("/api/rendu", {json: {projet: M.projet, preset, extrait_debut: M.T}});
  toast(`Rendu lancé. <a href="#" onclick="Onglets.aller('exporter');return false" style="color:var(--accent)">Suivre dans Exporter</a>`, 4000);
}
$("#btn-rendre").onclick = e => { e.stopPropagation(); $("#menu-rendre").hidden = !$("#menu-rendre").hidden; };
$$("#menu-rendre button").forEach(b => b.onclick = () => rendre(b.dataset.preset));
document.addEventListener("click", e => { if (!e.target.closest(".menu-rendu")) $("#menu-rendre").hidden = true; });

/* ============================================================ panneaux d'outils */
const AIDES = {
  plan: ["Plan", "Infos et réglages du plan sélectionné : durée, ordre, dupliquer.", "dupliquer le plan du produit pour le montrer deux fois"],
  couper: ["Couper", "Coupe le plan en deux à la tête de lecture.", "retirer la seconde en trop au début d'un plan"],
  vitesse: ["Vitesse", "Accélère ou ralentit le plan. Le son suit.", "1,25x pour un plan qui traîne"],
  volume: ["Volume", "Règle le son du plan. « Voix claire » enlève le souffle et rend la voix plus nette.", "baisser à 0 % un plan dont le son gêne"],
  texte: ["Texte", "Ajoute un titre, un sous-titre, un prix barré ou un bouton d'action, placé dans la zone sûre.", "« Livraison offerte » en bandeau du haut"],
  effets: ["Effets", "Flou, grain, glow… Glisse un effet sur un plan, ou touche-le pour l'appliquer au plan choisi.", "un léger grain pour un rendu moins « IA »"],
  filtres: ["Filtres", "Looks de couleur prêts. La peau reste naturelle sur tous les looks couleur.", "« Frais / clean » pour une cuisine"],
  ajuster: ["Ajuster", "Cadrage (remplir ou contenir), masques et zoom sur une zone.", "flouter un logo dans un coin"],
  transitions: ["Transitions", "Ce qui se passe entre deux plans. Glisse-la sur une jointure ⊕ de la timeline.", "un fondu au noir à la fin"],
  sons: ["Sons", "Ajoute une musique (baissée automatiquement sous la voix), un bruitage ou une voix.", "un « whoosh » sur une transition"],
  marqueur: ["Marqueur", "Pose un repère là où ça ne va pas, avec ton commentaire. Il part aussi chez Claude.", "« le texte arrive trop tôt »"],
  remplacer: ["Remplacer", "Remplace la vidéo du plan par une autre, sans toucher au reste.", "mettre la nouvelle génération de ziad"],
  supprimer: ["Supprimer", "Supprime l'élément sélectionné. Annuler (↶) le remet.", ""],
};
const PRESETS_1CLIC = [
  ["Style série", "Couleurs douces et grain léger.", pl => { pl.look = {id: "serie", force: .8}; pl.effets = [{type: "grain", force: .25}]; }],
  ["Pub dynamique", "Contraste et netteté pour arrêter le scroll.", pl => { pl.look = {id: "punchy", force: .7}; pl.effets = [{type: "nettete", force: .4}]; }],
  ["Teint naturel", "Juste un peu de relief, peau intacte.", pl => { pl.look = {id: "naturel", force: .6}; pl.effets = []; }],
  ["Voix claire", "Nettoie la voix sur tous les plans.", pl => { pl.voix_claire = true; }],
];
const Panneau = {
  outil: null, forceLook: 1,
  ouvrir(outil) {
    if (outil === "couper") return couper();
    if (outil === "supprimer") return supprimer();
    if (outil === "exporter") return Onglets.aller("exporter");
    this.outil = outil;
    $$("#outils button").forEach(b => b.classList.toggle("actif", b.dataset.outil === outil));
    const a = AIDES[outil];
    $("#panneau-titre").innerHTML = esc(a[0]) + aide(a[0], a[1], a[2]);
    $("#panneau").hidden = false; this.placer(); this.rafraichir();
  },
  placer() { // le panneau remonte au-dessus de la timeline : elle reste visible pour y déposer transitions, looks et effets
    const p = $("#panneau"); if (p.hidden) return;
    const bas = $("#outils").offsetHeight + $(".timeline-zone").offsetHeight;
    const dispo = $("#vue-montage").offsetHeight - bas - 50;
    if (innerWidth >= 1000) { // grand écran : tiroir à droite, le lecteur reste visible au centre
      const haut = $(".projet-barre").offsetHeight;
      p.classList.add("lateral"); p.style.top = haut + "px"; p.style.bottom = bas + "px"; p.style.maxHeight = "none";
    } else {
      p.classList.remove("lateral"); p.style.top = "auto";
      p.style.bottom = bas + "px"; p.style.maxHeight = Math.max(150, Math.min(dispo, 420)) + "px";
    }
  },
  fermer() { this.outil = null; $("#panneau").hidden = true; $$("#outils button").forEach(b => b.classList.remove("actif")); },
  rafraichir() { const f = OUTILS[this.outil]; if (f) f($("#panneau-corps")); },
};
$("#panneau-fermer").onclick = () => Panneau.fermer();
$$("#outils button").forEach(b => b.onclick = () => Panneau.ouvrir(b.dataset.outil));

function curseur(label, val, min, max, pas, suffixe, surChange, aideTxt = "") {
  const id = "c" + Math.random().toString(36).slice(2, 8);
  setTimeout(() => {
    const inp = document.getElementById(id); if (!inp) return; let premier = true;
    inp.oninput = () => { if (premier) { memoriser(); premier = false; } inp.nextElementSibling.textContent = fmtNb(inp.value) + suffixe; surChange(+inp.value); };
    inp.onchange = () => { premier = true; apresChangement(); };
  });
  return `<div class="curseur"><label>${label}${aideTxt}</label><input type="range" id="${id}" min="${min}" max="${max}" step="${pas}" value="${val}"><output>${fmtNb(val)}${suffixe}</output></div>`;
}
const pasDePlan = c => { c.innerHTML = `<p class="note">Touche un plan dans la timeline (ou place la tête de lecture dessus).</p>`; };

const OUTILS = {
  plan(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    const i = M.projet.plans.indexOf(pl);
    c.innerHTML = `<div class="rangee"><img src="${vign(pl.source, pl.debut + .3, 160)}" style="height:90px;border-radius:8px"><div>
      <b>Plan ${i + 1} sur ${M.projet.plans.length}</b><br><small class="note">${esc(pl.source)}</small><br>
      Durée à l'écran : <b>${fmtNb(dureePlan(pl))} s</b>${pl.type !== "image" ? ` · source ${fmtNb(pl.debut)} → ${fmtNb(pl.fin)} s` : ""}</div></div>
      <div class="rangee"><button class="btn" id="pl-g" ${i === 0 ? "disabled" : ""}>← Avancer</button><button class="btn" id="pl-d" ${i === M.projet.plans.length - 1 ? "disabled" : ""}>Reculer →</button>
      <button class="btn" id="pl-dup">Dupliquer</button><button class="btn" id="pl-aller">Aller au début du plan</button></div>
      <div class="avance-seul">${pl.type === "image" ? curseur("Durée (s)", pl.duree, .2, 10, .1, " s", v => { pl.duree = v; D = dispo(); dessiner(); }) :
      `<div class="rangee"><label class="champ">Début (s)<input type="number" id="pl-debut" step="0.033" value="${pl.debut}"></label><label class="champ">Fin (s)<input type="number" id="pl-fin" step="0.033" value="${pl.fin}"></label><button class="btn" id="pl-ok">Appliquer</button></div>`}</div>
      <p class="note">Astuce : glisse un plan (appui long au doigt) pour changer l'ordre ; tire ses bords blancs pour le raccourcir.</p>`;
    const bouger = d => { memoriser(); const p = M.projet.plans; p.splice(i, 1); p.splice(i + d, 0, pl); apresChangement(); };
    $("#pl-g", c).onclick = () => bouger(-1); $("#pl-d", c).onclick = () => bouger(1);
    $("#pl-dup", c).onclick = dupliquer; $("#pl-aller", c).onclick = () => allerA(D.debuts[i] + 0.001);
    const ok = $("#pl-ok", c); if (ok) ok.onclick = () => { memoriser(); pl.debut = Math.max(0, +$("#pl-debut", c).value); pl.fin = Math.max(pl.debut + .1, Math.min(pl.duree_source || 1e9, +$("#pl-fin", c).value)); apresChangement(); };
  },
  vitesse(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    const v = +pl.vitesse || 1;
    c.innerHTML = `<div class="rangee puces">${[0.5, 0.75, 1, 1.25, 1.5, 2].map(x => `<button data-v="${x}" class="${x === v ? "actif" : ""}">${fmtNb(x)}x</button>`).join("")}</div>
      <div class="avance-seul">${curseur("Vitesse libre", v, .25, 3, .05, "x", x => { pl.vitesse = x; D = dispo(); dessiner(); })}</div>
      <p class="note">Plan ${M.projet.plans.indexOf(pl) + 1} : ${fmtNb(dureePlan(pl))} s à l'écran.</p>`;
    $$("[data-v]", c).forEach(b => b.onclick = () => { memoriser(); pl.vitesse = +b.dataset.v; apresChangement(); });
  },
  volume(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    c.innerHTML = curseur("Volume du plan", Math.round((+pl.volume ?? 1) * 100), 0, 200, 5, " %", x => { pl.volume = x / 100; dessiner(); }) +
      `<label class="case" style="font-size:14px;color:var(--texte)"><input type="checkbox" id="vc" ${pl.voix_claire ? "checked" : ""}> Voix claire (réduction de bruit)${aide("Voix claire", "Coupe le grave inutile, enlève le souffle de fond, rend la voix plus présente.", "une voix enregistrée au téléphone")}</label>
      <div class="rangee"><button class="btn" id="vol-tous">Appliquer à tous les plans</button><button class="btn" id="vol-muet">Couper le son du plan</button></div>
      <p class="note">À l'export, tout le son est mesuré puis réglé à −14 LUFS, le niveau conseillé pour Meta et TikTok. La musique est baissée automatiquement quand quelqu'un parle.</p>`;
    $("#vc", c).onchange = e => { memoriser(); pl.voix_claire = e.target.checked; apresChangement(); };
    $("#vol-tous", c).onclick = () => { memoriser(); M.projet.plans.forEach(p => { p.volume = pl.volume; p.voix_claire = pl.voix_claire; }); apresChangement(); toast("Appliqué à tous les plans."); };
    $("#vol-muet", c).onclick = () => { memoriser(); pl.volume = 0; apresChangement(); };
  },
  texte(c) {
    const t = selection("texte");
    const st = CATALOGUE.styles, an = CATALOGUE.animations;
    const val = t || {texte: "", style: "sous-titre", animation: "fondu", ancien: ""};
    c.innerHTML = `<label class="champ">${t ? "Modifier le texte" : "Nouveau texte à " + fmtTc(M.T)}<textarea id="tx-texte" rows="2" placeholder="Écris ton texte…">${esc(val.texte)}</textarea></label>
      <div class="grille-cartes" id="tx-styles">${Object.entries(st).map(([k, n]) => `<button class="carte ${val.style === k ? "actif" : ""}" data-style="${k}"><img src="/apercu/texte?texte=${enc(k === "prix" ? "59,99 €" : k === "pastille" ? "-16%" : "Ton texte ici")}&style=${k}&l=540&h=960&ancien=${enc(k === "prix" ? "79,99 €" : "")}" style="background:#333 url('${M.projet.plans[0] ? vign(M.projet.plans[0].source, .5, 200) : ""}') center/cover"><b>${esc(n)}</b></button>`).join("")}</div>
      <div class="rangee"><label class="champ" id="tx-ancien-l" ${val.style === "prix" ? "" : "hidden"}>Ancien prix (barré)<input id="tx-ancien" value="${esc(val.ancien || "")}"></label>
      <label class="champ">Animation<select id="tx-anim">${Object.entries(an).map(([k, n]) => `<option value="${k}" ${val.animation === k ? "selected" : ""}>${n}</option>`).join("")}</select></label>
      ${t ? "" : `<label class="champ">Durée<select id="tx-duree"><option>1.5</option><option selected>2.5</option><option>4</option><option value="tout">Toute la vidéo</option></select></label>`}</div>
      <div class="rangee"><button class="btn btn-accent" id="tx-ok">${t ? "Mettre à jour" : "Ajouter le texte"}</button>${t ? `<button class="btn" id="tx-nouveau">+ Nouveau texte</button>` : ""}</div>
      <p class="note">Les textes restent dans la zone sûre (ni sous le nom du compte en haut, ni sous les boutons en bas). Bouton ▣ sous la vidéo pour la voir.</p>`;
    let style = val.style;
    $$("[data-style]", c).forEach(b => b.onclick = () => { style = b.dataset.style; $$("[data-style]", c).forEach(x => x.classList.toggle("actif", x === b)); $("#tx-ancien-l", c).hidden = style !== "prix"; });
    $("#tx-ok", c).onclick = () => {
      const texte = $("#tx-texte", c).value.trim(); if (!texte) return toast("Écris d'abord un texte.");
      memoriser(); M.projet.textes = M.projet.textes || [];
      if (t) Object.assign(t, {texte, style, animation: $("#tx-anim", c).value, ancien: $("#tx-ancien", c).value});
      else {
        const dv = $("#tx-duree", c).value, id = "t" + Date.now().toString(36);
        const debut = dv === "tout" ? 0 : M.T, fin = dv === "tout" ? D.total : Math.min(D.total, M.T + +dv);
        M.projet.textes.push({id, texte, style, animation: $("#tx-anim", c).value, ancien: $("#tx-ancien", c).value, debut: +debut.toFixed(3), fin: +Math.max(debut + .3, fin).toFixed(3)});
        M.choisi = {genre: "texte", id};
      }
      $("#calque-textes").dataset.cle = ""; apresChangement(); toast(t ? "Texte mis à jour." : "Texte ajouté.");
    };
    const n = $("#tx-nouveau", c); if (n) n.onclick = () => { M.choisi = null; Panneau.rafraichir(); };
  },
  effets(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    const img = pl.source, t = pl.type === "image" ? 0 : (pl.debut + pl.fin) / 2;
    c.innerHTML = `<p class="note">Glisse un effet sur un plan de la timeline (appui long au doigt), ou touche-le pour l'appliquer au plan ${M.projet.plans.indexOf(pl) + 1}.</p>
      <div class="grille-cartes">${Object.entries(CATALOGUE.effets).map(([k, e]) => { const on = (pl.effets || []).find(f => f.type === k);
        return `<div class="carte ${on ? "actif" : ""}" data-effet="${k}" role="button"><img loading="lazy" src="/apercu/effet?chemin=${enc(img)}&type=${k}&force=0.6&t=${t.toFixed(2)}"><b>${e.nom}</b>${aide(e.nom, e.aide)}</div>`; }).join("")}</div>
      <div id="fx-reglages"></div>`;
    const reglages = () => {
      $("#fx-reglages", c).innerHTML = (pl.effets || []).map((f, k) => curseur(CATALOGUE.effets[f.type]?.nom || f.type, f.force, 0, 1, .05, "", v => { f.force = v; dessiner(); })).join("") +
        ((pl.effets || []).length ? `<button class="btn" id="fx-rien">Retirer tous les effets</button>` : "");
      const r = $("#fx-rien", c); if (r) r.onclick = () => { memoriser(); pl.effets = []; apresChangement(); };
    };
    reglages();
    $$("[data-effet]", c).forEach(el => {
      const k = el.dataset.effet;
      rendreGlissable(el, {genre: "effet", type: k}, el.innerHTML);
      el.addEventListener("click", e => { if (el._vientDeGlisser || e.target.closest(".aide")) return; memoriser(); const on = (pl.effets || []).find(f => f.type === k);
        pl.effets = on ? pl.effets.filter(f => f !== on) : [...(pl.effets || []), {type: k, force: .5}]; apresChangement(); });
    });
  },
  filtres(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    const t = pl.type === "image" ? 0 : (pl.debut + pl.fin) / 2, f = pl.look?.force ?? Panneau.forceLook;
    c.innerHTML = `<h3 style="margin-top:0">Préréglages en 1 clic</h3><div class="rangee puces">${PRESETS_1CLIC.map((p, k) => `<button data-pre="${k}" title="${esc(p[1])}">${p[0]}</button>`).join("")}</div>
      <h3>Looks <small class="note">(AVANT | APRÈS sur ton plan)</small></h3>
      <div class="grille-cartes" style="grid-template-columns:repeat(auto-fill,minmax(170px,1fr))">${Object.entries(CATALOGUE.looks).map(([k, l]) =>
        `<div class="carte large ${pl.look?.id === k ? "actif" : ""}" data-look="${k}" role="button"><img loading="lazy" src="/apercu/look?chemin=${enc(pl.source)}&look=${k}&force=${f}&t=${t.toFixed(2)}"><b>${l.nom}</b><small>${l.aide}</small></div>`).join("")}</div>
      ${curseur("Intensité", Math.round(f * 100), 0, 100, 5, " %", v => { Panneau.forceLook = v / 100; if (pl.look) { pl.look.force = v / 100; } majCss(); })}
      <div class="rangee"><button class="btn" id="lk-tout">Appliquer à toute la vidéo</button><button class="btn" id="lk-rien">Retirer le look</button>
      <button class="btn-fantome" id="lk-test">Voir le test peau</button></div>
      <p class="note">Le lecteur montre une approximation ; le rendu applique le vrai look (LUT .cube), avec la peau protégée.</p>`;
    const majCss = () => { vids.forEach(v => v.style.filter = filtreCss(M.projet.plans[M.planCourant])); $("#image-plan").style.filter = filtreCss(M.projet.plans[M.planCourant]); };
    $$("[data-look]", c).forEach(el => {
      const k = el.dataset.look;
      rendreGlissable(el, {genre: "look", type: k}, el.innerHTML);
      el.addEventListener("click", () => { if (el._vientDeGlisser) return; memoriser(); pl.look = {id: k, force: Panneau.forceLook}; apresChangement(); });
    });
    $$("[data-pre]", c).forEach(b => b.onclick = () => { memoriser(); const fn = PRESETS_1CLIC[+b.dataset.pre][2];
      if (+b.dataset.pre === 3) M.projet.plans.forEach(fn); else fn(pl); apresChangement(); toast(PRESETS_1CLIC[+b.dataset.pre][0] + " appliqué."); });
    $("#lk-tout", c).onclick = () => { if (!pl.look) return toast("Choisis d'abord un look."); memoriser(); M.projet.plans.forEach(p => p.look = {...pl.look}); apresChangement(); toast("Look appliqué à toute la vidéo."); };
    $("#lk-rien", c).onclick = () => { memoriser(); pl.look = null; apresChangement(); };
    $("#lk-test", c).onclick = testPeau;
  },
  ajuster(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    const m = pl.masque || null;
    c.innerHTML = `<div class="rangee puces"><button data-aj="remplir" class="${(pl.ajuster || "remplir") === "remplir" ? "actif" : ""}">Remplir l'écran</button><button data-aj="contenir" class="${pl.ajuster === "contenir" ? "actif" : ""}">Contenir (bandes noires)</button></div>
      <h3>Masque ${aide("Masque", "Applique un flou, des pixels ou un zoom sur une zone de l'image seulement.", "flouter une marque visible sur un ustensile")}</h3>
      <div class="rangee puces"><button data-mq="">Aucun</button>${Object.entries(CATALOGUE.masques).map(([k, n]) => `<button data-mq="${k}" class="${m?.type === k ? "actif" : ""}">${n}</button>`).join("")}</div>
      ${m ? curseur("Position X", m.x, 0, 1, .01, "", v => m.x = v) + curseur("Position Y", m.y, 0, 1, .01, "", v => m.y = v) + curseur("Largeur", m.l, .05, 1, .01, "", v => m.l = v) + curseur("Hauteur", m.h, .05, 1, .01, "", v => m.h = v) +
        `<img src="/apercu/effet?chemin=${enc(pl.source)}&type=${m.type}&force=1&t=${((pl.debut + pl.fin) / 2).toFixed(2)}" style="height:160px;border-radius:8px" alt="aperçu (zone par défaut)">` : ""}`;
    $$("[data-aj]", c).forEach(b => b.onclick = () => { memoriser(); pl.ajuster = b.dataset.aj; apresChangement(); });
    $$("[data-mq]", c).forEach(b => b.onclick = () => { memoriser(); pl.masque = b.dataset.mq ? {type: b.dataset.mq, x: .25, y: .3, l: .5, h: .3} : null; apresChangement(); });
  },
  transitions(c) {
    const plans = M.projet.plans;
    if (plans.length === 0) return pasDePlan(c);
    let cle = M.choisi?.genre === "jointure" ? M.choisi.id : null;
    if (!cle) { const i = planA(M.T); cle = i > 0 ? plans[i - 1].id : (plans.length > 1 ? plans[0].id : "debut"); }
    const idx = plans.findIndex(p => p.id === cle);
    const a = cle === "debut" ? plans[0] : cle === "fin" ? plans[plans.length - 1] : plans[idx];
    const b = cle === "debut" || cle === "fin" ? a : plans[idx + 1] || a;
    const ia = a.type === "image" ? a.source : a.source, ta = a.type === "image" ? 0 : Math.max(a.debut, a.fin - .2), tb = b.type === "image" ? 0 : b.debut + .2;
    const imgA = vign(a.source, ta, 540), imgB = vign(b.source, tb, 540);
    const tr = transitionApres(cle);
    const nomJ = cle === "debut" ? "ouverture (début de la vidéo)" : cle === "fin" ? "sortie (fin de la vidéo)" : `entre le plan ${idx + 1} et le plan ${idx + 2}`;
    const types = cle === "debut" || cle === "fin" ? ["coupe", "noir", "blanc"] : Object.keys(CATALOGUE.transitions);
    c.innerHTML = `<p class="note">Jointure choisie : <b style="color:var(--texte)">${nomJ}</b>. Glisse une transition sur n'importe quelle jointure ⊕, ou touche-la.</p>
      <div class="grille-cartes">${types.map(k => { const t = CATALOGUE.transitions[k];
        return `<div class="carte ${(tr?.type || "coupe") === k ? "actif" : ""}" data-tr="${k}" role="button"><video muted loop autoplay playsinline preload="none" src="/apercu/transition?type=${k}&a=${enc(a.source)}&b=${enc(b.source)}" poster="${imgA}"></video><b>${t.nom}</b>${aide(t.nom, t.aide)}</div>`; }).join("")}</div>
      ${tr ? curseur("Durée", tr.duree || .4, .1, 1.5, .05, " s", v => { tr.duree = v; D = dispo(); dessiner(); }) : ""}
      <div class="rangee">${cle !== "debut" && cle !== "fin" ? `<button class="btn" id="tr-toutes">Appliquer à toutes les jointures</button>` : ""}${tr ? `<button class="btn" id="tr-retirer">Retirer</button>` : ""}</div>`;
    $$("[data-tr]", c).forEach(el => {
      const k = el.dataset.tr;
      rendreGlissable(el, {genre: "transition", type: k}, `<video muted autoplay loop src="/apercu/transition?type=${k}&a=${enc(a.source)}&b=${enc(b.source)}"></video><b>${CATALOGUE.transitions[k].nom}</b>`);
      el.addEventListener("click", e => { if (el._vientDeGlisser || e.target.closest(".aide")) return; appliquerTransition(cle, k); M.choisi = {genre: "jointure", id: cle}; dessiner(); Panneau.rafraichir(); });
    });
    const toutes = $("#tr-toutes", c); if (toutes) toutes.onclick = () => { const t = transitionApres(cle); if (!t) return toast("Choisis d'abord une transition."); memoriser();
      M.projet.transitions = (M.projet.transitions || []).filter(x => x.apres === "debut" || x.apres === "fin"); plans.slice(0, -1).forEach(p => M.projet.transitions.push({...t, apres: p.id})); apresChangement(); toast("Appliqué à toutes les jointures."); };
    const ret = $("#tr-retirer", c); if (ret) ret.onclick = () => { appliquerTransition(cle, "coupe"); Panneau.rafraichir(); };
  },
  async sons(c) {
    const s = selection("son");
    c.innerHTML = (s ? `<div class="ligne"><div class="grand"><b>${esc(nomFichier(s.source))}</b><small>${esc(s.type)} · commence à ${fmtTc(s.debut)}</small></div>
        <select id="sn-type"><option value="musique" ${s.type === "musique" ? "selected" : ""}>Musique</option><option value="bruitage" ${s.type === "bruitage" ? "selected" : ""}>Bruitage</option><option value="voix" ${s.type === "voix" ? "selected" : ""}>Voix / son principal</option></select></div>
        ${curseur("Volume", Math.round((+s.volume ?? 1) * 100), 0, 200, 5, " %", v => { s.volume = v / 100; dessiner(); })}<hr style="border-color:var(--ligne)">` : "") +
      `<p class="note">Sons trouvés dans tes dossiers (AgentsAds, Musique, Téléchargements). « Ajouter » le pose à la tête de lecture (${fmtTc(M.T)}).</p><div class="liste" id="sn-liste">Recherche…</div>`;
    if (s) $("#sn-type", c).onchange = e => { memoriser(); s.type = e.target.value; apresChangement(); };
    const liste = await api("/api/sons");
    $("#sn-liste", c).innerHTML = liste.length ? liste.slice(0, 120).map((x, k) => `<div class="ligne"><div class="grand"><b>${esc(x.nom)}</b><small>${esc(x.dossier)}</small></div>
      <button class="btn-icone petit" data-ecoute="${k}" title="Écouter">▶</button>
      <select data-type="${k}"><option value="musique">Musique</option><option value="bruitage">Bruitage</option><option value="voix">Voix</option></select>
      <button class="btn" data-ajout="${k}">Ajouter</button></div>`).join("") : `<p class="note">Aucun son trouvé.</p>`;
    let lecteurSon = null;
    $$("[data-ecoute]", c).forEach(b => b.onclick = async () => { const x = liste[+b.dataset.ecoute]; lecteurSon?.pause();
      let ch = x.chemin; if (!x.dans_projet) { ch = (await api("/api/sons/importer", {json: {chemin: x.chemin}})).chemin; x.chemin = ch; x.dans_projet = true; }
      lecteurSon = new Audio(media(ch)); lecteurSon.play(); });
    $$("[data-ajout]", c).forEach(b => b.onclick = async () => {
      const x = liste[+b.dataset.ajout]; let ch = x.chemin;
      try { if (!x.dans_projet) ch = (await api("/api/sons/importer", {json: {chemin: x.chemin}})).chemin; else ch = (await api("/api/sons/importer", {json: {chemin: x.chemin}})).chemin; } catch (e) { return toast(e.message); }
      memoriser(); const id = "s" + Date.now().toString(36); const type = $(`[data-type="${b.dataset.ajout}"]`, c).value;
      M.projet.sons = M.projet.sons || []; M.projet.sons.push({id, source: ch, type, debut: +M.T.toFixed(3), volume: type === "musique" ? .6 : 1});
      M.choisi = {genre: "son", id}; apresChangement(); toast(`${esc(x.nom)} ajouté.`);
    });
  },
  marqueur(c) {
    c.innerHTML = `<label class="champ">Commentaire au repère ${fmtTc(M.T)}<textarea id="mq-texte" rows="2" placeholder="Ex. « ça ne va pas ici : le texte arrive trop tôt »"></textarea></label>
      <div class="rangee"><button class="btn btn-accent" id="mq-ok">Poser le repère</button></div>
      <h3>Repères du projet</h3><div class="liste">${M.reperes.length ? M.reperes.slice().sort((a, b) => a.t - b.t).map(r => `<div class="ligne"><span style="color:var(--jaune)">⚑</span><div class="grand"><b>${fmtTc(r.t)}</b><small>${esc(r.texte)}</small></div><button class="btn" data-aller="${r.t}">Aller</button><button class="btn-icone petit" data-suppr="${r.id}" title="Retirer">✕</button></div>`).join("") : `<p class="note">Aucun repère.</p>`}</div>`;
    $("#mq-ok", c).onclick = async () => {
      const texte = $("#mq-texte", c).value.trim(); if (!texte) return toast("Écris ce qui ne va pas.");
      const i = planA(M.T);
      const r = await api(`/api/projets/${enc(M.projet.id)}/reperes`, {json: {t: M.T, texte, plan: M.projet.plans[i]?.id}});
      M.reperes.push(r); dessiner(); Panneau.rafraichir(); toast("Repère posé et envoyé à Claude.");
    };
    $$("[data-aller]", c).forEach(b => b.onclick = () => allerA(+b.dataset.aller));
    $$("[data-suppr]", c).forEach(b => b.onclick = async () => { await api(`/api/projets/${enc(M.projet.id)}/reperes/${b.dataset.suppr}`, {method: "DELETE"}); M.reperes = M.reperes.filter(r => r.id !== b.dataset.suppr); dessiner(); Panneau.rafraichir(); });
  },
  async remplacer(c) {
    const pl = selection("plan"); if (!pl) return pasDePlan(c);
    c.innerHTML = `<p class="note">Choisis la vidéo ou l'image qui remplace le plan ${M.projet.plans.indexOf(pl) + 1}. La durée à l'écran est gardée si possible.</p><div class="grille-creas" id="rp-liste">Chargement…</div>`;
    const creas = await api("/api/creas");
    $("#rp-liste", c).innerHTML = creas.slice(0, 80).map((x, k) => `<div class="crea ${x.type}" data-k="${k}"><span class="type">${x.type === "video" ? "vidéo" : "image"}</span><img loading="lazy" src="${vign(x.chemin, .5, 200)}"><small>${esc(nomFichier(x.chemin))}</small></div>`).join("");
    $$("[data-k]", c).forEach(el => el.onclick = async () => {
      const x = creas[+el.dataset.k], info = await api("/api/media/info?chemin=" + enc(x.chemin)); memoriser();
      const garde = dureePlan(pl) * (+pl.vitesse || 1); pl.source = x.chemin; pl.type = x.type;
      if (x.type === "image") { pl.duree = dureePlan(pl); pl.debut = 0; pl.fin = pl.duree; }
      else { pl.debut = 0; pl.fin = +Math.min(info.duree || garde, garde).toFixed(3); pl.duree_source = info.duree; pl.a_son = !!info.audio_hz; }
      apresChangement(); toast("Plan remplacé.");
    });
  },
};

async function testPeau() {
  modale(`<h2>Test peau des looks</h2><p class="note">Calcul en cours…</p>`);
  const r = await api("/api/looks/test?projet=" + enc(M.projet?.id || ""));
  const lignes = Object.entries(r.looks).map(([k, v]) => `<tr><td>${CATALOGUE.looks[k].nom}</td>${v.protection ? `<td colspan="3">${esc(v.protection)}</td>` :
    `<td>${fmtNb(v.sat_min, 3)} – ${fmtNb(v.sat_max, 3)}</td><td>≥ ${fmtNb(v.lum_min, 3)}</td><td style="color:${v.ok ? "var(--ok)" : "var(--ko)"}">${v.ok ? "OK" : "À revoir"}</td>`}</tr>`).join("");
  modale(`<h2>Test peau des looks</h2><p class="note">10 teintes de peau (de très claire à très foncée), 3 éclairages chacune, mesurées après passage dans ffmpeg. Règle : saturation de la peau entre 0,95 et 1,05 fois l'originale, luminosité jamais sous 0,9 fois.</p>
    <img src="/cache/test_peau/planche_peau.png?${Date.now()}" style="width:100%;border-radius:8px">
    <table style="width:100%;font-size:13px;margin-top:10px"><tr><th align="left">Look</th><th align="left">Saturation peau</th><th align="left">Luminosité</th><th></th></tr>${lignes}</table>
    ${r.limite ? `<p class="note">${esc(r.limite)}</p>` : ""}
    ${(r.images_reelles || []).length ? `<h3>Sur 3 images de ton projet</h3><p class="note">Pixels à teinte de peau (mains, mais aussi bois, jaune d'œuf…) : part qui reste dans la règle avec le look à 100 %.</p>
    <table style="width:100%;font-size:12px"><tr><th align="left">Look</th>${r.images_reelles.map((x, k) => `<th>Image ${k + 1}</th>`).join("")}</tr>
    ${Object.keys(r.images_reelles[0].looks).map(k => `<tr><td>${CATALOGUE.looks[k].nom}</td>${r.images_reelles.map(x => `<td align="center">${x.looks[k] ? fmtNb(x.looks[k].dans_regle_pct, 1) + " %" : "—"}</td>`).join("")}</tr>`).join("")}</table>` : ""}`);
}

/* ============================================================ clavier */
document.addEventListener("keydown", e => {
  if (Onglets.actif !== "montage" || e.target.matches("input,textarea,select")) return;
  if (e.code === "Space") { e.preventDefault(); lecture(); }
  else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "z") { e.preventDefault(); e.shiftKey ? refaire() : annuler(); }
  else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") { e.preventDefault(); $("#btn-enregistrer").click(); }
  else if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); supprimer(); }
  else if (e.key.toLowerCase() === "s") couper();
  else if (e.key.toLowerCase() === "m") Panneau.ouvrir("marqueur");
  else if (e.key === "ArrowRight") allerA(M.T + (e.shiftKey ? 1 : 1 / IPS));
  else if (e.key === "ArrowLeft") allerA(M.T - (e.shiftKey ? 1 : 1 / IPS));
  else if (e.key === "Escape") { Panneau.fermer(); choisir(null); }
});
window.addEventListener("beforeunload", e => { if (M.modifie) { e.preventDefault(); e.returnValue = ""; } });
window.addEventListener("resize", () => { if (M.projet) allerA(M.T); Panneau.placer(); });

Onglets.auChangement.montage = () => { if (!M.projet) listerProjets(); else requestAnimationFrame(() => allerA(M.T)); };
