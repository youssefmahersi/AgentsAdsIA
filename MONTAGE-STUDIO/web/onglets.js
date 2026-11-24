/* Studio Ads : onglets Générations, Bibliothèque, Exporter, Comparer, Claude, Références. */
"use strict";

/* ============================================================ GÉNÉRATIONS */
const Gen = {
  liste: [], phrase: "",
  async charger() {
    try {
      const d = await api("/api/generations");
      this.liste = d.liste; this.phrase = d.phrase;
      const n = d.compteurs.en_cours; const p = $("#nb-en-cours"); p.hidden = !n; p.textContent = n;
      if (Onglets.actif === "generations") this.dessiner();
    } catch {}
  },
  filtrer() {
    const per = $("#gen-periode").value, proj = $("#gen-projet").value, type = $("#gen-type").value, etat = $("#gen-etat").value, q = $("#gen-recherche").value.toLowerCase();
    const auj = new Date().toISOString().slice(0, 10), lim = Date.now() - 7 * 864e5;
    return this.liste.filter(g => {
      if (per === "jour" && !(g.date || "").startsWith(auj)) return false;
      if (per === "7" && new Date(g.date) < lim) return false;
      if (proj && (g.projet || "—") !== proj) return false;
      if (type && g.type !== type) return false;
      if (etat && g.etat !== etat) return false;
      if (q && !(g.prompt || "").toLowerCase().includes(q)) return false;
      return true;
    });
  },
  dessiner() {
    const projs = [...new Set(this.liste.map(g => g.projet || "—"))].sort();
    const sel = $("#gen-projet"), v = sel.value;
    sel.innerHTML = `<option value="">Tous les projets</option>` + projs.map(p => `<option ${p === v ? "selected" : ""}>${esc(p)}</option>`).join("");
    const l = this.filtrer();
    const c = {total: l.length, cours: l.filter(g => ["envoyé", "en file", "en cours"].includes(g.etat)).length, echecs: l.filter(g => g.etat === "échec").length,
      credits: l.reduce((s, g) => s + (+g.credits || 0), 0), usd: l.reduce((s, g) => s + (+g.cout_usd || 0), 0)};
    $("#gen-compteurs").innerHTML = [[c.total, "générations"], [c.cours, "en cours"], [c.echecs, "échecs"], [fmtNb(c.credits, 1), "crédits kie consommés"], [fmtNb(c.usd, 3) + " $", "Gemini (estimé)"]]
      .map(([n, t]) => `<div class="compteur"><b>${n}</b><span>${t}</span></div>`).join("");
    $("#gen-note").innerHTML = (ETAT.cle_kie ? "" : "Clé kie absente au lancement du studio : le suivi en direct chez kie.ai est en pause (le journal reste lu). ") +
      "Rafraîchi toutes les 5 s · état vérifié chez kie.ai toutes les 20 s pour les tâches en cours. Aucune clé n'est jamais affichée.";
    if (!l.length) { $("#gen-liste").innerHTML = `<p class="note">Aucune génération pour ces filtres. Essaie « Tout » dans la période.</p>`; return; }
    const ouverts = new Set($$("#gen-liste details[open]").map(d => d.dataset.id));
    $("#gen-liste").innerHTML = l.slice(0, 150).map(g => {
      const f = g.fichiers?.[0];
      const med = f ? (f.type === "video" ? `<video src="${media(f.chemin)}" controls muted preload="metadata" playsinline></video>` : `<img loading="lazy" src="${media(f.chemin)}">`)
        : `<div class="rien">${g.etat === "fini" ? "Fichier non noté dans le journal (génération faite avant le studio, ou sans dossier de sortie)." : g.etat === "échec" ? "Échec : " + esc(g.erreur || "") : "En attente du résultat…" + (g.progression ? ` ${g.progression} %` : "")}</div>`;
      const params = [g.modele, g.resolution, g.duree && g.duree + " s", g.ratio, g.plan && "plan " + g.plan, g.essai && "essai " + g.essai].filter(Boolean);
      return `<article class="gen"><div class="gen-media">${med}</div><div class="gen-corps">
        <div class="gen-tete"><span class="etat etat-${g.etat.replace(/\s/g, "-")}">${esc(g.etat)}</span><span>${esc(g.fournisseur)}</span><span>${esc((g.date || "").replace("T", " "))}</span>${g.projet ? `<span>· ${esc(g.projet)}</span>` : ""}</div>
        <div class="params">${params.map(p => `<span>${esc(p)}</span>`).join("")}${f?.probable ? `<span title="Le journal de l'époque ne notait pas le fichier : rapproché par l'heure d'écriture">fichier probable</span>` : ""}</div>
        <details data-id="${esc(g.id)}" ${ouverts.has(g.id) ? "open" : ""}><summary class="note">Prompt exact</summary><div class="prompt">${esc(g.prompt)}</div></details>
        ${g.image_debut ? `<div class="note">Image de départ : ${esc(nomFichier(g.image_debut))}</div>` : ""}${g.refs ? `<div class="note">Références : ${esc(Array.isArray(g.refs) ? g.refs.map(nomFichier).join(", ") : g.refs)}</div>` : ""}
        ${g.motif ? `<div class="note">Motif : ${esc(g.motif)}</div>` : ""}
        <div class="gen-pied"><span class="cout">${g.credits != null ? `${fmtNb(g.credits, 1)} crédits` : g.cout_estime != null ? `≈ ${fmtNb(g.cout_estime, 1)} crédits estimés` : g.cout_usd != null ? `≈ ${fmtNb(g.cout_usd, 3)} $` : ""}</span>
        ${f ? `<button class="btn" data-ajout-gen="${esc(f.chemin)}">+ Au montage</button>` : ""}
        ${g.fournisseur === "kie.ai" && g.alias ? `<button class="btn" data-relancer="${esc(g.id)}">Relancer modifié</button>` : ""}</div></div></article>`;
    }).join("");
    $$("[data-relancer]").forEach(b => b.onclick = () => this.relancer(b.dataset.relancer));
    $$("[data-ajout-gen]").forEach(b => b.onclick = () => ajouterAuMontage([b.dataset.ajoutGen]));
  },
  relancer(id) {
    const g = this.liste.find(x => x.id === id);
    modale(`<h2>Relancer avec un prompt modifié</h2><p class="note">${esc(g.modele)} · ${esc(g.type)}. Étape 1 : préparer à blanc (gratuit, rien n'est envoyé). Étape 2 : confirmer la dépense.</p>
      <label class="champ">Prompt<textarea id="rl-prompt" rows="8">${esc(g.prompt)}</textarea></label>
      <div class="rangee"><button class="btn" id="rl-blanc">1. Préparer à blanc</button></div><div id="rl-res"></div>`, c => {
      $("#rl-blanc", c).onclick = async () => {
        $("#rl-res", c).innerHTML = `<p class="note">Préparation…</p>`;
        const r = await api("/api/generations/preparer", {json: {id, prompt: $("#rl-prompt", c).value}});
        if (!r.ok && !r.apercu) { $("#rl-res", c).innerHTML = `<p class="note" style="color:var(--ko)">${esc(r.message)}</p>`; return; }
        $("#rl-res", c).innerHTML = `${r.avertissement ? `<p style="color:var(--attente)">${esc(r.avertissement)}</p>` : ""}<pre>${esc(r.apercu)}</pre>${r.cout ? `<p><b>Coût annoncé : ${esc(r.cout)} crédits</b></p>` : ""}
          <label class="champ">2. Pour dépenser, tape exactement : <b style="color:var(--texte)">${esc(this.phrase)}</b><input id="rl-phrase" autocomplete="off" spellcheck="false"></label>
          <button class="btn btn-danger" id="rl-go" disabled>Lancer la génération (payant)</button>`;
        const ph = $("#rl-phrase", c), go = $("#rl-go", c);
        ph.oninput = () => go.disabled = ph.value.trim().toUpperCase() !== this.phrase;
        go.onclick = async () => {
          const res = await api("/api/generations/lancer", {json: {id, prompt: $("#rl-prompt", c).value, phrase: ph.value}});
          toast(esc(res.message), 4000); if (res.ok) fermerModale();
        };
      };
    });
  },
};
["#gen-periode", "#gen-projet", "#gen-type", "#gen-etat"].forEach(s => $(s).onchange = () => Gen.dessiner());
$("#gen-recherche").oninput = () => Gen.dessiner();
Onglets.auChangement.generations = () => Gen.charger().then(() => Gen.dessiner());
setInterval(() => Gen.charger(), 5000); Gen.charger();

async function ajouterAuMontage(chemins) {
  if (!M.projet) { Onglets.aller("montage"); await listerProjets(); }
  memoriser();
  for (const ch of chemins) {
    const info = await api("/api/media/info?chemin=" + enc(ch));
    const img = /\.(png|jpe?g|webp|gif)$/i.test(ch);
    M.projet.plans.push(img ? {id: "p" + Math.random().toString(36).slice(2, 8), source: ch, type: "image", duree: 2, debut: 0, fin: 2, vitesse: 1, volume: 1, effets: [], look: null}
      : {id: "p" + Math.random().toString(36).slice(2, 8), source: ch, type: "video", debut: 0, fin: +(info.duree || 3).toFixed(3), duree_source: info.duree, a_son: !!info.audio_hz, vitesse: 1, volume: 1, effets: [], look: null});
  }
  Onglets.aller("montage"); apresChangement(); toast(`${chemins.length} plan(s) ajouté(s) à la fin de « ${esc(M.projet.nom)} ». Pense à Enregistrer.`);
}

/* ============================================================ BIBLIOTHÈQUE */
const Biblio = {
  sous: "creas", choix: new Set(), creas: [],
  aller(s) { this.sous = s; $$("#biblio-onglets button").forEach(b => b.classList.toggle("actif", b.dataset.sous === s)); this.dessiner(); },
  imageTest() { const p = M.projet?.plans?.[0]; return p ? {chemin: p.source, t: p.type === "image" ? 0 : (p.debut + p.fin) / 2} : null; },
  jeton: 0,
  async dessiner() {
    const c = $("#biblio-corps"); const s = this.sous; const jeton = ++this.jeton;
    const perime = () => jeton !== this.jeton;
    if (s === "creas") {
      c.innerHTML = `<p class="note">Tout ce que l'équipe produit (statics de hamid, vidéos de ziad, générations, exports) apparaît ici, rangé par dossier, avec le verdict d'omar quand il existe. Coche des fichiers pour en faire un projet de montage.</p><div id="cr-liste">Chargement…</div>`;
      const creas = await api("/api/creas"); if (perime()) return; this.creas = creas;
      const groupes = {};
      for (const x of this.creas) (groupes[x.dossier] = groupes[x.dossier] || []).push(x);
      $("#cr-liste").innerHTML = Object.entries(groupes).slice(0, 60).map(([d, l]) => {
        const v = l[0].controle;
        return `<div class="groupe"><div class="groupe-tete"><h3>${esc(d)}</h3>${l[0].livre ? `<span class="etiq v1">livré</span>` : ""}${l[0].concurrent ? `<span class="etiq">concurrent</span>` : ""}
          ${v?.verdict ? `<span class="verdict ${v.verdict}">omar : ${v.verdict}</span>` : ""}${v ? `<a class="note" href="${ETAT.lecteur || "http://127.0.0.1:8765/"}#/f/${enc("projet/" + v.fichier)}" target="_blank" rel="noopener">ouvrir le LISEZ-MOI</a>` : ""}</div>
          <div class="grille-creas">${l.slice(0, 40).map(x => `<div class="crea ${x.type} ${this.choix.has(x.chemin) ? "choisie" : ""}" data-chemin="${esc(x.chemin)}"><span class="type">${x.type === "video" ? "vidéo" : "image"}</span><span class="coche" data-coche="1"></span><img loading="lazy" src="${vign(x.chemin, .5, 260)}"><small>${esc(nomFichier(x.chemin))}</small></div>`).join("")}</div></div>`;
      }).join("") + `<div class="barre-selection" id="cr-barre" ${this.choix.size ? "" : "hidden"}><b id="cr-nb"></b><span class="espace"></span><button class="btn" id="cr-vider">Tout décocher</button><button class="btn" id="cr-ajout">Ajouter au projet ouvert</button><button class="btn btn-accent" id="cr-nouveau">Nouveau projet avec la sélection</button></div>`;
      const maj = () => { $("#cr-barre").hidden = !this.choix.size; $("#cr-nb").textContent = `${this.choix.size} fichier(s) choisi(s)`; };
      maj();
      $$("#cr-liste .crea").forEach(el => el.onclick = e => {
        const ch = el.dataset.chemin;
        if (e.target.dataset.coche || this.choix.size) { this.choix.has(ch) ? this.choix.delete(ch) : this.choix.add(ch); el.classList.toggle("choisie"); maj(); return; }
        const x = this.creas.find(y => y.chemin === ch);
        modale(`${x.type === "video" ? `<video class="visionneuse" src="${media(ch)}" controls autoplay playsinline></video>` : `<img class="visionneuse" src="${media(ch)}">`}
          <p class="note">${esc(ch)}</p><div class="rangee"><button class="btn" id="vz-choix">Cocher</button><button class="btn" id="vz-ajout">+ Au montage</button></div>`, m => {
          $("#vz-choix", m).onclick = () => { this.choix.add(ch); el.classList.add("choisie"); maj(); fermerModale(); };
          $("#vz-ajout", m).onclick = () => { fermerModale(); ajouterAuMontage([ch]); };
        });
      });
      $("#cr-vider").onclick = () => { this.choix.clear(); this.dessiner(); };
      $("#cr-ajout").onclick = () => { const l = [...this.choix]; this.choix.clear(); ajouterAuMontage(l); };
      $("#cr-nouveau").onclick = async () => {
        const nom = prompt("Nom du nouveau projet ?", "Nouveau montage"); if (!nom) return;
        const r = await api("/api/projets", {json: {nom, medias: [...this.choix]}}); this.choix.clear();
        Onglets.aller("montage"); M.modifie = false; await listerProjets(r.id); toast("Projet créé.");
      };
    } else if (s === "fiches") {
      const l = await api("/api/fiches"); if (perime()) return;
      c.innerHTML = `<p class="note">Les fiches de karim (FICHE-SOURCE) et les fiches produit validées (PRODUIT.md). Elles s'ouvrent dans le lecteur web (lancé à part : <code>python3 outils/lecteur.py</code>).</p><div class="liste">` +
        l.map(f => `<div class="ligne"><div class="grand"><b>${esc(f.nature)}</b><small>${esc(f.chemin)}</small></div><a class="btn" href="${ETAT.lecteur || "http://127.0.0.1:8765/"}#/f/${enc("projet/" + f.chemin)}" target="_blank" rel="noopener">Ouvrir</a></div>`).join("") + `</div>`;
    } else if (s === "transitions") {
      const it = this.imageTest(), p = M.projet?.plans || [];
      const a = p[0]?.source, b = (p[1] || p[0])?.source;
      c.innerHTML = `<p class="note">Aperçus animés faits avec deux plans de ton projet. Dans le Montage, glisse-les sur une jointure ⊕.</p><div class="grille-cartes">` +
        Object.entries(CATALOGUE.transitions).map(([k, t]) => `<div class="carte">${a ? `<video muted loop autoplay playsinline src="/apercu/transition?type=${k}&a=${enc(a)}&b=${enc(b)}"></video>` : ""}<b>${t.nom}</b><small>${t.aide}</small><span class="etiq v1">V1</span></div>`).join("") + `</div>`;
    } else if (s === "looks") {
      const it = this.imageTest();
      c.innerHTML = `<p class="note">9 looks fabriqués en LUT .cube (fichiers dans <code>MONTAGE-STUDIO/luts/</code>). Chaque look couleur protège la peau. Aperçu AVANT | APRÈS sur ton projet.</p>
        <div class="rangee"><button class="btn" id="lk-test2">Voir la planche du test peau</button></div>
        <div class="grille-cartes" style="grid-template-columns:repeat(auto-fill,minmax(220px,1fr))">` +
        Object.entries(CATALOGUE.looks).map(([k, l]) => `<div class="carte large">${it ? `<img loading="lazy" src="/apercu/look?chemin=${enc(it.chemin)}&look=${k}&force=1&t=${it.t}">` : ""}<b>${l.nom}</b><small>${l.aide}</small></div>`).join("") + `</div>`;
      $("#lk-test2").onclick = testPeau;
    } else if (s === "effets") {
      const it = this.imageTest();
      c.innerHTML = `<h3>Effets visuels</h3><div class="grille-cartes">` + Object.entries(CATALOGUE.effets).map(([k, e]) => `<div class="carte">${it ? `<img loading="lazy" src="/apercu/effet?chemin=${enc(it.chemin)}&type=${k}&force=0.7&t=${it.t}">` : ""}<b>${e.nom}</b><small>${e.aide}</small></div>`).join("") +
        `</div><h3>Masques</h3><div class="grille-cartes">` + Object.entries(CATALOGUE.masques).map(([k, n]) => `<div class="carte">${it ? `<img loading="lazy" src="/apercu/effet?chemin=${enc(it.chemin)}&type=${k}&force=1&t=${it.t}">` : ""}<b>${n}</b></div>`).join("") + `</div>`;
    } else if (s === "motion") {
      const fond = M.projet?.plans?.[0] ? vign(M.projet.plans[0].source, .5, 300) : "";
      const ex = {"prix": ["59,99 €", "79,99 €"], "pastille": ["-16%", ""], "cta": ["Je commande", ""], "hook": ["Ta poêle colle encore ?", ""], "nom": ["Sarah, 34 ans", ""], "titre": ["Le test des 30 jours", ""]};
      c.innerHTML = `<p class="note">Titres, cartons et sous-titres. Tous sont placés dans la zone sûre des Reels (ni en haut sous le nom du compte, ni en bas sous les boutons). Animations : fondu, glisse du bas, pop.</p><div class="grille-cartes" style="grid-template-columns:repeat(auto-fill,minmax(150px,1fr))">` +
        Object.entries(CATALOGUE.styles).map(([k, n]) => { const [t, an] = ex[k] || ["Ton texte ici", ""]; return `<div class="carte"><img loading="lazy" src="/apercu/texte?texte=${enc(t)}&style=${k}&l=540&h=960&ancien=${enc(an)}" style="background:#333 url('${fond}') center/cover"><b>${esc(n)}</b></div>`; }).join("") + `</div>`;
    } else if (s === "sons") {
      c.innerHTML = `<p class="note">Bruitages, musiques et voix trouvés dans AgentsAds, Musique et Téléchargements. « Importer » copie le fichier dans <code>MONTAGE-STUDIO/sons/</code> (l'original ne bouge pas).</p><div class="liste" id="sn-l">Recherche…</div>`;
      const l = await api("/api/sons"); if (perime()) return;
      $("#sn-l").innerHTML = l.length ? l.map((x, k) => `<div class="ligne"><div class="grand"><b>${esc(x.nom)}</b><small>${esc(x.dossier)}</small></div>${x.dans_projet ? `<audio controls preload="none" src="${media(x.chemin.replace(/^.*?AgentsAds\//, ""))}"></audio><span class="etiq v1">dans le projet</span>` : `<button class="btn" data-imp="${k}">Importer</button>`}</div>`).join("") : `<p class="note">Aucun son trouvé.</p>`;
      $$("[data-imp]").forEach(b => b.onclick = async () => { const r = await api("/api/sons/importer", {json: {chemin: l[+b.dataset.imp].chemin}}); toast("Importé : " + esc(r.chemin)); this.dessiner(); });
    } else if (s === "catalogue") {
      const v2 = [["Images clés", "Animer position, zoom, opacité dans le temps."], ["Rampes de vitesse", "Ralenti progressif au milieu d'un plan."], ["Pistes vidéo superposées", "Picture-in-picture, incrustation d'un 2e plan."],
        ["Suivi de mouvement", "Un texte qui suit un objet."], ["Fond vert", "Détourer une personne ou un produit."], ["Roues et courbes de couleur", "Étalonnage fin, plan par plan."],
        ["Sous-titres modifiables mot à mot", "Transcription automatique et style karaoké."], ["Glisser depuis la Bibliothèque", "Déposer une créa directement dans la timeline."], ["Relance Gemini depuis le studio", "Comme pour kie.ai, avec confirmation."]];
      c.innerHTML = `<p class="note">Ce qui n'est pas encore utilisable dans le studio. Un clic sur « Demander à Claude » envoie la demande dans la boîte d'ordres.</p><div class="catalogue">` +
        v2.map(([n, d]) => `<div class="ligne"><div class="grand"><b>${n}</b><small style="white-space:normal">${d}</small></div><span class="etiq v2">V2</span><button class="btn" data-demande="${esc(n)}">Demander à Claude</button></div>`).join("") + `</div>`;
      $$("[data-demande]").forEach(b => b.onclick = async () => { await api("/api/ordres", {json: {texte: `Ajoute au studio : ${b.dataset.demande}`}}); toast("Demande envoyée dans l'onglet Claude."); });
    }
  },
};
$$("#biblio-onglets button").forEach(b => b.onclick = () => Biblio.aller(b.dataset.sous));
Onglets.auChangement.bibliotheque = () => Biblio.dessiner();

/* ============================================================ EXPORTER */
const Exp = {
  async dessiner() {
    const projs = await api("/api/projets");
    const sel = $("#exp-projet"), v = sel.value || M.projet?.id;
    sel.innerHTML = projs.map(p => `<option value="${esc(p.id)}" ${p.id === v ? "selected" : ""}>${esc(p.nom)} (${p.version})</option>`).join("");
    const aides = {reels: "1080×1920 · H.264 · 30 i/s · ~10 Mb/s · AAC 48 kHz · −14 LUFS", telephone: "Même format, compressé sous 30 Mo pour l'envoyer par message", carre: "1080×1080, recadré au centre", portrait: "1080×1350, le format le plus grand dans le fil", vitesse108: "Un peu plus rapide : souvent meilleure rétention", vitesse112: "Encore plus nerveux", extrait: "5 s à partir du début réglé (Avancé) ou de la tête de lecture", apercu: "Petit fichier rapide pour vérifier"};
    $("#exp-presets").innerHTML = Object.entries(CATALOGUE.presets).map(([k, n]) => `<button class="preset" data-preset="${k}"><b>${n}</b><small>${aides[k] || ""}</small></button>`).join("");
    $$("#exp-presets .preset").forEach(b => b.onclick = async () => {
      const pid = $("#exp-projet").value;
      const projet = M.projet && M.projet.id === pid ? M.projet : (await api(`/api/projets/${enc(pid)}`)).projet;
      const debut = document.body.dataset.mode === "avance" ? +$("#exp-extrait").value : M.T;
      await api("/api/rendu", {json: {projet, preset: b.dataset.preset, extrait_debut: debut}});
      toast("Export lancé."); this.travaux();
    });
    this.travaux(); this.fichiers();
  },
  async travaux() {
    const l = await api("/api/rendus");
    $("#exp-travaux").innerHTML = l.length ? l.slice(0, 12).map(t => {
      const v = t.verif;
      return `<div class="travail"><div class="rangee" style="margin:0"><b>${esc(CATALOGUE.presets[t.preset] || t.preset)}</b><span class="note">· ${esc(t.projet)}</span><span class="espace"></span><span class="etat etat-${t.etat.replace(/\s/g, "-") === "fini" ? "fini" : t.etat === "échec" ? "échec" : "en-cours"}">${esc(t.etat)}</span>
        ${t.etat === "en cours" ? `<button class="btn" data-pause="${t.id}">Pause</button>` : t.etat === "en pause" ? `<button class="btn" data-reprendre="${t.id}">Reprendre</button>` : ""}</div>
        <div class="barre"><i style="width:${t.progression}%"></i></div><div class="note">${esc(t.message)}</div>
        ${v ? `<div class="verif"><span class="${v.ok ? "ok" : "ko"}">${v.ok ? "✔ contrôle OK" : "✖ contrôle à revoir"}</span><span>${esc(v.dimensions)}</span><span>${fmtNb(v.ips)} i/s</span><span>${v.audio_hz} Hz</span><span>${v.lufs} LUFS</span><span>${fmtNb(v.duree)} s</span><span>${fmtNb(v.taille_mo)} Mo</span></div>` : ""}
        ${t.sortie ? `<div class="rangee"><a class="btn" href="${media(t.sortie)}" download>Télécharger</a><button class="btn" data-cmp="${esc(t.sortie)}">Comparer</button></div>` : ""}
        <details><summary class="note">Journal</summary><pre class="prompt" data-journal="${t.id}"></pre></details></div>`;
    }).join("") : `<p class="note">Aucun rendu pour l'instant.</p>`;
    $$("[data-pause]").forEach(b => b.onclick = async () => { await api(`/api/rendus/${b.dataset.pause}/pause`, {method: "POST"}); this.travaux(); });
    $$("[data-reprendre]").forEach(b => b.onclick = async () => { await api(`/api/rendus/${b.dataset.reprendre}/reprendre`, {method: "POST"}); this.travaux(); });
    $$("[data-cmp]").forEach(b => b.onclick = () => { Cmp.choisirB = b.dataset.cmp; Onglets.aller("comparer"); });
    $$("details [data-journal]").forEach(p => p.parentElement.ontoggle = async () => { if (p.parentElement.open) p.textContent = (await api(`/api/rendus/${p.dataset.journal}/journal`)).texte; });
  },
  async fichiers() {
    const l = await api("/api/exports");
    $("#exp-fichiers").innerHTML = l.length ? l.slice(0, 40).map(f => `<div class="ligne"><img src="${vign(f.chemin, .5, 80)}" style="height:56px;border-radius:5px"><div class="grand"><b>${esc(f.nom)}</b><small>${esc(f.dimensions)} · ${fmtNb(f.duree)} s · ${fmtNb(f.taille_mo)} Mo</small></div><a class="btn" href="${media(f.chemin)}" download>Télécharger</a></div>`).join("") : `<p class="note">Aucun fichier exporté.</p>`;
  },
};
Onglets.auChangement.exporter = () => Exp.dessiner();
setInterval(() => { if (Onglets.actif === "exporter" && !$$("#exp-travaux details[open]").length) Exp.travaux(); }, 2000);

/* ============================================================ COMPARER */
const Cmp = {
  choisirB: null, sources: [],
  async dessiner() {
    const [exps, refs, creas] = await Promise.all([api("/api/exports"), api("/api/references"), api("/api/creas")]);
    this.sources = [
      ...refs.flatMap(r => r.fichiers.filter(f => f.type === "video").map(f => ({c: f.chemin, n: "Référence · " + nomFichier(f.chemin)}))),
      ...exps.map(f => ({c: f.chemin, n: "Export · " + f.nom})),
      ...creas.filter(x => x.type === "video").map(x => ({c: x.chemin, n: (x.concurrent ? "Concurrent · " : "Créa · ") + nomFichier(x.chemin)})),
    ];
    const opts = this.sources.map((s, k) => `<option value="${k}">${esc(s.n)}</option>`).join("");
    const va = $("#cmp-a").value, vb = $("#cmp-b").value;
    $("#cmp-a").innerHTML = opts; $("#cmp-b").innerHTML = opts;
    const ia = va || this.sources.findIndex(s => s.n.startsWith("Concurrent") || s.n.startsWith("Référence"));
    $("#cmp-a").value = ia >= 0 ? ia : 0;
    let ib = vb || this.sources.findIndex(s => s.n.startsWith("Export"));
    if (this.choisirB) { ib = this.sources.findIndex(s => s.c === this.choisirB); this.choisirB = null; }
    $("#cmp-b").value = ib >= 0 ? ib : Math.min(1, this.sources.length - 1);
    this.charger();
  },
  charger() {
    const a = this.sources[+$("#cmp-a").value], b = this.sources[+$("#cmp-b").value];
    if (a) { $("#cmp-video-a").src = media(a.c); $("#cmp-legende-a").textContent = a.n; }
    if (b) { $("#cmp-video-b").src = media(b.c); $("#cmp-legende-b").textContent = b.n; }
    this.son();
  },
  son() { const s = $("#cmp-son").value; $("#cmp-video-a").muted = s !== "a"; $("#cmp-video-b").muted = s !== "b"; },
  decalage() { return +$("#cmp-decalage").value; },
  caler(t) {
    const A = $("#cmp-video-a"), B = $("#cmp-video-b");
    A.currentTime = Math.max(0, t); B.currentTime = Math.max(0, t + this.decalage());
  },
};
$("#cmp-a").onchange = $("#cmp-b").onchange = () => Cmp.charger();
$("#cmp-son").onchange = () => Cmp.son();
$("#cmp-decalage").oninput = e => { $("#cmp-decalage-val").textContent = fmtNb(+e.target.value) + " s"; Cmp.caler($("#cmp-video-a").currentTime); };
$("#cmp-lecture").onclick = () => {
  const A = $("#cmp-video-a"), B = $("#cmp-video-b");
  if (A.paused) { Cmp.caler(A.currentTime >= A.duration - .05 ? 0 : A.currentTime); A.play(); B.play(); $("#cmp-lecture").textContent = "❚❚ Pause"; }
  else { A.pause(); B.pause(); $("#cmp-lecture").textContent = "▶ Lire les deux"; }
};
$("#cmp-video-a").ontimeupdate = () => {
  const A = $("#cmp-video-a"), B = $("#cmp-video-b");
  if (A.duration) $("#cmp-position").value = A.currentTime / A.duration * 1000;
  const cible = A.currentTime + Cmp.decalage();
  if (!A.paused && Math.abs(B.currentTime - cible) > 0.12 && cible >= 0 && cible < (B.duration || 1e9)) B.currentTime = cible;
};
$("#cmp-position").oninput = e => { const A = $("#cmp-video-a"); if (A.duration) Cmp.caler(e.target.value / 1000 * A.duration); };
Onglets.auChangement.comparer = () => Cmp.dessiner();

/* ============================================================ CLAUDE */
const Claude = {
  vus: 0,
  async charger() {
    let l; try { l = await api("/api/ordres"); } catch { return; }
    const nbRep = l.reduce((s, o) => s + o.reponses.length, 0);
    let vus = 0; try { vus = +localStorage.getItem("studio-reponses-vues") || 0; } catch {}
    const p = $("#nb-reponses"); p.hidden = nbRep <= vus || Onglets.actif === "claude"; p.textContent = nbRep - vus;
    if (Onglets.actif === "claude") { try { localStorage.setItem("studio-reponses-vues", nbRep); } catch {} }
    if (Onglets.actif !== "claude") return;
    $("#fil-ordres").innerHTML = l.length ? l.map(o => `<div class="message moi"><div class="meta"><span class="statut statut-${o.statut}">${o.statut}</span><span>${esc(o.nature || "ordre")}</span><span>${esc((o.date || "").replace("T", " "))}</span>
      ${o.projet ? `<span>· ${esc(o.projet)}${o.timecode != null ? " @ " + fmtTc(o.timecode) : ""}${o.plan ? " · plan " + esc(o.plan) : ""}</span>` : ""}</div>${esc(o.texte)}
      ${(o.pieces || []).length ? `<div class="note">Pièces : ${o.pieces.map(x => esc(nomFichier(x))).join(", ")}</div>` : ""}
      ${o.reponses.map(r => `<div class="reponse"><div class="meta">${esc(r.auteur)} · ${esc((r.date || "").replace("T", " "))}</div>${esc(r.texte).replace(/\n/g, "<br>")}</div>`).join("")}</div>`).join("")
      : `<p class="note" style="text-align:center">Aucun ordre pour l'instant. Écris ce que tu veux ci-dessous : Claude le lit avec <code>outils/ordres.py liste</code> et te répond ici.</p>`;
  },
};
function majContexteOrdre() {
  $("#ordre-contexte").textContent = $("#ordre-tc").checked && M.projet ? `📎 ${M.projet.nom} · ${M.projet.version} · ${fmtTc(M.T)}${M.projet.plans[planA(M.T)] ? " · plan " + (planA(M.T) + 1) : ""}` : "";
}
$("#ordre-tc").onchange = majContexteOrdre;
$("#form-ordre").onsubmit = async e => {
  e.preventDefault();
  const texte = $("#ordre-texte").value.trim(); if (!texte) return;
  const joindre = $("#ordre-tc").checked && M.projet;
  await api("/api/ordres", {json: {texte, projet: joindre ? M.projet.id : null, timecode: joindre ? M.T : null, plan: joindre ? M.projet.plans[planA(M.T)]?.id : null}});
  $("#ordre-texte").value = ""; toast("Ordre envoyé."); Claude.charger();
};
$("#ordre-texte").addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) $("#form-ordre").requestSubmit(); });
Onglets.auChangement.claude = () => { majContexteOrdre(); Claude.charger(); };
setInterval(() => Claude.charger(), 5000); Claude.charger();

/* ============================================================ RÉFÉRENCES */
async function envoyerReferences(fichiers) {
  fichiers = fichiers.filter(f => /\.(mp4|mov|m4v|webm|png|jpe?g|webp)$/i.test(f.name));
  if (!fichiers.length) return toast("Aucune vidéo ou image dans ce dépôt.");
  const fd = new FormData();
  fichiers.forEach(f => fd.append("fichiers", f, f.webkitRelativePath || f.chemin || f.name));
  fd.append("note", $("#ref-note").value);
  const total = fichiers.reduce((s, f) => s + f.size, 0);
  const x = new XMLHttpRequest();
  x.open("POST", "/api/references");
  x.upload.onprogress = e => $("#ref-progression").textContent = `Copie… ${Math.round(e.loaded / Math.max(total, 1) * 100)} %`;
  x.onload = () => {
    if (x.status !== 200) { $("#ref-progression").textContent = "Échec de la copie."; return; }
    const r = JSON.parse(x.responseText); $("#ref-progression").textContent = `${r.fichiers.length} fichier(s) copié(s) dans ${r.dossier}. Ordre « À REPRODUIRE » envoyé à Claude.`;
    $("#ref-note").value = ""; References.dessiner(); Claude.charger();
  };
  x.send(fd);
}
async function lireEntree(entree, chemin = "") {
  if (entree.isFile) return new Promise(res => entree.file(f => { f.chemin = chemin + f.name; res([f]); }, () => res([])));
  if (entree.isDirectory) {
    const lecteur = entree.createReader(); let tous = [], lot;
    do { lot = await new Promise(res => lecteur.readEntries(res, () => res([]))); tous = tous.concat(lot); } while (lot.length);
    return (await Promise.all(tous.map(e => lireEntree(e, chemin + entree.name + "/")))).flat();
  }
  return [];
}
const depot = $("#depot");
["dragenter", "dragover"].forEach(t => depot.addEventListener(t, e => { e.preventDefault(); depot.classList.add("survol"); }));
["dragleave", "drop"].forEach(t => depot.addEventListener(t, () => depot.classList.remove("survol")));
depot.addEventListener("drop", async e => {
  e.preventDefault();
  const items = [...(e.dataTransfer.items || [])].map(i => i.webkitGetAsEntry?.()).filter(Boolean);
  const fichiers = items.length ? (await Promise.all(items.map(i => lireEntree(i)))).flat() : [...e.dataTransfer.files];
  envoyerReferences(fichiers);
});
$("#ref-fichiers").onchange = e => envoyerReferences([...e.target.files]);
$("#ref-dossier").onchange = e => envoyerReferences([...e.target.files]);
const References = {
  async dessiner() {
    const l = await api("/api/references");
    $("#ref-liste").innerHTML = l.length ? l.map(r => `<div class="groupe"><div class="groupe-tete"><h3>${esc(r.nom)}</h3><span class="note">${r.fichiers.length} fichier(s)</span></div>
      <div class="grille-creas">${r.fichiers.map(f => `<div class="crea ${f.type}" data-ref="${esc(f.chemin)}"><span class="type">${f.type === "video" ? fmtNb(f.duree, 1) + " s" : "image"}</span><img loading="lazy" src="${vign(f.chemin, .5, 260)}"><small>${esc(nomFichier(f.chemin))}</small></div>`).join("")}</div></div>`).join("")
      : `<p class="note" style="text-align:center">Aucune référence déposée.</p>`;
    $$("[data-ref]").forEach(el => el.onclick = () => modale(`<video class="visionneuse" src="${media(el.dataset.ref)}" controls autoplay playsinline></video><div class="rangee"><button class="btn" id="rf-cmp">Comparer avec un export</button></div>`, m => {
      $("#rf-cmp", m).onclick = () => { fermerModale(); Onglets.aller("comparer"); };
    }));
  },
};
Onglets.auChangement.references = () => References.dessiner();
