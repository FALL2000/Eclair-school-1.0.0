/* =========================================================================
   Eclair School — prototype cliquable (maquette du frontend Angular + PrimeNG)
   Navigation par hash (#/eleves, #/notes...), FR/EN, mode clair/sombre,
   menus et actions filtrés par les permissions du rôle de démonstration.
   ========================================================================= */
(function () {
  "use strict";
  const D = window.DATA;
  const I18N = window.I18N;
  const AUJOURDHUI = "2026-12-14"; // date fictive : fin du trimestre 1

  /* ---------------- Préférences (localStorage, facultatif) ---------------- */
  const store = {
    get(cle, defaut) {
      try { const v = localStorage.getItem("eclair." + cle); return v === null ? defaut : JSON.parse(v); }
      catch (e) { return defaut; }
    },
    set(cle, valeur) { try { localStorage.setItem("eclair." + cle, JSON.stringify(valeur)); } catch (e) { /* stockage indisponible */ } },
  };

  const S = {
    lang: store.get("lang", "fr"),
    theme: store.get("theme", null), // null : suit le système
    role: store.get("role", 1),
    connecte: store.get("connecte", false),
    menuOuvert: false, // petit écran : menu affiché par-dessus le contenu
    menuReplie: store.get("menuReplie", false), // grand écran : barre latérale masquée (mémorisé)
    popup: false,
    tab: { admin: "structure", eleve: "infos", scolarite: "reglements", users: "users", insc: "nouvelle", sal: "etat" },
    calcule: { 2: true }, // la Séquence 2 (évaluation parente) a déjà été calculée
    f: {
      eleves: { q: "", qApplique: "", genre: "", page: 1, pageSize: 10 },
      notes: { evaluation: 1, matiere: 5 },
      discipline: { evaluation: 1 },
      bulletin: { langue: "FR", type: "trimestre", periode: 1, seuil: 10, regles: [
        { min: 0, max: 8.99, decision: "Redouble" },
        { min: 9, max: 9.99, decision: "Promu en cas de rattrapage" },
        { min: 10, max: 20, decision: "Promu" },
      ] },
      regl: { tranche: 1, statut: "tous" },
      presence: { cours: 0 },
      roleSel: 3,
      baremeSel: 1,
    },
    insc: { etape: 1, type: "nouveau", niveau: "", classe: "", redoublant: false },
    appel: {},
    choixClasse: {},
    // Sélection en cascade partagée par tous les écrans (mémorisée)
    sel: store.get("selection", { section: 1, cycle: 3, niveau: 5, classe: 6 }),
    // Données chargées par écran : clé des filtres au moment du clic sur « Afficher » / « Rechercher »
    affiche: {},
    qEcole: "",
    // Historique des inscriptions : filtres saisis / appliqués (envoyés au backend) et pagination
    hist: { du: "", au: "", q: "", applique: { du: "", au: "", q: "" }, page: 1, pageSize: 10 },
    editInsc: null,
    // Enseignants : filtres saisis / appliqués (backend), pagination, dialogues
    ens: { q: "", matiere: "", applique: { q: "", matiere: "" }, page: 1, pageSize: 10 },
    matiereAAjouter: "",
    // Salaires : mois sélectionné, filtres appliqués (backend), pagination
    sal: { periode: "2026-10", q: "", matiere: "", statut: "tous", applique: null, page: 1, pageSize: 10 },
    // Versements de salaire : filtres saisis / appliqués (backend), pagination. Tous les versements de l'année par défaut
    vers: { periode: "", q: "", matiere: "", applique: { periode: "", q: "", matiere: "" }, page: 1, pageSize: 10 },
    // Moyens de paiement : non configurés par défaut, filtres nom / matière appliqués (backend), pagination
    nc: null, // nouveau cours (dialogue d'ajout)
    // Présence des enseignants : date et nom appliqués (GET /presence-enseignant/jour), saisie en cours non enregistrée
    pe: { date: AUJOURDHUI, q: "", applique: { date: AUJOURDHUI, q: "" }, saisie: {} }, // applique.classe : fixée au 1er affichage
    mp: { config: "non", q: "", matiere: "", applique: { q: "", matiere: "" }, page: 1, pageSize: 10 },
    rechercheEcole: null,
  };
  // Paramètres d'URL pour la démonstration : index.html?connecte&role=2&theme=dark&lang=en#/bulletins
  const params = new URLSearchParams(location.search);
  if (params.has("connecte")) S.connecte = true;
  if (params.get("role")) S.role = Number(params.get("role"));
  if (params.get("theme")) S.theme = params.get("theme");
  if (params.get("lang")) S.lang = params.get("lang");
  // ?f=notes.evaluation:2 (filtre) et ?tab=users:roles (onglet)
  for (const f of params.getAll("f")) {
    const [chemin, v] = f.split(":"); const [a, b] = chemin.split(".");
    if (a === "insc" || a === "sal" || a === "vers" || a === "pe" || S.f[a]) setFiltre(chemin, v);
    if (a === "vers" || a === "pe") S[a].applique[b] = S[a][b]; // filtre appliqué directement
  }
  for (const tb of params.getAll("tab")) { const [k, v] = tb.split(":"); S.tab[k] = v; }
  if (params.has("afficher")) S.autoAffiche = true;
  if (params.get("q")) { S.qEcole = params.get("q"); S.rechercheEcole = params.get("q"); }
  if (params.has("sel")) { S.sel = { section: "", cycle: "", niveau: "", classe: "" }; for (const x of params.getAll("sel")) { const [k, v] = x.split(":"); S.sel[k] = Number(v); } }

  /* ---------------- Utilitaires ---------------- */
  // Traduction dans une langue donnée (par défaut la langue de l'interface)
  function tL(lang, cle, vars) {
    let s = (I18N[lang] && I18N[lang][cle]) ?? I18N.fr[cle] ?? cle;
    if (vars) for (const [k, v] of Object.entries(vars)) s = s.split("{" + k + "}").join(v);
    return s;
  }
  const t = (cle, vars) => tL(S.lang, cle, vars);
  // Documents bilingues (reçu) : langue sélectionnée mise en avant, l'autre langue en retrait en dessous
  const autreLangue = () => S.lang === "fr" ? "en" : "fr";
  const bi = (cle, vars) => `<span class="l1">${tL(S.lang, cle, vars)}</span><span class="l2">${tL(autreLangue(), cle, vars)}</span>`;
  // Variante sur une seule ligne : « Exemplaire de l'élève / Student copy »
  const biLigne = (cle, vars) => `<span class="l1">${tL(S.lang, cle, vars)}</span><span class="l2 inline"> / ${tL(autreLangue(), cle, vars)}</span>`;
  const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const r2 = v => Math.round(v * 100) / 100;
  const fmt = v => v == null ? "—" : Number(v).toLocaleString(S.lang === "fr" ? "fr-FR" : "en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const fmtInt = v => Number(v).toLocaleString(S.lang === "fr" ? "fr-FR" : "en-US");
  const fcfa = v => fmtInt(v) + " FCFA";
  const fmtDate = iso => new Date(iso + "T00:00:00").toLocaleDateString(S.lang === "fr" ? "fr-FR" : "en-GB", { day: "2-digit", month: "short", year: "numeric" });
  const initiales = (n, p) => ((n || "")[0] || "") + ((p || "")[0] || "");
  const tag = (sev, texte, icone) => `<span class="tag ${sev}">${icone ? `<i class="pi ${icone}"></i>` : ""}${esc(texte)}</span>`;
  const byId = (liste, id) => liste.find(x => x.id === Number(id));
  const classe = id => byId(D.classes, id);
  // Montant de l'inscription : fixé par niveau
  const montantInscription = idClasse => byId(D.niveaux, classe(idClasse).niveau).montantInscription;
  const eleve = id => byId(D.eleves, id);
  const matiere = id => byId(D.matieres, id);
  const bareme = id => byId(D.baremes, id);
  const evaluation = id => byId(D.evaluations, id);
  const option = (valeur, libelle, courant) => `<option value="${esc(valeur)}" ${String(valeur) === String(courant) ? "selected" : ""}>${esc(libelle)}</option>`;

  /* ---------------- Permissions ---------------- */
  const roleCourant = () => byId(D.roles, S.role);
  const utilisateurCourant = () => D.utilisateurs.find(u => u.roles.includes(S.role)) || D.utilisateurs[0];
  // code : une permission, ou une liste (au moins une des permissions)
  function can(code) {
    if (!code) return true;
    if (Array.isArray(code)) return code.some(c => can(c));
    const r = roleCourant();
    return r.permissions === "*" || r.permissions.includes(code);
  }

  /* ---------------- Règles de calcul (identiques au backend) ---------------- */
  const coefficient = m => (D.ecole.typeSchool === "education_base" ? 1 : (m.coef || 1));
  function sur20(note, m) {
    const b = bareme(m.bareme);
    return b.valeurMax === 20 ? note : r2(note * 20 / b.valeurMax);
  }
  function appreciation(v, idBareme = 1) {
    if (v == null) return null;
    const a = D.appreciations.find(x => x.bareme === idBareme && v >= x.min && v <= x.max);
    return a ? (S.lang === "en" && a.libelleEn ? a.libelleEn : a.libelle) : null;
  }
  // Arrondi des notes calculées : .00-.19 -> entier, .20-.30 -> .25, .31-.59 -> .5, .60-.79 -> .75, .80-.99 -> entier suivant
  function arrondiQuart(v) {
    const c = Math.round(v * 100), e = Math.floor(c / 100), d = c % 100;
    const q = d < 20 ? 0 : d <= 30 ? 25 : d < 60 ? 50 : d < 80 ? 75 : 100;
    return (e * 100 + q) / 100;
  }
  const depsDe = idEval => D.dependances.filter(d => d.parent === Number(idEval));
  const parentDe = idEval => D.dependances.find(d => d.dependance === Number(idEval));
  // Note d'un élève dans une évaluation (dans le barème de la matière) ; undefined = non classé
  function noteEval(idEval, idMat, idEl) {
    const deps = depsDe(idEval);
    if (deps.length) {
      if (!S.calcule[idEval]) return undefined;
      const notees = deps.filter(d => noteEval(d.dependance, idMat, idEl) != null);
      if (!notees.length) return undefined;
      const total = notees.reduce((s, d) => s + d.pourcentage, 0);
      return arrondiQuart(notees.reduce((s, d) => s + noteEval(d.dependance, idMat, idEl) * d.pourcentage, 0) / total);
    }
    const n = D.notes[idEval]?.[idMat]?.[idEl];
    return n == null ? undefined : n;
  }
  const elevesClasse = idClasse => D.eleves.filter(e => e.classe === Number(idClasse) && e.actif);
  const evalsTrimestre = idT => D.evaluations.filter(e => e.trimestre === Number(idT) && !parentDe(e.id));

  // Notes sur 20 : {idEleve: {idMatiere: note}}
  function notes20Evaluation(idEval, eleves) {
    const res = {};
    for (const e of eleves) {
      res[e.id] = {};
      for (const m of D.matieres) {
        const n = noteEval(idEval, m.id, e.id);
        if (n != null) res[e.id][m.id] = sur20(n, m);
      }
    }
    return res;
  }
  function notes20Trimestre(idT, eleves) {
    const evals = evalsTrimestre(idT);
    const res = {};
    for (const e of eleves) {
      res[e.id] = {};
      for (const m of D.matieres) {
        const ns = evals.map(ev => noteEval(ev.id, m.id, e.id)).filter(n => n != null).map(n => sur20(n, m));
        if (ns.length) res[e.id][m.id] = r2(ns.reduce((a, b) => a + b, 0) / ns.length);
      }
    }
    return res;
  }
  function moyenne(notesEleve, matieres = D.matieres) {
    const notees = matieres.filter(m => notesEleve[m.id] != null);
    if (!notees.length) return { coefs: 0, points: null, moy: null };
    const coefs = notees.reduce((s, m) => s + coefficient(m), 0);
    const points = notees.reduce((s, m) => s + notesEleve[m.id] * coefficient(m), 0);
    return { coefs, points: r2(points), moy: r2(points / coefs) };
  }
  function rangs(valeurs) { // {cle: valeur} -> {cle: {rang, exaequo}}
    const occ = {};
    Object.values(valeurs).forEach(v => { occ[v] = (occ[v] || 0) + 1; });
    const tri = Object.entries(valeurs).sort((a, b) => b[1] - a[1]);
    const res = {};
    let rang = 0, prec = null;
    tri.forEach(([cle, v], i) => { if (v !== prec) { rang = i + 1; prec = v; } res[cle] = { rang, exaequo: occ[v] > 1 }; });
    return res;
  }
  function libelleRang(r, genre) {
    if (!r) return "—";
    let s;
    if (S.lang === "fr") s = r.rang === 1 ? (genre === "F" ? "1ère" : "1er") : `${r.rang}e`;
    else { const n = r.rang, suf = (n % 100 >= 11 && n % 100 <= 13) ? "th" : ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th"); s = n + suf; }
    return r.exaequo ? `${s} ${t("bul.exaequo")}` : s;
  }
  function stats(valeurs, seuil) {
    const n = valeurs.length;
    if (!n) return { effectif: 0, moyenne: null, max: null, min: null, ecart: null, mediane: null, reussite: 0, taux: null };
    const m = valeurs.reduce((a, b) => a + b, 0) / n;
    const tri = [...valeurs].sort((a, b) => a - b);
    const reussite = valeurs.filter(v => v >= seuil).length;
    return {
      effectif: n, moyenne: r2(m), max: r2(Math.max(...valeurs)), min: r2(Math.min(...valeurs)),
      ecart: r2(Math.sqrt(valeurs.reduce((s, v) => s + (v - m) ** 2, 0) / n)),
      mediane: r2(n % 2 ? tri[(n - 1) / 2] : (tri[n / 2 - 1] + tri[n / 2]) / 2),
      reussite, taux: r2(reussite * 100 / n),
    };
  }
  const decisionDiscipline = total => { const d = D.decisions.find(x => total >= x.min && total <= x.max); return d ? (S.lang === "en" && d.libelleEn ? d.libelleEn : d.libelle) : null; };
  function discipline(idEl, evals) {
    let nj = 0, j = 0, trouve = false;
    for (const ev of evals) {
      const d = D.disciplines[ev]?.[idEl];
      if (d) { nj += d.nonJustifie; j += d.justifie; trouve = true; }
    }
    return { nj, j, total: nj + j, decision: trouve ? decisionDiscipline(nj + j) : null };
  }

  // Bulletins d'une classe : periode = {type: evaluation|trimestre|annuel, id}
  function calculerBulletins(idClasse, periode) {
    const eleves = elevesClasse(idClasse);
    let notes, seuil = 10, distinction = true, evalsDiscipline, moyennesImposees = null, complements = {};
    if (periode.type === "evaluation") {
      notes = notes20Evaluation(periode.id, eleves);
      distinction = false;
      evalsDiscipline = [Number(periode.id)];
    } else if (periode.type === "trimestre") {
      notes = notes20Trimestre(periode.id, eleves);
      evalsDiscipline = evalsTrimestre(periode.id).map(e => e.id);
    } else {
      seuil = Number(S.f.bulletin.seuil);
      const parTrimestre = D.trimestres.map(tr => ({ tr, notes: notes20Trimestre(tr.id, eleves) }));
      notes = {}; moyennesImposees = {};
      for (const e of eleves) {
        notes[e.id] = {};
        for (const m of D.matieres) {
          const ns = parTrimestre.map(p => p.notes[e.id][m.id]).filter(n => n != null);
          if (ns.length) notes[e.id][m.id] = r2(ns.reduce((a, b) => a + b, 0) / ns.length);
        }
        const moysT = parTrimestre.map(p => ({ id: p.tr.id, libelle: p.tr.libelle, moy: moyenne(p.notes[e.id]).moy }));
        const valides = moysT.filter(x => x.moy != null).map(x => x.moy);
        moyennesImposees[e.id] = valides.length ? r2(valides.reduce((a, b) => a + b, 0) / valides.length) : null;
        const regle = S.f.bulletin.regles.find(r => moyennesImposees[e.id] != null && moyennesImposees[e.id] >= Number(r.min) && moyennesImposees[e.id] <= Number(r.max));
        complements[e.id] = { trimestres: moysT, decisionFinale: regle ? regle.decision : null };
      }
      evalsDiscipline = D.trimestres.flatMap(tr => evalsTrimestre(tr.id).map(e => e.id));
    }

    const bulletins = eleves.map(e => {
      const n = notes[e.id] || {};
      const groupes = D.groupes.map(g => {
        const mats = D.matieres.filter(m => m.groupe === g.id);
        const lignes = mats.map(m => {
          const brute = periode.type === "evaluation" ? noteEval(periode.id, m.id, e.id) : undefined;
          return { m, brute, note: n[m.id] ?? null, coef: coefficient(m), points: n[m.id] != null ? r2(n[m.id] * coefficient(m)) : null,
            appreciation: brute != null ? appreciation(brute, m.bareme) : appreciation(n[m.id]) };
        });
        return { g, lignes, ...moyenne(n, mats) };
      });
      const gen = moyenne(n);
      const moy = moyennesImposees ? moyennesImposees[e.id] : gen.moy;
      return {
        e, groupes, coefs: gen.coefs, points: gen.points, moy, appreciation: appreciation(moy),
        reussite: moy != null ? moy >= seuil : null,
        distinction: distinction && moy != null && moy >= 12,
        discipline: discipline(e.id, evalsDiscipline),
        ...(complements[e.id] || {}),
      };
    });
    // Rangs : général, par groupe, par matière
    const rg = rangs(Object.fromEntries(bulletins.filter(b => b.moy != null).map(b => [b.e.id, b.moy])));
    bulletins.forEach(b => { b.rang = rg[b.e.id]; });
    D.groupes.forEach((g, gi) => {
      const rgG = rangs(Object.fromEntries(bulletins.filter(b => b.groupes[gi].moy != null).map(b => [b.e.id, b.groupes[gi].moy])));
      bulletins.forEach(b => { b.groupes[gi].rang = rgG[b.e.id]; });
      b0lignes(gi).forEach((_, li) => {
        const rgM = rangs(Object.fromEntries(bulletins.filter(b => b.groupes[gi].lignes[li].note != null).map(b => [b.e.id, b.groupes[gi].lignes[li].note])));
        bulletins.forEach(b => { b.groupes[gi].lignes[li].rang = rgM[b.e.id]; });
      });
    });
    function b0lignes(gi) { return bulletins.length ? bulletins[0].groupes[gi].lignes : []; }
    const moys = bulletins.map(b => b.moy).filter(v => v != null);
    return {
      bulletins: bulletins.sort((a, b) => (a.rang?.rang ?? 999) - (b.rang?.rang ?? 999)),
      stats: stats(moys, seuil), seuil, distinction,
      honneur: moys.filter(v => v >= 12).length,
      parGenre: ["M", "F"].map(g => ({ g, ...stats(bulletins.filter(b => b.e.genre === g && b.moy != null).map(b => b.moy), seuil) })),
      repartition: [[0, 5, "[0;5["], [5, 8, "[5;8["], [8, 10, "[8;10["], [10, 12, "[10;12["], [12, 14, "[12;14["], [14, 16, "[14;16["], [16, 99, "[16;20]"]]
        .map(([a, b, l]) => ({ l, n: moys.filter(v => v >= a && v < b).length })),
      parMatiere: D.matieres.map(m => ({ m, ...stats(eleves.map(e => notes[e.id]?.[m.id]).filter(v => v != null), seuil) })),
      decisionsFinales: periode.type === "annuel" ? S.f.bulletin.regles.map(r => ({ d: r.decision, n: bulletins.filter(b => b.decisionFinale === r.decision).length })) : null,
    };
  }

  /* ---------------- Règlements ---------------- */
  const reglementsEleve = (idEl, idTranche) => D.reglements.filter(r => r.eleve === idEl && (idTranche == null || r.tranche === Number(idTranche)));
  function situationTranche(idEl, idTranche) {
    const tr = byId(D.tranches, idTranche);
    const regle = reglementsEleve(idEl, idTranche).filter(r => r.statut === "valide").reduce((s, r) => s + r.montant, 0);
    const statut = regle <= 0 ? "aucun" : regle >= tr.montant ? "total" : "partiel";
    return { tr, regle, reste: Math.max(tr.montant - regle, 0), statut, pct: Math.min(100, Math.round(regle * 100 / tr.montant)) };
  }
  const tagPaiement = s => tag({ total: "success", partiel: "warn", aucun: "danger" }[s], t("pay." + s));

  /* ---------------- Logo ---------------- */
  const LOGO = `<svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#2563EB"/><path d="M10 21.5c7.2-3.4 14-3.4 20.5 0V47c-6.5-3.4-13.3-3.4-20.5 0z" fill="#fff"/><path d="M33.5 21.5c6.5-3.4 13.3-3.4 20.5 0V47c-7.2-3.4-14-3.4-20.5 0z" fill="#DBEAFE"/><path d="M36.5 7 22 34.5h9.2L26.5 57 43 26.8h-9.4L39.8 7z" fill="#FBBF24" stroke="#2563EB" stroke-width="2.4" stroke-linejoin="round"/></svg>`;
  const marque = () => `<div class="brand">${LOGO}<div class="brand-name"><b>Eclair</b> <span>School</span></div></div>`;
  // Établissement (table de configuration de l'école) : logo et nom
  const blocEcole = () => `<div class="ecole-card"><span class="logo-ecole">${D.ecole.logo}</span><div class="ecole-infos"><div class="ecole-nom" title="${esc(D.ecole.nom)}">${esc(D.ecole.nom)}</div><div class="small muted">${esc(D.ecole.ville)} · ${esc(D.ecole.annee)}</div></div></div>`;
  // En-tête des documents imprimés : logo, nom et coordonnées de l'école à gauche ; droite = titre du document
  const enteteDocument = (droite, bilingue = false) => `<div class="ph"><div class="doc-ecole"><span class="logo-ecole">${D.ecole.logo}</span><div>
      <div class="doc-ecole-nom">${esc(D.ecole.nom)}</div>
      <div class="doc-ecole-coord">${esc(D.ecole.adresse)} · ${esc(D.ecole.telephone)}</div>
      <div class="doc-ecole-coord">${bilingue ? biLigne("c.anneeScolaire") : t("c.anneeScolaire")} ${esc(D.ecole.annee)} · <i>${esc(D.ecole.devise)}</i></div></div></div>${droite}</div>`;
  // Pied des documents : logo et nom de l'application
  const piedApplication = (bilingue = false, droite = "") => `<div class="doc-pied"><span class="doc-app">${LOGO}<span>${bilingue ? biLigne("doc.generePar") : t("doc.generePar")} <b>Eclair School</b></span></span>${droite}</div>`;

  /* ---------------- Menu ---------------- */
  const MENU = [
    { g: "nav.g.general", items: [{ r: "dashboard", i: "pi-home", l: "nav.dashboard" }] },
    { g: "nav.g.eleves", items: [
      { r: "eleves", i: "pi-users", l: "nav.eleves", p: "eleve:consulter" },
      { r: "inscription", i: "pi-user-plus", l: "nav.inscription", p: "eleve:inscrire" },
    ] },
    { g: "nav.g.enseignement", items: [
      { r: "enseignants", i: "pi-id-card", l: "nav.enseignants", p: "enseignant:consulter" },
      { r: "emploi-du-temps", i: "pi-calendar", l: "nav.edt", p: "cours:consulter" },
      { r: "presences", i: "pi-check-square", l: "nav.presences", p: ["presence_eleve:consulter", "presence_enseignant:consulter"] },
      { r: "salaires", i: "pi-money-bill", l: "nav.salaires", p: "salaire:consulter" },
    ] },
    { g: "nav.g.evaluations", items: [
      { r: "evaluations", i: "pi-list", l: "nav.evaluations", p: "evaluation:consulter" },
      { r: "notes", i: "pi-pencil", l: "nav.notes", p: "notation:consulter" },
      { r: "discipline", i: "pi-exclamation-triangle", l: "nav.discipline", p: "discipline_eleve:consulter" },
      { r: "bulletins", i: "pi-file", l: "nav.bulletins", p: "bulletin:generer" },
    ] },
    { g: "nav.g.scolarite", items: [{ r: "scolarite", i: "pi-wallet", l: "nav.scolarite", p: "reglement:consulter" }] },
    { g: "nav.g.administration", items: [
      { r: "administration", i: "pi-cog", l: "nav.parametrage", p: "classe:consulter" },
      { r: "utilisateurs", i: "pi-shield", l: "nav.utilisateurs", p: "utilisateur:consulter" },
    ] },
  ];
  const tousItems = () => MENU.flatMap(g => g.items);

  /* ---------------- Toast & dialog ---------------- */
  function toast(sev, titre, message) {
    const icones = { success: "pi-check-circle", danger: "pi-times-circle", warn: "pi-exclamation-triangle", info: "pi-info-circle" };
    const el = document.createElement("div");
    el.className = "toast " + sev;
    el.innerHTML = `<i class="pi ${icones[sev]}"></i><div><b>${esc(titre)}</b><span class="small muted">${esc(message || "")}</span></div>`;
    document.getElementById("toasts").appendChild(el);
    setTimeout(() => el.remove(), 3800);
  }
  function dialog(titre, corps, pied, large) {
    document.getElementById("dialog-root").innerHTML = `
      <div class="overlay" data-act="fermer-overlay">
        <div class="dialog ${large ? "wide" : ""}" role="dialog" aria-modal="true">
          <div class="dialog-head"><h2>${esc(titre)}</h2><button class="btn text icon rounded" data-act="fermer" aria-label="${t("c.fermer")}"><i class="pi pi-times"></i></button></div>
          <div class="dialog-body">${corps}</div>
          ${pied ? `<div class="dialog-foot">${pied}</div>` : ""}
        </div>
      </div>`;
    ameliorerSelects(document.getElementById("dialog-root"));
  }
  const fermer = () => { fermerSelect(); document.getElementById("dialog-root").innerHTML = ""; };

  /* ---------------- Listes de sélection avec recherche (équivalent de p-select [filter]="true") ----------------
     Chaque <select class="select"> est remplacé à l'affichage par un bouton qui ouvre un panneau
     avec un champ de recherche (insensible aux accents et à la casse). Le <select> d'origine reste
     dans la page : le choix met à jour sa valeur et déclenche son événement « change ». */
  const normaliser = s => String(s).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  let selectOuvert = null;
  function fermerSelect() {
    document.querySelectorAll(".ss-panel").forEach(p => p.remove());
    selectOuvert = null;
  }
  function ameliorerSelects(racine = document) {
    racine.querySelectorAll("select.select:not([data-ss])").forEach(sel => {
      sel.setAttribute("data-ss", "1");
      const wrap = document.createElement("div");
      wrap.className = "ss";
      if (sel.style.width) wrap.style.width = sel.style.width;
      sel.parentNode.insertBefore(wrap, sel);
      wrap.appendChild(sel);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "select ss-btn";
      if (sel.style.height) btn.style.height = sel.style.height;
      btn.disabled = sel.disabled;
      btn.setAttribute("aria-haspopup", "listbox");
      const label = sel.closest(".field")?.querySelector("label")?.textContent || sel.getAttribute("aria-label") || "";
      if (label) btn.setAttribute("aria-label", label.replace("*", "").trim());
      const opt = sel.options[sel.selectedIndex];
      btn.innerHTML = `<span>${esc(opt ? opt.textContent : "")}</span>`;
      wrap.appendChild(btn);
    });
  }
  function ouvrirSelect(wrap) {
    fermerSelect();
    const sel = wrap.querySelector("select"), btn = wrap.querySelector(".ss-btn");
    const r = btn.getBoundingClientRect();
    const largeur = Math.max(r.width, 220);
    const panel = document.createElement("div");
    panel.className = "ss-panel";
    panel.style.width = largeur + "px";
    panel.style.left = Math.max(8, Math.min(r.left, window.innerWidth - largeur - 8)) + "px";
    const espaceBas = window.innerHeight - r.bottom;
    if (espaceBas < 260 && r.top > espaceBas) panel.style.bottom = (window.innerHeight - r.top + 4) + "px";
    else panel.style.top = (r.bottom + 4) + "px";
    panel.innerHTML = `<div class="input-icon"><i class="pi pi-search"></i><input class="input" placeholder="${t("c.rechercherListe")}" aria-label="${t("c.rechercherListe")}"></div><div class="ss-list" role="listbox"></div>`;
    const input = panel.querySelector("input"), liste = panel.querySelector(".ss-list");
    const options = [...sel.options].map(o => ({ v: o.value, l: o.textContent }));
    const remplir = () => {
      const q = normaliser(input.value.trim());
      const visibles = options.filter(o => normaliser(o.l).includes(q));
      liste.innerHTML = visibles.length
        ? visibles.map((o, i) => `<div class="ss-option ${o.v === sel.value ? "selected" : ""} ${q && i === 0 ? "active" : ""}" data-ssv="${esc(o.v)}" role="option" aria-selected="${o.v === sel.value}">${esc(o.l)}</div>`).join("")
        : `<div class="ss-empty">${t("c.aucunResultat")}</div>`;
    };
    const choisir = v => {
      fermerSelect();
      btn.querySelector("span").textContent = options.find(o => o.v === v)?.l || "";
      if (sel.value !== v) { sel.value = v; sel.dispatchEvent(new Event("change", { bubbles: true })); }
      else btn.focus();
    };
    remplir();
    input.addEventListener("input", remplir);
    input.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); const premier = liste.querySelector(".ss-option"); if (premier) choisir(premier.dataset.ssv); }
      if (e.key === "Escape") { e.stopPropagation(); fermerSelect(); btn.focus(); }
    });
    panel.addEventListener("click", e => { const o = e.target.closest(".ss-option"); if (o) choisir(o.dataset.ssv); });
    document.body.appendChild(panel);
    selectOuvert = wrap;
    // Défilement interne à la liste uniquement (scrollIntoView ferait défiler la page et refermerait la liste)
    const choisi = liste.querySelector(".selected");
    if (choisi) liste.scrollTop = choisi.offsetTop - liste.offsetTop - liste.clientHeight / 2;
    input.focus({ preventScroll: true });
  }
  if (!params.has("ouvrirListe")) window.addEventListener("resize", fermerSelect); // capture headless : redimensionnement
  window.addEventListener("scroll", e => { if (!(e.target instanceof Element && e.target.closest(".ss-panel"))) fermerSelect(); }, true);

  /* ---------------- Mise en page ---------------- */
  function appliquerPreferences() {
    const html = document.documentElement;
    if (S.theme) html.setAttribute("data-theme", S.theme); else html.removeAttribute("data-theme");
    html.lang = S.lang;
    document.title = "Eclair School — " + t("app.titre");
  }
  const sombre = () => S.theme ? S.theme === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;

  function outilsPreferences() {
    return `
      <div class="segmented" role="group" aria-label="${t("c.langue")}">
        <button class="${S.lang === "fr" ? "on" : ""}" data-act="lang" data-v="fr">FR</button>
        <button class="${S.lang === "en" ? "on" : ""}" data-act="lang" data-v="en">EN</button>
      </div>
      <button class="btn secondary icon" data-act="theme" title="${t(sombre() ? "c.modeClair" : "c.modeSombre")}" aria-label="${t(sombre() ? "c.modeClair" : "c.modeSombre")}">
        <i class="pi ${sombre() ? "pi-sun" : "pi-moon"}"></i>
      </button>`;
  }

  function layout(route, contenu) {
    const u = utilisateurCourant();
    const item = tousItems().find(i => i.r === route);
    const menu = MENU.map(g => {
      const items = g.items.filter(i => can(i.p));
      if (!items.length) return "";
      return `<div class="menu-group"><div class="menu-group-title">${t(g.g)}</div>${items.map(i => `
        <div class="menu-item ${i.r === route ? "active" : ""}" data-go="${i.r}"><i class="pi ${i.i}"></i>${t(i.l)}</div>`).join("")}</div>`;
    }).join("");
    return `
      <div class="layout ${S.menuReplie ? "replie" : ""}">
        ${S.menuOuvert ? `<div class="menu-backdrop" data-act="fermer-menu"></div>` : ""}
        <aside class="sidebar ${S.menuOuvert ? "open" : ""}">
          <div class="sidebar-head">${marque()}<button class="btn text icon menu-close" data-act="fermer-menu" aria-label="${t("nav.masquerMenu")}" title="${t("nav.masquerMenu")}"><i class="pi pi-times"></i></button></div>
          ${blocEcole()}
          <nav class="menu">${menu}</nav>
          <div class="sidebar-foot">${t("c.anneeScolaire")} ${esc(D.ecole.annee)}</div>
        </aside>
        <div class="main">
          <header class="topbar">
            <button class="btn text icon menu-toggle" data-act="menu" aria-label="Menu" title="${t(S.menuReplie ? "nav.afficherMenu" : "nav.masquerMenu")}"><i class="pi pi-bars"></i></button>
            ${S.menuReplie ? `<div class="topbar-marque hide-sm">${marque()}</div>` : ""}
            <div class="breadcrumb hide-sm"><i class="pi pi-home"></i><i class="pi pi-chevron-right"></i><span>${t(item ? item.l : "nav.profil")}</span></div>
            <div class="grow"></div>
            <span class="tag info rounded hide-sm"><i class="pi pi-calendar"></i>${esc(D.ecole.annee)}</span>
            ${outilsPreferences()}
            <div class="relative">
              <div class="user-chip" data-act="popup">
                <span class="avatar">${esc(initiales(u.prenom, u.nom))}</span>
                <div class="hide-sm"><div style="font-weight:600">${esc(u.prenom)} ${esc(u.nom)}</div><div class="small muted">${esc(roleCourant().nom)}</div></div>
                <i class="pi pi-angle-down muted"></i>
              </div>
              ${S.popup ? popupUtilisateur() : ""}
            </div>
          </header>
          <main class="content">${contenu}</main>
        </div>
      </div>`;
  }
  function popupUtilisateur() {
    return `<div class="popup">
      <div class="title">${t("demo.role")}</div>
      ${D.roles.map(r => `<div class="item" data-act="role" data-v="${r.id}"><i class="pi ${r.id === S.role ? "pi-check-circle" : "pi-circle"}"></i>${esc(r.nom)}</div>`).join("")}
      <div class="sep"></div>
      <div class="item" data-go="profil"><i class="pi pi-user"></i>${t("nav.profil")}</div>
      <div class="item" data-act="deconnexion"><i class="pi pi-sign-out"></i>${t("c.deconnexion")}</div>
    </div>`;
  }
  const entete = (titre, sousTitre, actions) => `
    <div class="page-head"><div><h1>${titre}</h1>${sousTitre ? `<p>${sousTitre}</p>` : ""}</div><div class="row">${actions || ""}</div></div>`;
  const accesRefuse = () => `<div class="card card-body"><div class="message danger"><i class="pi pi-lock"></i><div><b>${t("c.accesRefuse")}</b><div>${t("c.accesRefuseTexte")}</div></div></div></div>`;

  /* Filtre en cascade section > cycle > niveau > classe (futur composant Angular partagé).
     Chaque liste ne propose que les valeurs compatibles avec les filtres précédents. */
  const NIVEAUX_CASCADE = ["section", "cycle", "niveau", "classe"];
  function optionsCascade(sel) {
    const cycles = D.cycles.filter(c => !sel.section || c.section === Number(sel.section));
    const niveaux = D.niveaux.filter(n => cycles.some(c => c.id === n.cycle) && (!sel.cycle || n.cycle === Number(sel.cycle)));
    const classes = D.classes.filter(c => niveaux.some(n => n.id === c.niveau) && (!sel.niveau || c.niveau === Number(sel.niveau)));
    return { section: D.sections, cycle: cycles, niveau: niveaux, classe: classes };
  }
  function preselectionAutomatique() {
    // Une liste qui ne contient qu'une valeur est sélectionnée d'office
    for (const k of NIVEAUX_CASCADE) {
      const liste = optionsCascade(S.sel)[k];
      if (!S.sel[k] && liste.length === 1) S.sel[k] = liste[0].id;
    }
  }
  function filtreClasse(classeObligatoire) {
    preselectionAutomatique();
    const o = optionsCascade(S.sel);
    const libelles = { section: "adm.section", cycle: "adm.cycle", niveau: "c.niveau", classe: "c.classe" };
    return NIVEAUX_CASCADE.map(k => {
      const obligatoire = classeObligatoire && k === "classe";
      return `<div class="field" style="width:170px"><label>${t(libelles[k])}${obligatoire ? " *" : ""}</label>
        <select class="select" data-cascade="${k}">${option("", t(obligatoire ? "c.choisir" : "c.tous"), S.sel[k] || "")}${o[k].map(x => option(x.id, x.libelle, S.sel[k] || "")).join("")}</select></div>`;
    }).join("");
  }
  /* Bouton « Afficher » : un seul appel au backend, quand les filtres sont complets.
     Les données restent affichées tant que les filtres ne changent pas. */
  const CLES_ECRANS = {
    eleves: () => [],
    edt: () => [],
    presences: () => [S.f.presence.cours],
    notes: () => [S.f.notes.evaluation, S.f.notes.matiere],
    discipline: () => [S.f.discipline.evaluation],
    bulletins: () => [S.f.bulletin.type, S.f.bulletin.periode, S.f.bulletin.seuil, JSON.stringify(S.f.bulletin.regles)],
    scolarite: () => [S.f.regl.tranche],
  };
  const cleEcran = e => JSON.stringify([S.sel.classe, ...CLES_ECRANS[e]()]);
  const estAffiche = e => Boolean(S.sel.classe) && (S.autoAffiche || S.affiche[e] === cleEcran(e));
  const boutonAfficher = (e, libelle = "c.afficher") =>
    `<button class="btn" data-act="afficher" data-v="${e}" ${S.sel.classe ? "" : "disabled"}><i class="pi pi-search"></i>${t(libelle)}</button>`;
  function zoneVide(e) {
    if (S.sel.classe && !estAffiche(e)) return `<div class="card"><div class="empty"><i class="pi pi-search" style="font-size:28px"></i><p>${t(e === "eleves" ? "c.cliquerRechercher" : "c.cliquerAfficher")}</p></div></div>`;
    return videClasse();
  }
  const videClasse = () => `<div class="card"><div class="empty"><i class="pi ${S.sel.classe ? "pi-inbox" : "pi-filter"}" style="font-size:28px"></i><p>${t(S.sel.classe ? "c.videClasse" : "c.choisirClasse")}</p></div></div>`;

  /* =======================================================================
     ÉCRANS
     ======================================================================= */

  /* ---------------- Connexion ---------------- */
  function ecranConnexion() {
    return `
      <div class="login">
        <section class="login-side">
          ${marque()}
          <div>
            <h1>${t("login.accroche")}</h1>
            <p>${t("login.texte")}</p>
            <div class="login-features">
              <div><i class="pi pi-users"></i>${t("login.f1")}</div>
              <div><i class="pi pi-chart-bar"></i>${t("login.f2")}</div>
              <div><i class="pi pi-wallet"></i>${t("login.f3")}</div>
            </div>
          </div>
          <p class="small">© 2026 Eclair School</p>
        </section>
        <section class="login-form relative">
          <div class="login-tools">${outilsPreferences()}</div>
          <form data-form="login">
            <div class="hide-desktop">${marque()}</div>
            ${blocEcole()}
            <div><h1>${t("login.titre")}</h1><p class="muted" style="margin:6px 0 0">${t("login.sousTitre")}</p></div>
            <div class="field"><label for="lg-user">${t("login.utilisateur")}</label>
              <div class="input-icon"><i class="pi pi-user"></i><input id="lg-user" class="input" value="admin" autocomplete="username"></div></div>
            <div class="field"><label for="lg-pass">${t("login.motDePasse")}</label>
              <div class="input-icon"><i class="pi pi-lock"></i><input id="lg-pass" class="input" type="password" value="••••••••" autocomplete="current-password"></div></div>
            <button class="btn" type="submit" style="height:40px"><i class="pi pi-sign-in"></i>${t("login.connexion")}</button>
            <div class="message"><i class="pi pi-info-circle"></i><span class="small">${t("login.demo")}</span></div>
          </form>
        </section>
      </div>`;
  }

  /* ---------------- Tableau de bord ---------------- */
  function ecranDashboard() {
    const effectif = D.classes.reduce((s, c) => s + c.effectif, 0);
    const res = calculerBulletins(6, { type: "trimestre", id: 1 });
    const situations = elevesClasse(6).map(e => situationTranche(e.id, 1));
    const attendu = situations.reduce((s, x) => s + x.tr.montant, 0);
    const encaisse = situations.reduce((s, x) => s + Math.min(x.regle, x.tr.montant), 0);
    const heures = elevesClasse(6).reduce((s, e) => s + discipline(e.id, [1, 2]).total, 0);
    const moyennesClasses = [["6e A", 11.42], ["6e B", 10.87], ["5e A", 11.9], ["4e A", 10.31], ["3e A", 12.04], ["2nde C", res.stats.moyenne], ["1ère D", 11.15], ["Tle C", 12.61]];
    const maxBar = 20;
    const derniers = [...D.reglements].filter(r => r.statut === "valide").sort((a, b) => b.date.localeCompare(a.date)).slice(0, 5);
    const aSuivre = res.bulletins.filter(b => (b.moy != null && b.moy < 10) || b.discipline.total >= 8).slice(0, 4);
    const actions = [
      can("eleve:inscrire") ? `<button class="btn" data-go="inscription"><i class="pi pi-user-plus"></i>${t("dash.aInscrire")}</button>` : "",
      can("notation:ajouter") ? `<button class="btn outlined" data-go="notes"><i class="pi pi-pencil"></i>${t("dash.aNotes")}</button>` : "",
      can("reglement:ajouter") ? `<button class="btn outlined" data-go="scolarite"><i class="pi pi-wallet"></i>${t("dash.aReglement")}</button>` : "",
    ].join("");
    const carte = (icone, sev, label, valeur, sous) => `<div class="card stat"><div class="stat-icon ${sev}"><i class="pi ${icone}"></i></div><div><div class="stat-label">${label}</div><div class="stat-value">${valeur}</div><div class="stat-sub">${sous}</div></div></div>`;
    const statutEval = ev => ev.fin < AUJOURDHUI ? tag("secondary", t("eval.terminee")) : ev.debut <= AUJOURDHUI ? tag("success", t("eval.enCours")) : tag("info", t("eval.aVenir"));
    return entete(t("dash.bonjour", { nom: utilisateurCourant().prenom }), t("dash.sousTitre", { annee: D.ecole.annee }), actions) + `
      <div class="grid grid-4">
        ${carte("pi-users", "", t("dash.eleves"), fmtInt(effectif), t("dash.elevesSous", { n: D.classes.length }))}
        ${carte("pi-chart-line", "success", t("dash.moyenne"), fmt(res.stats.moyenne), t("dash.moyenneSous", { taux: fmt(res.stats.taux) }))}
        ${can("reglement:consulter") ? carte("pi-wallet", "warn", t("dash.recouvrement"), Math.round(encaisse * 100 / attendu) + " %", t("dash.recouvrementSous", { m: fcfa(encaisse) })) : carte("pi-list", "warn", t("dash.evaluations"), D.evaluations.length, t("dash.evaluationsSous"))}
        ${carte("pi-clock", "danger", t("dash.absences"), fmtInt(heures) + " h", t("dash.absencesSous"))}
      </div>
      <div class="grid grid-main-side" style="margin-top:16px">
        <div class="card">
          <div class="card-head"><h2>${t("dash.moyennesClasses")}</h2><span class="tag secondary">${t("c.trimestre")} 1</span></div>
          <div class="card-body"><div class="bars">${moyennesClasses.map(([l, v], i) => `
            <div class="bar ${l === "2nde C" ? "" : "alt"}"><b>${fmt(v)}</b><div style="height:${(v / maxBar) * 100}%"></div><small>${esc(l)}</small></div>`).join("")}
          </div></div>
        </div>
        <div class="card">
          <div class="card-head"><h2>${t("dash.evaluations")}</h2></div>
          <div class="card-body stack" style="gap:12px">
            ${D.evaluations.filter(e => !parentDe(e.id)).slice(0, 5).map(ev => `
              <div class="row-between"><div><div style="font-weight:600">${esc(ev.libelle)}</div><div class="small muted">${fmtDate(ev.debut)} → ${fmtDate(ev.fin)}</div></div>${statutEval(ev)}</div>`).join("")}
          </div>
        </div>
      </div>
      <div class="grid ${can("reglement:consulter") && can("eleve:consulter") ? "grid-2" : ""}" style="margin-top:16px">
        ${can("reglement:consulter") ? `<div class="card">
          <div class="card-head"><h2>${t("dash.derniersReglements")}</h2>${can("reglement:consulter") ? `<button class="btn text sm" data-go="scolarite">${t("c.voirTout")}<i class="pi pi-arrow-right"></i></button>` : ""}</div>
          <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.eleve")}</th><th>${t("c.date")}</th><th class="num">${t("c.montant")}</th></tr></thead><tbody>
            ${derniers.map(r => { const e = eleve(r.eleve); return `<tr><td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span><div>${esc(e.nom)} ${esc(e.prenom)}<div class="sub">${esc(byId(D.tranches, r.tranche).libelle)}</div></div></div></td><td>${fmtDate(r.date)}</td><td class="num">${fcfa(r.montant)}</td></tr>`; }).join("")}
          </tbody></table></div>
        </div>` : ""}
        ${can("eleve:consulter") ? `<div class="card">
          <div class="card-head"><h2>${t("dash.aSuivre")}</h2><span class="tag warn">2nde C</span></div>
          <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.eleve")}</th><th class="num">${t("bul.moyenne")}</th><th class="num">${t("disc.heures")}</th><th>${t("c.motif")}</th></tr></thead><tbody>
            ${aSuivre.map(b => `<tr class="clickable" data-go="eleves/${b.e.id}"><td><div class="person"><span class="avatar">${esc(initiales(b.e.prenom, b.e.nom))}</span>${esc(b.e.nom)} ${esc(b.e.prenom)}</div></td><td class="num">${fmt(b.moy)}</td><td class="num">${b.discipline.total} h</td><td>${b.moy < 10 ? tag("danger", t("dash.motifMoyenne")) : ""} ${b.discipline.total >= 8 ? tag("warn", t("dash.motifAbsences")) : ""}</td></tr>`).join("")}
          </tbody></table></div>
        </div>` : ""}
      </div>`;
  }

  /* ---------------- Élèves ---------------- */
  // Simule GET /eleves/by-classe/{id}?page=&page_size=&q=&genre= (filtre et pagination faits par le backend)
  function pageElevesClasse() {
    const f = S.f.eleves;
    const termes = f.qApplique.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const tous = D.eleves.filter(e => e.classe === Number(S.sel.classe) && (!f.genre || e.genre === f.genre)
      && termes.every(x => `${e.nom} ${e.prenom} ${e.matricule}`.toLowerCase().includes(x)))
      .sort((a, b) => `${a.nom} ${a.prenom}`.localeCompare(`${b.nom} ${b.prenom}`));
    const totalPages = Math.max(1, Math.ceil(tous.length / f.pageSize));
    const page = Math.min(Math.max(1, f.page), totalPages);
    return { page, totalPages, total: tous.length, eleves: tous.slice((page - 1) * f.pageSize, page * f.pageSize) };
  }
  function paginateur(p, pageSize, actionPage = "page-eleves", champTaille = "eleves.pageSize") {
    const de = p.total ? (p.page - 1) * pageSize + 1 : 0, a = Math.min(p.page * pageSize, p.total);
    const pages = Array.from({ length: p.totalPages }, (_, i) => i + 1);
    return `<div class="paginator">
      <span>${t("c.pagination", { de, a, total: p.total })}</span>
      <div class="row">
        <div class="pages">
          <button data-act="${actionPage}" data-v="${p.page - 1}" ${p.page <= 1 ? "disabled" : ""} aria-label="${t("c.precedent")}"><i class="pi pi-angle-left"></i></button>
          ${pages.map(n => `<button class="${n === p.page ? "on" : ""}" data-act="${actionPage}" data-v="${n}">${n}</button>`).join("")}
          <button data-act="${actionPage}" data-v="${p.page + 1}" ${p.page >= p.totalPages ? "disabled" : ""} aria-label="${t("c.suivant")}"><i class="pi pi-angle-right"></i></button>
        </div>
        <select class="select" style="width:90px;height:32px" data-f="${champTaille}" aria-label="${t("c.parPage")}">${[10, 25, 50].map(n => option(n, n, pageSize)).join("")}</select>
      </div>
    </div>`;
  }
  function lignesEleves(liste) {
    if (!liste.length) return `<tr><td colspan="7"><div class="empty">${t("c.aucunResultat")}</div></td></tr>`;
    return liste.map(e => `
      <tr class="clickable" data-go="eleves/${e.id}">
        <td class="mono">${esc(e.matricule)}</td>
        <td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span><div>${esc(e.nom)} ${esc(e.prenom)}<div class="sub">${t("eleve.ne", { date: fmtDate(e.naissance), lieu: e.lieu })}</div></div></div></td>
        <td>${e.genre === "F" ? t("c.fille") : t("c.garcon")}</td>
        <td>${esc(classe(e.classe).libelle)}</td>
        <td>${e.redoublant ? tag("warn", t("eleve.redoublant")) : ""} ${e.nouveau ? tag("info", t("eleve.nouveau")) : ""}</td>
        <td>${tag("success", t("c.inscrit"))}</td>
        <td class="right">${can("eleve:modifier") ? `<button class="btn text icon sm" data-act="modifier-eleve" data-v="${e.id}" title="${t("c.modifier")}"><i class="pi pi-pencil"></i></button>` : ""}<button class="btn text icon sm" data-go="eleves/${e.id}" title="${t("c.voir")}"><i class="pi pi-eye"></i></button></td>
      </tr>`).join("");
  }
  const ligneResultatEcole = e => `<tr class="clickable" data-go="eleves/${e.id}"><td class="mono">${esc(e.matricule)}</td>
    <td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span><div>${esc(e.nom)} ${esc(e.prenom)}<div class="sub">${t("eleve.ne", { date: fmtDate(e.naissance), lieu: e.lieu })}</div></div></div></td>
    <td>${esc(classe(e.classe).libelle)}</td><td class="right"><button class="btn text icon sm" data-go="eleves/${e.id}" title="${t("c.voir")}"><i class="pi pi-eye"></i></button></td></tr>`;
  function ecranEleves() {
    const f = S.f.eleves;
    // 1. Recherche sur toute l'école (un appel, déclenché par le bouton ou Entrée, 3 caractères minimum)
    const q = (S.rechercheEcole || "").toLowerCase();
    const resultats = S.rechercheEcole == null ? null
      : D.eleves.filter(e => `${e.nom} ${e.prenom} ${e.matricule}`.toLowerCase().includes(q)).slice(0, 20);
    const carteEcole = can("eleve:rechercher") ? `
      <div class="card" style="margin-bottom:16px">
        <div class="card-head"><div><h2>${t("eleves.rechercheEcole")}</h2><div class="small muted">${t("eleves.rechercheEcoleAide")}</div></div></div>
        <div class="card-body"><form class="filters" data-form="recherche-ecole">
          <div class="field" style="width:380px"><label>${t("eleves.nomOuMatricule")}</label><div class="input-icon"><i class="pi pi-search"></i><input class="input" id="q-ecole" data-live="ecole-q" value="${esc(S.qEcole)}" placeholder="${t("eleves.rechercherPh")}" autocomplete="off"></div></div>
          <button class="btn" type="submit" id="btn-ecole" ${S.qEcole.trim().length >= 3 ? "" : "disabled"}><i class="pi pi-search"></i>${t("c.rechercher")}</button>
          ${resultats ? `<button class="btn text" type="button" data-act="effacer-ecole"><i class="pi pi-times"></i>${t("c.effacer")}</button>` : ""}
        </form></div>
        ${resultats ? `<div class="card-head" style="border-top:1px solid var(--border)"><span class="small muted">${t("eleves.resultatsEcole", { n: resultats.length, q: S.rechercheEcole })}</span></div>
          <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.matricule")}</th><th>${t("c.eleve")}</th><th>${t("c.classe")}</th><th></th></tr></thead><tbody>
          ${resultats.length ? resultats.map(ligneResultatEcole).join("") : `<tr><td colspan="4"><div class="empty">${t("c.aucunResultat")}</div></td></tr>`}
          </tbody></table></div>` : ""}
      </div>` : "";
    // 2. Recherche par classe : un appel au clic sur « Rechercher », puis filtre local sans appel
    const charge = estAffiche("eleves");
    const pageCourante = charge ? pageElevesClasse() : null;
    const nbClasse = charge ? D.eleves.filter(e => e.classe === Number(S.sel.classe)).length : 0;
    return entete(t("eleves.titre"), t("eleves.sousTitre"), can("eleve:inscrire") ? `<button class="btn" data-go="inscription"><i class="pi pi-user-plus"></i>${t("dash.aInscrire")}</button>` : "") + carteEcole + `
      <div class="card">
        <div class="card-head"><div><h2>${t("eleves.parClasse")}</h2><div class="small muted">${t("eleves.parClasseAide")}</div></div></div>
        <div class="card-body"><div class="filters">${filtreClasse(true)}${boutonAfficher("eleves", "c.rechercher")}</div></div>
        ${charge ? `
        <div class="card-head" style="border-top:1px solid var(--border)">
          <form class="filters" data-form="filtre-classe">
            <div class="field" style="width:280px"><label>${t("eleves.filtrerClasse")}</label><div class="input-icon"><i class="pi pi-filter"></i><input class="input" id="q-classe" value="${esc(f.q)}" placeholder="${t("eleves.rechercherPh")}" autocomplete="off"></div></div>
            <div class="field"><label>${t("c.genre")}</label><select class="select" data-f="eleves.genre">${option("", t("c.tous"), f.genre)}${option("F", t("c.fille"), f.genre)}${option("M", t("c.garcon"), f.genre)}</select></div>
            <button class="btn outlined" type="submit"><i class="pi pi-filter"></i>${t("c.filtrer")}</button>
            ${f.qApplique || f.genre ? `<button class="btn text" type="button" data-act="effacer-filtre-classe"><i class="pi pi-times"></i>${t("c.effacer")}</button>` : ""}
          </form>
          <div class="row"><span class="tag info">${classe(S.sel.classe).libelle} · ${nbClasse} ${t("c.eleves")}</span><button class="btn secondary sm"><i class="pi pi-download"></i>${t("c.exporter")}</button></div>
        </div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.matricule")}</th><th>${t("c.eleve")}</th><th>${t("c.genre")}</th><th>${t("c.classe")}</th><th>${t("eleve.statut")}</th><th>${t("c.inscription")}</th><th></th></tr></thead>
          <tbody>${lignesEleves(pageCourante.eleves)}</tbody></table></div>
        ${paginateur(pageCourante, f.pageSize)}` : `<div style="border-top:1px solid var(--border)">${zoneVide("eleves").replace('<div class="card">', "<div>")}</div>`}
      </div>`;
  }

  function ecranFicheEleve(id) {
    const e = eleve(id);
    if (!e) return accesRefuse();
    const tab = S.tab.eleve;
    const res = calculerBulletins(e.classe, { type: "trimestre", id: 1 });
    const b = res.bulletins.find(x => x.e.id === e.id);
    const onglets = [["infos", "eleve.tInfos"], ["notes", "eleve.tNotes"], ["scolarite", "eleve.tScolarite"], ["discipline", "eleve.tDiscipline"]];
    let corps = "";
    if (tab === "infos") {
      const champ = (l, v) => `<div class="field"><label>${t(l)}</label><div>${esc(v || "—")}</div></div>`;
      corps = `<div class="form-grid">
        ${champ("eleve.nom", e.nom)}${champ("eleve.prenom", e.prenom)}${champ("eleve.naissance", fmtDate(e.naissance))}${champ("eleve.lieu", e.lieu)}
        ${champ("c.genre", e.genre === "F" ? t("c.fille") : t("c.garcon"))}${champ("eleve.quartier", e.quartier)}
        ${champ("eleve.pere", e.pere)}${champ("eleve.mere", e.mere)}${champ("eleve.telephone", e.telephone)}${champ("c.matricule", e.matricule)}
      </div>`;
    } else if (tab === "notes") {
      corps = `<div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.matiere")}</th><th class="num">${t("eval.seq1")}</th><th class="num">${t("eval.seq2")}</th><th class="num">${t("bul.moyT1")}</th><th class="num">${t("bul.coef")}</th><th>${t("bul.appreciation")}</th></tr></thead><tbody>
        ${D.matieres.map(m => { const l = b.groupes.flatMap(g => g.lignes).find(x => x.m.id === m.id); const n1 = noteEval(1, m.id, e.id), n2 = noteEval(2, m.id, e.id);
          return `<tr><td>${esc(m.libelle)}</td><td class="num">${n1 != null ? fmt(sur20(n1, m)) : `<span class="muted">${t("notes.nc")}</span>`}</td><td class="num">${n2 != null ? fmt(sur20(n2, m)) : `<span class="muted">${t("notes.nc")}</span>`}</td><td class="num"><b>${fmt(l.note)}</b></td><td class="num">${l.coef}</td><td>${esc(l.appreciation || "—")}</td></tr>`; }).join("")}
        <tr class="total"><td>${t("bul.moyenneGenerale")}</td><td colspan="2"></td><td class="num">${fmt(b.moy)}</td><td></td><td>${libelleRang(b.rang, e.genre)} / ${res.stats.effectif}</td></tr>
      </tbody></table></div>`;
    } else if (tab === "scolarite") {
      corps = `<div class="stack">${D.tranches.map(tr => { const s = situationTranche(e.id, tr.id); return `
        <div><div class="row-between"><div><b>${esc(tr.libelle)}</b> <span class="muted small">· ${fcfa(tr.montant)}</span></div>${tagPaiement(s.statut)}</div>
        <div class="progress ${s.statut === "total" ? "success" : s.statut === "partiel" ? "warn" : "danger"}" style="margin:8px 0 4px"><div style="width:${s.pct}%"></div></div>
        <div class="small muted">${t("pay.regleReste", { regle: fcfa(s.regle), reste: fcfa(s.reste) })}</div></div>`; }).join("")}</div>`;
    } else {
      corps = `<div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.evaluation")}</th><th class="num">${t("disc.nonJustifiees")}</th><th class="num">${t("disc.justifiees")}</th><th class="num">${t("disc.total")}</th><th>${t("disc.decision")}</th></tr></thead><tbody>
        ${[1, 2].map(ev => { const d = discipline(e.id, [ev]); return `<tr><td>${esc(evaluation(ev).libelle)}</td><td class="num">${d.nj}</td><td class="num">${d.j}</td><td class="num"><b>${d.total}</b></td><td>${tag(d.total > 5 ? "warn" : "success", d.decision)}</td></tr>`; }).join("")}
      </tbody></table></div>`;
    }
    return `
      <div class="row" style="margin-bottom:14px"><button class="btn text sm" data-go="eleves"><i class="pi pi-arrow-left"></i>${t("eleves.retour")}</button></div>
      <div class="card card-body" style="margin-bottom:16px">
        <div class="row-between">
          <div class="row" style="gap:16px"><span class="avatar lg">${esc(initiales(e.prenom, e.nom))}</span>
            <div><h1>${esc(e.nom)} ${esc(e.prenom)}</h1><div class="row small muted" style="margin-top:6px"><span class="mono">${esc(e.matricule)}</span>·<span>${esc(classe(e.classe).libelle)}</span>·<span>${esc(D.ecole.annee)}</span></div>
            <div class="row" style="margin-top:8px">${tag("success", t("c.inscrit"))}${e.redoublant ? tag("warn", t("eleve.redoublant")) : ""}${e.nouveau ? tag("info", t("eleve.nouveau")) : ""}</div></div></div>
          <div class="row">
            <button class="btn secondary" data-act="recu-eleve" data-v="${e.id}"><i class="pi pi-print"></i>${t("recu.bouton")}</button>
            ${can("eleve:modifier") ? `<button class="btn secondary" data-act="modifier-eleve" data-v="${e.id}"><i class="pi pi-pencil"></i>${t("c.modifier")}</button>` : ""}
            ${can("bulletin:generer") ? `<button class="btn" data-act="apercu-bulletin" data-v="${e.id}"><i class="pi pi-file"></i>${t("bul.bulletinT1")}</button>` : ""}
          </div>
        </div>
      </div>
      <div class="card">
        <div class="tabs" style="padding:0 10px">${onglets.map(([k, l]) => `<div class="tab ${tab === k ? "on" : ""}" data-tab="eleve" data-v="${k}">${t(l)}</div>`).join("")}</div>
        <div class="card-body">${corps}</div>
      </div>`;
  }

  /* ---------------- Inscription ---------------- */
  const ongletsInscription = () => `<div class="tabs" style="margin-bottom:16px">${[["nouvelle", "insc.tNouvelle", "pi-user-plus"], ["historique", "insc.tHistorique", "pi-history"]]
    .map(([k, l, i]) => `<div class="tab ${S.tab.insc === k ? "on" : ""}" data-tab="insc" data-v="${k}"><i class="pi ${i}"></i> ${t(l)}</div>`).join("")}</div>`;

  /* ---------------- Historique des inscriptions ---------------- */
  const infoEleveInscription = ins => ins.eleve ? eleve(ins.eleve) : ins.eleveInfo;
  // Simule GET /inscription/historique?date_debut=&date_fin=&q=&page=&page_size= (tri par date décroissante)
  function pageHistorique() {
    const H = S.hist, f = H.applique;
    const termes = normaliser(f.q.trim()).split(/\s+/).filter(Boolean);
    const lignes = D.inscriptions
      .filter(ins => (!f.du || ins.date >= f.du) && (!f.au || ins.date <= f.au))
      .filter(ins => { const e = infoEleveInscription(ins); const texte = normaliser(`${e.nom} ${e.prenom || ""} ${e.matricule}`); return termes.every(x => texte.includes(x)); })
      .sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id);
    const totalPages = Math.max(1, Math.ceil(lignes.length / H.pageSize));
    const page = Math.min(Math.max(1, H.page), totalPages);
    return { page, totalPages, total: lignes.length, lignes: lignes.slice((page - 1) * H.pageSize, page * H.pageSize) };
  }
  function ecranHistoriqueInscriptions() {
    const H = S.hist;
    const p = pageHistorique();
    const filtreActif = H.applique.du || H.applique.au || H.applique.q;
    const peutModifier = can("eleve:inscrire");
    return entete(t("insc.titre"), t("insc.sousTitre")) + ongletsInscription() + `
      <div class="card">
        <div class="card-body"><form class="filters" data-form="filtre-hist">
          <div class="field" style="width:170px"><label>${t("hist.du")}</label><input class="input" type="date" id="hist-du" value="${esc(H.du)}"></div>
          <div class="field" style="width:170px"><label>${t("hist.au")}</label><input class="input" type="date" id="hist-au" value="${esc(H.au)}"></div>
          <div class="field" style="width:300px"><label>${t("eleves.nomOuMatricule")}</label><div class="input-icon"><i class="pi pi-search"></i><input class="input" id="hist-q" value="${esc(H.q)}" placeholder="${t("eleves.rechercherPh")}" autocomplete="off"></div></div>
          <button class="btn" type="submit"><i class="pi pi-filter"></i>${t("c.filtrer")}</button>
          ${filtreActif ? `<button class="btn text" type="button" data-act="effacer-hist"><i class="pi pi-times"></i>${t("c.effacer")}</button>` : ""}
          <div id="hist-erreur" class="grow"></div>
        </form></div>
        <div class="card-head" style="border-top:1px solid var(--border)"><span class="small muted"><i class="pi pi-sort-amount-down"></i> ${t("hist.tri")}</span><span class="tag info">${t("hist.total", { n: p.total })}</span></div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.date")}</th><th>${t("hist.recu")}</th><th>${t("c.eleve")}</th><th>${t("c.classe")}</th><th>${t("recu.type")}</th><th>${t("eleve.redoublant")}</th><th>${t("recu.enregistrePar")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
        ${p.lignes.length ? p.lignes.map(ins => { const e = infoEleveInscription(ins), c = classe(ins.classe);
          return `<tr><td class="mono">${fmtDate(ins.date)}</td><td class="mono small">${esc(ins.numero)}</td>
          <td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span><div>${esc(e.nom)} ${esc(e.prenom || "")}<div class="sub mono">${esc(e.matricule)}</div></div></div></td>
          <td><b>${esc(c.libelle)}</b><div class="small muted">${esc(byId(D.niveaux, c.niveau).libelle)}</div></td>
          <td>${tag(ins.type === "nouveau" ? "info" : "secondary", t(ins.type === "nouveau" ? "recu.typeNouveau" : "recu.typeReinscription"))}</td>
          <td>${t(ins.redoublant ? "c.oui" : "c.non")}</td><td class="mono small">${esc(ins.user)}</td>
          <td>${ins.derniereModif ? `${tag("warn", t("hist.modifiee"), "pi-pencil")}<div class="small muted">${fmtDate(ins.derniereModif.date)} · ${esc(ins.derniereModif.user)}</div>` : tag("success", t("hist.originale"))}</td>
          <td class="right"><button class="btn text icon sm" data-act="recu-inscription" data-v="${ins.id}" title="${t("hist.reimprimer")}"><i class="pi pi-print"></i></button>${peutModifier ? `<button class="btn text icon sm" data-act="modifier-insc" data-v="${ins.id}" title="${t("hist.modifier")}"><i class="pi pi-pencil"></i></button>` : ""}</td></tr>`; }).join("")
          : `<tr><td colspan="9"><div class="empty">${t("c.aucunResultat")}</div></td></tr>`}
        </tbody></table></div>
        ${paginateur(p, H.pageSize, "page-hist", "hist.pageSize")}
      </div>`;
  }
  function dialogModifierInscription() {
    const E = S.editInsc, ins = byId(D.inscriptions, E.id), e = infoEleveInscription(ins);
    const classesNiveau = D.classes.filter(c => c.niveau === Number(E.niveau));
    const bloquee = donneesAnnee(ins).length > 0;
    dialog(t("hist.modifierTitre", { e: `${e.nom} ${e.prenom || ""}` }), `<div class="stack">
      <div class="row small muted"><span class="mono">${esc(ins.numero)}</span>·<span>${fmtDate(ins.date)}</span>·<span>${t("hist.classeActuelle")} : <b>${esc(classe(ins.classe).libelle)}</b></span></div>
      <div class="form-grid">
        <div class="field"><label>${t("c.niveau")} *</label><select class="select" data-edit-insc="niveau" ${bloquee ? "disabled" : ""}>${D.niveaux.map(n => option(n.id, `${n.libelle} · ${byId(D.cycles, n.cycle).libelle}`, E.niveau)).join("")}</select></div>
        <div class="field"><label>${t("c.classe")} *</label><select class="select" data-edit-insc="classe" ${bloquee ? "disabled" : ""}>${option("", t("c.choisir"), E.classe)}${classesNiveau.map(c => option(c.id, `${c.libelle} (${c.effectif} ${t("c.eleves")})`, E.classe)).join("")}</select></div>
        <div class="field"><label>${t("eleve.redoublant")}</label><label class="row"><span class="switch"><input type="checkbox" data-edit-insc="redoublant" ${E.redoublant ? "checked" : ""}><span></span></span>${t(E.redoublant ? "c.oui" : "c.non")}</label></div>
      </div>
      ${bloquee
        ? `<div class="message danger"><i class="pi pi-lock"></i><div class="small"><b>${t("hist.classeBloquee")}</b><div>${t("hist.classeBloqueeTexte", { d: donneesAnnee(ins).map(x => t("hist.donnee." + x)).join(", ") })}</div></div></div>`
        : `<div class="message"><i class="pi pi-info-circle"></i><div class="small">${t("hist.infoModification")}</div></div>`}
    </div>`, `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" data-act="enregistrer-insc" ${E.classe ? "" : "disabled"}><i class="pi pi-check"></i>${t("c.enregistrer")}</button>`);
  }
  // Données de l'élève dans l'année en cours qui empêchent de changer sa classe (simule le contrôle du backend)
  function donneesAnnee(ins) {
    if (!ins.eleve) return [];
    const donnees = [];
    if (Object.values(D.notes).some(parMatiere => Object.values(parMatiere).some(parEleve => parEleve[ins.eleve] != null))) donnees.push("notes");
    if (Object.values(D.disciplines).some(parEleve => parEleve[ins.eleve])) donnees.push("discipline");
    return donnees;
  }
  function enregistrerModificationInscription() {
    const E = S.editInsc, ins = byId(D.inscriptions, E.id);
    const user = utilisateurCourant().username;
    const changements = [];
    if (Number(E.classe) !== ins.classe) changements.push(`${t("c.classe")} : ${classe(ins.classe).libelle} → ${classe(E.classe).libelle}`);
    if (E.redoublant !== ins.redoublant) changements.push(`${t("eleve.redoublant")} : ${t(E.redoublant ? "c.oui" : "c.non")}`);
    fermer();
    if (!changements.length) { toast("info", t("hist.aucunChangement"), ""); return; }
    ins.derniereModif = { date: AUJOURDHUI, user };
    ins.classe = Number(E.classe);
    ins.redoublant = E.redoublant;
    if (ins.eleve) { const e = eleve(ins.eleve); e.classe = ins.classe; e.redoublant = ins.redoublant; }
    render();
    toast("success", t("hist.modifieOk"), changements.join(" · "));
  }

  function ecranInscription() {
    if (S.tab.insc === "historique") return ecranHistoriqueInscriptions();
    const I = S.insc;
    const etapes = I.type === "nouveau" ? ["insc.eType", "insc.eEleve", "insc.eClasse", "insc.eConfirmation"] : ["insc.eType", "insc.eChoixClasse"];
    const barre = `<div class="steps">${etapes.map((l, i) => `${i ? `<div class="step-line"></div>` : ""}<div class="step ${I.etape === i + 1 ? "on" : I.etape > i + 1 ? "done" : ""}"><span class="n">${I.etape > i + 1 ? `<i class="pi pi-check"></i>` : i + 1}</span>${t(l)}</div>`).join("")}</div>`;
    let corps = "";
    if (I.etape === 1) {
      const choix = (v, icone, titre, texte) => `<div class="card card-body clickable" data-act="insc-type" data-v="${v}" style="cursor:pointer;${I.type === v ? "border-color:var(--primary);box-shadow:var(--focus-ring)" : ""}">
        <div class="row"><div class="stat-icon"><i class="pi ${icone}"></i></div><div><h3>${t(titre)}</h3><div class="muted small">${t(texte)}</div></div></div></div>`;
      corps = `<div class="grid grid-2">${choix("nouveau", "pi-user-plus", "insc.nouveau", "insc.nouveauTexte")}${choix("ancien", "pi-replay", "insc.ancien", "insc.ancienTexte")}</div>`;
    } else if (I.type === "ancien") {
      const q = (I.qAncien || "").trim().toLowerCase();
      const liste = D.anciensEleves.filter(a => !q || `${a.nom} ${a.prenom} ${a.matricule}`.toLowerCase().includes(q));
      corps = `<div class="message" style="margin-bottom:14px"><i class="pi pi-info-circle"></i><div class="small">${t("insc.ancienInfo")}</div></div>
        <div class="filters" style="margin-bottom:12px"><div class="field" style="width:320px"><label>${t("c.rechercher")}</label><div class="input-icon"><i class="pi pi-search"></i><input class="input" data-f="insc.qAncien" value="${esc(I.qAncien || "")}" placeholder="${t("eleves.rechercherPh")}"></div></div></div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.eleve")}</th><th>${t("insc.anneePrec")}</th><th>${t("insc.decisionPrec")}</th><th>${t("insc.niveauPassage")}</th><th style="width:200px">${t("insc.classe")}</th><th></th></tr></thead><tbody>
        ${liste.length ? liste.map(a => { const classes = D.classes.filter(c => c.niveau === a.niveau); const choix = S.choixClasse[a.id] || classes[0].id;
          return `<tr><td><div class="person"><span class="avatar">${esc(initiales(a.prenom, a.nom))}</span><div>${esc(a.nom)} ${esc(a.prenom)}<div class="sub mono">${esc(a.matricule)}</div></div></div></td>
          <td>${esc(a.ancienneClasse)} <span class="small muted">· 2025-2026</span></td>
          <td>${tag(a.decision === "Promu" ? "success" : "warn", t(a.decision === "Promu" ? "insc.promu" : "insc.redouble"))}</td>
          <td><b>${esc(byId(D.niveaux, a.niveau).libelle)}</b></td>
          <td><select class="select" data-choix="${a.id}">${classes.map(c => option(c.id, `${c.libelle} (${c.effectif})`, choix)).join("")}</select></td>
          <td class="right"><button class="btn sm" data-act="inscrire-ancien" data-v="${a.id}"><i class="pi pi-check"></i>${t("insc.inscrire")}</button></td></tr>`; }).join("")
          : `<tr><td colspan="6"><div class="empty">${t("insc.aucunAncien")}</div></td></tr>`}
        </tbody></table></div>`;
    } else if (I.etape === 2) {
      const ch = (l, type = "text", val = "", req = true) => `<div class="field"><label>${t(l)}${req ? " *" : ""}</label><input class="input" type="${type}" value="${esc(val)}"></div>`;
      corps = `<div class="form-grid">
        ${ch("eleve.nom", "text", "TAMBA")}${ch("eleve.prenom", "text", "Eliane", false)}
        ${ch("eleve.naissance", "date", "2011-04-18")}${ch("eleve.lieu", "text", "Douala")}
        <div class="field"><label>${t("c.genre")} *</label><div class="segmented"><button class="on">${t("c.fille")}</button><button>${t("c.garcon")}</button></div></div>
        ${ch("eleve.quartier", "text", "Akwa")}
        ${ch("eleve.pere", "text", "", false)}${ch("eleve.mere", "text", "NGASSA Rose")}
        ${ch("eleve.telephone1", "tel", "6 77 45 12 98")}${ch("eleve.telephone2", "tel", "", false)}
        <div class="field full"><span class="hint"><i class="pi pi-info-circle"></i> ${t("insc.matriculeAuto")}</span></div>
      </div>`;
    } else if (I.etape === 3) {
      corps = `<div class="form-grid">
        <div class="field"><label>${t("c.niveau")} *</label><select class="select" data-f="insc.niveau">${option("", t("c.choisir"), I.niveau)}${D.niveaux.map(n => option(n.id, `${n.libelle} · ${byId(D.cycles, n.cycle).libelle}`, I.niveau)).join("")}</select></div>
        <div class="field"><label>${t("c.classe")} *</label><select class="select" data-f="insc.classe" ${I.niveau ? "" : "disabled"}>${option("", t(I.niveau ? "c.choisir" : "insc.choisirNiveau"), I.classe)}${D.classes.filter(c => c.niveau === Number(I.niveau)).map(c => option(c.id, `${c.libelle} (${c.effectif} ${t("c.eleves")})`, I.classe)).join("")}</select></div>
        <div class="field"><label>${t("insc.anneeScolaire")}</label><input class="input" value="${esc(D.ecole.annee)}" disabled></div>
        <div class="field"><label>${t("eleve.redoublant")}</label><label class="row"><span class="switch"><input type="checkbox" ${I.redoublant ? "checked" : ""} data-act="insc-redoublant"><span></span></span>${t(I.redoublant ? "c.oui" : "c.non")}</label></div>
        <div class="field"><label>${t("eleve.nouveau")}</label><label class="row"><span class="switch"><input type="checkbox" checked><span></span></span>${t("c.oui")}</label></div>
      </div>`;
    } else {
      corps = `<div class="message success" style="margin-bottom:14px"><i class="pi pi-check-circle"></i>${t("insc.pret")}</div>
        <div class="form-grid"><div class="field"><label>${t("c.eleve")}</label><div><b>TAMBA Eliane</b> · ${t("c.fille")} · ${fmtDate("2011-04-18")}</div></div>
        <div class="field"><label>${t("c.classe")}</label><div><b>${esc(classe(I.classe).libelle)}</b> · ${esc(D.ecole.annee)}</div></div>
        <div class="field"><label>${t("c.matricule")}</label><div class="mono">26F0013 <span class="muted small">(${t("insc.genere")})</span></div></div>
        <div class="field"><label>${t("c.date")}</label><div>${fmtDate(AUJOURDHUI)}</div></div></div>`;
    }
    const nav = I.type === "ancien" && I.etape > 1 ? `<button class="btn secondary" data-act="insc-prec"><i class="pi pi-arrow-left"></i>${t("c.precedent")}</button>`
      : `<div class="row-between" style="width:100%">${I.etape > 1 ? `<button class="btn secondary" data-act="insc-prec"><i class="pi pi-arrow-left"></i>${t("c.precedent")}</button>` : "<span></span>"}
         ${I.etape < 4 ? `<button class="btn" data-act="insc-suiv" ${I.etape === 3 && !I.classe ? "disabled" : ""}>${t("c.suivant")}<i class="pi pi-arrow-right"></i></button>` : `<button class="btn success" data-act="insc-valider"><i class="pi pi-check"></i>${t("insc.valider")}</button>`}</div>`;
    return entete(t("insc.titre"), t("insc.sousTitre")) + ongletsInscription() + `<div class="card"><div class="card-body">${barre}${corps}</div><div class="dialog-foot">${nav}</div></div>`;
  }

  /* ---------------- Enseignants ---------------- */
  const MATIERES_ENSEIGNEES = () => [...new Set(D.matieres.map(m => m.libelle))].sort((a, b) => a.localeCompare(b));
  // Simule GET /enseignant/all?q=&matiere=&page=&page_size= (filtre et pagination faits par le backend)
  function pageEnseignants() {
    const E = S.ens, f = E.applique;
    const termes = normaliser(f.q.trim()).split(/\s+/).filter(Boolean);
    const liste = D.enseignants
      .filter(p => termes.every(x => normaliser(`${p.nom} ${p.prenom || ""}`).includes(x)))
      .filter(p => !f.matiere || p.matieres.includes(f.matiere))
      .sort((a, b) => `${a.nom} ${a.prenom}`.localeCompare(`${b.nom} ${b.prenom}`));
    const totalPages = Math.max(1, Math.ceil(liste.length / E.pageSize));
    const page = Math.min(Math.max(1, E.page), totalPages);
    return { page, totalPages, total: liste.length, lignes: liste.slice((page - 1) * E.pageSize, page * E.pageSize) };
  }
  function ecranEnseignants() {
    const E = S.ens, p = pageEnseignants();
    const filtreActif = E.applique.q || E.applique.matiere;
    return entete(t("ens.titre"), t("ens.sousTitre"), can("enseignant:ajouter") ? `<button class="btn" data-act="ajouter-enseignant"><i class="pi pi-plus"></i>${t("ens.ajouter")}</button>` : "") + `
      <div class="card">
        <div class="card-body"><form class="filters" data-form="filtre-ens">
          <div class="field" style="width:300px"><label>${t("ens.nomPrenom")}</label><div class="input-icon"><i class="pi pi-search"></i><input class="input" id="ens-q" value="${esc(E.q)}" placeholder="${t("ens.nomPrenom")}" autocomplete="off"></div></div>
          <div class="field" style="width:240px"><label>${t("ens.matiereEnseignee")}</label><select class="select" id="ens-matiere">${option("", t("c.toutes"), E.matiere)}${MATIERES_ENSEIGNEES().map(m => option(m, m, E.matiere)).join("")}</select></div>
          <button class="btn" type="submit"><i class="pi pi-filter"></i>${t("c.filtrer")}</button>
          ${filtreActif ? `<button class="btn text" type="button" data-act="effacer-ens"><i class="pi pi-times"></i>${t("c.effacer")}</button>` : ""}
        </form></div>
        <div class="card-head" style="border-top:1px solid var(--border)"><span class="small muted">${t("ens.tri")}</span><span class="tag info">${t("ens.total", { n: p.total })}</span></div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("ens.enseignant")}</th><th>${t("c.genre")}</th><th>${t("c.telephone")}</th><th>${t("ens.salaire")}</th><th>${t("ens.matieres")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
        ${p.lignes.length ? p.lignes.map(x => `<tr><td><div class="person"><span class="avatar">${esc(initiales(x.prenom, x.nom))}</span><div>${esc(x.nom)} ${esc(x.prenom || "")}<div class="sub">${esc(x.diplome)}</div></div></div></td>
          <td>${t(x.genre === "F" ? "ens.femme" : "ens.homme")}</td>
          <td class="mono small">${esc(x.telephone)}${x.telephone2 ? `<div>${esc(x.telephone2)}</div>` : ""}</td>
          <td>${tag(x.salaire === "Mensuel" ? "info" : "secondary", t(x.salaire === "Mensuel" ? "ens.mensuel" : "ens.horaire"))}<div class="small muted">${fcfa(x.montant)}${x.salaire === "Horaire" ? " / h" : ""}</div></td>
          <td><div class="row" style="gap:4px">${x.matieres.length ? x.matieres.map(m => tag("", m)).join("") : `<span class="muted small">${t("ens.aucuneMatiere")}</span>`}</div></td>
          <td>${x.actif ? tag("success", t("c.actif")) : tag("secondary", t("c.inactif"))}</td>
          <td class="right" style="white-space:nowrap">${can("enseignement:ajouter") || can("enseignement:supprimer") ? `<button class="btn text icon sm" data-act="matieres-ens" data-v="${x.id}" title="${t("ens.gererMatieres")}"><i class="pi pi-book"></i></button>` : ""}${can("enseignant:modifier") ? `<button class="btn text icon sm" data-act="modifier-ens" data-v="${x.id}" title="${t("c.modifier")}"><i class="pi pi-pencil"></i></button>` : ""}${can("enseignant:supprimer") ? `<button class="btn text icon sm" data-act="confirmer-suppression" title="${t("c.supprimer")}"><i class="pi pi-trash" style="color:var(--danger)"></i></button>` : ""}</td></tr>`).join("")
          : `<tr><td colspan="7"><div class="empty">${t("c.aucunResultat")}</div></td></tr>`}
        </tbody></table></div>
        ${paginateur(p, E.pageSize, "page-ens", "ens.pageSize")}
      </div>`;
  }
  const MOYENS_PAIEMENT = [["ESPECE", "ens.espece", "pi-money-bill"], ["COMPTE BANCAIRE", "ens.compteBancaire", "pi-building"], ["MOBILE", "ens.mobile", "pi-mobile"]];
  const avecCompte = moyen => moyen === "COMPTE BANCAIRE" || moyen === "MOBILE";
  // Numéro de compte complet : seulement pour la gestion des salaires (comme le backend)
  const peutVoirCompte = () => can("salaire:ajouter") || can("salaire:modifier");
  const masquerCompte = n => { const c = (n || "").replace(/\s/g, ""); return c.length > 4 ? `•••• ${c.slice(-4)}` : "••••"; };
  // complet = true : fiche salaire de l'enseignant (numéro en clair si autorisé) ; sinon numéro toujours masqué (listes)
  const moyenPaiement = (x, complet = false) => {
    if (!x.moyenPaiement) return tag("warn", t("sal.nonConfigure"));
    const [, l, i] = MOYENS_PAIEMENT.find(m => m[0] === x.moyenPaiement);
    if (!avecCompte(x.moyenPaiement)) return `<i class="pi ${i}"></i> ${t(l)}`;
    return `<i class="pi ${i}"></i> ${t(l)} · <span class="mono">${esc(complet && peutVoirCompte() ? x.numeroCompte : masquerCompte(x.numeroCompte))}</span>`;
  };
  // Bloc « compte de paiement » de la fiche salaire, avec bouton copier pour le gestionnaire des salaires
  const blocComptePaiement = e => !e.moyenPaiement
    ? `<div class="message warn"><i class="pi pi-exclamation-triangle"></i><div class="small grow">${t("sal.moyenNonConfigure")}</div>${can("salaire:modifier") ? `<button type="button" class="btn sm outlined" data-act="configurer-mp" data-v="${e.id}"><i class="pi pi-cog"></i>${t("sal.configurer")}</button>` : ""}</div>`
    : `<div class="message"><i class="pi pi-wallet"></i><div class="small">
      <div><b>${t("ens.moyenPaiement")}</b> : ${moyenPaiement(e, true)}${avecCompte(e.moyenPaiement) && peutVoirCompte() ? ` <button type="button" class="btn text icon sm" data-act="copier-compte" data-v="${esc(e.numeroCompte)}" title="${t("ens.copierCompte")}"><i class="pi pi-copy"></i></button>` : ""}</div>
      ${avecCompte(e.moyenPaiement) && e.intituleCompte ? `<div><b>${t("ens.intituleCompte")}</b> : ${esc(e.intituleCompte)}</div>` : ""}
      ${avecCompte(e.moyenPaiement) && !peutVoirCompte() ? `<div class="muted">${t("ens.compteMasque")}</div>` : ""}</div></div>`;
  // Ajout / modification d'un enseignant (POST via /enseignement/add-bulk-with-enseignant, PATCH /enseignant/update/{id})
  function dialogEnseignant(id) {
    const x = id ? byId(D.enseignants, id) : { nom: "", prenom: "", genre: "M", diplome: "", telephone: "", telephone2: "", salaire: "Mensuel", montant: "", actif: true };
    const champ = (cle, label, valeur, type = "text", obligatoire = true) => `<div class="field"><label for="ens-${cle}">${t(label)}${obligatoire ? " *" : ""}</label><input class="input" id="ens-${cle}" name="${cle}" type="${type}" value="${esc(valeur ?? "")}" ${obligatoire ? "required" : ""}></div>`;
    dialog(t(id ? "ens.modifierTitre" : "ens.ajouter", { e: `${x.nom} ${x.prenom || ""}` }), `<form id="form-ens" data-form="ens-edit" data-id="${id || ""}"><div class="form-grid">
        ${champ("nom", "c.nom", x.nom)}${champ("prenom", "c.prenom", x.prenom, "text", false)}
        <div class="field"><label>${t("c.genre")} *</label><select class="select" name="genre">${option("M", t("ens.homme"), x.genre)}${option("F", t("ens.femme"), x.genre)}</select></div>
        ${champ("diplome", "ens.diplome", x.diplome)}
        ${champ("telephone", "ens.telephone1", x.telephone, "tel")}${champ("telephone2", "ens.telephone2", x.telephone2, "tel", false)}
        <div class="field"><label>${t("ens.salaire")} *</label><select class="select" name="salaire">${option("Mensuel", t("ens.mensuel"), x.salaire)}${option("Horaire", t("ens.horaire"), x.salaire)}</select></div>
        ${champ("montant", "ens.montant", x.montant, "number", false)}
        ${id ? `<div class="field"><label>${t("c.statut")}</label><label class="row"><span class="switch"><input type="checkbox" name="actif" ${x.actif ? "checked" : ""}><span></span></span>${t("c.actif")}</label></div>` : ""}
        ${id ? "" : `<div class="field full"><span class="hint"><i class="pi pi-info-circle"></i> ${t("ens.apresCreation")}</span></div>`}
      </div></form>`, `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" type="submit" form="form-ens"><i class="pi pi-check"></i>${t("c.enregistrer")}</button>`);
  }
  function enregistrerEnseignant(form) {
    const d = Object.fromEntries(new FormData(form).entries());
    const donnees = { ...d, montant: d.montant ? Number(d.montant) : null, actif: form.querySelector("[name=actif]") ? Boolean(d.actif) : true };
    fermer();
    if (form.dataset.id) {
      Object.assign(byId(D.enseignants, form.dataset.id), donnees);
      render();
      toast("success", t("ens.modifieOk"), `${donnees.nom} ${donnees.prenom || ""}`);
    } else {
      const nouvel = { id: Date.now(), matieres: [], moyenPaiement: null, numeroCompte: "", intituleCompte: "", ...donnees };
      D.enseignants.push(nouvel);
      render();
      toast("success", t("ens.ajouteOk"), `${nouvel.nom} ${nouvel.prenom || ""}`);
      dialogMatieresEnseignant(nouvel.id);
    }
  }
  // Matières enseignées : ajout (POST /enseignement/add) et retrait (DELETE /enseignement/delete/{id})
  function dialogMatieresEnseignant(id) {
    const x = byId(D.enseignants, id);
    const disponibles = MATIERES_ENSEIGNEES().filter(m => !x.matieres.includes(m));
    const coursDe = m => D.cours.filter(c => matiere(c[3]).libelle === m && c[4] === x.id).length;
    dialog(t("ens.matieresDe", { e: `${x.nom} ${x.prenom || ""}` }), `<div class="stack">
      <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.matiere")}</th><th>${t("ens.coursPlanifies")}</th><th></th></tr></thead><tbody>
        ${x.matieres.length ? x.matieres.map(m => { const n = coursDe(m); return `<tr><td><b>${esc(m)}</b></td><td>${n ? tag("warn", t("ens.nbCours", { n })) : `<span class="muted small">—</span>`}</td>
          <td class="right">${can("enseignement:supprimer") ? `<button class="btn danger outlined sm" data-act="retirer-matiere" data-v="${x.id}|${esc(m)}" ${n ? `disabled title="${t("ens.retraitImpossible")}"` : ""}><i class="pi pi-times"></i>${t("ens.retirer")}</button>` : ""}</td></tr>`; }).join("")
          : `<tr><td colspan="3"><div class="empty">${t("ens.aucuneMatiere")}</div></td></tr>`}
      </tbody></table></div>
      ${x.matieres.some(m => coursDe(m)) ? `<div class="message warn"><i class="pi pi-info-circle"></i><div class="small">${t("ens.retraitImpossible")}</div></div>` : ""}
      ${can("enseignement:ajouter") ? `<div class="filters"><div class="field grow" style="width:auto"><label>${t("ens.ajouterMatiere")}</label><select class="select" data-matiere-ens>${option("", t("c.choisir"), S.matiereAAjouter)}${disponibles.map(m => option(m, m, S.matiereAAjouter)).join("")}</select></div>
        <button class="btn" data-act="ajouter-matiere" data-v="${x.id}" ${S.matiereAAjouter ? "" : "disabled"}><i class="pi pi-plus"></i>${t("c.ajouter")}</button></div>` : ""}
    </div>`, `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button>`);
  }

  /* ---------------- Salaires des enseignants ---------------- */
  // Mois de l'année scolaire 2026-2027 : septembre 2026 à août 2027 (mois + année civile)
  const MOIS_ANNEE = Array.from({ length: 12 }, (_, i) => { const m = (8 + i) % 12 + 1, a = m >= 9 ? 2026 : 2027; return `${a}-${String(m).padStart(2, "0")}`; });
  const libelleMois = periode => { const [a, m] = periode.split("-").map(Number); const s = new Date(a, m - 1, 1).toLocaleDateString(S.lang === "fr" ? "fr-FR" : "en-GB", { month: "long", year: "numeric" }); return s[0].toUpperCase() + s.slice(1); };
  // Simule GET /salaire/mois : dû = salaire mensuel, ou heures payées x taux horaire (absences justifiées selon la configuration)
  function situationSalaire(e, periode) {
    const [annee, mois] = periode.split("-").map(Number);
    let nbHeures = null, heuresJustifiees = 0, du;
    if (e.salaire === "Horaire") {
      const h = D.heuresEnseignants[e.id]?.[periode] || { p: 0, j: 0 };
      heuresJustifiees = D.configuration.isAbsenceJustifieePayee ? h.j : 0;
      nbHeures = h.p + heuresJustifiees;
      du = r2(nbHeures * e.montant);
    } else du = e.montant || 0;
    const versements = D.versementsSalaire.filter(v => v.ens === e.id && v.mois === mois && v.annee === annee);
    const verse = versements.filter(v => v.statut === "valide").reduce((s, v) => s + v.montant, 0);
    const statut = verse <= 0 ? "aucun" : verse >= du ? "total" : "partiel";
    return { e, nbHeures, heuresJustifiees, du, verse, reste: Math.max(du - verse, 0), statut, versements, pct: du ? Math.min(100, Math.round(verse * 100 / du)) : 0, mois, annee };
  }
  const nbNonConfigures = () => D.enseignants.filter(e => e.actif && !e.moyenPaiement).length;
  const ongletsSalaires = () => `<div class="tabs" style="margin-bottom:16px">${[["etat", "sal.tEtat", "pi-chart-bar"], ["versements", "sal.tVersements", "pi-list"], ["moyens", "sal.tMoyens", "pi-wallet"]]
    .map(([k, l, i]) => `<div class="tab ${S.tab.sal === k ? "on" : ""}" data-tab="sal" data-v="${k}"><i class="pi ${i}"></i> ${t(l)}${k === "moyens" && nbNonConfigures() ? ` <span class="tag warn">${nbNonConfigures()}</span>` : ""}</div>`).join("")}</div>`;
  // Filtres nom / prénom et matière enseignée, communs aux deux onglets
  const filtreEnseignantSalaire = (prefixe, F) => `
      <div class="field" style="width:240px"><label>${t("ens.nomPrenom")}</label><div class="input-icon"><i class="pi pi-search"></i><input class="input" id="${prefixe}-q" value="${esc(F.q)}" placeholder="${t("ens.nomPrenom")}" autocomplete="off"></div></div>
      <div class="field" style="width:220px"><label>${t("ens.matiereEnseignee")}</label><select class="select" id="${prefixe}-matiere">${option("", t("c.toutes"), F.matiere)}${MATIERES_ENSEIGNEES().map(m => option(m, m, F.matiere)).join("")}</select></div>`;
  const filtreTexteMatiere = A => {
    const termes = normaliser(A.q.trim()).split(/\s+/).filter(Boolean);
    return e => termes.every(x => normaliser(`${e.nom} ${e.prenom || ""}`).includes(x)) && (!A.matiere || e.matieres.includes(A.matiere));
  };
  function ecranSalaires() {
    if (S.tab.sal === "versements") return ecranVersementsSalaire();
    if (S.tab.sal === "moyens") return ecranMoyensPaiement();
    const F = S.sal, A = F.applique || (S.autoAffiche ? { periode: F.periode, q: F.q, matiere: F.matiere } : null);
    const formulaire = ongletsSalaires() + `<div class="card" style="margin-bottom:16px"><div class="card-body"><form class="filters" data-form="filtre-sal">
      <div class="field" style="width:200px"><label>${t("sal.mois")} *</label><select class="select" id="sal-periode">${MOIS_ANNEE.map(p => option(p, libelleMois(p), F.periode)).join("")}</select></div>
      ${filtreEnseignantSalaire("sal", F)}
      <button class="btn" type="submit"><i class="pi pi-search"></i>${t("c.afficher")}</button>
      <div class="field" style="width:auto;margin-left:auto"><label>${t("sco.statutPaiement")}</label><div class="segmented">${[["tous", "c.tous"], ["total", "sal.paye"], ["partiel", "pay.partiel"], ["aucun", "sal.nonPaye"]].map(([k, l]) => `<button type="button" class="${F.statut === k ? "on" : ""}" data-act="sal-statut" data-v="${k}">${t(l)}</button>`).join("")}</div></div>
    </form></div></div>
    <div class="message" style="margin-bottom:16px"><i class="pi pi-info-circle"></i><div class="small">${t(D.configuration.isAbsenceJustifieePayee ? "sal.regleAvecJustifiees" : "sal.regleSansJustifiees")}</div></div>`;
    if (!A) return entete(t("sal.titre"), t("sal.sousTitre")) + formulaire + `<div class="card"><div class="empty"><i class="pi pi-search" style="font-size:28px"></i><p>${t("c.cliquerAfficher")}</p></div></div>`;
    const correspond = filtreTexteMatiere(A);
    // Actifs et inactifs (colonne « État de l'enseignant »)
    const toutes = D.enseignants.filter(e => correspond(e))
      .sort((a, b) => `${a.nom} ${a.prenom}`.localeCompare(`${b.nom} ${b.prenom}`))
      .map(e => situationSalaire(e, A.periode));
    const filtrees = toutes.filter(s => F.statut === "tous" || s.statut === F.statut);
    const totalPages = Math.max(1, Math.ceil(filtrees.length / F.pageSize)), page = Math.min(F.page, totalPages);
    const lignes = filtrees.slice((page - 1) * F.pageSize, page * F.pageSize);
    const somme = k => filtrees.reduce((s, x) => s + (k === "verse" ? Math.min(x.verse, x.du) : x[k]), 0);
    const nb = k => toutes.filter(s => s.statut === k).length;
    const carte = (icone, sev, l, v, sous) => `<div class="card stat"><div class="stat-icon ${sev}"><i class="pi ${icone}"></i></div><div><div class="stat-label">${l}</div><div class="stat-value" style="font-size:20px">${v}</div><div class="stat-sub">${sous || ""}</div></div></div>`;
    return entete(t("sal.titre"), t("sal.sousTitre")) + formulaire + `
      <div class="grid grid-4" style="margin-bottom:16px">
        ${carte("pi-wallet", "", t("sal.totalDu"), fcfa(somme("du")), libelleMois(A.periode))}
        ${carte("pi-check-circle", "success", t("sal.totalVerse"), fcfa(somme("verse")))}
        ${carte("pi-hourglass", "warn", t("sal.resteAVerser"), fcfa(somme("reste")))}
        ${carte("pi-users", "danger", t("sal.repartition"), `${nb("total")} / ${nb("partiel")} / ${nb("aucun")}`, t("sal.repartitionSous"))}
      </div>
      <div class="card"><div class="table-wrap"><table class="dt"><thead><tr><th>${t("ens.enseignant")}</th><th>${t("sal.etatEnseignant")}</th><th>${t("ens.salaire")}</th><th class="num">${t("sal.heures")}</th><th class="num">${t("sal.du")}</th><th class="num">${t("sal.verse")}</th><th class="num">${t("sco.reste")}</th><th style="width:150px">${t("sco.progression")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
      ${lignes.length ? lignes.map(s => `<tr><td><div class="person"><span class="avatar">${esc(initiales(s.e.prenom, s.e.nom))}</span><div>${esc(s.e.nom)} ${esc(s.e.prenom || "")}</div></div></td>
        <td>${s.e.actif ? tag("success", t("c.actif")) : tag("secondary", t("c.inactif"))}</td>
        <td>${tag(s.e.salaire === "Mensuel" ? "info" : "secondary", t(s.e.salaire === "Mensuel" ? "ens.mensuel" : "ens.horaire"))}<div class="small muted">${fcfa(s.e.montant)}${s.e.salaire === "Horaire" ? " / h" : ""}</div><div class="small muted" style="white-space:nowrap">${moyenPaiement(s.e)}</div></td>
        <td class="num">${s.nbHeures == null ? "—" : `${fmt(s.nbHeures)} h${s.heuresJustifiees ? `<div class="small muted">${t("sal.dontJustifiees", { h: fmt(s.heuresJustifiees) })}</div>` : ""}`}</td>
        <td class="num">${fcfa(s.du)}</td><td class="num">${fcfa(s.verse)}</td><td class="num"><b>${fcfa(s.reste)}</b></td>
        <td><div class="progress ${s.statut === "total" ? "success" : s.statut === "partiel" ? "warn" : "danger"}"><div style="width:${s.pct}%"></div></div></td>
        <td>${tag({ total: "success", partiel: "warn", aucun: "danger" }[s.statut], t({ total: "sal.paye", partiel: "pay.partiel", aucun: "sal.nonPaye" }[s.statut]))}</td>
        <td class="right" style="white-space:nowrap"><button class="btn text icon sm" data-act="detail-salaire" data-v="${s.e.id}" title="${t("sal.versements")}"><i class="pi pi-history"></i></button>${can("salaire:ajouter") && s.reste > 0 ? `<button class="btn sm" data-act="verser-salaire" data-v="${s.e.id}" ${s.e.actif ? "" : `disabled title="${t("sal.verserInactif")}"`}><i class="pi pi-plus"></i>${t("sal.verser")}</button>` : ""}</td></tr>`).join("")
        : `<tr><td colspan="10"><div class="empty">${t("c.aucunResultat")}</div></td></tr>`}
      </tbody></table></div>
      ${paginateur({ page, totalPages, total: filtrees.length }, F.pageSize, "page-sal", "sal.pageSize")}</div>`;
  }
  // Simule GET /salaire/versements : versements de l'année scolaire, du plus récent au plus ancien
  function ecranVersementsSalaire() {
    const F = S.vers, A = F.applique;
    const formulaire = ongletsSalaires() + `<div class="card" style="margin-bottom:16px"><div class="card-body"><form class="filters" data-form="filtre-vers">
      <div class="field" style="width:200px"><label>${t("sal.moisPaye")}</label><select class="select" id="vers-periode">${option("", t("sal.tousMois"), F.periode)}${MOIS_ANNEE.map(p => option(p, libelleMois(p), F.periode)).join("")}</select></div>
      ${filtreEnseignantSalaire("vers", F)}
      <button class="btn" type="submit"><i class="pi pi-filter"></i>${t("c.filtrer")}</button>
      ${A.periode || A.q || A.matiere ? `<button class="btn text" type="button" data-act="effacer-vers"><i class="pi pi-times"></i>${t("c.effacer")}</button>` : ""}
    </form></div></div>`;
    const correspond = filtreTexteMatiere(A);
    const filtres = D.versementsSalaire
      .map(v => ({ ...v, e: byId(D.enseignants, v.ens), periode: `${v.annee}-${String(v.mois).padStart(2, "0")}` }))
      .filter(v => (!A.periode || v.periode === A.periode) && correspond(v.e))
      .sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id);
    const totalPages = Math.max(1, Math.ceil(filtres.length / F.pageSize)), page = Math.min(F.page, totalPages);
    const lignes = filtres.slice((page - 1) * F.pageSize, page * F.pageSize);
    const valides = filtres.filter(v => v.statut === "valide");
    const carte = (icone, sev, l, v, sous) => `<div class="card stat"><div class="stat-icon ${sev}"><i class="pi ${icone}"></i></div><div><div class="stat-label">${l}</div><div class="stat-value" style="font-size:20px">${v}</div><div class="stat-sub">${sous || ""}</div></div></div>`;
    return entete(t("sal.titre"), t("sal.sousTitreVersements")) + formulaire + `
      <div class="grid grid-3" style="margin-bottom:16px">
        ${carte("pi-check-circle", "success", t("sal.totalVerse"), fcfa(valides.reduce((s, v) => s + v.montant, 0)), A.periode ? libelleMois(A.periode) : t("sal.anneeScolaire"))}
        ${carte("pi-list", "", t("sal.nbVersements"), valides.length)}
        ${carte("pi-ban", "danger", t("sal.nbAnnules"), filtres.length - valides.length)}
      </div>
      <div class="card"><div class="table-wrap"><table class="dt"><thead><tr><th>${t("sal.dateVersement")}</th><th>${t("ens.enseignant")}</th><th>${t("sal.moisPaye")}</th><th class="num">${t("c.montant")}</th><th>${t("sco.enregistrePar")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
      ${lignes.length ? lignes.map(v => `<tr${v.statut === "valide" ? "" : ` class="muted"`}><td>${fmtDate(v.date)}</td>
        <td><b>${esc(v.e.nom)}</b> ${esc(v.e.prenom || "")}<div class="small muted">${esc(v.e.matieres.join(", "))}</div></td>
        <td>${libelleMois(v.periode)}</td><td class="num">${fcfa(v.montant)}</td><td class="mono small">${esc(v.user)}</td>
        <td>${v.statut === "valide" ? tag("success", t("sco.valide")) : tag("secondary", t("sco.annule"))}</td>
        <td class="right" style="white-space:nowrap">${v.statut === "valide" && can("salaire:annuler") ? `<button class="btn danger outlined sm" data-act="annuler-versement-liste" data-v="${v.id}"><i class="pi pi-ban"></i>${t("sco.annuler")}</button>` : ""}</td></tr>`).join("")
        : `<tr><td colspan="7"><div class="empty">${t("sal.aucunVersementFiltre")}</div></td></tr>`}
      </tbody></table></div>
      ${paginateur({ page, totalPages, total: filtres.length }, F.pageSize, "page-vers", "vers.pageSize")}</div>`;
  }
  // Simule GET /salaire/moyens-paiement?configure= : enseignants actifs, triés par nom
  function ecranMoyensPaiement() {
    const F = S.mp, A = F.applique, n = nbNonConfigures();
    const correspond = filtreTexteMatiere(A);
    const liste = D.enseignants.filter(e => e.actif && correspond(e) && (F.config === "tous" || Boolean(e.moyenPaiement) === (F.config === "oui")))
      .sort((a, b) => `${a.nom} ${a.prenom}`.localeCompare(`${b.nom} ${b.prenom}`));
    const totalPages = Math.max(1, Math.ceil(liste.length / F.pageSize)), page = Math.min(F.page, totalPages);
    const lignes = liste.slice((page - 1) * F.pageSize, page * F.pageSize);
    return entete(t("sal.titre"), t("sal.sousTitreMoyens")) + ongletsSalaires() + `
      ${n ? `<div class="message warn" style="margin-bottom:16px"><i class="pi pi-exclamation-triangle"></i><div class="small">${t("sal.alerteNonConfigures", { n })}</div></div>` : ""}
      <div class="card" style="margin-bottom:16px"><div class="card-body"><form class="filters" data-form="filtre-mp">
        ${filtreEnseignantSalaire("mp", F)}
        <button class="btn" type="submit"><i class="pi pi-filter"></i>${t("c.filtrer")}</button>
        ${A.q || A.matiere ? `<button class="btn text" type="button" data-act="effacer-mp"><i class="pi pi-times"></i>${t("c.effacer")}</button>` : ""}
        <div class="field" style="width:auto;margin-left:auto"><label>${t("sal.configuration")}</label><div class="segmented">${[["non", "sal.nonConfigures"], ["oui", "sal.configures"], ["tous", "c.tous"]].map(([k, l]) => `<button type="button" class="${F.config === k ? "on" : ""}" data-act="mp-config" data-v="${k}">${t(l)}</button>`).join("")}</div></div>
      </form></div></div>
      <div class="card"><div class="table-wrap"><table class="dt"><thead><tr><th>${t("ens.enseignant")}</th><th>${t("c.telephone")}</th><th>${t("ens.salaire")}</th><th>${t("ens.moyenPaiement")}</th><th>${t("ens.numeroCompte")}</th><th>${t("ens.intituleCompte")}</th><th></th></tr></thead><tbody>
      ${lignes.length ? lignes.map(e => {
        const [, l, i] = MOYENS_PAIEMENT.find(m => m[0] === e.moyenPaiement) || [];
        return `<tr><td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span><div>${esc(e.nom)} ${esc(e.prenom || "")}<div class="sub">${esc(e.matieres.join(", "))}</div></div></div></td>
        <td class="mono small">${esc(e.telephone)}</td>
        <td>${tag(e.salaire === "Mensuel" ? "info" : "secondary", t(e.salaire === "Mensuel" ? "ens.mensuel" : "ens.horaire"))}</td>
        <td>${e.moyenPaiement ? `<i class="pi ${i}"></i> ${t(l)}` : tag("warn", t("sal.nonConfigure"))}</td>
        <td class="mono small" style="white-space:nowrap">${avecCompte(e.moyenPaiement) ? `${esc(peutVoirCompte() ? e.numeroCompte : masquerCompte(e.numeroCompte))}${peutVoirCompte() ? ` <button type="button" class="btn text icon sm" data-act="copier-compte" data-v="${esc(e.numeroCompte)}" title="${t("ens.copierCompte")}"><i class="pi pi-copy"></i></button>` : ""}` : "—"}</td>
        <td>${avecCompte(e.moyenPaiement) && e.intituleCompte ? esc(e.intituleCompte) : "—"}</td>
        <td class="right">${can("salaire:modifier") ? `<button class="btn sm ${e.moyenPaiement ? "outlined" : ""}" data-act="configurer-mp" data-v="${e.id}"><i class="pi ${e.moyenPaiement ? "pi-pencil" : "pi-cog"}"></i>${t(e.moyenPaiement ? "c.modifier" : "sal.configurer")}</button>` : ""}</td></tr>`;
      }).join("") : `<tr><td colspan="7"><div class="empty">${t(F.config === "non" && !A.q && !A.matiere ? "sal.aucunNonConfigure" : "c.aucunResultat")}</div></td></tr>`}
      </tbody></table></div>
      ${paginateur({ page, totalPages, total: liste.length }, F.pageSize, "page-mp", "mp.pageSize")}</div>`;
  }
  // PATCH /salaire/moyen-paiement/{id_enseignant} (salaire:modifier)
  function dialogMoyenPaiement(id) {
    const e = byId(D.enseignants, id), compte = avecCompte(e.moyenPaiement);
    dialog(t("sal.configurerTitre", { e: `${e.nom} ${e.prenom || ""}` }), `<form id="form-mp" data-form="moyen-paiement" data-id="${id}"><div class="form-grid">
        <div class="field full"><label>${t("ens.moyenPaiement")} *</label><select class="select" name="moyenPaiement" id="mp-moyen" required>${e.moyenPaiement ? "" : option("", t("c.choisir"), "")}${MOYENS_PAIEMENT.map(([v, l]) => option(v, t(l), e.moyenPaiement || "")).join("")}</select></div>
        <div class="field" data-compte style="${compte ? "" : "display:none"}"><label for="mp-numero">${t("ens.numeroCompte")} *</label><input class="input" id="mp-numero" name="numeroCompte" value="${esc(e.numeroCompte || "")}" maxlength="60" ${compte ? "required" : ""}><span class="hint" id="mp-hint">${t(e.moyenPaiement === "MOBILE" ? "ens.numeroMobileHint" : "ens.numeroBancaireHint")}</span></div>
        <div class="field" data-compte style="${compte ? "" : "display:none"}"><label for="mp-intitule">${t("ens.intituleCompte")}</label><input class="input" id="mp-intitule" name="intituleCompte" value="${esc(e.intituleCompte || "")}" maxlength="255" placeholder="${esc(`${e.nom} ${e.prenom || ""}`.trim())}"></div>
        <div class="field full" id="mp-erreur"></div>
      </div></form>`, `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" type="submit" form="form-mp"><i class="pi pi-check"></i>${t("c.enregistrer")}</button>`);
  }
  function dialogVerserSalaire(id) {
    const s = situationSalaire(byId(D.enseignants, id), (S.sal.applique || S.sal).periode);
    dialog(t("sal.verserTitre"), `<form id="form-verser" data-form="verser-salaire" data-id="${id}"><div class="stack">
      <div class="person"><span class="avatar">${esc(initiales(s.e.prenom, s.e.nom))}</span><div><b>${esc(s.e.nom)} ${esc(s.e.prenom || "")}</b><div class="sub">${libelleMois(`${s.annee}-${String(s.mois).padStart(2, "0")}`)} · ${t(s.e.salaire === "Mensuel" ? "ens.mensuel" : "ens.horaire")}</div></div></div>
      <div class="message"><i class="pi pi-info-circle"></i><span class="small">${t("sal.situation", { du: fcfa(s.du), verse: fcfa(s.verse), reste: fcfa(s.reste) })}${s.nbHeures != null ? ` · ${t("sal.calculHoraire", { h: fmt(s.nbHeures), taux: fcfa(s.e.montant) })}` : ""}</span></div>
      <div class="form-grid"><div class="field"><label for="sal-montant">${t("c.montant")} (FCFA) *</label><input class="input" id="sal-montant" type="number" min="1" max="${s.reste}" step="any" value="${s.reste}" required><span class="hint">${t("sal.maxReste", { r: fcfa(s.reste) })}</span></div>
      <div class="field"><label for="sal-date">${t("sal.dateVersement")} *</label><input class="input" id="sal-date" type="date" value="${AUJOURDHUI}" max="${AUJOURDHUI}" required></div></div>
      ${blocComptePaiement(s.e)}
      <div id="sal-erreur"></div>
    </div></form>`, `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" type="submit" form="form-verser"><i class="pi pi-check"></i>${t("sal.enregistrerVersement")}</button>`);
  }
  function dialogDetailSalaire(id) {
    const s = situationSalaire(byId(D.enseignants, id), (S.sal.applique || S.sal).periode);
    dialog(t("sal.versementsDe", { e: `${s.e.nom} ${s.e.prenom || ""}`, m: libelleMois(`${s.annee}-${String(s.mois).padStart(2, "0")}`) }), `<div class="stack">
      <div class="row">${tag("", `${t("sal.du")} : ${fcfa(s.du)}`)}${tag("success", `${t("sal.verse")} : ${fcfa(s.verse)}`)}${tag("warn", `${t("sco.reste")} : ${fcfa(s.reste)}`)}</div>
      ${blocComptePaiement(s.e)}
      <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.date")}</th><th class="num">${t("c.montant")}</th><th>${t("sco.enregistrePar")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
      ${s.versements.length ? s.versements.map(v => `<tr><td>${fmtDate(v.date)}</td><td class="num">${fcfa(v.montant)}</td><td class="mono small">${esc(v.user)}</td><td>${v.statut === "valide" ? tag("success", t("sco.valide")) : tag("secondary", t("sco.annule"))}</td>
        <td class="right">${v.statut === "valide" && can("salaire:annuler") ? `<button class="btn danger outlined sm" data-act="annuler-versement" data-v="${v.id}"><i class="pi pi-ban"></i>${t("sco.annuler")}</button>` : ""}</td></tr>`).join("")
        : `<tr><td colspan="5"><div class="empty">${t("sal.aucunVersement")}</div></td></tr>`}
      </tbody></table></div></div>`, `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button>`, true);
  }

  /* ---------------- Présence des enseignants ---------------- */
  // Simule GET /presence-enseignant/jour?date_cours=&q= : cours de ce jour de la semaine (toutes classes) avec la présence saisie
  const clePresence = (date, idx) => `${date}|${idx}`;
  // Lignes affichées : cours du jour de la semaine de la date appliquée, filtrés par niveau, classe et nom
  function lignesPresenceEns() {
    const A = S.pe.applique;
    const jourSemaine = new Date(A.date + "T00:00:00").getDay() - 1; // 0 = lundi
    const termes = normaliser(A.q.trim()).split(/\s+/).filter(Boolean);
    return D.cours.map((c, idx) => ({ c, idx, e: byId(D.enseignants, c[4]), saisi: D.presencesEnseignants[clePresence(A.date, idx)] }))
      .filter(l => l.c[0] === jourSemaine && termes.every(x => normaliser(`${l.e.nom} ${l.e.prenom || ""}`).includes(x))
        && (!A.classe || l.c[5] === Number(A.classe)))
      .sort((a, b) => a.c[1].localeCompare(b.c[1]) || classe(a.c[5]).libelle.localeCompare(classe(b.c[5]).libelle));
  }
  function ecranPresencesEnseignants() {
    const F = S.pe, A = F.applique;
    // 1er affichage : la classe déjà sélectionnée (sélection commune aux écrans) est appliquée
    if (A.classe === undefined) { preselectionAutomatique(); A.classe = S.sel.classe || ""; }
    const jourSemaine = new Date(A.date + "T00:00:00").getDay() - 1; // 0 = lundi
    const lignes = lignesPresenceEns();
    // Valeur affichée : saisie en cours, sinon présence enregistrée, sinon présent par défaut
    const etat = l => F.saisie[l.idx] || l.saisi || "P";
    const verrouille = l => l.saisi && !can("presence_enseignant:modifier");
    const nbSaisis = lignes.filter(l => l.saisi).length, modifs = lignes.filter(l => F.saisie[l.idx] && F.saisie[l.idx] !== l.saisi).length;
    const titreJour = new Date(A.date + "T00:00:00").toLocaleDateString(S.lang === "fr" ? "fr-FR" : "en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    const nb = k => lignes.filter(l => etat(l) === k).length;
    return entete(t("pres.titre"), t("pres.sousTitreEns")) + ongletsPresence() + `
      <div class="card" style="margin-bottom:16px"><div class="card-body"><form class="filters" data-form="filtre-pe">
        <div class="field" style="width:180px"><label for="pe-date">${t("c.date")} *</label><input class="input" type="date" id="pe-date" value="${F.date}" max="${AUJOURDHUI}" required></div>
        ${filtreClasse(false)}
        <div class="field" style="width:220px"><label>${t("ens.nomPrenom")}</label><div class="input-icon"><i class="pi pi-search"></i><input class="input" id="pe-q" value="${esc(F.q)}" placeholder="${t("ens.nomPrenom")}" autocomplete="off"></div></div>
        <button class="btn" type="submit"><i class="pi pi-search"></i>${t("c.afficher")}</button>
        ${lignes.length ? `<div class="row" style="margin-left:auto">${tag("success", `${t("pres.presents")} : ${nb("P")}`)}${tag("danger", `${t("pres.absents")} : ${nb("A")}`)}${tag("warn", `${t("pres.justifies")} : ${nb("J")}`)}</div>` : ""}
      </form></div></div>
      <div class="message" style="margin-bottom:16px"><i class="pi pi-info-circle"></i><div class="small">${t("pres.aideEns")} ${t(D.configuration.isAbsenceJustifieePayee ? "sal.regleAvecJustifiees" : "sal.regleSansJustifiees")}</div></div>
      <div class="card"><div class="card-head"><h3 style="text-transform:capitalize">${esc(titreJour)}</h3>
        <div class="row">${lignes.length ? tag(nbSaisis === lignes.length ? "success" : "warn", t("pres.saisis", { n: nbSaisis, t: lignes.length })) : ""}
        ${lignes.length && can("presence_enseignant:ajouter") ? `<button class="btn secondary sm" data-act="pe-tous-presents"><i class="pi pi-check"></i>${t("pres.tousPresents")}</button>` : ""}</div></div>
      ${lignes.length ? `<div class="table-wrap"><table class="dt"><thead><tr><th>${t("pres.horaire")}</th><th>${t("c.classe")}</th><th>${t("c.matiere")}</th><th>${t("ens.enseignant")}</th><th>${t("pres.statut")}</th><th>${t("pres.saisie")}</th></tr></thead><tbody>
      ${lignes.map(l => `<tr><td class="mono small" style="white-space:nowrap">${l.c[1]} – ${l.c[2]}</td><td><b>${esc(classe(l.c[5]).libelle)}</b></td><td>${esc(matiere(l.c[3]).libelle)}</td>
        <td><div class="person"><span class="avatar">${esc(initiales(l.e.prenom, l.e.nom))}</span>${esc(l.e.nom)} ${esc(l.e.prenom || "")}</div></td>
        <td><div class="segmented">${[["P", "pres.present"], ["A", "pres.absent"], ["J", "pres.absentJustifie"]].map(([k, lb]) => `<button class="${etat(l) === k ? "on" : ""}" data-act="pe-statut" data-v="${l.idx}|${k}" ${verrouille(l) || !can("presence_enseignant:ajouter") ? "disabled" : ""}>${t(lb)}</button>`).join("")}</div></td>
        <td>${F.saisie[l.idx] && F.saisie[l.idx] !== l.saisi ? tag("info", t("pres.nonEnregistre")) : l.saisi ? tag("success", t("pres.enregistreTag")) : tag("secondary", t("pres.nonSaisi"))}</td></tr>`).join("")}
      </tbody></table></div>
      ${can("presence_enseignant:ajouter") ? `<div class="dialog-foot">${nbSaisis && !can("presence_enseignant:modifier") ? `<span class="small muted" style="margin-right:auto">${t("pres.modifRefusee")}</span>` : ""}<button class="btn" data-act="pe-enregistrer" ${nbSaisis === lignes.length && !modifs ? "disabled" : ""}><i class="pi pi-save"></i>${t("pres.enregistrerEns")}</button></div>` : ""}`
      : `<div class="empty"><i class="pi pi-calendar-times" style="font-size:28px"></i><p>${t(jourSemaine < 0 || jourSemaine > 4 ? "pres.weekEnd" : "pres.aucunCours")}</p></div>`}</div>`;
  }

  /* ---------------- Emploi du temps ---------------- */
  function ecranEmploiDuTemps() {
    const jours = ["c.lundi", "c.mardi", "c.mercredi", "c.jeudi", "c.vendredi"];
    const coursClasse = D.cours.filter(c => c[5] === Number(S.sel.classe)), avecCours = coursClasse.length > 0;
    const colonnes = jours.map((j, ji) => `<div class="card"><div class="card-head" style="padding:10px 14px"><h3>${t(j)}</h3></div><div class="card-body stack" style="gap:8px;padding:10px">
      ${avecCours ? coursClasse.filter(c => c[0] === ji).sort((a, b) => a[1].localeCompare(b[1])).map(([, deb, fin, idm, ide]) => { const m = matiere(idm), e = byId(D.enseignants, ide); return `<div class="slot c${m.groupe + 1}"><b>${esc(m.libelle)}</b>${deb} – ${fin}<div class="small">${esc(e.nom)} ${esc(e.prenom || "")}</div></div>`; }).join("") : `<div class="muted small center">—</div>`}
    </div></div>`).join("");
    return entete(t("edt.titre"), t("edt.sousTitre"), can("cours:ajouter") ? `<button class="btn" data-act="ajouter-cours"><i class="pi pi-plus"></i>${t("edt.ajouter")}</button>` : "") + `
      <div class="card" style="margin-bottom:16px"><div class="card-body"><div class="filters">${filtreClasse(true)}${boutonAfficher("edt")}</div></div></div>
      ${estAffiche("edt") ? `<div class="grid" style="grid-template-columns:repeat(5,minmax(150px,1fr));overflow-x:auto">${colonnes}</div>` : zoneVide("edt")}`;
  }

  /* ---------------- Présences (appel) ---------------- */
  // Onglets de l'écran Appel : élèves (appel pendant un cours) et enseignants (présence aux cours, base des salaires horaires)
  const ongletPresence = () => S.tab.pres === "enseignants" && can("presence_enseignant:consulter") || !can("presence_eleve:consulter") ? "enseignants" : "eleves";
  const ongletsPresence = () => can("presence_eleve:consulter") && can("presence_enseignant:consulter")
    ? `<div class="tabs" style="margin-bottom:16px">${[["eleves", "pres.tEleves", "pi-users"], ["enseignants", "pres.tEnseignants", "pi-id-card"]]
      .map(([k, l, i]) => `<div class="tab ${ongletPresence() === k ? "on" : ""}" data-tab="pres" data-v="${k}"><i class="pi ${i}"></i> ${t(l)}</div>`).join("")}</div>` : "";
  function ecranPresences() {
    if (ongletPresence() === "enseignants") return ecranPresencesEnseignants();
    if (!D.configuration.isAppel) return entete(t("pres.titre"), t("pres.sousTitre")) + ongletsPresence() + `<div class="message warn"><i class="pi pi-exclamation-triangle"></i>${t("pres.appelInactif")}</div>`;
    const eleves = elevesClasse(S.sel.classe);
    const coursJour = D.cours.filter(c => c[0] === 0 && c[5] === Number(S.sel.classe));
    const etat = id => S.appel[id] || "P";
    const nb = k => eleves.filter(e => etat(e.id) === k).length;
    return entete(t("pres.titre"), t("pres.sousTitre")) + ongletsPresence() + `
      <div class="card" style="margin-bottom:16px"><div class="card-body"><div class="filters">
        ${filtreClasse(true)}
        <div class="field"><label>${t("c.cours")}</label><select class="select" data-f="presence.cours">${coursJour.map((c, i) => option(i, `${c[1]} – ${c[2]} · ${matiere(c[3]).libelle}`, S.f.presence.cours)).join("")}</select></div>
        <div class="field"><label>${t("c.date")}</label><input class="input" type="date" value="${AUJOURDHUI}"></div>
        ${boutonAfficher("presences")}
        ${estAffiche("presences") ? `<div class="row" style="margin-left:auto">${tag("success", `${t("pres.presents")} : ${nb("P")}`)}${tag("danger", `${t("pres.absents")} : ${nb("A")}`)}${tag("warn", `${t("pres.justifies")} : ${nb("J")}`)}</div>` : ""}
      </div></div></div>
      ${estAffiche("presences") && eleves.length ? `<div class="card"><div class="card-head"><div class="row"><button class="btn secondary sm" data-act="tous-presents"><i class="pi pi-check"></i>${t("pres.tousPresents")}</button></div><span class="small muted">${t("pres.aide")}</span></div>
      <div class="table-wrap"><table class="dt"><thead><tr><th>#</th><th>${t("c.eleve")}</th><th>${t("pres.statut")}</th></tr></thead><tbody>
      ${eleves.map((e, i) => `<tr><td class="muted">${i + 1}</td><td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span>${esc(e.nom)} ${esc(e.prenom)}</div></td>
        <td><div class="segmented">${[["P", "pres.present"], ["A", "pres.absent"], ["J", "pres.absentJustifie"]].map(([k, l]) => `<button class="${etat(e.id) === k ? "on" : ""}" data-act="appel" data-v="${e.id}|${k}">${t(l)}</button>`).join("")}</div></td></tr>`).join("")}
      </tbody></table></div>
      <div class="dialog-foot">${can("presence_eleve:ajouter") ? `<button class="btn" data-act="enregistrer-appel"><i class="pi pi-save"></i>${t("pres.enregistrer")}</button>` : ""}</div></div>` : zoneVide("presences")}`;
  }

  /* ---------------- Évaluations ---------------- */
  function ecranEvaluations() {
    const statutEval = ev => ev.fin < AUJOURDHUI ? tag("secondary", t("eval.terminee")) : ev.debut <= AUJOURDHUI ? tag("success", t("eval.enCours")) : tag("info", t("eval.aVenir"));
    const typeEval = ev => {
      const deps = depsDe(ev.id), p = parentDe(ev.id);
      if (deps.length) return tag("", t("eval.calculee", { d: deps.map(d => `${evaluation(d.dependance).libelle} ${d.pourcentage}%`).join(" + ") }), "pi-calculator");
      if (p) return tag("warn", t("eval.dependanceDe", { p: evaluation(p.parent).libelle, pc: p.pourcentage }), "pi-link");
      return tag("secondary", t("eval.simple"));
    };
    return entete(t("eval.titre"), t("eval.sousTitre"), can("evaluation:ajouter") ? `<button class="btn" data-act="ajouter-evaluation"><i class="pi pi-plus"></i>${t("eval.ajouter")}</button>` : "") +
      D.trimestres.map(tr => `<div class="card" style="margin-bottom:16px"><div class="card-head"><h2>${esc(tr.libelle)}</h2><span class="tag secondary">${D.evaluations.filter(e => e.trimestre === tr.id).length} ${t("eval.evaluations")}</span></div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.code")}</th><th>${t("c.libelle")}</th><th>${t("eval.periode")}</th><th>${t("eval.type")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
        ${D.evaluations.filter(e => e.trimestre === tr.id).map(ev => `<tr><td class="mono">${esc(ev.code)}</td><td><b>${esc(ev.libelle)}</b></td><td>${fmtDate(ev.debut)} → ${fmtDate(ev.fin)}</td><td>${typeEval(ev)}</td><td>${statutEval(ev)}</td>
          <td class="right">${can("evaluation:modifier") ? `<button class="btn text sm" data-act="dependances" data-v="${ev.id}"><i class="pi pi-sitemap"></i>${t("eval.dependances")}</button><button class="btn text icon sm" title="${t("c.modifier")}"><i class="pi pi-pencil"></i></button>` : ""}${can("evaluation:supprimer") ? `<button class="btn text icon sm" data-act="supprimer-evaluation" data-v="${ev.id}" title="${t("c.supprimer")}"><i class="pi pi-trash" style="color:var(--danger)"></i></button>` : ""}</td></tr>`).join("")}
        </tbody></table></div></div>`).join("");
  }
  function dialogDependances(idEval) {
    const ev = evaluation(idEval);
    const deps = depsDe(idEval);
    const total = deps.reduce((s, d) => s + d.pourcentage, 0);
    const bloque = deps.length && S.calcule[idEval];
    const candidates = D.evaluations.filter(e => e.trimestre === ev.trimestre && e.id !== ev.id && !depsDe(e.id).length && !deps.some(d => d.dependance === e.id));
    dialog(t("eval.dependancesDe", { e: ev.libelle }), `
      <div class="stack">
        <div class="message"><i class="pi pi-info-circle"></i><div class="small">${t("eval.reglesDependances")}</div></div>
        ${bloque ? `<div class="message warn"><i class="pi pi-lock"></i><div class="small">${t("eval.dependancesBloquees")}</div></div>` : ""}
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.evaluation")}</th><th>${t("eval.periode")}</th><th class="num">${t("eval.pourcentage")}</th><th></th></tr></thead><tbody>
          ${deps.length ? deps.map(d => { const e = evaluation(d.dependance); return `<tr><td>${esc(e.libelle)}</td><td class="small">${fmtDate(e.debut)} → ${fmtDate(e.fin)}</td><td class="num"><input class="input note" value="${d.pourcentage}" ${bloque ? "disabled" : ""}> %</td><td class="right"><button class="btn text icon sm" ${bloque ? "disabled" : ""}><i class="pi pi-trash"></i></button></td></tr>`; }).join("")
            : `<tr><td colspan="4"><div class="empty">${t("eval.aucuneDependance")}</div></td></tr>`}
        </tbody></table></div>
        <div><div class="row-between small"><span>${t("eval.totalPourcentage")}</span><b>${total} %</b></div><div class="progress ${total === 100 ? "success" : "warn"}" style="margin-top:6px"><div style="width:${total}%"></div></div></div>
        ${!bloque ? `<div class="filters"><div class="field grow" style="width:auto"><label>${t("eval.ajouterDependance")}</label><select class="select">${candidates.map(c => option(c.id, c.libelle)).join("") || option("", "—")}</select></div><div class="field" style="width:110px"><label>${t("eval.pourcentage")}</label><input class="input" value="${Math.max(0, 100 - total)}"></div><button class="btn outlined"><i class="pi pi-plus"></i>${t("c.ajouter")}</button></div>` : ""}
      </div>`, `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button>${!bloque ? `<button class="btn" data-act="toast-ok" data-v="eval.dependancesOk">${t("c.enregistrer")}</button>` : ""}`);
  }

  /* ---------------- Saisie des notes ---------------- */
  function ecranNotes() {
    const f = S.f.notes;
    const ev = evaluation(f.evaluation), m = matiere(f.matiere), b = bareme(m.bareme);
    const eleves = elevesClasse(S.sel.classe);
    const deps = depsDe(ev.id);
    const filtres = `<div class="card" style="margin-bottom:16px"><div class="card-body"><div class="filters">
      <div class="field"><label>${t("c.evaluation")}</label><select class="select" data-f="notes.evaluation">${D.evaluations.filter(e => e.trimestre === 1).map(e => option(e.id, e.libelle + (depsDe(e.id).length ? " (" + t("notes.calculee") + ")" : ""), f.evaluation)).join("")}</select></div>
      ${filtreClasse(true)}
      <div class="field"><label>${t("c.matiere")}</label><select class="select" data-f="notes.matiere">${D.matieres.map(x => option(x.id, x.libelle, f.matiere)).join("")}</select></div>
      ${boutonAfficher("notes")}
      <div class="row" style="margin-left:auto">${tag("info", `${t("notes.bareme")} : ${b.libelle}`, "pi-sliders-h")}${tag("secondary", `${t("bul.coef")} ${m.coef}`)}${tag("secondary", m.prof, "pi-user")}</div>
    </div></div></div>`;
    if (!estAffiche("notes") || !eleves.length) return entete(t("notes.titre"), t("notes.sousTitre")) + filtres + zoneVide("notes");
    const valeurs = eleves.map(e => noteEval(ev.id, m.id, e.id)).filter(v => v != null).map(v => sur20(v, m));
    const st = stats(valeurs, 10);
    const pied = `<div class="paginator"><div class="row">${tag("", `${t("bul.moyenneClasse")} : ${fmt(st.moyenne)}`)}${tag("success", `${t("bul.plusHaute")} : ${fmt(st.max)}`)}${tag("danger", `${t("bul.plusBasse")} : ${fmt(st.min)}`)}${tag("secondary", `${t("bul.reussite")} : ${st.taux == null ? "—" : fmt(st.taux) + " %"}`)}</div><span>${t("notes.surVingt")}</span></div>`;

    if (deps.length) {
      const calcule = S.calcule[ev.id];
      return entete(t("notes.titre"), t("notes.sousTitre")) + filtres + `
        <div class="message" style="margin-bottom:16px"><i class="pi pi-calculator"></i><div><b>${t("notes.parentTitre")}</b><div class="small">${t("notes.parentTexte", { d: deps.map(d => `${evaluation(d.dependance).libelle} (${d.pourcentage} %)`).join(" + ") })}</div></div></div>
        <div class="card"><div class="card-head"><h2>${esc(ev.libelle)} · ${esc(m.libelle)}</h2>${can("notation:calculer") ? `<button class="btn" data-act="calculer-notes"><i class="pi pi-calculator"></i>${t(calcule ? "notes.recalculer" : "notes.calculer")}</button>` : ""}</div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>#</th><th>${t("c.eleve")}</th>${deps.map(d => `<th class="num">${esc(evaluation(d.dependance).libelle)}<div class="small muted">${d.pourcentage} %</div></th>`).join("")}<th class="num">${t("notes.noteCalculee")}</th><th>${t("bul.appreciation")}</th></tr></thead><tbody>
        ${eleves.map((e, i) => { const n = noteEval(ev.id, m.id, e.id); return `<tr><td class="muted">${i + 1}</td><td>${esc(e.nom)} ${esc(e.prenom)}</td>
          ${deps.map(d => { const v = noteEval(d.dependance, m.id, e.id); return `<td class="num">${v != null ? fmt(v) : `<span class="tag secondary">${t("notes.nc")}</span>`}</td>`; }).join("")}
          <td class="num"><b>${n != null ? fmt(n) : "—"}</b></td><td>${esc(n != null ? appreciation(n, m.bareme) : "—")}</td></tr>`; }).join("")}
        </tbody></table></div>${pied}
        <div class="card-body small muted" style="border-top:1px solid var(--border)"><i class="pi pi-info-circle"></i> ${t("notes.regleArrondi")}</div></div>`;
    }

    const parent = parentDe(ev.id);
    const modifiable = can(valeurs.length ? "notation:modifier" : "notation:ajouter");
    return entete(t("notes.titre"), t("notes.sousTitre")) + filtres + `
      ${parent && S.calcule[parent.parent] ? `<div class="message warn" style="margin-bottom:16px"><i class="pi pi-sync"></i><div class="small">${t("notes.recalculParent", { p: evaluation(parent.parent).libelle })}</div></div>` : ""}
      <div class="card"><div class="card-head"><h2>${esc(ev.libelle)} · ${esc(m.libelle)}</h2><div class="row"><span class="small muted">${t("notes.aideSaisie", { max: b.valeurMax })}</span></div></div>
      <div class="table-wrap"><table class="dt"><thead><tr><th>#</th><th>${t("c.matricule")}</th><th>${t("c.eleve")}</th><th class="num">${t("notes.note")} / ${b.valeurMax}</th><th class="num">${t("notes.surVingtCol")}</th><th>${t("bul.appreciation")}</th></tr></thead><tbody>
      ${eleves.map((e, i) => { const n = noteEval(ev.id, m.id, e.id); return `<tr><td class="muted">${i + 1}</td><td class="mono small">${esc(e.matricule)}</td><td>${esc(e.nom)} ${esc(e.prenom)}</td>
        <td class="num"><input class="input note" inputmode="decimal" data-note="${ev.id}|${m.id}|${e.id}" value="${n != null ? String(n).replace(".", S.lang === "fr" ? "," : ".") : ""}" placeholder="${t("notes.nc")}" ${modifiable ? "" : "disabled"}></td>
        <td class="num">${n != null ? fmt(sur20(n, m)) : "—"}</td><td>${n != null ? esc(appreciation(n, m.bareme)) : `<span class="muted">${t("notes.nonClasse")}</span>`}</td></tr>`; }).join("")}
      </tbody></table></div>${pied}
      <div class="dialog-foot"><button class="btn secondary">${t("c.annuler")}</button>${modifiable ? `<button class="btn" data-act="enregistrer-notes"><i class="pi pi-save"></i>${t("notes.enregistrer")}</button>` : ""}</div></div>`;
  }

  /* ---------------- Discipline ---------------- */
  function ecranDiscipline() {
    const f = S.f.discipline;
    const eleves = elevesClasse(S.sel.classe);
    const appel = D.configuration.isAppel;
    return entete(t("disc.titre"), t("disc.sousTitre")) + `
      <div class="card" style="margin-bottom:16px"><div class="card-body"><div class="filters">
        <div class="field"><label>${t("c.evaluation")}</label><select class="select" data-f="discipline.evaluation">${D.evaluations.filter(e => !parentDe(e.id) && e.trimestre === 1).map(e => option(e.id, e.libelle, f.evaluation)).join("")}</select></div>
        ${filtreClasse(true)}
        ${boutonAfficher("discipline")}
        <div class="row" style="margin-left:auto">${appel ? tag("success", t("disc.modeAppel"), "pi-check-square") : tag("secondary", t("disc.modeManuel"), "pi-pencil")}</div>
      </div></div></div>
      <div class="message ${appel ? "" : "warn"}" style="margin-bottom:16px"><i class="pi pi-info-circle"></i><div class="small">${t(appel ? "disc.infoAppel" : "disc.infoManuel")}</div></div>
      ${estAffiche("discipline") && eleves.length ? `<div class="card"><div class="card-head"><h2>${esc(evaluation(f.evaluation).libelle)} · ${esc(classe(S.sel.classe).libelle)}</h2>
        ${appel && can("discipline_eleve:calculer") ? `<button class="btn" data-act="calculer-discipline"><i class="pi pi-calculator"></i>${t("disc.calculer")}</button>` : ""}</div>
      <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.eleve")}</th><th class="num">${t("disc.nonJustifiees")}</th><th class="num">${t("disc.justifiees")}</th><th class="num">${t("disc.total")}</th><th>${t("disc.decision")}</th></tr></thead><tbody>
      ${eleves.map(e => { const d = discipline(e.id, [Number(f.evaluation)]); const champ = v => appel ? `<b>${v}</b>` : `<input class="input note" value="${v}">`;
        return `<tr><td><div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span>${esc(e.nom)} ${esc(e.prenom)}</div></td><td class="num">${champ(d.nj)}</td><td class="num">${champ(d.j)}</td><td class="num"><b>${d.total} h</b></td><td>${d.decision ? tag(d.total > 10 ? "danger" : d.total > 5 ? "warn" : "success", d.decision) : "—"}</td></tr>`; }).join("")}
      </tbody></table></div>
      ${!appel ? `<div class="dialog-foot"><button class="btn"><i class="pi pi-save"></i>${t("c.enregistrer")}</button></div>` : ""}</div>` : zoneVide("discipline")}`;
  }

  /* ---------------- Bulletins ---------------- */
  function ecranBulletins() {
    const f = S.f.bulletin;
    const periodes = f.type === "evaluation" ? D.evaluations.filter(e => e.trimestre === 1) : f.type === "trimestre" ? D.trimestres : [];
    const res = calculerBulletins(S.sel.classe, { type: f.type, id: f.periode });
    const libellePeriode = f.type === "evaluation" ? evaluation(f.periode)?.libelle : f.type === "trimestre" ? byId(D.trimestres, f.periode)?.libelle : t("bul.annee", { a: D.ecole.annee });
    const filtres = `<div class="card" style="margin-bottom:16px"><div class="card-body stack">
      <div class="filters">
        ${filtreClasse(true)}
        <div class="field" style="width:auto"><label>${t("bul.type")}</label><div class="segmented">${[["evaluation", "bul.tEvaluation"], ["trimestre", "bul.tTrimestre"], ["annuel", "bul.tAnnuel"]].map(([k, l]) => `<button class="${f.type === k ? "on" : ""}" data-act="bul-type" data-v="${k}">${t(l)}</button>`).join("")}</div></div>
        <div class="field" style="width:auto"><label>${t("bul.langue")}</label><div class="segmented">${["FR", "EN"].map(k => `<button class="${f.langue === k ? "on" : ""}" data-act="bul-langue" data-v="${k}">${k}</button>`).join("")}</div></div>
        ${periodes.length ? `<div class="field"><label>${t(f.type === "evaluation" ? "c.evaluation" : "c.trimestre")}</label><select class="select" data-f="bulletin.periode">${periodes.map(p => option(p.id, p.libelle, f.periode)).join("")}</select></div>` : ""}
        ${boutonAfficher("bulletins")}
        <div class="row" style="margin-left:auto">
          <button class="btn outlined" data-act="pdf-bulletins" ${estAffiche("bulletins") ? "" : "disabled"}><i class="pi pi-file-pdf"></i>${t("bul.genererPdf")}</button>
        </div>
      </div>
      ${f.type === "annuel" ? `<div class="grid grid-main-side" style="align-items:start">
        <div><h3 style="margin-bottom:8px">${t("bul.reglesDecision")}</h3><div class="table-wrap"><table class="dt"><thead><tr><th>${t("bul.moyMin")}</th><th>${t("bul.moyMax")}</th><th>${t("bul.decision")}</th></tr></thead><tbody>
          ${f.regles.map((r, i) => `<tr><td><input class="input note" data-regle="${i}|min" value="${r.min}"></td><td><input class="input note" data-regle="${i}|max" value="${r.max}"></td><td><input class="input" data-regle="${i}|decision" value="${esc(r.decision)}"></td></tr>`).join("")}
        </tbody></table></div></div>
        <div class="field"><label>${t("bul.seuilAnnuel")}</label><input class="input" data-f="bulletin.seuil" value="${f.seuil}"><span class="hint">${t("bul.seuilAide")}</span></div>
      </div>` : `<div class="small muted"><i class="pi pi-info-circle"></i> ${t(f.type === "evaluation" ? "bul.infoEvaluation" : "bul.infoTrimestre")}</div>`}
    </div></div>`;
    if (!estAffiche("bulletins") || !res.bulletins.length || !res.stats.effectif) return entete(t("bul.titre"), t("bul.sousTitre")) + filtres + zoneVide("bulletins");
    const s = res.stats;
    const carte = (l, v, sev) => `<div class="card stat" style="padding:14px 16px"><div><div class="stat-label">${l}</div><div class="stat-value" style="font-size:21px;${sev ? `color:var(--${sev})` : ""}">${v}</div></div></div>`;
    const maxRep = Math.max(1, ...res.repartition.map(r => r.n));
    return entete(t("bul.titre"), t("bul.sousTitre")) + filtres + `
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
        ${carte(t("bul.moyenneClasse"), fmt(s.moyenne))}${carte(t("bul.moyPremier"), fmt(s.max), "success")}${carte(t("bul.moyDernier"), fmt(s.min), "danger")}
        ${carte(t("bul.ecartType"), fmt(s.ecart))}${carte(t("bul.mediane"), fmt(s.mediane))}${carte(t("bul.tauxReussite"), fmt(s.taux) + " %")}
        ${res.distinction ? carte(t("bul.tableauHonneur"), res.honneur, "warn") : ""}
      </div>
      <div class="grid grid-3" style="margin-top:16px">
        <div class="card"><div class="card-head"><h2>${t("bul.repartition")}</h2></div><div class="card-body"><div class="bars" style="height:140px">${res.repartition.map(r => `<div class="bar"><b>${r.n}</b><div style="height:${r.n / maxRep * 100}%"></div><small>${r.l}</small></div>`).join("")}</div></div></div>
        <div class="card"><div class="card-head"><h2>${t("bul.parGenre")}</h2></div><div class="card-body stack" style="gap:14px">${res.parGenre.map(g => `<div><div class="row-between"><b>${t(g.g === "F" ? "c.filles" : "c.garcons")}</b><span class="small muted">${g.effectif} ${t("c.eleves")} · ${t("bul.moyenne")} ${fmt(g.moyenne)}</span></div><div class="progress success" style="margin-top:6px"><div style="width:${g.taux || 0}%"></div></div><div class="small muted" style="margin-top:4px">${t("bul.reussite")} : ${g.taux == null ? "—" : fmt(g.taux) + " %"}</div></div>`).join("")}</div></div>
        <div class="card"><div class="card-head"><h2>${f.type === "annuel" ? t("bul.decisionsFinales") : t("bul.discipline")}</h2></div><div class="card-body stack" style="gap:10px">
          ${f.type === "annuel" ? res.decisionsFinales.map(d => `<div class="row-between"><span>${esc(d.d)}</span><b>${d.n}</b></div>`).join("")
            : `<div class="row-between"><span>${t("disc.totalHeures")}</span><b>${res.bulletins.reduce((x, b) => x + b.discipline.total, 0)} h</b></div><div class="row-between"><span>${t("disc.moyenneParEleve")}</span><b>${fmt(res.bulletins.reduce((x, b) => x + b.discipline.total, 0) / res.bulletins.length)} h</b></div>
               ${D.decisions.map(d => ({ d: d.libelle, n: res.bulletins.filter(b => b.discipline.decision === d.libelle).length })).filter(x => x.n).map(x => `<div class="row-between"><span>${esc(x.d)}</span>${tag("secondary", x.n)}</div>`).join("")}`}
        </div></div>
      </div>
      <div class="card" style="margin-top:16px"><div class="card-head"><h2>${t("bul.classement")} · ${esc(libellePeriode || "")}</h2><span class="small muted">${t("bul.seuil")} : ${res.seuil}/20</span></div>
      <div class="table-wrap"><table class="dt"><thead><tr><th>${t("bul.rang")}</th><th>${t("c.eleve")}</th><th class="num">${t("bul.moyenne")}</th><th>${t("bul.appreciation")}</th>${f.type === "annuel" ? `<th>${t("bul.moyTrimestres")}</th><th>${t("bul.decision")}</th>` : ""}<th>${t("bul.distinction")}</th><th class="num">${t("disc.heures")}</th><th></th></tr></thead><tbody>
      ${res.bulletins.map(b => `<tr><td><b>${libelleRang(b.rang, b.e.genre)}</b></td><td><div class="person"><span class="avatar">${esc(initiales(b.e.prenom, b.e.nom))}</span>${esc(b.e.nom)} ${esc(b.e.prenom)}</div></td>
        <td class="num"><b style="color:var(--${b.moy == null ? "text-muted" : b.reussite ? "success" : "danger"})">${b.moy == null ? t("notes.nc") : fmt(b.moy)}</b></td><td>${esc(b.appreciation || "—")}</td>
        ${f.type === "annuel" ? `<td class="small">${b.trimestres.map(x => `${esc(x.libelle.replace("Trimestre ", "T"))} : ${fmt(x.moy)}`).join(" · ")}</td><td>${b.decisionFinale ? tag(b.decisionFinale === "Promu" ? "success" : b.decisionFinale === "Redouble" ? "danger" : "warn", b.decisionFinale) : "—"}</td>` : ""}
        <td>${b.distinction ? tag("warn", t("bul.tableauHonneur"), "pi-star") : ""}</td><td class="num">${b.discipline.total} h</td>
        <td class="right"><button class="btn text sm" data-act="apercu-bulletin" data-v="${b.e.id}"><i class="pi pi-eye"></i>${t("bul.apercu")}</button></td></tr>`).join("")}
      </tbody></table></div></div>
      <div class="card" style="margin-top:16px"><div class="card-head"><h2>${t("bul.statsMatieres")}</h2></div><div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.matiere")}</th><th class="num">${t("bul.coef")}</th><th class="num">${t("bul.moyenne")}</th><th class="num">${t("bul.plusHaute")}</th><th class="num">${t("bul.plusBasse")}</th><th class="num">${t("bul.ecartType")}</th><th>${t("bul.tauxReussite")}</th></tr></thead><tbody>
        ${res.parMatiere.map(x => `<tr><td>${esc(x.m.libelle)}</td><td class="num">${coefficient(x.m)}</td><td class="num"><b>${fmt(x.moyenne)}</b></td><td class="num">${fmt(x.max)}</td><td class="num">${fmt(x.min)}</td><td class="num">${fmt(x.ecart)}</td><td><div class="row" style="gap:8px;flex-wrap:nowrap"><div class="progress grow ${x.taux >= 50 ? "success" : "danger"}" style="min-width:80px"><div style="width:${x.taux || 0}%"></div></div><span class="small mono">${x.taux == null ? "—" : fmt(x.taux) + " %"}</span></div></td></tr>`).join("")}
      </tbody></table></div></div>`;
  }
  function apercuBulletin(idEleve) {
    const f = S.f.bulletin;
    // Le bulletin est construit dans sa langue (paramètre langue envoyé au backend) ; la fenêtre reste dans la langue de l'interface
    const langueInterface = S.lang;
    S.lang = (f.langue || "FR").toLowerCase();
    const periode = location.hash.startsWith("#/bulletins") ? { type: f.type, id: f.periode } : { type: "trimestre", id: 1 };
    const res = calculerBulletins(eleve(idEleve).classe, periode);
    const b = res.bulletins.find(x => x.e.id === Number(idEleve));
    const libellePeriode = periode.type === "evaluation" ? evaluation(periode.id).libelle : periode.type === "trimestre" ? byId(D.trimestres, periode.id).libelle : t("bul.annee", { a: D.ecole.annee });
    const e = b.e;
    const papier = `<div class="paper">
      ${enteteDocument(`<div style="text-align:right"><h2>${t("bul.bulletinDeNotes")}</h2><div style="font-weight:700">${esc(libellePeriode)}</div></div>`)}
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px 16px">
        <div><span style="color:#64748b">${t("c.eleve")} :</span> <b>${esc(e.nom)} ${esc(e.prenom)}</b></div>
        <div><span style="color:#64748b">${t("c.matricule")} :</span> <b>${esc(e.matricule)}</b></div>
        <div><span style="color:#64748b">${t("c.classe")} :</span> <b>${esc(classe(e.classe).libelle)}</b> (${res.stats.effectif} ${t("c.eleves")})</div>
        <div><span style="color:#64748b">${t("eleve.naissance")} :</span> ${fmtDate(e.naissance)} · ${esc(e.lieu)}</div>
        <div><span style="color:#64748b">${t("c.genre")} :</span> ${e.genre === "F" ? t("c.fille") : t("c.garcon")}</div>
        <div><span style="color:#64748b">${t("eleve.redoublant")} :</span> ${t(e.redoublant ? "c.oui" : "c.non")}</div>
      </div>
      <table><thead><tr><th>${t("c.matiere")}</th>${periode.type === "evaluation" ? `<th class="num">${t("notes.note")}</th>` : ""}<th class="num">${t("bul.noteSur20")}</th><th class="num">${t("bul.coef")}</th><th class="num">${t("bul.points")}</th><th class="num">${t("bul.rang")}</th><th>${t("bul.appreciation")}</th><th>${t("bul.professeur")}</th></tr></thead><tbody>
      ${b.groupes.map(g => g.lignes.map(l => `<tr><td>${esc(l.m.libelle)}</td>${periode.type === "evaluation" ? `<td class="num">${l.brute != null ? `${fmt(l.brute)}/${bareme(l.m.bareme).valeurMax}` : t("notes.nc")}</td>` : ""}<td class="num">${l.note != null ? fmt(l.note) : t("notes.nc")}</td><td class="num">${l.coef}</td><td class="num">${fmt(l.points)}</td><td class="num">${libelleRang(l.rang, e.genre)}</td><td>${esc(l.appreciation || "")}</td><td>${esc(l.m.prof)}</td></tr>`).join("")
        + `<tr class="g"><td>${esc(g.g.libelle)}</td>${periode.type === "evaluation" ? "<td></td>" : ""}<td class="num">${fmt(g.moy)}</td><td class="num">${g.coefs}</td><td class="num">${fmt(g.points)}</td><td class="num">${libelleRang(g.rang, e.genre)}</td><td colspan="2">${esc(appreciation(g.moy) || "")}</td></tr>`).join("")}
      </tbody></table>
      <div class="boxes">
        <div class="box"><h4>${t("bul.resultat")}</h4><div class="big">${fmt(b.moy)} / 20</div><div>${t("bul.rang")} : <b>${libelleRang(b.rang, e.genre)}</b> / ${res.stats.effectif}</div><div>${esc(b.appreciation || "")}</div>${b.distinction ? `<div class="honneur">★ ${t("bul.tableauHonneur")}</div>` : ""}${b.decisionFinale ? `<div style="margin-top:6px">${t("bul.decision")} : <b>${esc(b.decisionFinale)}</b></div>` : ""}</div>
        <div class="box"><h4>${t("bul.profilClasse")}</h4><div>${t("bul.moyenneClasse")} : <b>${fmt(res.stats.moyenne)}</b></div><div>${t("bul.moyPremier")} : <b>${fmt(res.stats.max)}</b></div><div>${t("bul.moyDernier")} : <b>${fmt(res.stats.min)}</b></div><div>${t("bul.ecartType")} : <b>${fmt(res.stats.ecart)}</b></div><div>${t("bul.tauxReussite")} : <b>${fmt(res.stats.taux)} %</b></div></div>
        <div class="box"><h4>${t("bul.discipline")}</h4><div>${t("disc.nonJustifiees")} : <b>${b.discipline.nj} h</b></div><div>${t("disc.justifiees")} : <b>${b.discipline.j} h</b></div><div>${t("disc.total")} : <b>${b.discipline.total} h</b></div><div>${t("disc.decision")} : <b>${esc(b.discipline.decision || "—")}</b></div></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:22px;color:#64748b"><span>${t("bul.signParent")}</span><span>${t("bul.signTitulaire")}</span><span>${t("bul.signDirecteur")}</span></div>
      ${piedApplication()}
    </div>`;
    S.lang = langueInterface;
    dialog(t("bul.apercuDe", { e: `${e.nom} ${e.prenom}` }), papier, `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button><button class="btn" data-act="pdf-bulletins"><i class="pi pi-file-pdf"></i>${t("bul.genererPdfEleve")}</button>`, true);
  }

  /* ---------------- Reçu d'inscription (imprimable) ---------------- */
  let numeroRecu = 127;
  const prochainNumeroRecu = () => `REC-2026-${String(++numeroRecu).padStart(5, "0")}`;
  function recuInscription(d) {
    const numero = d.numero || prochainNumeroRecu();
    const u = d.user ? (D.utilisateurs.find(x => x.username === d.user) || utilisateurCourant()) : utilisateurCourant();
    // Reçu bilingue : libellés et valeurs traduisibles dans les deux langues ; dates au format numérique (communes aux deux langues)
    const dateRecu = iso => iso.split("-").reverse().join("/");
    const ligne = (cle, v) => `<tr><th style="width:42%">${bi(cle)}</th><td>${v}</td></tr>`;
    const mention = { e: `${esc(d.nom)} ${esc(d.prenom || "")}`, c: esc(d.classe), a: esc(D.ecole.annee) };
    const exemplaire = cleExemplaire => `
      <div class="recu">
        ${enteteDocument(`<div style="text-align:right;flex:none"><h2>${bi("recu.titre")}</h2><div style="font-weight:700" class="mono">N° ${numero}</div><div style="color:#64748b">${dateRecu(d.date || AUJOURDHUI)}</div>${d.duplicata ? `<div class="duplicata">${tL("fr", "recu.duplicata")} · ${tL("en", "recu.duplicata")} · ${dateRecu(AUJOURDHUI)}</div>` : ""}</div>`, true)}
        <table>
          ${ligne("c.eleve", `<b>${esc(d.nom)} ${esc(d.prenom || "")}</b>`)}
          ${ligne("c.matricule", `<span class="mono">${esc(d.matricule)}</span>`)}
          ${ligne("eleve.naissance", `${dateRecu(d.naissance)}${d.lieu ? " · " + esc(d.lieu) : ""}`)}
          ${ligne("c.genre", bi(d.genre === "F" ? "c.fille" : "c.garcon"))}
          ${ligne("c.classe", `<b>${esc(d.classe)}</b>`)}
          <tr class="montant"><th>${bi("recu.montant")}</th><td><b>${fcfa(d.montant)}</b></td></tr>
          ${ligne("eleve.redoublant", bi(d.redoublant ? "c.oui" : "c.non"))}
          ${ligne("recu.enregistrePar", `${esc(u.prenom)} ${esc(u.nom)} (${esc(u.username)})`)}
        </table>
        <p style="margin:10px 0 0">${bi("recu.mention", mention)}</p>
        <div style="display:flex;justify-content:space-between;margin-top:22px;color:#64748b"><span>${bi("recu.signature")}</span><span style="text-align:right">${bi("recu.cachet")}</span></div>
        ${piedApplication(true, `<span>${biLigne(cleExemplaire)}</span>`)}
      </div>`;
    dialog(t("recu.dialogTitre"), `<div class="paper print-area">${exemplaire("recu.exemplaireEleve")}<div class="decoupe"><span>✂</span></div>${exemplaire("recu.exemplaireEcole")}</div>`,
      `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button><button class="btn" data-act="imprimer"><i class="pi pi-print"></i>${t("recu.imprimer")}</button>`, true);
  }

  /* ---------------- Modification des informations d'un élève (PATCH /eleves/update/{id}) ---------------- */
  function dialogModifierEleve(id) {
    const e = eleve(id);
    const champ = (cle, label, valeur, type = "text", obligatoire = true) => `<div class="field"><label for="ed-${cle}">${t(label)}${obligatoire ? " *" : ""}</label><input class="input" id="ed-${cle}" name="${cle}" type="${type}" value="${esc(valeur || "")}" ${obligatoire ? "required" : ""}></div>`;
    dialog(t("eleve.modifierTitre", { e: `${e.nom} ${e.prenom}` }), `<form id="form-eleve-edit" data-form="eleve-edit" data-id="${e.id}"><div class="form-grid">
        <div class="field full"><span class="small muted">${t("c.matricule")} : <b class="mono">${esc(e.matricule)}</b> · ${t("eleve.matriculeFixe")}</span></div>
        ${champ("nom", "eleve.nom", e.nom)}${champ("prenom", "eleve.prenom", e.prenom, "text", false)}
        ${champ("naissance", "eleve.naissance", e.naissance, "date")}${champ("lieu", "eleve.lieu", e.lieu)}
        <div class="field"><label>${t("c.genre")} *</label><select class="select" name="genre">${option("F", t("c.fille"), e.genre)}${option("M", t("c.garcon"), e.genre)}</select></div>
        ${champ("quartier", "eleve.quartier", e.quartier)}
        ${champ("pere", "eleve.pere", e.pere, "text", false)}${champ("mere", "eleve.mere", e.mere)}
        ${champ("telephone", "eleve.telephone1", e.telephone, "tel")}${champ("telephone2", "eleve.telephone2", e.telephone2, "tel", false)}
      </div></form>`, `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" type="submit" form="form-eleve-edit"><i class="pi pi-check"></i>${t("c.enregistrer")}</button>`);
  }
  function enregistrerEleve(form) {
    const e = eleve(form.dataset.id);
    const donnees = Object.fromEntries(new FormData(form).entries());
    const modifies = Object.keys(donnees).filter(k => (e[k] || "") !== donnees[k]);
    Object.assign(e, donnees);
    fermer();
    render();
    toast(modifies.length ? "success" : "info", t(modifies.length ? "eleve.modifieOk" : "hist.aucunChangement"), modifies.length ? `${e.nom} ${e.prenom}` : "");
  }

  /* ---------------- Scolarité ---------------- */
  function ecranScolarite() {
    const tab = S.tab.scolarite;
    const onglets = `<div class="tabs" style="margin-bottom:16px">${[["reglements", "sco.tReglements"], ["tranches", "sco.tTranches"]].map(([k, l]) => `<div class="tab ${tab === k ? "on" : ""}" data-tab="scolarite" data-v="${k}">${t(l)}</div>`).join("")}</div>`;
    if (tab === "tranches") {
      const total = D.tranches.reduce((s, x) => s + x.montant, 0);
      return entete(t("sco.titre"), t("sco.sousTitre"), can("tranche_pension:ajouter") ? `<button class="btn"><i class="pi pi-plus"></i>${t("sco.ajouterTranche")}</button>` : "") + onglets + `
        <div class="filters" style="margin-bottom:16px"><div class="field"><label>${t("c.niveau")}</label><select class="select">${D.niveaux.map(n => option(n.id, n.libelle, 5)).join("")}</select></div></div>
        <div class="card"><div class="table-wrap"><table class="dt"><thead><tr><th>${t("sco.ordre")}</th><th>${t("c.code")}</th><th>${t("c.libelle")}</th><th class="num">${t("c.montant")}</th><th></th></tr></thead><tbody>
        ${D.tranches.map(x => `<tr><td>${x.ordre}</td><td class="mono">${esc(x.code)}</td><td>${esc(x.libelle)}</td><td class="num">${fcfa(x.montant)}</td><td class="right">${can("tranche_pension:modifier") ? `<button class="btn text icon sm"><i class="pi pi-pencil"></i></button>` : ""}</td></tr>`).join("")}
        <tr class="total"><td colspan="3">${t("sco.totalPension")}</td><td class="num">${fcfa(total)}</td><td></td></tr>
        </tbody></table></div></div>`;
    }
    const f = S.f.regl;
    // Seules les tranches du niveau de la classe sont proposées (le backend refuse une tranche d'un autre niveau)
    const tranchesNiveau = S.sel.classe ? D.tranches.filter(x => x.niveau === classe(S.sel.classe).niveau) : [];
    if (tranchesNiveau.length && !tranchesNiveau.some(x => x.id === f.tranche)) f.tranche = tranchesNiveau[0].id;
    const eleves = tranchesNiveau.length ? elevesClasse(S.sel.classe) : [];
    const situations = eleves.map(e => ({ e, ...situationTranche(e.id, f.tranche) }));
    const filtrees = situations.filter(s => f.statut === "tous" || s.statut === f.statut);
    const attendu = situations.reduce((s, x) => s + x.tr.montant, 0), encaisse = situations.reduce((s, x) => s + Math.min(x.regle, x.tr.montant), 0);
    const nb = k => situations.filter(s => s.statut === k).length;
    const carte = (icone, sev, l, v, sous) => `<div class="card stat"><div class="stat-icon ${sev}"><i class="pi ${icone}"></i></div><div><div class="stat-label">${l}</div><div class="stat-value" style="font-size:20px">${v}</div><div class="stat-sub">${sous || ""}</div></div></div>`;
    return entete(t("sco.titre"), t("sco.sousTitre")) + onglets + `
      <div class="card" style="margin-bottom:16px"><div class="card-body"><div class="filters">
        ${filtreClasse(true)}
        <div class="field" style="width:280px"><label>${t("sco.tranche")}</label><select class="select" data-f="regl.tranche" ${tranchesNiveau.length ? "" : "disabled"}>${tranchesNiveau.map(x => option(x.id, `${x.libelle} · ${fcfa(x.montant)}`, f.tranche)).join("") || option("", "—")}</select></div>
        ${boutonAfficher("scolarite")}
        <div class="field" style="width:auto"><label>${t("sco.statutPaiement")}</label><div class="segmented">${[["tous", "c.tous"], ["total", "pay.total"], ["partiel", "pay.partiel"], ["aucun", "pay.aucun"]].map(([k, l]) => `<button class="${f.statut === k ? "on" : ""}" data-act="regl-statut" data-v="${k}">${t(l)}</button>`).join("")}</div></div>
      </div></div></div>
      ${estAffiche("scolarite") && eleves.length ? `<div class="grid grid-4" style="margin-bottom:16px">
        ${carte("pi-wallet", "", t("sco.attendu"), fcfa(attendu))}
        ${carte("pi-check-circle", "success", t("sco.encaisse"), fcfa(encaisse), `${Math.round(encaisse * 100 / attendu)} % ${t("sco.duMontant")}`)}
        ${carte("pi-hourglass", "warn", t("sco.resteARecouvrer"), fcfa(attendu - encaisse))}
        ${carte("pi-users", "danger", t("sco.repartition"), `${nb("total")} / ${nb("partiel")} / ${nb("aucun")}`, t("sco.repartitionSous"))}
      </div>
      <div class="card"><div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.eleve")}</th><th class="num">${t("sco.montantTranche")}</th><th class="num">${t("sco.regle")}</th><th class="num">${t("sco.reste")}</th><th style="width:180px">${t("sco.progression")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
      ${filtrees.length ? filtrees.map(s => `<tr><td><div class="person"><span class="avatar">${esc(initiales(s.e.prenom, s.e.nom))}</span><div>${esc(s.e.nom)} ${esc(s.e.prenom)}<div class="sub mono">${esc(s.e.matricule)}</div></div></div></td>
        <td class="num">${fcfa(s.tr.montant)}</td><td class="num">${fcfa(s.regle)}</td><td class="num"><b>${fcfa(s.reste)}</b></td>
        <td><div class="progress ${s.statut === "total" ? "success" : s.statut === "partiel" ? "warn" : "danger"}"><div style="width:${s.pct}%"></div></div></td><td>${tagPaiement(s.statut)}</td>
        <td class="right"><button class="btn text icon sm" data-act="historique" data-v="${s.e.id}" title="${t("sco.historique")}"><i class="pi pi-history"></i></button>${can("reglement:ajouter") && s.statut !== "total" ? `<button class="btn sm" data-act="nouveau-reglement" data-v="${s.e.id}"><i class="pi pi-plus"></i>${t("sco.encaisser")}</button>` : ""}</td></tr>`).join("")
        : `<tr><td colspan="7"><div class="empty">${t("c.aucunResultat")}</div></td></tr>`}
      </tbody></table></div></div>` : zoneVide("scolarite")}`;
  }
  function dialogNouveauReglement(idEl) {
    const e = eleve(idEl), s = situationTranche(e.id, S.f.regl.tranche);
    dialog(t("sco.encaisserTitre"), `<div class="stack">
      <div class="person"><span class="avatar">${esc(initiales(e.prenom, e.nom))}</span><div><b>${esc(e.nom)} ${esc(e.prenom)}</b><div class="sub">${esc(classe(e.classe).libelle)} · ${esc(s.tr.libelle)}</div></div></div>
      <div class="message"><i class="pi pi-info-circle"></i><span class="small">${t("pay.regleReste", { regle: fcfa(s.regle), reste: fcfa(s.reste) })}</span></div>
      <div class="form-grid"><div class="field"><label>${t("c.montant")} (FCFA) *</label><input class="input" value="${s.reste}"></div>
      <div class="field"><label>${t("sco.typeReglement")}</label><div class="segmented"><button class="on">${t("pay.total")}</button><button>${t("pay.partiel")}</button></div></div>
      <div class="field"><label>${t("c.date")}</label><input class="input" type="date" value="${AUJOURDHUI}" disabled></div>
      <div class="field"><label>${t("sco.enregistrePar")}</label><input class="input" value="${esc(utilisateurCourant().username)}" disabled></div></div></div>`,
      `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" data-act="valider-reglement" data-v="${e.id}"><i class="pi pi-check"></i>${t("sco.valider")}</button>`);
  }
  function dialogHistorique(idEl) {
    const e = eleve(idEl);
    const liste = reglementsEleve(e.id);
    dialog(t("sco.historiqueDe", { e: `${e.nom} ${e.prenom}` }), `<div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.date")}</th><th>${t("sco.tranche")}</th><th class="num">${t("c.montant")}</th><th>${t("sco.typeReglement")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
      ${liste.length ? liste.map(r => `<tr><td>${fmtDate(r.date)}</td><td>${esc(byId(D.tranches, r.tranche).libelle)}</td><td class="num">${fcfa(r.montant)}</td><td>${t("pay." + r.type)}</td><td>${r.statut === "valide" ? tag("success", t("sco.valide")) : tag("secondary", t("sco.annule"))}</td>
        <td class="right">${r.statut === "valide" && can("reglement:annuler") ? `<button class="btn danger outlined sm" data-act="annuler-reglement" data-v="${r.id}"><i class="pi pi-ban"></i>${t("sco.annuler")}</button>` : ""}</td></tr>`).join("")
        : `<tr><td colspan="6"><div class="empty">${t("sco.aucunReglement")}</div></td></tr>`}
    </tbody></table></div>`, `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button>`, true);
  }

  /* ---------------- Paramétrage (administration) ---------------- */
  function ecranAdministration() {
    const tab = S.tab.admin;
    const onglets = [["structure", "adm.tStructure"], ["matieres", "adm.tMatieres"], ["baremes", "adm.tBaremes"], ["decisions", "adm.tDecisions"], ["annees", "adm.tAnnees"], ["configuration", "adm.tConfiguration"]];
    const actions = (code) => `<td class="right">${can(code + ":modifier") ? `<button class="btn text icon sm" title="${t("c.modifier")}"><i class="pi pi-pencil"></i></button>` : ""}${can(code + ":supprimer") ? `<button class="btn text icon sm" data-act="confirmer-suppression" title="${t("c.supprimer")}"><i class="pi pi-trash" style="color:var(--danger)"></i></button>` : ""}</td>`;
    let corps = "";
    if (tab === "structure") {
      corps = `<div class="card"><div class="card-head"><h2>${t("adm.structure")}</h2>${can("classe:ajouter") ? `<button class="btn sm"><i class="pi pi-plus"></i>${t("adm.ajouterClasse")}</button>` : ""}</div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("adm.section")} / ${t("adm.cycle")} / ${t("c.niveau")}</th><th>${t("c.classe")}</th><th class="num">${t("c.effectif")}</th><th></th></tr></thead><tbody>
        ${D.sections.map(sec => `<tr class="group"><td colspan="4"><i class="pi pi-sitemap"></i> ${esc(sec.libelle)}</td></tr>` + D.cycles.filter(c => c.section === sec.id).map(cy =>
          D.niveaux.filter(n => n.cycle === cy.id).map(n => D.classes.filter(c => c.niveau === n.id).map((c, i) => `<tr><td>${i === 0 ? `<span class="muted small">${esc(cy.libelle)} ›</span> <b>${esc(n.libelle)}</b>` : ""}</td><td>${esc(c.libelle)} <span class="mono small muted">${esc(c.code)}</span></td><td class="num">${c.effectif}</td>${actions("classe")}</tr>`).join("")).join("")).join("")).join("")}
        </tbody></table></div></div>`;
    } else if (tab === "matieres") {
      corps = `<div class="card"><div class="card-head"><div class="filters"><div class="field"><label>${t("c.niveau")}</label><select class="select">${D.niveaux.map(n => option(n.id, n.libelle, 5)).join("")}</select></div></div>${can("matiere_evalue:ajouter") ? `<button class="btn sm"><i class="pi pi-plus"></i>${t("adm.ajouterMatiere")}</button>` : ""}</div>
        <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.code")}</th><th>${t("c.matiere")}</th><th class="num">${t("bul.coef")}</th><th>${t("notes.bareme")}</th><th></th></tr></thead><tbody>
        ${D.groupes.map(g => `<tr class="group"><td colspan="5">${esc(g.libelle)}</td></tr>` + D.matieres.filter(m => m.groupe === g.id).map(m => `<tr><td class="mono">${esc(m.code)}</td><td>${esc(m.libelle)}</td><td class="num">${m.coef}</td><td>${tag(m.bareme === 1 ? "info" : "warn", bareme(m.bareme).libelle)}</td>${actions("matiere_evalue")}</tr>`).join("")).join("")}
        </tbody></table></div><div class="card-body small muted" style="border-top:1px solid var(--border)"><i class="pi pi-info-circle"></i> ${t("adm.infoCoef")}</div></div>`;
    } else if (tab === "baremes") {
      const b = bareme(S.f.baremeSel);
      const apps = D.appreciations.filter(a => a.bareme === b.id);
      corps = `<div class="grid grid-main-side" style="grid-template-columns:minmax(0,1fr) minmax(0,2fr)">
        <div class="card"><div class="card-head"><h2>${t("adm.baremes")}</h2>${can("bareme:ajouter") ? `<button class="btn sm"><i class="pi pi-plus"></i>${t("c.ajouter")}</button>` : ""}</div>
          <div class="table-wrap"><table class="dt"><tbody>${D.baremes.map(x => `<tr class="clickable ${x.id === b.id ? "selected" : ""}" data-act="bareme-sel" data-v="${x.id}"><td><b>${esc(x.libelle)}</b><div class="small muted mono">${esc(x.code)}</div></td><td class="num">${t("adm.noteMax")} : <b>${x.valeurMax}</b></td></tr>`).join("")}</tbody></table></div></div>
        <div class="card"><div class="card-head"><h2>${t("adm.appreciationsDe", { b: b.libelle })}</h2>${can("appreciation:ajouter") ? `<button class="btn sm"><i class="pi pi-plus"></i>${t("c.ajouter")}</button>` : ""}</div>
          <div class="card-body"><div style="display:flex;height:30px;border-radius:6px;overflow:hidden;border:1px solid var(--border)">${apps.map((a, i) => `<div title="${esc(a.libelle)}" style="width:${(a.max - a.min + 0.01) / b.valeurMax * 100}%;background:var(--p-primary-${[100, 200, 300, 400, 500, 600, 700, 800][Math.min(7, Math.round(i * 7 / Math.max(1, apps.length - 1)))]});"></div>`).join("")}</div>
          <div class="row-between small muted" style="margin-top:4px"><span>0</span><span>${b.valeurMax}</span></div></div>
          <div class="table-wrap"><table class="dt"><thead><tr><th>${t("c.libelle")}</th><th>${t("adm.libelleEn")}</th><th class="num">${t("adm.min")}</th><th class="num">${t("adm.max")}</th><th></th></tr></thead><tbody>
          ${apps.map(a => `<tr><td>${esc(a.libelle)}</td><td>${a.libelleEn ? esc(a.libelleEn) : `<span class="muted">—</span>`}</td><td class="num">${fmt(a.min)}</td><td class="num">${fmt(a.max)}</td>${actions("appreciation")}</tr>`).join("")}</tbody></table></div>
          <div class="card-body small muted" style="border-top:1px solid var(--border)"><i class="pi pi-info-circle"></i> ${t("adm.infoIntervalles")}</div></div></div>`;
    } else if (tab === "decisions") {
      corps = `<div class="message warn" style="margin-bottom:16px"><i class="pi pi-lock"></i><div class="small">${t("adm.decisionsBloquees")}</div></div>
        <div class="card"><div class="card-head"><h2>${t("adm.decisions")}</h2></div><div class="table-wrap"><table class="dt"><thead><tr><th>${t("disc.decision")}</th><th>${t("adm.libelleEn")}</th><th class="num">${t("adm.heuresMin")}</th><th class="num">${t("adm.heuresMax")}</th><th class="num">${t("adm.elevesConcernes")}</th></tr></thead><tbody>
        ${D.decisions.map(d => `<tr><td>${esc(d.libelle)}</td><td>${d.libelleEn ? esc(d.libelleEn) : `<span class="muted">—</span>`}</td><td class="num">${d.min}</td><td class="num">${d.max === 999 ? "∞" : d.max}</td><td class="num">${D.eleves.filter(e => { const x = discipline(e.id, [1]); return x.total >= d.min && x.total <= d.max; }).length}</td></tr>`).join("")}
        </tbody></table></div></div>`;
    } else if (tab === "annees") {
      corps = `<div class="grid grid-2"><div class="card"><div class="card-head"><h2>${t("adm.annees")}</h2>${can("annee:ajouter") ? `<button class="btn sm"><i class="pi pi-plus"></i>${t("c.ajouter")}</button>` : ""}</div><div class="table-wrap"><table class="dt"><tbody>
        ${D.annees.map(a => `<tr><td><b>${esc(a.libelle)}</b></td><td>${a.cloture ? tag("secondary", t("adm.cloturee")) : tag("success", t("adm.enCours"))}</td><td class="right">${!a.cloture && can("annee:cloturer") ? `<button class="btn danger outlined sm" data-act="cloturer"><i class="pi pi-lock"></i>${t("adm.cloturer")}</button>` : ""}</td></tr>`).join("")}
        </tbody></table></div></div>
        <div class="card"><div class="card-head"><h2>${t("adm.trimestres")}</h2></div><div class="table-wrap"><table class="dt"><tbody>${D.trimestres.map(x => `<tr><td class="mono">${esc(x.code)}</td><td>${esc(x.libelle)}</td><td class="num">${D.evaluations.filter(e => e.trimestre === x.id).length} ${t("eval.evaluations")}</td></tr>`).join("")}</tbody></table></div></div></div>`;
    } else {
      corps = `<div class="card card-body stack">
        <div class="row-between"><div><h3>${t("adm.appel")}</h3><div class="muted small" style="max-width:620px">${t("adm.appelTexte")}</div></div>
          <label class="switch"><input type="checkbox" data-act="toggle-appel" ${D.configuration.isAppel ? "checked" : ""} ${can("configuration:modifier") ? "" : "disabled"}><span></span></label></div>
        <div class="row-between"><div><h3>${t("adm.absencesPayees")}</h3><div class="muted small" style="max-width:620px">${t("adm.absencesPayeesTexte")}</div></div>
          <label class="switch"><input type="checkbox" data-act="toggle-absences-payees" ${D.configuration.isAbsenceJustifieePayee ? "checked" : ""} ${can("configuration:modifier") ? "" : "disabled"}><span></span></label></div>
        <div class="row-between"><div><h3>${t("adm.typeEcole")}</h3><div class="muted small">${t("adm.typeEcoleTexte")}</div></div>${tag("info", t("adm.secondaire"))}</div>
      </div>`;
    }
    return entete(t("adm.titre"), t("adm.sousTitre")) + `<div class="tabs" style="margin-bottom:16px">${onglets.map(([k, l]) => `<div class="tab ${tab === k ? "on" : ""}" data-tab="admin" data-v="${k}">${t(l)}</div>`).join("")}</div>${corps}`;
  }

  /* ---------------- Utilisateurs, rôles et permissions ---------------- */
  function ecranUtilisateurs() {
    const tab = can("role:consulter") ? S.tab.users : "users";
    const onglets = `<div class="tabs" style="margin-bottom:16px"><div class="tab ${tab === "users" ? "on" : ""}" data-tab="users" data-v="users">${t("usr.tUsers")}</div>${can("role:consulter") ? `<div class="tab ${tab === "roles" ? "on" : ""}" data-tab="users" data-v="roles">${t("usr.tRoles")}</div>` : ""}</div>`;
    if (tab === "users") {
      const moi = utilisateurCourant();
      return entete(t("usr.titre"), t("usr.sousTitre"), can("utilisateur:ajouter") ? `<button class="btn" data-act="ajouter-utilisateur"><i class="pi pi-user-plus"></i>${t("usr.ajouter")}</button>` : "") + onglets + `
        <div class="card"><div class="table-wrap"><table class="dt"><thead><tr><th>${t("usr.utilisateur")}</th><th>${t("usr.identifiant")}</th><th>${t("usr.roles")}</th><th>${t("c.statut")}</th><th></th></tr></thead><tbody>
        ${D.utilisateurs.map(u => { const sa = u.roles.includes(1), protege = sa && S.role !== 1;
          return `<tr><td><div class="person"><span class="avatar">${esc(initiales(u.prenom, u.nom))}</span>${esc(u.prenom)} ${esc(u.nom)}${u.id === moi.id ? ` ${tag("info", t("usr.vous"))}` : ""}</div></td><td class="mono">${esc(u.username)}</td>
          <td><div class="row" style="gap:4px">${u.roles.map(r => tag(r === 1 ? "danger" : r === 2 ? "warn" : "", byId(D.roles, r).nom)).join("")}</div></td><td>${u.actif ? tag("success", t("c.actif")) : tag("secondary", t("usr.desactive"))}</td>
          <td class="right">${can("utilisateur:modifier") ? `<button class="btn text icon sm" ${protege ? `disabled title="${t("usr.protege")}"` : `title="${t("c.modifier")}"`}><i class="pi pi-pencil"></i></button>` : ""}
          ${can("role:attribuer") ? `<button class="btn text icon sm" title="${t("usr.attribuerRoles")}"><i class="pi pi-shield"></i></button>` : ""}
          ${can("utilisateur:supprimer") && u.actif ? `<button class="btn text icon sm" data-act="desactiver" data-v="${u.id}" ${u.id === moi.id || protege ? `disabled title="${t(u.id === moi.id ? "usr.pasSoiMeme" : "usr.protege")}"` : `title="${t("usr.desactiver")}"`}><i class="pi pi-ban" style="color:var(--danger)"></i></button>` : ""}</td></tr>`; }).join("")}
        </tbody></table></div></div>`;
    }
    const role = byId(D.roles, S.f.roleSel);
    const ORDRE_ACTIONS = ["ajouter", "inscrire", "modifier", "supprimer", "annuler", "consulter", "rechercher", "calculer", "generer", "cloturer", "attribuer"];
    const actionsDomaine = d => ORDRE_ACTIONS.filter(a => D.catalogue[d].some(([, aa]) => aa.includes(a)));
    const matrice = role.permissions === "*" ? `<div class="message"><i class="pi pi-shield"></i><div><b>${t("usr.superAdminTitre")}</b><div class="small">${t("usr.superAdminTexte")}</div></div></div>`
      : Object.keys(D.catalogue).map(d => { const acts = actionsDomaine(d); return `<div class="perm-domain"><h3><i class="pi pi-folder-open" style="color:var(--primary)"></i>${t("dom." + d)}${d === "administration" && role.id === 2 ? tag("info", t("usr.domaineAdmin")) : ""}</h3>
        <div class="table-wrap"><table class="dt perm-table"><thead><tr><th>${t("usr.module")}</th>${acts.map(a => `<th>${t("act." + a)}</th>`).join("")}</tr></thead><tbody>
        ${D.catalogue[d].map(([mod, aa]) => `<tr><td>${t("mod." + mod)}</td>${acts.map(a => aa.includes(a) ? `<td><input type="checkbox" class="check" ${role.permissions.includes(`${mod}:${a}`) ? "checked" : ""} ${can("role:attribuer") ? "" : "disabled"} data-act="perm" data-v="${mod}:${a}"></td>` : `<td class="muted">—</td>`).join("")}</tr>`).join("")}
        </tbody></table></div></div>`; }).join("");
    return entete(t("usr.titre"), t("usr.sousTitre")) + onglets + `
      <div class="grid" style="grid-template-columns:260px minmax(0,1fr);align-items:start">
        <div class="card"><div class="card-head"><h2>${t("usr.roles")}</h2>${can("role:ajouter") ? `<button class="btn text icon sm" title="${t("c.ajouter")}"><i class="pi pi-plus"></i></button>` : ""}</div>
          <div class="menu" style="padding:8px">${D.roles.map(r => `<div class="menu-item ${r.id === role.id ? "active" : ""}" data-act="role-sel" data-v="${r.id}"><i class="pi ${r.systeme ? "pi-lock" : "pi-users"}"></i><span class="grow">${esc(r.nom)}</span>${r.systeme ? `<span class="tag secondary">${t("usr.systeme")}</span>` : ""}</div>`).join("")}</div></div>
        <div class="card"><div class="card-head"><div><h2>${esc(role.nom)}</h2><div class="small muted">${role.permissions === "*" ? t("usr.toutes") : t("usr.nbPermissions", { n: role.permissions.length })}</div></div>
          ${role.permissions !== "*" && can("role:attribuer") ? `<button class="btn" data-act="toast-ok" data-v="usr.permissionsOk"><i class="pi pi-save"></i>${t("c.enregistrer")}</button>` : ""}</div>
          <div class="card-body">${matrice}</div></div>
      </div>`;
  }

  /* ---------------- Profil ---------------- */
  function ecranProfil() {
    const u = utilisateurCourant();
    return entete(t("nav.profil"), t("prof.sousTitre")) + `
      <div class="grid grid-2" style="align-items:start">
        <div class="card card-body stack">
          <div class="row" style="gap:16px"><span class="avatar lg">${esc(initiales(u.prenom, u.nom))}</span><div><h2>${esc(u.prenom)} ${esc(u.nom)}</h2><div class="muted mono">${esc(u.username)}</div><div class="row" style="margin-top:8px">${u.roles.map(r => tag("", byId(D.roles, r).nom)).join("")}</div></div></div>
          <div class="field"><label>${t("c.langue")}</label><div class="segmented"><button class="${S.lang === "fr" ? "on" : ""}" data-act="lang" data-v="fr">Français</button><button class="${S.lang === "en" ? "on" : ""}" data-act="lang" data-v="en">English</button></div></div>
          <div class="field"><label>${t("prof.theme")}</label><div class="segmented">${[[null, "prof.systeme"], ["light", "prof.clair"], ["dark", "prof.sombre"]].map(([v, l]) => `<button class="${S.theme === v ? "on" : ""}" data-act="theme-set" data-v="${v || ""}">${t(l)}</button>`).join("")}</div></div>
        </div>
        <form class="card" data-form="password"><div class="card-head"><h2>${t("prof.motDePasse")}</h2></div><div class="card-body stack">
          <div class="field"><label>${t("prof.ancien")} *</label><input class="input" type="password" id="pw-old" autocomplete="current-password"></div>
          <div class="field"><label>${t("prof.nouveau")} *</label><input class="input" type="password" id="pw-new" autocomplete="new-password"><span class="hint">${t("prof.regle")}</span></div>
          <div class="field"><label>${t("prof.confirmation")} *</label><input class="input" type="password" id="pw-conf" autocomplete="new-password"></div>
          <div id="pw-msg"></div>
        </div><div class="dialog-foot"><button class="btn" type="submit"><i class="pi pi-lock"></i>${t("prof.changer")}</button></div></form>
      </div>`;
  }

  /* =======================================================================
     ROUTEUR ET ÉVÉNEMENTS
     ======================================================================= */
  const ECRANS = {
    dashboard: ecranDashboard, eleves: ecranEleves, inscription: ecranInscription, enseignants: ecranEnseignants,
    "emploi-du-temps": ecranEmploiDuTemps, presences: ecranPresences, salaires: ecranSalaires, evaluations: ecranEvaluations, notes: ecranNotes,
    discipline: ecranDiscipline, bulletins: ecranBulletins, scolarite: ecranScolarite, administration: ecranAdministration,
    utilisateurs: ecranUtilisateurs, profil: ecranProfil,
  };
  function routeCourante() {
    const [route, param] = (location.hash.replace(/^#\/?/, "") || "dashboard").split("/");
    return { route, param };
  }
  function render() {
    appliquerPreferences();
    const app = document.getElementById("app");
    const { route, param } = routeCourante();
    if (!S.connecte || route === "login") { app.innerHTML = ecranConnexion(); return; }
    const item = tousItems().find(i => i.r === route);
    let contenu;
    if (!ECRANS[route]) contenu = ecranDashboard();
    else if (item && !can(item.p)) contenu = entete(t(item.l)) + accesRefuse();
    else if (route === "eleves" && param) contenu = ecranFicheEleve(param);
    else contenu = ECRANS[route]();
    app.innerHTML = layout(route, contenu);
    ameliorerSelects(app);
  }
  const aller = r => { S.menuOuvert = false; S.popup = false; if (location.hash === "#/" + r) render(); else location.hash = "#/" + r; };

  function setFiltre(chemin, valeur) {
    const [a, b] = chemin.split(".");
    const cible = a === "insc" ? S.insc : a === "hist" ? S.hist : a === "ens" ? S.ens : a === "sal" ? S.sal : a === "vers" ? S.vers : a === "mp" ? S.mp : S.f[a];
    cible[b] = isNaN(valeur) || valeur === "" ? valeur : Number(valeur);
  }

  const ACTIONS = {
    lang: v => { S.lang = v; store.set("lang", v); render(); },
    theme: () => { S.theme = sombre() ? "light" : "dark"; store.set("theme", S.theme); render(); },
    "theme-set": v => { S.theme = v || null; store.set("theme", S.theme); render(); },
    "fermer-menu": () => { S.menuOuvert = false; render(); },
    // Petit écran : ouvre / ferme le menu par-dessus le contenu ; grand écran : masque / réaffiche la barre latérale
    menu: () => {
      if (window.matchMedia("(max-width: 900px)").matches) S.menuOuvert = !S.menuOuvert;
      else { S.menuReplie = !S.menuReplie; store.set("menuReplie", S.menuReplie); }
      render();
    },
    popup: () => { S.popup = !S.popup; render(); },
    role: v => { S.role = Number(v); store.set("role", S.role); S.popup = false; render(); toast("info", t("demo.roleChange"), byId(D.roles, v).nom); },
    deconnexion: () => { S.connecte = false; store.set("connecte", false); S.popup = false; location.hash = "#/login"; render(); },
    fermer: () => fermer(),
    "fermer-overlay": (v, el, ev) => { if (ev.target === el) fermer(); },
    "toast-ok": v => { fermer(); toast("success", t("c.succes"), t(v)); },
    "insc-type": v => { S.insc.type = v; render(); },
    "insc-suiv": () => { S.insc.etape++; render(); },
    "insc-prec": () => { S.insc.etape = Math.max(1, S.insc.etape - 1); render(); },
    "insc-redoublant": () => { S.insc.redoublant = !S.insc.redoublant; render(); },
    "insc-valider": () => {
      const info = { nom: "TAMBA", prenom: "Eliane", genre: "F", naissance: "2011-04-18", lieu: "Douala", matricule: "26F0013" };
      const ins = { id: Date.now(), eleveInfo: info, classe: Number(S.insc.classe), date: AUJOURDHUI, type: "nouveau", redoublant: S.insc.redoublant,
        user: utilisateurCourant().username, numero: prochainNumeroRecu(), derniereModif: null };
      D.inscriptions.push(ins);
      S.insc.etape = 1; render();
      toast("success", t("insc.succes"), t("insc.succesTexte", { m: info.matricule }));
      recuInscription({ ...info, classe: classe(ins.classe).libelle, montant: montantInscription(ins.classe), type: ins.type, redoublant: ins.redoublant, numero: ins.numero, date: ins.date });
    },
    "inscrire-ancien": v => {
      const a = byId(D.anciensEleves, v);
      const idClasse = S.choixClasse[a.id] || D.classes.find(c => c.niveau === a.niveau).id;
      D.anciensEleves = D.anciensEleves.filter(x => x.id !== a.id);
      const ins = { id: Date.now(), eleveInfo: { nom: a.nom, prenom: a.prenom, genre: a.genre, naissance: a.naissance, lieu: a.lieu, matricule: a.matricule },
        classe: idClasse, date: AUJOURDHUI, type: "reinscription", redoublant: a.decision === "Redouble",
        user: utilisateurCourant().username, numero: prochainNumeroRecu(), derniereModif: null };
      D.inscriptions.push(ins);
      render();
      toast("success", t("insc.succes"), `${a.nom} ${a.prenom} · ${classe(idClasse).libelle}`);
      recuInscription({ ...ins.eleveInfo, classe: classe(idClasse).libelle, montant: montantInscription(idClasse), type: ins.type, redoublant: ins.redoublant, numero: ins.numero, date: ins.date });
    },
    "recu-eleve": v => { const ins = D.inscriptions.find(x => x.eleve === Number(v)); ACTIONS["recu-inscription"](ins.id); },
    "recu-inscription": v => {
      const ins = byId(D.inscriptions, v), e = infoEleveInscription(ins);
      recuInscription({ ...e, classe: classe(ins.classe).libelle, montant: montantInscription(ins.classe), type: ins.type, redoublant: ins.redoublant, numero: ins.numero, date: ins.date, user: ins.user, duplicata: true });
    },
    "page-hist": v => { S.hist.page = Number(v); render(); },
    "effacer-hist": () => { Object.assign(S.hist, { du: "", au: "", q: "", applique: { du: "", au: "", q: "" }, page: 1 }); render(); },
    "modifier-insc": v => { const ins = byId(D.inscriptions, v); S.editInsc = { id: ins.id, niveau: classe(ins.classe).niveau, classe: ins.classe, redoublant: ins.redoublant }; dialogModifierInscription(); },
    "enregistrer-insc": () => enregistrerModificationInscription(),
    imprimer: () => window.print(),
    afficher: v => {
      if (v === "eleves") Object.assign(S.f.eleves, { q: "", qApplique: "", genre: "", page: 1 });
      S.affiche[v] = cleEcran(v);
      render();
    },
    "page-eleves": v => { S.f.eleves.page = Number(v); render(); },
    "effacer-filtre-classe": () => { Object.assign(S.f.eleves, { q: "", qApplique: "", genre: "", page: 1 }); render(); },
    "effacer-ecole": () => { S.qEcole = ""; S.rechercheEcole = null; render(); },
    appel: v => { const [id, k] = v.split("|"); S.appel[id] = k; render(); },
    "tous-presents": () => { S.appel = {}; render(); },
    "pe-statut": v => { const [idx, k] = v.split("|"); S.pe.saisie[idx] = k; render(); },
    "pe-tous-presents": () => {
      lignesPresenceEns().forEach(l => { if (!(l.saisi && !can("presence_enseignant:modifier"))) S.pe.saisie[l.idx] = "P"; });
      render();
    },
    // Simule POST /presence-enseignant/jour : toutes les lignes affichées (présent par défaut)
    "pe-enregistrer": () => {
      const A = S.pe.applique;
      let n = 0;
      lignesPresenceEns().forEach(({ idx }) => {
        const cle = clePresence(A.date, idx), avant = D.presencesEnseignants[cle], apres = S.pe.saisie[idx] || avant || "P";
        if (avant && avant !== apres && !can("presence_enseignant:modifier")) return;
        if (avant !== apres) { D.presencesEnseignants[cle] = apres; n++; }
      });
      S.pe.saisie = {};
      render();
      toast("success", t("pres.enregistreEns"), t("pres.enregistreEnsTexte", { n }));
    },
    "enregistrer-appel": () => toast("success", t("pres.enregistre"), t("pres.enregistreTexte")),
    dependances: v => dialogDependances(v),
    "supprimer-evaluation": v => confirmation(t("eval.confirmerSuppression", { e: evaluation(v).libelle }), depsDe(v).length && S.calcule[v] ? "eval.suppressionImpossible" : null),
    "calculer-notes": () => { S.calcule[S.f.notes.evaluation] = true; render(); toast("success", t("notes.calculOk"), t("notes.calculOkTexte")); },
    "enregistrer-notes": () => {
      const p = parentDe(S.f.notes.evaluation);
      toast("success", t("notes.enregistreOk"), p && S.calcule[p.parent] ? t("notes.parentRecalcule", { p: evaluation(p.parent).libelle }) : t("notes.enregistreOkTexte"));
    },
    "calculer-discipline": () => toast("success", t("disc.calculOk"), t("disc.calculOkTexte")),
    "bul-langue": v => { S.f.bulletin.langue = v; render(); },
    "bul-type": v => { S.f.bulletin.type = v; S.f.bulletin.periode = 1; render(); },
    "apercu-bulletin": v => apercuBulletin(v),
    "pdf-bulletins": () => { fermer(); toast("info", t("bul.pdfLance"), t("bul.pdfLanceTexte")); },
    "regl-statut": v => { S.f.regl.statut = v; render(); },
    "nouveau-reglement": v => dialogNouveauReglement(v),
    "valider-reglement": v => {
      const s = situationTranche(Number(v), S.f.regl.tranche);
      D.reglements.push({ id: Date.now(), eleve: Number(v), tranche: S.f.regl.tranche, montant: s.reste, type: s.regle ? "partiel" : "total", statut: "valide", date: AUJOURDHUI, user: utilisateurCourant().username });
      fermer(); render(); toast("success", t("sco.reglementOk"), fcfa(s.reste));
    },
    historique: v => dialogHistorique(v),
    "annuler-reglement": v => { const r = D.reglements.find(x => x.id === Number(v)); r.statut = "annule"; dialogHistorique(r.eleve); render(); dialogHistorique(r.eleve); toast("warn", t("sco.annuleOk"), fcfa(r.montant)); },
    "bareme-sel": v => { S.f.baremeSel = Number(v); render(); },
    "toggle-appel": () => { D.configuration.isAppel = !D.configuration.isAppel; toast("success", t("adm.configOk"), t(D.configuration.isAppel ? "adm.appelActive" : "adm.appelDesactive")); },
    cloturer: () => confirmation(t("adm.confirmerCloture"), null),
    "role-sel": v => { S.f.roleSel = Number(v); render(); },
    perm: () => {},
    desactiver: v => { const u = byId(D.utilisateurs, v); confirmation(t("usr.confirmerDesactivation", { u: u.username }), null, () => { u.actif = false; render(); toast("success", t("usr.desactiveOk"), u.username); }); },
    "confirmer-suppression": () => confirmation(t("c.confirmerSuppression"), null),
    "modifier-eleve": v => dialogModifierEleve(v),
    "ajouter-enseignant": () => dialogEnseignant(null),
    "modifier-ens": v => dialogEnseignant(Number(v)),
    "matieres-ens": v => { S.matiereAAjouter = ""; dialogMatieresEnseignant(Number(v)); },
    "ajouter-matiere": v => {
      const x = byId(D.enseignants, v), m = S.matiereAAjouter;
      x.matieres.push(m); S.matiereAAjouter = "";
      render(); dialogMatieresEnseignant(x.id);
      toast("success", t("ens.matiereAjoutee"), `${m} · ${x.nom}`);
    },
    "retirer-matiere": v => {
      const [id, m] = v.split("|"), x = byId(D.enseignants, id);
      x.matieres = x.matieres.filter(y => y !== m);
      render(); dialogMatieresEnseignant(x.id);
      toast("warn", t("ens.matiereRetiree"), `${m} · ${x.nom}`);
    },
    "sal-statut": v => { S.sal.statut = v; S.sal.page = 1; render(); },
    "page-sal": v => { S.sal.page = Number(v); render(); },
    "page-vers": v => { S.vers.page = Number(v); render(); },
    "page-mp": v => { S.mp.page = Number(v); render(); },
    "mp-config": v => { S.mp.config = v; S.mp.page = 1; render(); },
    "effacer-mp": () => { Object.assign(S.mp, { q: "", matiere: "", applique: { q: "", matiere: "" }, page: 1 }); render(); },
    "configurer-mp": v => dialogMoyenPaiement(Number(v)),
    "copier-compte": v => { try { navigator.clipboard.writeText(v); } catch (e) { /* aperçu sans presse-papiers */ } toast("success", t("ens.compteCopie"), v); },
    "effacer-vers": () => { Object.assign(S.vers, { periode: "", q: "", matiere: "", applique: { periode: "", q: "", matiere: "" }, page: 1 }); render(); },
    "annuler-versement-liste": v => {
      const x = D.versementsSalaire.find(y => y.id === Number(v));
      x.statut = "annule";
      render();
      toast("warn", t("sal.versementAnnule"), `${byId(D.enseignants, x.ens).nom} · ${fcfa(x.montant)}`);
    },
    "verser-salaire": v => dialogVerserSalaire(Number(v)),
    "detail-salaire": v => dialogDetailSalaire(Number(v)),
    "annuler-versement": v => {
      const x = D.versementsSalaire.find(y => y.id === Number(v));
      x.statut = "annule";
      render(); dialogDetailSalaire(x.ens);
      toast("warn", t("sal.versementAnnule"), fcfa(x.montant));
    },
    "toggle-absences-payees": () => { D.configuration.isAbsenceJustifieePayee = !D.configuration.isAbsenceJustifieePayee; toast("success", t("adm.configOk"), t(D.configuration.isAbsenceJustifieePayee ? "sal.regleAvecJustifiees" : "sal.regleSansJustifiees")); },
    "page-ens": v => { S.ens.page = Number(v); render(); },
    "effacer-ens": () => { Object.assign(S.ens, { q: "", matiere: "", applique: { q: "", matiere: "" }, page: 1 }); render(); },
    // v (optionnel, démonstration) : matière présélectionnée
    "ajouter-cours": v => {
      const profs = enseignantsMatiere(v);
      S.nc = { classe: S.sel.classe || "", matiere: v || "", enseignant: profs.length === 1 ? String(profs[0].id) : "", jour: 0, debut: "08:00", fin: "10:00" };
      dialogCours();
    },
    "ajouter-evaluation": () => dialogSimple("eval.ajouter", ["c.code", "c.libelle"], null, true),
    "ajouter-utilisateur": () => dialogSimple("usr.ajouter", ["usr.identifiant", "c.nom", "c.prenom", "login.motDePasse"]),
    "confirmer-ok": () => { const cb = S.confirmCb; fermer(); if (cb) cb(); else toast("success", t("c.succes"), t("demo.actionSimulee")); },
  };
  function confirmation(message, erreurCle, callback) {
    S.confirmCb = callback || null;
    dialog(t("c.confirmation"), erreurCle ? `<div class="message danger"><i class="pi pi-times-circle"></i>${t(erreurCle)}</div>` : `<div class="row"><i class="pi pi-exclamation-triangle" style="font-size:22px;color:var(--warn)"></i><span>${esc(message)}</span></div>`,
      erreurCle ? `<button class="btn secondary" data-act="fermer">${t("c.fermer")}</button>` : `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn danger" data-act="confirmer-ok">${t("c.confirmer")}</button>`);
  }
  function dialogSimple(titre, champs, salaire, periode) {
    dialog(t(titre), `<div class="form-grid">${champs.map(c => `<div class="field"><label>${t(c)} *</label><input class="input" ${c === "login.motDePasse" ? 'type="password"' : ""}></div>`).join("")}
      ${salaire ? `<div class="field"><label>${t(salaire)}</label><select class="select">${option("1", t("ens.mensuel"))}${option("2", t("ens.horaire"))}</select></div>` : ""}
      ${periode ? `<div class="field"><label>${t("c.trimestre")}</label><select class="select">${D.trimestres.map(x => option(x.id, x.libelle)).join("")}</select></div><div class="field"><label>${t("eval.debut")}</label><input class="input" type="date"></div><div class="field"><label>${t("eval.fin")}</label><input class="input" type="date"></div>` : ""}
      ${titre === "usr.ajouter" ? `<div class="field full"><label>${t("usr.roles")}</label><div class="row">${D.roles.filter(r => r.id !== 1 || S.role === 1).map(r => `<label class="row" style="gap:6px"><input type="checkbox" class="check">${esc(r.nom)}</label>`).join("")}</div></div>` : ""}
    </div>`, `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" data-act="toast-ok" data-v="demo.actionSimulee"><i class="pi pi-check"></i>${t("c.enregistrer")}</button>`);
  }
  // POST /cours/add?id_enseignant=&id_classe=&id_matiere= : enseignant actif qui enseigne la matière, sans conflit de créneau
  const JOURS_COURS = ["c.lundi", "c.mardi", "c.mercredi", "c.jeudi", "c.vendredi"];
  const enseignantsMatiere = idMatiere => !idMatiere ? [] : D.enseignants
    .filter(e => e.actif && e.matieres.includes(matiere(Number(idMatiere)).libelle))
    .sort((a, b) => `${a.nom} ${a.prenom}`.localeCompare(`${b.nom} ${b.prenom}`));
  function dialogCours() {
    const N = S.nc, profs = enseignantsMatiere(N.matiere);
    const champEnseignant = !N.matiere
      ? `<select class="select" disabled>${option("", t("edt.choisirMatiere"), "")}</select>`
      : profs.length
        ? `<select class="select" id="nc-enseignant" data-nc="enseignant" required>${profs.length > 1 ? option("", t("c.choisir"), N.enseignant) : ""}${profs.map(e => option(e.id, `${e.nom} ${e.prenom || ""}`, N.enseignant)).join("")}</select><span class="hint">${t("edt.enseignantsMatiere")}</span>`
        : `<div class="message warn small"><i class="pi pi-exclamation-triangle"></i>${t("edt.aucunEnseignant")}</div>`;
    dialog(t("edt.ajouter"), `<form id="form-cours" data-form="cours"><div class="stack"><div class="form-grid">
      <div class="field"><label>${t("c.classe")} *</label><select class="select" id="nc-classe" data-nc="classe" required>${option("", t("c.choisir"), N.classe)}${D.classes.map(c => option(c.id, c.libelle, N.classe)).join("")}</select></div>
      <div class="field"><label>${t("c.matiere")} *</label><select class="select" id="nc-matiere" data-nc="matiere" required>${option("", t("c.choisir"), N.matiere)}${D.matieres.map(m => option(m.id, m.libelle, N.matiere)).join("")}</select></div>
      <div class="field full"><label>${t("ens.enseignant")} *</label>${champEnseignant}</div>
      <div class="field"><label>${t("edt.jour")} *</label><select class="select" id="nc-jour" data-nc="jour">${JOURS_COURS.map((j, i) => option(i, t(j), N.jour)).join("")}</select></div>
      <div class="field"></div>
      <div class="field"><label for="nc-debut">${t("edt.debut")} *</label><input class="input" type="time" id="nc-debut" data-nc="debut" value="${N.debut}" required></div>
      <div class="field"><label for="nc-fin">${t("edt.fin")} *</label><input class="input" type="time" id="nc-fin" data-nc="fin" value="${N.fin}" required></div>
      </div><div id="nc-erreur"></div></div></form>`,
      `<button class="btn secondary" data-act="fermer">${t("c.annuler")}</button><button class="btn" type="submit" form="form-cours" ${N.matiere && !profs.length ? "disabled" : ""}><i class="pi pi-check"></i>${t("c.enregistrer")}</button>`);
  }
  function enregistrerCours() {
    const N = S.nc;
    ["classe", "matiere", "jour", "debut", "fin"].forEach(k => { N[k] = document.getElementById(`nc-${k}`).value; });
    N.enseignant = document.getElementById("nc-enseignant")?.value || "";
    const [cl, m, e, j] = [Number(N.classe), Number(N.matiere), Number(N.enseignant), Number(N.jour)];
    const chevauche = c => c[0] === j && N.debut < c[2] && N.fin > c[1];
    const conflitClasse = D.cours.find(c => c[5] === cl && chevauche(c)), conflitEnseignant = D.cours.find(c => c[4] === e && chevauche(c));
    const creneau = c => ({ j: t(JOURS_COURS[c[0]]).toLowerCase(), d: c[1], f: c[2] });
    const erreur = !cl || !m || !e || !N.debut || !N.fin ? t("edt.errChamps")
      : N.fin <= N.debut ? t("edt.errHeures")
      : conflitClasse ? t("edt.errConflitClasse", { m: matiere(conflitClasse[3]).libelle, ...creneau(conflitClasse) })
      : conflitEnseignant ? t("edt.errConflitEnseignant", { e: byId(D.enseignants, e).nom, c: classe(conflitEnseignant[5]).libelle, ...creneau(conflitEnseignant) })
      : null;
    if (erreur) {
      document.getElementById("nc-erreur").innerHTML = `<div class="message danger"><i class="pi pi-times-circle"></i><div class="small"><b>${t("edt.conflit")}</b><div>${erreur}</div></div></div>`;
      return;
    }
    D.cours.push([j, N.debut, N.fin, m, e, cl]);
    fermer(); render();
    toast("success", t("edt.coursAjoute"), `${classe(cl).libelle} · ${matiere(m).libelle} · ${t(JOURS_COURS[j])} ${N.debut} – ${N.fin}`);
  }

  document.addEventListener("click", ev => {
    if (ev.target.closest(".ss-panel")) return;
    const boutonListe = ev.target.closest(".ss-btn");
    if (boutonListe) {
      if (selectOuvert === boutonListe.parentNode) fermerSelect(); else ouvrirSelect(boutonListe.parentNode);
      return;
    }
    fermerSelect();
    const go = ev.target.closest("[data-go]");
    if (go && !ev.target.closest("[data-act]:not([data-go])")) { ev.preventDefault(); aller(go.dataset.go); return; }
    const tabEl = ev.target.closest("[data-tab]");
    if (tabEl) { S.tab[tabEl.dataset.tab] = tabEl.dataset.v; render(); return; }
    const el = ev.target.closest("[data-act]");
    if (el && ACTIONS[el.dataset.act]) {
      if (el.tagName === "BUTTON" && el.disabled) return;
      ACTIONS[el.dataset.act](el.dataset.v, el, ev);
      return;
    }
    if (S.popup && !ev.target.closest(".popup")) { S.popup = false; render(); }
  });
  document.addEventListener("change", ev => {
    const el = ev.target;
    if (el.dataset.nc) {
      S.nc[el.dataset.nc] = el.value;
      if (el.dataset.nc === "matiere") {
        const profs = enseignantsMatiere(el.value);
        ["debut", "fin"].forEach(k => { S.nc[k] = document.getElementById(`nc-${k}`).value; });
        S.nc.enseignant = profs.length === 1 ? String(profs[0].id) : "";
        dialogCours();
      }
      return;
    }
    if (el.id === "mp-moyen") {
      const compte = avecCompte(el.value);
      document.querySelectorAll("[data-compte]").forEach(f => { f.style.display = compte ? "" : "none"; });
      document.getElementById("mp-numero").required = compte;
      document.getElementById("mp-hint").textContent = t(el.value === "MOBILE" ? "ens.numeroMobileHint" : "ens.numeroBancaireHint");
      return;
    }
    if (el.dataset.f) {
      setFiltre(el.dataset.f, el.value);
      if (el.dataset.f === "eleves.genre" || el.dataset.f === "eleves.pageSize") S.f.eleves.page = 1;
      if (el.dataset.f === "hist.pageSize") S.hist.page = 1;
      if (el.dataset.f === "ens.pageSize") S.ens.page = 1;
      if (el.dataset.f === "sal.pageSize") S.sal.page = 1;
      if (el.dataset.f === "vers.pageSize") S.vers.page = 1;
      if (el.dataset.f === "mp.pageSize") S.mp.page = 1;
      if (el.dataset.f === "insc.niveau") {
        const classesNiveau = D.classes.filter(c => c.niveau === Number(S.insc.niveau));
        S.insc.classe = classesNiveau.length === 1 ? classesNiveau[0].id : "";
      }
      render();
      return;
    }
    if (el.dataset.cascade) {
      const k = el.dataset.cascade;
      // Présence des enseignants : garder la date et le nom saisis lors du rafraîchissement
      if (document.getElementById("pe-date")) { S.pe.date = document.getElementById("pe-date").value; S.pe.q = document.getElementById("pe-q").value; }
      S.sel[k] = el.value ? Number(el.value) : "";
      NIVEAUX_CASCADE.slice(NIVEAUX_CASCADE.indexOf(k) + 1).forEach(x => { S.sel[x] = ""; });
      preselectionAutomatique();
      store.set("selection", S.sel);
      render();
      return;
    }
    if (el.hasAttribute("data-matiere-ens")) {
      S.matiereAAjouter = el.value;
      const bouton = document.querySelector('[data-act="ajouter-matiere"]');
      if (bouton) bouton.disabled = !el.value;
      return;
    }
    if (el.dataset.editInsc) {
      const k = el.dataset.editInsc, E = S.editInsc;
      if (k === "redoublant") E.redoublant = el.checked;
      else if (k === "niveau") { E.niveau = Number(el.value); const cl = D.classes.filter(c => c.niveau === E.niveau); E.classe = cl.length === 1 ? cl[0].id : ""; }
      else E.classe = el.value ? Number(el.value) : "";
      dialogModifierInscription();
      return;
    }
    if (el.dataset.choix) { S.choixClasse[el.dataset.choix] = Number(el.value); return; }
    if (el.dataset.regle) { const [i, k] = el.dataset.regle.split("|"); S.f.bulletin.regles[i][k] = k === "decision" ? el.value : Number(el.value.replace(",", ".")); render(); return; }
    if (el.dataset.note) {
      const [idEval, idMat, idEl] = el.dataset.note.split("|").map(Number);
      const brut = el.value.trim().replace(",", ".");
      const max = bareme(matiere(idMat).bareme).valeurMax;
      if (brut === "") { delete D.notes[idEval][idMat][idEl]; render(); return; }
      const v = Number(brut);
      if (isNaN(v) || v < 0 || v > max) { el.classList.add("invalid"); toast("danger", t("notes.horsBareme"), t("notes.horsBaremeTexte", { max })); return; }
      D.notes[idEval][idMat][idEl] = Math.round(v * 100) / 100;
      render();
    }
  });
  document.addEventListener("input", ev => {
    if (ev.target.dataset.live === "ecole-q") { S.qEcole = ev.target.value; document.getElementById("btn-ecole").disabled = S.qEcole.trim().length < 3; }
  });
  document.addEventListener("submit", ev => {
    const form = ev.target.closest("[data-form]");
    if (!form) return;
    ev.preventDefault();
    if (form.dataset.form === "filtre-hist") {
      const du = document.getElementById("hist-du").value, au = document.getElementById("hist-au").value, q = document.getElementById("hist-q").value;
      if (du && au && du > au) { document.getElementById("hist-erreur").innerHTML = `<div class="message danger small"><i class="pi pi-times-circle"></i>${t("hist.errDates")}</div>`; return; }
      Object.assign(S.hist, { du, au, q, applique: { du, au, q }, page: 1 });
      render();
      return;
    }
    if (form.dataset.form === "eleve-edit") { enregistrerEleve(form); return; }
    if (form.dataset.form === "ens-edit") { enregistrerEnseignant(form); return; }
    if (form.dataset.form === "filtre-sal") {
      const periode = document.getElementById("sal-periode").value, q = document.getElementById("sal-q").value, matiere = document.getElementById("sal-matiere").value;
      Object.assign(S.sal, { periode, q, matiere, applique: { periode, q, matiere }, page: 1 });
      render();
      return;
    }
    if (form.dataset.form === "cours") { enregistrerCours(); return; }
    if (form.dataset.form === "filtre-pe") {
      const date = document.getElementById("pe-date").value, q = document.getElementById("pe-q").value;
      if (!date || date > AUJOURDHUI) return;
      // Seule la classe filtre (section, cycle et niveau servent à remplir la liste des classes) ; vide = toutes les classes
      Object.assign(S.pe, { date, q, applique: { date, q, classe: S.sel.classe || "" }, saisie: {} });
      render();
      return;
    }
    if (form.dataset.form === "filtre-mp") {
      const q = document.getElementById("mp-q").value, matiere = document.getElementById("mp-matiere").value;
      Object.assign(S.mp, { q, matiere, applique: { q, matiere }, page: 1 });
      render();
      return;
    }
    if (form.dataset.form === "moyen-paiement") {
      const e = byId(D.enseignants, form.dataset.id);
      const moyen = document.getElementById("mp-moyen").value;
      const numero = document.getElementById("mp-numero").value.trim(), intitule = document.getElementById("mp-intitule").value.trim();
      const erreur = !moyen ? t("sal.errMoyen") : avecCompte(moyen) && !numero ? t("sal.errNumero") : null;
      if (erreur) {
        document.getElementById("mp-erreur").innerHTML = `<div class="message danger small"><i class="pi pi-times-circle"></i>${erreur}</div>`;
        return;
      }
      // Comme le backend : en espèces, le numéro et l'intitulé du compte sont effacés
      Object.assign(e, { moyenPaiement: moyen, numeroCompte: avecCompte(moyen) ? numero : "", intituleCompte: avecCompte(moyen) ? intitule : "" });
      fermer(); render();
      toast("success", t("sal.moyenOk"), `${e.nom} ${e.prenom || ""} · ${t(MOYENS_PAIEMENT.find(m => m[0] === moyen)[1])}`);
      return;
    }
    if (form.dataset.form === "filtre-vers") {
      const periode = document.getElementById("vers-periode").value, q = document.getElementById("vers-q").value, matiere = document.getElementById("vers-matiere").value;
      Object.assign(S.vers, { periode, q, matiere, applique: { periode, q, matiere }, page: 1 });
      render();
      return;
    }
    if (form.dataset.form === "verser-salaire") {
      const s = situationSalaire(byId(D.enseignants, form.dataset.id), (S.sal.applique || S.sal).periode);
      const montant = Number(document.getElementById("sal-montant").value);
      const dateVersement = document.getElementById("sal-date").value;
      const erreur = !(montant > 0) || montant > s.reste ? t("sal.errMontant", { r: fcfa(s.reste) })
        : !dateVersement || dateVersement > AUJOURDHUI ? t("sal.errDate") : null;
      if (erreur) {
        document.getElementById("sal-erreur").innerHTML = `<div class="message danger small"><i class="pi pi-times-circle"></i>${erreur}</div>`;
        return;
      }
      D.versementsSalaire.push({ id: Date.now(), ens: s.e.id, mois: s.mois, annee: s.annee, montant, date: dateVersement, statut: "valide", user: utilisateurCourant().username });
      fermer(); render();
      toast("success", t("sal.versementOk"), `${s.e.nom} · ${fcfa(montant)}${montant < s.reste ? ` · ${t("sal.resteApres", { r: fcfa(s.reste - montant) })}` : ""}`);
      return;
    }
    if (form.dataset.form === "filtre-ens") {
      const q = document.getElementById("ens-q").value, matiere = document.getElementById("ens-matiere").value;
      Object.assign(S.ens, { q, matiere, applique: { q, matiere }, page: 1 });
      render();
      return;
    }
    if (form.dataset.form === "filtre-classe") {
      S.f.eleves.q = document.getElementById("q-classe").value;
      S.f.eleves.qApplique = S.f.eleves.q;
      S.f.eleves.page = 1;
      render();
      return;
    }
    if (form.dataset.form === "recherche-ecole") {
      if (S.qEcole.trim().length >= 3) { S.rechercheEcole = S.qEcole.trim(); render(); }
      return;
    }
    if (form.dataset.form === "login") { S.connecte = true; store.set("connecte", true); location.hash = "#/dashboard"; render(); toast("success", t("login.bienvenue"), t("login.bienvenueTexte")); }
    if (form.dataset.form === "password") {
      const old = document.getElementById("pw-old").value, nouv = document.getElementById("pw-new").value, conf = document.getElementById("pw-conf").value;
      const msg = document.getElementById("pw-msg");
      let erreur = null;
      if (!old) erreur = "prof.errAncien"; else if (nouv.length < 6) erreur = "prof.errLongueur"; else if (nouv === old) erreur = "prof.errIdentique"; else if (nouv !== conf) erreur = "prof.errConfirmation";
      msg.innerHTML = erreur ? `<div class="message danger"><i class="pi pi-times-circle"></i>${t(erreur)}</div>` : `<div class="message success"><i class="pi pi-check-circle"></i>${t("prof.ok")}</div>`;
    }
  });
  window.addEventListener("hashchange", render);
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (!S.theme) render(); });
  document.addEventListener("keydown", ev => {
    if (ev.key !== "Escape") return;
    if (selectOuvert) fermerSelect();
    else if (document.getElementById("dialog-root").innerHTML) fermer();
    else if (S.menuOuvert) { S.menuOuvert = false; render(); }
  });

  render();
  if (params.get("apercu") && S.connecte) apercuBulletin(Number(params.get("apercu")));
  if (params.get("recu") && S.connecte) ACTIONS["recu-eleve"](params.get("recu"));
  // ?act=modifier-insc:6 : déclenche une action au chargement (démonstration)
  if (params.get("act") && S.connecte) { const [nom, v] = params.get("act").split(":"); if (ACTIONS[nom]) ACTIONS[nom](v); }
  // ?ouvrirListe=2&chercher=sec : ouvre la 3e liste de l'écran et y saisit « sec » (démonstration)
  if (params.has("ouvrirListe")) {
    const wrap = document.querySelectorAll(".ss")[Number(params.get("ouvrirListe"))];
    if (wrap) {
      ouvrirSelect(wrap);
      const champ = document.querySelector(".ss-panel input");
      if (params.get("chercher")) { champ.value = params.get("chercher"); champ.dispatchEvent(new Event("input")); }
    }
  }
})();
