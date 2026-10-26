# Eclair School — maquette du frontend

Prototype cliquable, **local et non publié**, du futur frontend Angular + PrimeNG.

## Ouvrir la maquette

Double-cliquer sur `index.html`. La page s'ouvre dans le navigateur.
Une connexion internet est nécessaire pour la police Inter et les icônes PrimeIcons ; tout le reste est local.

- **Connexion** : cliquer sur « Se connecter », sans saisir d'identifiants.
- **Rôle de démonstration** : à changer dans le menu utilisateur (en haut à droite). Les rôles sont SUPER ADMIN, ADMIN, COMPTABLE, ENSEIGNANT et SECRÉTAIRE. Le menu, les boutons et les blocs du tableau de bord s'adaptent aux permissions du rôle.
- **Langue** : FR / EN dans la barre du haut.
- **Thème** : bouton soleil / lune, ou réglage Système / Clair / Sombre dans « Mon profil ».
- **Données** : seule la classe **2nde C** est remplie (12 élèves, notes du trimestre 1).

Paramètres d'URL utiles pour une démonstration :
`index.html?connecte&role=4&theme=dark&lang=en#/notes`

## Fichiers

| Fichier | Contenu |
|---|---|
| `logo.svg` | Logo de l'application : livre ouvert bleu traversé par un éclair jaune |
| `styles.css` | Thème inspiré de PrimeNG Aura (primaire `blue`), modes clair et sombre |
| `i18n.js` | Traductions FR / EN (482 libellés) ; équivalent des fichiers `fr.json` / `en.json` |
| `data.js` | Données fictives reprenant les entités du backend |
| `app.js` | Écrans, navigation, permissions et règles de calcul (identiques au backend) |

## Écrans et correspondance avec le backend

| Écran | Route | Endpoints principaux | Permission |
|---|---|---|---|
| Connexion | `#/login` | `POST /auth/login` | — |
| Tableau de bord | `#/dashboard` | agrégats (notes, règlements, discipline) | selon les blocs |
| Élèves (liste, fiche) | `#/eleves`, `#/eleves/{id}` | `/eleves/*` | `eleve:consulter` |
| Historique des inscriptions (onglet de l'écran Inscriptions) | `#/inscription` | `GET /inscription/historique?date_debut=&date_fin=&q=&page=&page_size=` (tri par date décroissante) et `PATCH /inscription/update/{id}` (classe, redoublant ; date et utilisateur de la dernière modification enregistrés sur l'inscription ; classe non modifiable si l'élève a déjà des notes, une discipline, des présences — ou des règlements en cas de changement de niveau — dans l'année en cours). Réimpression du reçu en duplicata | `eleve:consulter` / `eleve:inscrire` |
| Modification d'un élève (liste et fiche) | `#/eleves` | `PATCH /eleves/update/{id}` (existant) | `eleve:modifier` |
| Inscriptions (+ reçu imprimable) | `#/inscription` | `/inscription/nouveau-eleve`, réinscription d'un ancien élève dans une classe de son nouveau niveau (passage automatique à venir) | `eleve:inscrire` |
| Enseignants (paginés, filtres nom/prénom et matière enseignée, ajout, modification sans aucune information de paiement, gestion des matières) | `#/enseignants` | `GET /enseignant/recherche?q=&id_matiere=&page=&page_size=` (permission `enseignant:rechercher`), `PATCH /enseignant/update/{id}`, `POST /enseignement/add-bulk-with-enseignant`, `POST /enseignement/add`, `DELETE /enseignement/delete/{id}` (refusé si des cours sont planifiés pour cette matière dans l'année en cours) | `enseignant:consulter`, `enseignement:ajouter/supprimer` |
| Emploi du temps (ajout d'un cours : classe, matière, enseignant actif à qui la matière est attribuée, jour et heures ; conflits de créneaux de la classe et de l'enseignant) | `#/emploi-du-temps` | `/cours/by-classe`, `POST /cours/add?id_enseignant=&id_classe=&id_matiere=` (404 `ENSEIGNANT_NOT_FOUND`, 409 `ENSEIGNANT_INACTIF`, 400 `MATIERE_NON_ENSEIGNEE`, `HEURES_INVALIDES`, conflits) ; liste des enseignants : `GET /enseignant/recherche?id_matiere=` | `cours:consulter` / `ajouter` |
| Salaires des enseignants — état (onglet « État des salaires » : enseignants actifs et inactifs avec colonne d'état, par mois de l'année scolaire, paginés, filtres nom, matière et situation total / partiel / non payé, versements totaux ou partiels, annulation) | `#/salaires` | `GET /salaire/mois?mois=&annee_civile=&q=&id_matiere=&statut=&page=&page_size=`, `GET /salaire/enseignant/{id}?mois=&annee_civile=`, `POST /salaire/versement`, `PATCH /salaire/versement/annuler/{id}` ; réglage `is_absence_justifiee_payee` dans la configuration | `salaire:consulter` / `ajouter` / `annuler` |
| Salaires des enseignants — versements (onglet « Versements » : tous les versements de l'année, plus récents en premier, paginés, filtres mois payé, nom / prénom et matière, annulation) | `#/salaires` (onglet Versements) | `GET /salaire/versements?mois=&annee_civile=&q=&id_matiere=&page=&page_size=`, `PATCH /salaire/versement/annuler/{id}` | `salaire:consulter` / `annuler` |
| Salaires des enseignants — moyens de paiement (onglet « Moyens de paiement » : enseignants actifs non configurés par défaut, filtre configurés / tous, nom / prénom et matière, paginés ; configuration ESPECE / COMPTE BANCAIRE / MOBILE, numéro de compte obligatoire hors espèces, intitulé ; numéro complet avec `salaire:ajouter` ou `salaire:modifier`, sinon masqué « •••• 9012 ») | `#/salaires` (onglet Moyens de paiement) | `GET /salaire/moyens-paiement?configure=&q=&id_matiere=&page=&page_size=`, `PATCH /salaire/moyen-paiement/{id_enseignant}` | `salaire:consulter` / `modifier` |
| Appel — élèves (onglet « Élèves ») | `#/presences` | `/presence-eleve/*` | `presence_eleve:consulter` |
| Appel — présence des enseignants (onglet « Enseignants » : date (pas dans le futur), classe (section > cycle > niveau pour remplir la liste ; vide = toutes les classes) et nom / prénom ; tous les cours de ce jour, toutes classes ; Présent / Absent / Absence justifiée, présent par défaut ; une présence déjà enregistrée n'est modifiable qu'avec `modifier` ; base du calcul des salaires horaires) | `#/presences` (onglet Enseignants) | `GET /presence-enseignant/jour?date_cours=&q=&id_classe=&id_enseignant=`, `POST /presence-enseignant/jour` (400 `DATE_FUTURE`, `JOUR_COURS_DIFFERENT`, 403 si modification sans droit) | `presence_enseignant:consulter` / `ajouter` / `modifier` |
| Évaluations et dépendances | `#/evaluations` | `/evaluation/*`, `/evaluation/add-dependances/{id}` | `evaluation:consulter` |
| Saisie des notes | `#/notes` | `/notation/list`, `/add-bulk`, `/update-bulk`, `/calculer` | `notation:consulter` |
| Discipline | `#/discipline` | `/discipline-eleve/*` | `discipline_eleve:consulter` |
| Bulletins | `#/bulletins` | `/bulletin/evaluation`, `/bulletin/trimestre`, `/bulletin/annuel` | `bulletin:generer` |
| Pensions et règlements | `#/scolarite` | `/reglement/by-classe/{id}/tranche/{id}?statut_paiement=`, `/reglement/annuler/{id}` | `reglement:consulter` |
| Paramétrage | `#/administration` | sections, cycles, niveaux, classes, matières évaluées, barèmes, appréciations, décisions, années, configuration | `classe:consulter` |
| Utilisateurs et rôles | `#/utilisateurs` | `/user/*`, `/role/*` | `utilisateur:consulter` |
| Mon profil | `#/profil` | `GET /user/me`, `PATCH /user/password` | connecté |

## Composants PrimeNG à utiliser

| Élément de la maquette | Composant PrimeNG |
|---|---|
| Menu latéral | `p-drawer` (mobile) et menu personnalisé, ou `p-panelmenu` |
| Tableaux | `p-table` (pagination, tri, filtres, `rowGroupMode` pour les groupes de matières) |
| Saisie des notes | `p-table` en édition de cellule + `p-inputnumber` (`minFractionDigits` 2) |
| Filtres | `p-select`, `p-inputtext` avec `p-iconfield`, `p-datepicker` |
| Toutes les listes de sélection | `p-select` avec **`[filter]="true"`** (recherche dans la liste, insensible aux accents et à la casse ; Entrée choisit le premier résultat). À définir une fois par défaut dans un composant partagé |
| Inscription — affectation | **Niveau** puis **Classe** : la classe est désactivée tant que le niveau n'est pas choisi, puis ne propose que les classes de ce niveau |
| Filtre section > cycle > niveau > classe | composant Angular partagé (4 `p-select` liés) utilisé par les écrans Élèves, Emploi du temps, Appel, Notes, Discipline, Bulletins et Règlements ; sélection commune aux écrans et mémorisée. La structure (sections, cycles, niveaux, classes) est chargée **une seule fois** et mise en cache : choisir dans les listes ne fait aucun appel au backend |
| Chargement des données | bouton **Afficher** (ou **Rechercher** sur Élèves), actif quand la classe est choisie : un seul appel par clic. Les données restent affichées tant que les filtres ne changent pas |
| Élèves | recherche dans toute l'école (≥ 3 caractères, Entrée ou bouton, 20 résultats max → `GET /eleves/search?q=`) et élèves d'une classe **paginés** (`GET /eleves/by-classe/{id}?page=&page_size=&q=&genre=`) : le filtre dans la classe et le genre sont appliqués par le backend, au clic sur « Filtrer » ou avec Entrée |
| Type de bulletin, présence, langue | `p-selectbutton` |
| Onglets | `p-tabs` |
| Étapes d'inscription | `p-stepper` |
| Statuts | `p-tag` |
| Boîtes de dialogue, confirmations | `p-dialog`, `p-confirmdialog` |
| Notifications | `p-toast` |
| Progression des paiements | `p-progressbar` |
| Matrice des permissions | `p-table` + `p-checkbox` |
| Graphiques | `p-chart` (Chart.js) |
| Appel activé | `p-toggleswitch` |

Thème : preset **Aura** avec `primary: '{blue}'`. Mode sombre via `darkModeSelector` (classe sur `<html>`).

> Le projet `frontend/` utilise aujourd'hui **Angular Material**. Pour suivre cette maquette, il faudra installer `primeng`, `@primeng/themes` et `primeicons`.
