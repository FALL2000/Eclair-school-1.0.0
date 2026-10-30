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
| Saisies en masse (appel des élèves, présence des enseignants, notes, discipline en mode manuel) | règle commune : **1re saisie** = rien de coché ni pré-rempli, bandeau « pas encore enregistré », toutes les lignes obligatoires (sauf notes : vide = non classé), bouton **Enregistrer** ; **déjà enregistré** = lecture seule, bouton **Modifier** → saisie modifiable avec **Annuler** / **Enregistrer** (brouillon jusqu'à l'enregistrement) | 1re saisie : `add-bulk` (permission `ajouter`) ; modification : `update-bulk` (permission `modifier`) |
| Appel — élèves (onglet « Élèves » : date (pas dans le futur) puis cours de la classe ce jour-là) | `#/presences` | `/presence-eleve/*` | `presence_eleve:consulter` / `ajouter` / `modifier` |
| Appel — présence des enseignants (onglet « Enseignants » : date (pas dans le futur), classe (section > cycle > niveau pour remplir la liste ; vide = toutes les classes) et nom / prénom ; tous les cours de ce jour, toutes classes ; Présent / Absent / Absence justifiée, présent par défaut ; une présence déjà enregistrée n'est modifiable qu'avec `modifier` ; base du calcul des salaires horaires) | `#/presences` (onglet Enseignants) | `GET /presence-enseignant/jour?date_cours=&q=&id_classe=&id_enseignant=`, `POST /presence-enseignant/jour` (400 `DATE_FUTURE`, `JOUR_COURS_DIFFERENT`, 403 si modification sans droit) | `presence_enseignant:consulter` / `ajouter` / `modifier` |
| Évaluations et dépendances (ajout / modification : code unique, libellé, trimestre, dates ; période cohérente avec les dépendances et l'évaluation parente) | `#/evaluations` | `POST /evaluation/add?id_trimestre=`, `PATCH /evaluation/update/{id}` (400 `INVALID_DATES`, `TRIMESTRE_DIFFERENT`, `PERIODE_HORS_INTERVALLE`, 409 `DUPLICATION_CODE`), `/evaluation/add-dependances/{id}` | `evaluation:consulter` / `ajouter` / `modifier` |
| Saisie des notes | `#/notes` | `/notation/list`, `/add-bulk`, `/update-bulk`, `/calculer` | `notation:consulter` |
| Discipline | `#/discipline` | `/discipline-eleve/*` | `discipline_eleve:consulter` |
| Bulletins (aperçu au format A5 portrait ; bulletin trimestriel : notes de chaque évaluation du trimestre + moyenne trimestrielle ; bulletin annuel : notes de toutes les évaluations de l'année + moyenne annuelle ; bulletin d'une évaluation calculée : notes de ses dépendances (avec leur %) + note de l'évaluation → `entete.evaluations` et `ligne.notes_evaluations` ; langue du bulletin FR / EN : libellés, rangs 1st/2nd…, appréciations et décisions disciplinaires en anglais via `libelle_en`, sinon libellé français) | `#/bulletins` | `/bulletin/evaluation`, `/bulletin/trimestre`, `/bulletin/annuel` avec `?langue=FR|EN` (FR par défaut) | `bulletin:generer` |
| Pensions et règlements (reçu de règlement bilingue imprimé après l'enregistrement, réimprimable depuis l'historique de l'élève et l'onglet Historique ; numéro REG-<année>-<id> ; situation de la tranche au moment du règlement) | `#/scolarite` | `/reglement/by-classe/{id}/tranche/{id}?statut_paiement=` (total / partiel / aucun / `non_solde` = partiel et aucun ; liste triée par nom ; **Exporter en PDF** généré dans Angular à partir de cette liste, titre « <tranche> – Liste des élèves à jour / en règlement partiel / n'ayant rien réglé / non à jour », ou « Situation des règlements » sans filtre), `/reglement/annuler/{id}`, `GET /reglement/recu/{id}` | `reglement:consulter` |
| Tranches de pension (onglet : par niveau, ajout et modification ; code unique, numéro d'ordre unique par niveau, montant > 0) | `#/scolarite` (onglet Tranches) | `GET /tranche-pension/by-niveau/{id_niveau}`, `POST /tranche-pension/add?id_niveau=`, `PATCH /tranche-pension/update/{id}` (409 `DUPLICATION_CODE`, `DUPLICATION_NUMERO_ORDRE`) | `tranche_pension:consulter` / `ajouter` / `modifier` |
| Historique des règlements (onglet : année scolaire en cours, du plus récent au plus ancien, paginé ; filtres intervalle de dates, nom / prénom / matricule et statut Tous / Valides / Annulés ; total encaissé ; annulation) | `#/scolarite` (onglet Historique) | `GET /reglement/historique?date_debut=&date_fin=&q=&statut=valide|annule&page=&page_size=` (400 `INTERVALLE_DATES_INVALIDE`), `PATCH /reglement/annuler/{id}` | `reglement:consulter` / `annuler` |
| Paramétrage (onglet Structure : arbre section › cycle › niveau › classe ; boutons + Section / Cycle / Niveau / Classe (section, cycle puis niveau choisis en cascade) et « + » sur chaque ligne (parents pré-remplis et verrouillés) ; onglet Séries : `/serie/*`, série choisie à la création d'un niveau ; crayon = modifier code, libellé, montant d'inscription ; le parent et la série ne se modifient pas) | `#/administration` | `POST /section/add`, `/cycle/add?section_id=`, `/niveau/add?cycle_id=&serie_id=`, `/classe/add?niveau_id=` (404 parent introuvable, 409 `DUPLICATION_CODE`), `PATCH /<type>/update/{id}` ; sections, cycles, niveaux, classes, matières évaluées, barèmes, appréciations, décisions, années, configuration | `classe:consulter` |
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
| Identité de l'établissement (simulée dans `data.js` → `ecole`) | barre latérale (bloc logo + nom sous la marque Eclair School), écran de connexion, en-tête des documents imprimés (reçu, bulletin) ; le logo et le nom d'Eclair School restent dans la marque et en pied des documents (« Document généré par Eclair School ») | à créer : table de configuration de l'école avec `nom`, `sigle`, `ville`, `adresse`, `telephone`, `email`, `devise`, `logo` (fichier image) |
| Bandeau officiel des documents (reçu, bulletin) | « RÉPUBLIQUE DU CAMEROUN / Paix – Travail – Patrie » puis le ministère selon `type_school` : MINISTÈRE DES ENSEIGNEMENTS SECONDAIRES (secondaire) ou MINISTÈRE DE L'ÉDUCATION DE BASE (`education_base`) ; langue du document à gauche, l'autre langue à droite en retrait. Bulletin : titre, en-tête et infos de l'élève / de la classe bilingues, langue du bulletin (`langue` FR/EN) mise en avant | template WeasyPrint : `entete.type_school` et `entete.langue` déjà fournis par le service des bulletins |
| Filtre section > cycle > niveau > classe | composant Angular partagé (4 `p-select` liés) utilisé par les écrans Élèves, Emploi du temps, Appel, Notes, Discipline, Bulletins et Règlements ; sélection commune aux écrans et mémorisée. La structure (sections, cycles, niveaux, classes) est chargée **une seule fois** et mise en cache : choisir dans les listes ne fait aucun appel au backend |
| Chargement des données | bouton **Afficher** (ou **Rechercher** sur Élèves), actif quand la classe est choisie : un seul appel par clic. Les données restent affichées tant que les filtres ne changent pas |
| Élèves | recherche dans toute l'école (≥ 3 caractères, Entrée ou bouton, 20 résultats max → `GET /eleves/search?q=`) et élèves d'une classe **paginés** (`GET /eleves/by-classe/{id}?page=&page_size=&q=&genre=&statut=`, statut = `tous` (défaut) / `inscrit` / `non_inscrit`, champ `is_inscris` par ligne) : le filtre dans la classe, le genre et l'inscription sont appliqués par le backend, au clic sur « Filtrer » ou avec Entrée. **Exporter en PDF** : liste A4 selon les filtres appliqués, toutes pages confondues (même appel sans `page` ni `page_size`) ; le PDF est **généré dans Angular** à partir des données retournées, pas par le backend |
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
