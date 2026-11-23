# Eclair School — frontend

Application Angular 21 construite avec **PrimeNG** (thème Aura, couleur primaire `blue`) et **NgRx**.
Les écrans, les libellés et les règles de calcul suivent la maquette du dossier [`../maquette`](../maquette/README.md).

## Commandes

| Commande | Rôle |
|---|---|
| `ng serve` | Serveur de développement sur `http://localhost:4200/` |
| `ng build` | Build de production dans `dist/` |
| `ng test` | Tests unitaires (Vitest) |
| `ng generate component <nom>` | Création d'un composant |

## Installation à faire

- Ajouter PrimeNG 21 (`primeng`, `@primeuix/themes`, `primeicons`), avec le thème Aura et la couleur primaire `blue`.
- Ajouter NgRx : `@ngrx/store`, `@ngrx/effects`, `@ngrx/signals`, `@ngrx/store-devtools`.
- Retirer Angular Material (`@angular/material`, `@angular/cdk` s'il n'est plus utilisé), remplacé par PrimeNG.
- Retirer le rendu côté serveur (`@angular/ssr`, `server.ts`, `main.server.ts`, `app.config.server.ts`, `app.routes.server.ts`, `express`) : l'application est utilisée après connexion, et le SSR gêne l'accès à `localStorage` et la gestion du jeton.

## Principes d'architecture

1. **Composants d'affichage** (`shared/ui`, `shared/print`) : ils ne reçoivent que des `input()` et n'émettent que des `output()`. Ils n'injectent ni le store, ni les services HTTP, ni le router. On peut donc les réutiliser dans n'importe quel écran.
2. **Pages** (`features/*`) : seules elles lisent le store NgRx et déclenchent les actions. Elles assemblent les composants d'affichage.
3. **PrimeNG en direct** quand il suffit (`p-table`, `p-dialog`, `p-tabs`, `p-select`, `p-datepicker`, `p-stepper`, `p-toast`, `p-confirmdialog`, `p-chart`, `p-tag`). On ne l'enveloppe dans un composant à nous que si on lui ajoute un comportement propre à l'application.
4. **Composants autonomes** (`standalone`), signaux et `ChangeDetectionStrategy.OnPush` partout.
5. Chaque dossier de `features` est **chargé à la demande** (`loadChildren` / `loadComponent`).

## Arborescence

```
src/app/
  core/
    layout/      coquille de l'application (menu, barre du haut, en-tête de page)
    auth/        garde de route, intercepteur du jeton, service de connexion
    i18n/        traductions FR / EN
    http/        configuration de l'API, gestion des erreurs
  shared/
    ui/          composants d'affichage réutilisables
    print/       éléments des documents imprimables
    pipes/
    directives/
    utils/       fonctions pures (règles de calcul)
    models/      interfaces des entités du backend
  store/         store global : auth, school, referentiel, selection, preferences
  features/
    dashboard/  eleves/  inscriptions/  enseignants/  emploi-du-temps/
    presences/  salaires/  evaluations/  notes/  discipline/
    bulletins/  scolarite/  parametrage/  utilisateurs/  profil/
```

Chaque dossier de `features` contient ses pages, son service HTTP et son état de page (SignalStore).

## Mise en page (`core/layout`)

| Composant | Rôle |
|---|---|
| `AppShellComponent` | Menu latéral repliable, barre du haut, zone de contenu |
| `SidebarMenuComponent` | Menu par groupes. Reçoit les entrées déjà filtrées par permission |
| `TopbarComponent` | Fil d'Ariane, année scolaire, langue, thème, menu utilisateur |
| `PreferencesToolsComponent` | Choix de la langue (FR / EN) et du thème. Utilisé sur la page de connexion et dans la barre du haut |
| `BrandComponent` | Logo et nom de l'application |
| `SchoolCardComponent` | Bloc de l'établissement (logo, nom, ville, année), sur la page de connexion et dans le menu |
| `PageHeaderComponent` | Titre, sous-titre et emplacement pour les boutons. Utilisé sur toutes les pages |

## Composants réutilisables (`shared/ui`)

Le nombre d'utilisations est relevé dans la maquette.

| Composant | Utilisations | Détail |
|---|---|---|
| `StatCardComponent` | 6 écrans | Icône, couleur, libellé, valeur, sous-texte |
| `StatusTagComponent` | partout | Sur `p-tag`, avec une table de correspondance statut → couleur : paiement, inscription, évaluation, salaire |
| `PersonCellComponent` | 16 | Avatar avec initiales, nom, ligne secondaire |
| `ClassCascadeFilterComponent` | 9 écrans | Section → Cycle → Niveau → Classe. Reçoit les listes et la sélection, émet la nouvelle sélection. Composant clé |
| `FilterBarComponent` | 7 | Emplacement pour les filtres et bouton « Afficher » / « Rechercher », désactivé tant que les filtres sont incomplets |
| `EmptyStateComponent` | 8 | Icône et message (choisir une classe, aucun résultat, cliquer sur « Afficher ») |
| `PagedTableComponent` | 8 | Configuration commune de `p-table` avec pagination côté serveur (`page`, `page_size`) et sortie `pageChange` |
| `DateRangeSearchComponent` | 3 historiques | Du / au / recherche. Le filtre n'est envoyé au backend qu'au clic |
| `TeacherFilterComponent` | 3 (salaires, versements, moyens de paiement) | Nom et matière enseignée |
| `SchoolSearchComponent` | 1 | Recherche d'un élève dans toute l'école, 3 caractères minimum |
| `RowActionsComponent` | 6 et plus | Boutons Modifier / Supprimer selon les permissions, désactivés avec une infobulle qui donne la raison (année en cours, groupe non vide…) |
| `FoldableTreeTableComponent` | 4 (structure, matières, matières évaluées) | Lignes de groupe pliables, « Tout déplier » / « Tout replier ». Peut s'appuyer sur `p-treeTable` |
| `BarChartComponent` | tableau de bord | Sur `p-chart`, barres verticales et horizontales |
| `FormDialogComponent` | 33 dialogues | `p-dialog` avec le formulaire dans un emplacement, boutons Annuler / Enregistrer et zone d'erreur |
| `SkeletonComponent` (sur `p-skeleton`) | tous les composants de données | Squelettes prêts à l'emploi : `stat`, `table`, `bars`, `liste`. Chaque composant de données a un `input()` `loading` et affiche son squelette tant qu'il vaut `true`. Pas de loader global pour la page |
| `BulkEntryFooterComponent` | 4 écrans | Pied des saisies en masse (appel, présence des enseignants, notes, discipline) : état (enregistré, non enregistré, en modification) et boutons Modifier / Enregistrer / Annuler |

Services d'affichage :

| Service | Rôle |
|---|---|
| `ConfirmService` | Demande de confirmation (14 dans la maquette), s'appuie sur `ConfirmationService` de PrimeNG |
| `NotificationService` | Messages de succès ou d'erreur (59 dans la maquette), s'appuie sur `MessageService` de PrimeNG |

## Documents imprimables (`shared/print`)

Documents concernés : reçu d'inscription, reçu de règlement, bulletin, liste des élèves, liste des règlements.

| Composant | Rôle |
|---|---|
| `OfficialHeaderComponent` | Bandeau République / ministère, bilingue |
| `DocumentHeaderComponent` | En-tête de l'établissement |
| `DocumentFooterComponent` | Pied de page |
| `BilingualLabelComponent` | Libellé FR / EN sur deux lignes |
| `PrintLayoutComponent` | Mise en forme de la page pour l'impression |

## Pipes, directives et fonctions (`shared`)

| Élément | Rôle |
|---|---|
| Pipe `fcfa` | Montant en FCFA (61 utilisations dans la maquette) |
| Pipe `note` | Note à 2 décimales, « — » si elle est vide |
| Pipe `localDate` | Date selon la langue choisie |
| Pipes `initials`, `appreciation`, `rangLabel` | Initiales, appréciation d'une note selon le barème, rang (« 1er », « 2e ex æquo ») |
| Directive `*hasPermission` | Affiche un élément selon une permission, par exemple `'eleve:inscrire'` (104 vérifications dans la maquette) |
| Garde `permissionGuard` | Bloque une route selon la permission indiquée dans ses `data` |
| `shared/utils` | Fonctions pures reprises du backend : moyenne, rang, note ramenée sur 20, arrondi au quart |

## NgRx

**Store global** (`@ngrx/store` et `@ngrx/effects`) : les données partagées par plusieurs écrans.

| Slice | Contenu |
|---|---|
| `auth` | Utilisateur connecté, jeton, permissions |
| `school` | Configuration de l'établissement : `typeSchool`, `isDisciplineManage`, année en cours |
| `referentiel` | Sections, cycles, niveaux, classes, trimestres, évaluations, matières. Chargés une fois puis mis en cache |
| `selection` | Classe choisie dans la cascade, partagée entre les écrans et mémorisée |
| `preferences` | Langue et thème |

**État de chaque page** (`@ngrx/signals`, `signalStore`) : filtres saisis et appliqués, pagination, liste chargée, brouillons des saisies en masse, et un indicateur de chargement **par bloc de données** (par exemple `moyennesLoading`, `effectifsLoading` sur le tableau de bord) pour que chaque composant affiche son propre squelette. Cet état reste local à la page et n'a pas besoin d'actions ni de reducers.
