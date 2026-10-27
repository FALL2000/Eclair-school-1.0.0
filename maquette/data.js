/* =========================================================================
   Données fictives de la maquette — reprennent les entités du backend.
   ========================================================================= */
(function () {
  // Générateur pseudo-aléatoire déterministe (mêmes données à chaque ouverture)
  let graine = 42;
  function alea() {
    graine = (graine * 16807) % 2147483647;
    return (graine - 1) / 2147483646;
  }
  const entre = (min, max) => min + alea() * (max - min);
  const quart = v => Math.round(v * 4) / 4;

  // Établissement (simulé) : en développement, ces informations viendront de la table de configuration de l'école
  const ecole = {
    nom: "Complexe Scolaire Bilingue La Réussite", sigle: "CSB La Réussite", ville: "Yaoundé",
    adresse: "B.P. 1234 Yaoundé · Mvog-Mbi", telephone: "+237 6 99 00 11 22", email: "contact@lareussite.cm",
    devise: "Travail · Discipline · Réussite",
    logo: '<svg viewBox="0 0 64 72" aria-hidden="true"><path d="M32 2 60 10v24c0 18-12 30-28 36C16 64 4 52 4 34V10z" fill="#7f1d1d"/><path d="M32 7 55 13.5V34c0 15-10 25-23 30.5C19 59 9 49 9 34V13.5z" fill="none" stroke="#e0b341" stroke-width="2"/><path d="m32 14 2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z" fill="#e0b341"/><path d="M15 36c5.5-2.4 11-2.4 16 .6V55c-5-3-10.5-3-16-.6z" fill="#fff"/><path d="M49 36c-5.5-2.4-11-2.4-16 .6V55c5-3 10.5-3 16-.6z" fill="#f5e6c4"/></svg>',
    annee: "2026-2027", typeSchool: "secondaire",
  };

  const sections = [
    { id: 1, code: "FRANCO", libelle: "FRANCOPHONE" },
    { id: 2, code: "ANGLO", libelle: "ANGLOPHONE" },
  ];
  const cycles = [
    { id: 1, code: "FRANCO-1", libelle: "PREMIER CYCLE", section: 1 },
    { id: 3, code: "FRANCO-2", libelle: "SECOND CYCLE", section: 1 },
    { id: 2, code: "ANGLO-1", libelle: "FIRST CYCLE", section: 2 },
  ];
  // montantInscription : montant de l'inscription du niveau (niveau.montant_inscription)
  const niveaux = [
    { id: 1, code: "6E", libelle: "Sixième", cycle: 1, montantInscription: 10000 },
    { id: 2, code: "5E", libelle: "Cinquième", cycle: 1, montantInscription: 10000 },
    { id: 3, code: "4E", libelle: "Quatrième", cycle: 1, montantInscription: 10000 },
    { id: 4, code: "3E", libelle: "Troisième", cycle: 1, montantInscription: 12500 },
    { id: 5, code: "2NDE", libelle: "Seconde", cycle: 3, montantInscription: 15000 },
    { id: 6, code: "1ERE", libelle: "Première", cycle: 3, montantInscription: 15000 },
    { id: 7, code: "TLE", libelle: "Terminale", cycle: 3, montantInscription: 17500 },
    { id: 8, code: "F1", libelle: "Form 1", cycle: 2, montantInscription: 10000 },
  ];
  const classes = [
    { id: 1, code: "6EA", libelle: "6e A", niveau: 1, effectif: 48 },
    { id: 2, code: "6EB", libelle: "6e B", niveau: 1, effectif: 46 },
    { id: 3, code: "5EA", libelle: "5e A", niveau: 2, effectif: 44 },
    { id: 10, code: "5EB", libelle: "5e B", niveau: 2, effectif: 42 },
    { id: 4, code: "4EA", libelle: "4e A", niveau: 3, effectif: 41 },
    { id: 5, code: "3EA", libelle: "3e A", niveau: 4, effectif: 39 },
    { id: 6, code: "2NDC", libelle: "2nde C", niveau: 5, effectif: 12 },
    { id: 7, code: "1ERED", libelle: "1ère D", niveau: 6, effectif: 37 },
    { id: 8, code: "TLEC", libelle: "Tle C", niveau: 7, effectif: 33 },
    { id: 11, code: "TLED", libelle: "Tle D", niveau: 7, effectif: 36 },
    { id: 12, code: "2NDA", libelle: "2nde A", niveau: 5, effectif: 40 },
    { id: 9, code: "F1A", libelle: "Form 1 A", niveau: 8, effectif: 35 },
  ];

  const baremes = [
    { id: 1, code: "B20", libelle: "Sur 20", valeurMax: 20 },
    { id: 2, code: "B10", libelle: "Sur 10", valeurMax: 10 },
  ];
  const appreciations = [
    { id: 1, bareme: 1, min: 0, max: 4.99, libelle: "Très faible", libelleEn: "Very poor" },
    { id: 2, bareme: 1, min: 5, max: 7.99, libelle: "Faible", libelleEn: "Poor" },
    { id: 3, bareme: 1, min: 8, max: 9.99, libelle: "Insuffisant", libelleEn: "Insufficient" },
    { id: 4, bareme: 1, min: 10, max: 11.99, libelle: "Passable", libelleEn: "Fair" },
    { id: 5, bareme: 1, min: 12, max: 13.99, libelle: "Assez bien", libelleEn: "Fairly good" },
    { id: 6, bareme: 1, min: 14, max: 15.99, libelle: "Bien", libelleEn: "Good" },
    { id: 7, bareme: 1, min: 16, max: 17.99, libelle: "Très bien", libelleEn: "Very good" },
    { id: 8, bareme: 1, min: 18, max: 20, libelle: "Excellent", libelleEn: "Excellent" },
    { id: 9, bareme: 2, min: 0, max: 4.99, libelle: "Non acquis", libelleEn: "Not acquired" },
    { id: 10, bareme: 2, min: 5, max: 7.49, libelle: "En cours d'acquisition", libelleEn: "Being acquired" },
    { id: 11, bareme: 2, min: 7.5, max: 10, libelle: "Acquis", libelleEn: "Acquired" },
  ];

  // Programme du niveau Seconde (classe de démonstration : 2nde C)
  const groupes = [
    { id: 1, code: "LIT", libelle: "Matières littéraires" },
    { id: 2, code: "SCI", libelle: "Matières scientifiques" },
    { id: 3, code: "AUT", libelle: "Autres matières" },
  ];
  const matieres = [
    { id: 1, code: "FRA", libelle: "Français", groupe: 1, coef: 3, bareme: 1, prof: "M. NKOULOU" },
    { id: 2, code: "ANG", libelle: "Anglais", groupe: 1, coef: 2, bareme: 1, prof: "Mme TABI" },
    { id: 3, code: "HG", libelle: "Histoire-Géographie", groupe: 1, coef: 2, bareme: 1, prof: "M. ESSAMA" },
    { id: 4, code: "ECM", libelle: "Éducation civique", groupe: 1, coef: 1, bareme: 1, prof: "M. ESSAMA" },
    { id: 5, code: "MATH", libelle: "Mathématiques", groupe: 2, coef: 5, bareme: 1, prof: "M. FOUDA" },
    { id: 6, code: "PCT", libelle: "Physique-Chimie", groupe: 2, coef: 4, bareme: 1, prof: "Mme NGO BATA" },
    { id: 7, code: "SVT", libelle: "SVT", groupe: 2, coef: 2, bareme: 1, prof: "M. MOUSSA" },
    { id: 8, code: "INFO", libelle: "Informatique", groupe: 2, coef: 2, bareme: 2, prof: "M. KENFACK" },
    { id: 9, code: "EPS", libelle: "EPS", groupe: 3, coef: 1, bareme: 1, prof: "M. ABENA" },
  ];

  const trimestres = [
    { id: 1, code: "TRIM-1", libelle: "Trimestre 1" },
    { id: 2, code: "TRIM-2", libelle: "Trimestre 2" },
    { id: 3, code: "TRIM-3", libelle: "Trimestre 3" },
  ];
  // Séquence 2 est une évaluation « parente » : sa note est calculée à partir de ses dépendances
  const evaluations = [
    { id: 1, code: "SEQ1", libelle: "Séquence 1", trimestre: 1, debut: "2026-09-28", fin: "2026-10-16" },
    { id: 2, code: "SEQ2", libelle: "Séquence 2", trimestre: 1, debut: "2026-10-26", fin: "2026-12-11" },
    { id: 3, code: "DS2", libelle: "Devoir surveillé", trimestre: 1, debut: "2026-10-26", fin: "2026-11-06" },
    { id: 4, code: "CMP2", libelle: "Composition", trimestre: 1, debut: "2026-11-30", fin: "2026-12-11" },
    { id: 5, code: "SEQ3", libelle: "Séquence 3", trimestre: 2, debut: "2027-01-11", fin: "2027-02-05" },
    { id: 6, code: "SEQ4", libelle: "Séquence 4", trimestre: 2, debut: "2027-02-22", fin: "2027-03-19" },
    { id: 7, code: "SEQ5", libelle: "Séquence 5", trimestre: 3, debut: "2027-04-12", fin: "2027-05-07" },
    { id: 8, code: "SEQ6", libelle: "Séquence 6", trimestre: 3, debut: "2027-05-17", fin: "2027-06-04" },
  ];
  const dependances = [
    { id: 1, parent: 2, dependance: 3, pourcentage: 40 },
    { id: 2, parent: 2, dependance: 4, pourcentage: 60 },
  ];

  const decisions = [
    { id: 1, libelle: "Aucune sanction", libelleEn: "No sanction", min: 0, max: 5 },
    { id: 2, libelle: "Avertissement", libelleEn: "Warning", min: 6, max: 10 },
    { id: 3, libelle: "Blâme", libelleEn: "Reprimand", min: 11, max: 20 },
    { id: 4, libelle: "Exclusion temporaire", libelleEn: "Temporary exclusion", min: 21, max: 40 },
    { id: 5, libelle: "Conseil de discipline", libelleEn: "Disciplinary board", min: 41, max: 999 },
  ];

  const nomsEleves = [
    ["NGONO", "Marie Claire", "F"], ["TCHOUAMENI", "Paul", "M"], ["EYENGA", "Grâce", "F"],
    ["FOTSO", "Junior", "M"], ["MBALLA", "Christelle", "F"], ["KAMGA", "Brice", "M"],
    ["ATANGANA", "Lionel", "M"], ["NJOYA", "Aïcha", "F"], ["ESSOMBA", "Ruth", "F"],
    ["BELLO", "Ibrahim", "M"], ["ONANA", "Stéphane", "M"], ["MANGA", "Larissa", "F"],
  ];
  const quartiers = ["Bastos", "Mvog-Ada", "Biyem-Assi", "Essos", "Mimboman", "Nkolbisson", "Emana", "Odza"];
  const villes = ["Yaoundé", "Douala", "Bafoussam", "Ebolowa", "Garoua", "Bertoua"];
  const eleves = nomsEleves.map(([nom, prenom, genre], i) => ({
    id: i + 1,
    matricule: `26${"ABCDEFGHJKLM"[i]}${String(i + 1).padStart(4, "0")}`,
    nom, prenom, genre,
    naissance: `20${10 + (i % 3)}-${String(1 + (i * 5) % 12).padStart(2, "0")}-${String(3 + (i * 7) % 25).padStart(2, "0")}`,
    lieu: villes[i % villes.length],
    pere: `${nom} ${["Jean", "Pierre", "Joseph", "André"][i % 4]}`,
    mere: `${["NANGA", "ABENA", "MENGUE", "BILOA"][i % 4]} ${["Hélène", "Odile", "Esther", "Brigitte"][i % 4]}`,
    quartier: quartiers[i % quartiers.length],
    telephone: `6 9${i % 10} ${String(10 + i * 7).slice(-2)} ${String(30 + i * 3).slice(-2)} ${String(55 + i).slice(-2)}`,
    classe: 6,
    redoublant: i === 6 || i === 10,
    nouveau: i % 3 === 0,
    actif: true,
  }));
  // Niveau de chaque élève (pour des notes cohérentes)
  const niveauEleve = [15.5, 12, 16.5, 10.5, 13, 8.5, 9.5, 14, 11.5, 7.5, 12.5, 13.5];

  // Notes : evaluation -> matiere -> eleve -> note (dans le barème de la matière)
  const notes = {};
  const evaluationsNotees = [1, 3, 4];
  for (const idEval of evaluationsNotees) {
    notes[idEval] = {};
    for (const m of matieres) {
      notes[idEval][m.id] = {};
      const max = baremes.find(b => b.id === m.bareme).valeurMax;
      for (const e of eleves) {
        // Un élève absent à l'évaluation est « non classé » (pas de note)
        if (idEval === 3 && e.id === 9 && m.id === 6) continue;
        const sur20 = Math.min(20, Math.max(2, niveauEleve[e.id - 1] + entre(-3.5, 3.5)));
        notes[idEval][m.id][e.id] = quart(sur20 * max / 20);
      }
    }
  }

  // Présences (appel) : heures d'absence par élève et par évaluation
  const disciplines = {};
  for (const idEval of [1, 2]) {
    disciplines[idEval] = {};
    for (const e of eleves) {
      const nj = Math.floor(alea() * (e.id === 10 ? 14 : 5));
      const j = Math.floor(alea() * 4);
      disciplines[idEval][e.id] = { nonJustifie: nj, justifie: j };
    }
  }

  const tranches = [
    { id: 1, code: "T1-2NDE", libelle: "Première tranche", ordre: 1, montant: 75000, niveau: 5 },
    { id: 2, code: "T2-2NDE", libelle: "Deuxième tranche", ordre: 2, montant: 50000, niveau: 5 },
    { id: 3, code: "T3-2NDE", libelle: "Troisième tranche", ordre: 3, montant: 40000, niveau: 5 },
  ];
  const reglements = [];
  let idReglement = 1;
  const jours = ["2026-09-02", "2026-09-07", "2026-09-15", "2026-10-01", "2026-10-12", "2026-10-20"];
  eleves.forEach((e, i) => {
    // Tranche 1 : la plupart ont tout payé, certains partiellement, deux rien
    if (i === 3 || i === 9) return;
    if (i === 5 || i === 11) {
      reglements.push({ id: idReglement++, eleve: e.id, tranche: 1, montant: 40000, type: "partiel", statut: "valide", date: jours[i % 6], user: "secretaire" });
      return;
    }
    reglements.push({ id: idReglement++, eleve: e.id, tranche: 1, montant: 75000, type: "total", statut: "valide", date: jours[i % 6], user: "comptable" });
    if (i % 4 === 0) reglements.push({ id: idReglement++, eleve: e.id, tranche: 2, montant: 25000, type: "partiel", statut: "valide", date: "2026-10-22", user: "comptable" });
  });
  reglements.push({ id: idReglement++, eleve: 4, tranche: 1, montant: 30000, type: "partiel", statut: "annule", date: "2026-09-10", user: "comptable" });

  // Enseignants (mêmes champs que le backend) ; matieres = matières enseignées (table enseignement)
  const enseignant = (id, nom, prenom, genre, diplome, telephone, salaire, montant, matieres, actif = true) =>
    ({ id, nom, prenom, genre, diplome, telephone, telephone2: "", salaire, montant, matieres, actif, moyenPaiement: null, numeroCompte: "", intituleCompte: "" });
  const enseignants = [
    enseignant(1, "FOUDA", "Martin", "M", "Master en mathématiques", "6 77 21 45 10", "Mensuel", 180000, ["Mathématiques"]),
    enseignant(2, "NKOULOU", "Hervé", "M", "DIPES II Lettres modernes", "6 99 12 03 44", "Mensuel", 175000, ["Français"]),
    enseignant(3, "TABI", "Sandrine", "F", "Licence en anglais", "6 55 40 88 21", "Horaire", 2500, ["Anglais"]),
    enseignant(4, "NGO BATA", "Josiane", "F", "DIPES II Physique", "6 98 76 54 32", "Mensuel", 180000, ["Physique-Chimie"]),
    enseignant(5, "ESSAMA", "Roger", "M", "Master en histoire", "6 70 11 22 33", "Horaire", 2500, ["Histoire-Géographie", "Éducation civique"]),
    enseignant(6, "MOUSSA", "Alim", "M", "Licence en biologie", "6 91 40 50 60", "Horaire", 2000, ["SVT"]),
    enseignant(7, "KENFACK", "Ulrich", "M", "BTS Informatique", "6 52 63 74 85", "Horaire", 2000, ["Informatique"]),
    enseignant(8, "ABENA", "Serge", "M", "CAPIEMP", "6 80 90 10 20", "Horaire", 1500, ["EPS"], false),
    enseignant(9, "MBARGA", "Lucie", "F", "DIPES I Mathématiques", "6 74 10 20 30", "Mensuel", 160000, ["Mathématiques", "Informatique"]),
    enseignant(10, "TCHOUPO", "Didier", "M", "Master en physique", "6 95 33 21 08", "Horaire", 2500, ["Physique-Chimie"]),
    enseignant(11, "EKOTTO", "Mireille", "F", "Licence en lettres", "6 56 87 12 44", "Horaire", 2000, ["Français", "Éducation civique"]),
    enseignant(12, "ZAMBO", "Thierry", "M", "DIPES II SVT", "6 99 01 45 67", "Mensuel", 170000, ["SVT"]),
    enseignant(13, "NJIKE", "Paulette", "F", "Licence en anglais", "6 78 66 41 29", "Horaire", 2500, ["Anglais"]),
    enseignant(14, "OYONO", "Gaston", "M", "Master en géographie", "6 51 23 89 90", "Horaire", 2500, ["Histoire-Géographie"]),
  ];
  // Moyen de paiement du salaire, configuré dans Salaires > Moyens de paiement (null = pas encore configuré) :
  // ESPECE, COMPTE BANCAIRE ou MOBILE (numéro de compte obligatoire)
  [[2, "ESPECE", "", ""], [12, "ESPECE", "", ""], [10, "ESPECE", "", ""], [1, "COMPTE BANCAIRE", "10005 00001 01234567890 12", "FOUDA Martin"], [4, "COMPTE BANCAIRE", "10033 05201 98765432101 45", "NGO BATA Josiane"],
    [9, "COMPTE BANCAIRE", "10029 26008 11223344556 07", "MBARGA Lucie"], [3, "MOBILE", "6 55 40 88 21", "TABI Sandrine"],
    [5, "MOBILE", "6 70 11 22 33", "ESSAMA Roger"], [13, "MOBILE", "6 78 66 41 29", "NJIKE Paulette"]]
    .forEach(([id, moyenPaiement, numeroCompte, intituleCompte]) => Object.assign(enseignants.find(e => e.id === id), { moyenPaiement, numeroCompte, intituleCompte }));
  // Emploi du temps de la 2nde C : [jour (0-4), heure début, heure fin, matière]
  const cours = [
    [0, "07:30", "09:30", 5], [0, "09:45", "11:45", 1], [0, "13:00", "14:00", 9],
    [1, "07:30", "09:30", 6], [1, "09:45", "10:45", 2], [1, "10:45", "11:45", 4],
    [2, "07:30", "09:30", 5], [2, "09:45", "11:45", 3], [2, "13:00", "15:00", 8],
    [3, "07:30", "08:30", 7], [3, "08:30", "10:30", 1], [3, "10:45", "11:45", 2],
    [4, "07:30", "09:30", 6], [4, "09:45", "10:45", 7], [4, "10:45", "11:45", 5],
  ];
  // Chaque cours : [jour, début, fin, matière, enseignant, classe] (cours d'exemple : 2nde C)
  cours.forEach(c => { const m = matieres.find(x => x.id === c[3]); c.push(enseignants.find(e => m.prof.includes(e.nom)).id, 6); });
  // Présence des enseignants (table presence_enseignant) : "date|index du cours" -> P (présent), A (absent), J (absence justifiée)
  // Exemple : vendredi 11/12/2026 saisi, le dernier cours de la journée avec une absence
  const presencesEnseignants = {};
  cours.forEach((c, i) => { if (c[0] === 4) presencesEnseignants[`2026-12-11|${i}`] = c[1] === "10:45" ? "A" : "P"; });

  // Catalogue des permissions (identique au script data_roles_permissions.py du backend)
  const CRUD = ["ajouter", "modifier", "supprimer", "consulter"];
  const catalogue = {
    administration: [
      ["annee", ["ajouter", "modifier", "consulter", "cloturer"]], ["configuration", ["ajouter", "modifier", "consulter"]],
      ["section", CRUD], ["cycle", CRUD], ["niveau", CRUD], ["classe", CRUD], ["serie", CRUD], ["trimestre", CRUD],
      ["groupe_matiere", CRUD], ["matiere", CRUD], ["groupe_matiere_evalue", CRUD], ["matiere_evalue", CRUD],
      ["bareme", CRUD], ["appreciation", CRUD], ["discipline_decision", CRUD], ["tranche_pension", CRUD], ["utilisateur", CRUD],
    ],
    securite: [["role", CRUD.concat(["attribuer"])]],
    eleves: [["eleve", ["ajouter", "inscrire", "modifier", "consulter", "rechercher"]]],
    enseignement: [
      ["enseignant", CRUD.concat(["rechercher"])], ["enseignement", CRUD], ["cours", CRUD],
      ["presence_eleve", ["ajouter", "modifier", "consulter"]], ["presence_enseignant", ["ajouter", "modifier", "consulter"]],
      ["salaire", ["ajouter", "modifier", "annuler", "consulter"]],
    ],
    evaluations: [
      ["evaluation", CRUD], ["notation", ["ajouter", "modifier", "consulter", "calculer"]],
      ["discipline_eleve", ["ajouter", "modifier", "consulter", "calculer"]], ["bulletin", ["generer"]],
    ],
    scolarite: [["reglement", ["ajouter", "modifier", "annuler", "consulter", "rechercher"]]],
  };
  const tous = d => catalogue[d].flatMap(([m, actions]) => actions.map(a => `${m}:${a}`));
  const roles = [
    { id: 1, nom: "SUPER ADMIN", systeme: true, permissions: "*" },
    { id: 2, nom: "ADMIN", systeme: true, permissions: tous("administration") },
    { id: 3, nom: "COMPTABLE", systeme: false, permissions: tous("scolarite").concat(["eleve:consulter", "eleve:rechercher", "tranche_pension:consulter", "salaire:ajouter", "salaire:modifier", "salaire:annuler", "salaire:consulter"]) },
    { id: 4, nom: "ENSEIGNANT", systeme: false, permissions: ["notation:ajouter", "notation:modifier", "notation:consulter", "presence_eleve:ajouter", "presence_eleve:modifier", "presence_eleve:consulter", "cours:consulter", "evaluation:consulter", "eleve:consulter"] },
    { id: 5, nom: "SECRÉTAIRE", systeme: false, permissions: tous("eleves").concat(["reglement:ajouter", "reglement:consulter", "classe:consulter", "bulletin:generer"]) },
  ];
  const utilisateurs = [
    { id: 1, username: "admin", nom: "MBARGA", prenom: "Axel", roles: [1], actif: true },
    { id: 2, username: "directeur", nom: "OWONA", prenom: "Bernard", roles: [2], actif: true },
    { id: 3, username: "comptable", nom: "NANA", prenom: "Florence", roles: [3], actif: true },
    { id: 4, username: "m.fouda", nom: "FOUDA", prenom: "Martin", roles: [4], actif: true },
    { id: 5, username: "secretaire", nom: "BIYA", prenom: "Carine", roles: [5], actif: true },
    { id: 6, username: "ancien.prof", nom: "ABENA", prenom: "Serge", roles: [4], actif: false },
  ];

  // Anciens élèves à réinscrire : le niveau a déjà été déterminé par le passage automatique de fin d'année
  const anciensEleves = [
    { id: 101, nom: "ZANGA", prenom: "Félix", genre: "M", naissance: "2013-03-12", lieu: "Yaoundé", matricule: "25B0042", ancienneClasse: "6e A", decision: "Promu", niveau: 2 },
    { id: 102, nom: "MEKA", prenom: "Jeanne", genre: "F", naissance: "2010-07-02", lieu: "Douala", matricule: "25D0017", ancienneClasse: "2nde C", decision: "Redouble", niveau: 5 },
    { id: 103, nom: "NDJOCK", prenom: "Pascal", genre: "M", naissance: "2008-11-21", lieu: "Edéa", matricule: "24A0008", ancienneClasse: "1ère D", decision: "Promu", niveau: 7 },
    { id: 104, nom: "ABOUBAKAR", prenom: "Hawa", genre: "F", naissance: "2012-01-30", lieu: "Garoua", matricule: "25C0031", ancienneClasse: "6e B", decision: "Promu", niveau: 2 },
  ];

  // Historique des inscriptions de l'année (une ligne par inscription, avec sa dernière modification)
  const inscriptions = eleves.map((e, i) => ({
    id: i + 1,
    eleve: e.id,
    classe: e.classe,
    date: `2026-${i < 7 ? "08" : "09"}-${String(4 + (i * 3) % 26).padStart(2, "0")}`,
    type: e.nouveau ? "nouveau" : "reinscription",
    redoublant: e.redoublant,
    user: ["secretaire", "admin", "secretaire"][i % 3],
    numero: `REC-2026-${String(101 + i).padStart(5, "0")}`,
    derniereModif: null, // { date, user } : date et utilisateur de la dernière modification
  }));
  inscriptions[5].derniereModif = { date: "2026-09-21", user: "admin" };
  inscriptions[10].derniereModif = { date: "2026-09-25", user: "secretaire" };
  // Inscriptions d'autres classes (élèves non détaillés dans la maquette)
  const autres = [
    ["ADA", "Brenda", "F", 1], ["BIKOKO", "Samuel", "M", 1], ["DJOMO", "Kevin", "M", 2], ["ELOUNDOU", "Sarah", "F", 3],
    ["FONKOU", "Ariane", "F", 3], ["GUEMO", "Patrick", "M", 4], ["HAMADOU", "Moussa", "M", 5], ["ITOUA", "Laure", "F", 7],
    ["JIOGO", "Cédric", "M", 7], ["KOUAM", "Nadège", "F", 8], ["LEKANE", "Boris", "M", 11], ["MBIDA", "Yvette", "F", 12],
    ["NANA", "Arnaud", "M", 9], ["OWONO", "Rita", "F", 10],
  ];
  autres.forEach(([nom, prenom, genre, idClasse], i) => {
    inscriptions.push({
      id: 100 + i,
      eleveInfo: { nom, prenom, genre, matricule: `26${"NPQRSTUVWXYZAB"[i]}${String(20 + i).padStart(4, "0")}`, naissance: `201${1 + i % 4}-0${1 + i % 9}-1${i % 9}`, lieu: villes[i % villes.length] },
      classe: idClasse,
      date: `2026-${["08", "09", "10"][i % 3]}-${String(2 + (i * 5) % 27).padStart(2, "0")}`,
      type: i % 3 === 0 ? "nouveau" : "reinscription",
      redoublant: i % 5 === 0,
      user: ["secretaire", "admin"][i % 2],
      numero: `REC-2026-${String(113 + i).padStart(5, "0")}`,
      derniereModif: i === 3 ? { date: "2026-10-02", user: "admin" } : null,
    });
  });

  // Salaires : heures d'appel des enseignants horaires par mois (présent / absence justifiée) et versements
  const heuresEnseignants = {};
  enseignants.filter(e => e.salaire === "Horaire").forEach((e, i) => {
    heuresEnseignants[e.id] = {
      "2026-09": { p: 12 + i * 2, j: i % 3 === 0 ? 2 : 0 },
      "2026-10": { p: 16 + i * 2, j: i % 2 === 0 ? 1.5 : 0 },
      "2026-11": { p: 14 + i, j: i % 4 === 0 ? 3 : 0 },
      "2026-12": { p: 8 + i, j: 0 },
    };
  });
  const versementsSalaire = [];
  let idVersement = 1;
  enseignants.forEach((e, i) => {
    // Septembre : tout le monde est payé ; octobre : certains partiellement, d'autres pas encore
    const du = m => e.salaire === "Mensuel" ? e.montant : (heuresEnseignants[e.id]?.[m]?.p || 0) * e.montant;
    if (!e.actif) return;
    versementsSalaire.push({ id: idVersement++, ens: e.id, mois: 9, annee: 2026, montant: du("2026-09"), date: "2026-10-03", statut: "valide", user: "comptable" });
    // Un salaire peut être versé en plusieurs fois (avance puis complément)
    if (i % 3 === 0) versementsSalaire.push({ id: idVersement++, ens: e.id, mois: 10, annee: 2026, montant: du("2026-10"), date: "2026-10-25", statut: "valide", user: "comptable" });
    else if (i % 3 === 1) {
      versementsSalaire.push({ id: idVersement++, ens: e.id, mois: 10, annee: 2026, montant: Math.round(du("2026-10") * 0.3), date: "2026-10-15", statut: "valide", user: "comptable" });
      versementsSalaire.push({ id: idVersement++, ens: e.id, mois: 10, annee: 2026, montant: Math.round(du("2026-10") * 0.2), date: "2026-10-24", statut: "valide", user: "comptable" });
    }
  });

  window.DATA = {
    ecole, sections, cycles, niveaux, classes, baremes, appreciations, groupes, matieres, trimestres,
    evaluations, dependances, decisions, eleves, notes, disciplines, tranches, reglements, enseignants, cours,
    catalogue, roles, utilisateurs, anciensEleves, inscriptions, heuresEnseignants, versementsSalaire, presencesEnseignants,
    configuration: { isAppel: true, isAbsenceJustifieePayee: false },
    annees: [
      { id: 1, code: "2025-2026", libelle: "2025-2026", cloture: true },
      { id: 2, code: "2026-2027", libelle: "2026-2027", cloture: false },
    ],
  };
})();
