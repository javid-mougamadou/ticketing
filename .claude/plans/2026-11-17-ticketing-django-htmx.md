# Plan — Projet portfolio "ticketing" (Django + HTMX)

## 1. Objectif

Créer un nouveau repo GitHub public `ticketing` : un système de gestion de
tickets (support/bug tracking) en Django + HTMX, en démo publique sans
authentification complexe, démontrant un vrai skill Django côté serveur
(modèles, vues, formulaires, DB, admin) avec des interactions dynamiques
HTMX (filtres de liste, changement de statut, ajout de commentaire — sans
rechargement de page). Déployé sur Hostinger via Ansible, sur son propre
sous-domaine `ticketing.javid-space.cloud`. Pièce de portfolio pour le
pilier "Django Developer", scope volontairement raisonnable (pas un SaaS
complet). Le second projet ("dashboarding") est hors scope de ce plan.

## 2. Contexte & contraintes

**Conventions confirmées par exploration du disque :**

- Tous les repos portfolio vivent en sibling dirs sous
  `/Users/Javid/Documents/Projects/spaces-v1/<nom>/` (ex. `platform-studio`,
  `n8n-automation`) → nouveau projet en
  `/Users/Javid/Documents/Projects/spaces-v1/ticketing/`.
- Stack Django déjà pratiquée par Javid : `n8n-automation/web` (Django +
  Postgres + Gunicorn + Whitenoise + entrypoint.sh) et une exploration dédiée
  `exploration/htmx` (Django 5 + `django-htmx` + structure `config/` +
  template `base.html`). Ce plan reprend ces deux patterns.
- Settings : lecture via `os.environ.get(...)` brut (pas de `django-environ`),
  variables `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
  `POSTGRES_DB/USER/PASSWORD/HOST/PORT` — copié tel quel depuis
  `n8n-automation/web/config/settings.py`.
- DB Postgres (pas sqlite) dans tous les projets Django "réels" de Javid
  (`n8n-automation`, `support-flow` archivé) → cohérence du portfolio.
- Docker : `Dockerfile` + `entrypoint.sh` (wait `pg_isready` → `migrate` →
  `collectstatic` → serveur) + `docker-compose.yml` (dev, bind-mount code,
  `runserver`) + `docker-compose.prod.yml` (overlay : pas de bind-mount, pas
  de port publié, `gunicorn`), mirroring exact de `n8n-automation`.
- Déploiement Hostinger : `/deploy-project` zippe et extrait le code dans
  `/data/projects/<nom>` (ne démarre rien) ; un playbook dédié
  `deploy-<nom>.yml` fait le `docker compose up --build -d` sur le serveur
  (voir `deploy-n8n-automation.yml`) ; un playbook `caddy-add-<nom>.yml`
  connecte le conteneur web au réseau Docker `proxy` externe et ajoute un
  site Caddy `reverse_proxy <projet>-web-1:8000` (voir `caddy-add-cc1.yml`).
  Nom de conteneur par défaut = `<nom-dossier>-<service>-<n>` (pas de
  `COMPOSE_PROJECT_NAME` custom dans les projets existants).
- Serveur cible : `hostinger-01`, IP confirmée dans
  `spaces-v1/ansible/inventory/hosts.yml` → l'enregistrement DNS `ticketing`
  sera de type **A** vers cette IP (pas de CNAME GitHub Pages, contrairement
  à `platform-studio`).
- `/hostinger-dns` et `/create-github-repo` sont les commandes existantes à
  utiliser pour DNS et repo GitHub — pas de nouveau tooling à créer.
- Modèle de domaine ticket : inspiré du vieux repo `support-flow`
  (`archived/support-flow/support_flow/tickets/models.py`), qui a déjà
  `TicketStatus` (open/in_progress/resolved/closed), `Ticket`,
  `TicketComment`, `TicketStatusHistory`, `TicketAssignmentHistory`. Ce plan
  en reprend le cœur (statut, commentaires, historique de statut) sans la
  partie `TicketAssignmentHistory`/`TicketWatcher`/`TicketAttachment`/
  `TicketTag` (hors scope demandé — pas de pièces jointes ni de watchers).
- Risque connu et déjà documenté (mémoire projet) : un conteneur web
  recréé perd sa connexion au réseau `proxy` tant que
  `caddy-add-<nom>.yml` n'est pas rejoué — à répéter après chaque
  redéploiement qui recrée le conteneur, pas seulement au premier déploiement
  (cf. §5).

## 3. Hypothèses & questions ouvertes

Aucune de ces hypothèses n'est bloquante pour découper la tâche — chacune a
un défaut raisonnable et cohérent avec l'existant, à valider/ajuster par
l'utilisateur pendant l'implémentation si besoin.

1. **Authentification / mode démo** : pas d'auth publique. Création de
   ticket et ajout de commentaire se font via un champ texte libre
   (`reporter_name` / `author_name`), sans compte. L'assignation
   (`assigned_to`) pointe vers des comptes `auth.User` ("agents") créés
   uniquement par le jeu de données de démo et gérables via l'admin Django
   (connexion superuser réservée à Javid, pas exposée publiquement). Pas de
   rate-limiting anti-spam prévu (acceptable pour une démo portfolio,
   mentionné en risque §5).
2. **Catégorie** : modélisée comme un modèle `Category` à part (FK sur
   `Ticket`), gérable depuis l'admin — plus démonstratif qu'un simple
   `TextChoices` figé. Alternative plus simple si préférée : `TextChoices`
   sans table dédiée.
3. **Style Tailwind** : build via le binaire standalone `tailwindcss` CLI
   dans un stage Docker dédié (pas de runtime Node dans l'image finale, pas
   de CDN Tailwind en prod). Alternative plus rapide à mettre en place mais
   moins "propre" en prod : `<script src="cdn.tailwindcss.com">` en CDN.
4. **Données de démo** : commande de management `seed_demo_data` (Faker,
   idempotente — no-op si des tickets existent déjà, sauf `--flush`) plutôt
   que des fixtures JSON statiques — génère un jeu plus varié et sert aussi
   de démonstration de compétence (management command custom). Branchée dans
   `entrypoint.sh` après `migrate`.
5. **Framework de tests** : `pytest` + `pytest-django` (reprend la
   convention déjà utilisée par Javid dans `archived/support-flow`).
   Alternative zéro-dépendance : `django.test.TestCase` natif.
6. **Mount point des URLs** : app unique `tickets`, montée à la racine `/`
   (redirection `/` → `/tickets/`) plutôt que sous un préfixe — cohérent
   avec un portfolio mono-fonctionnalité.

## 4. Liste de tâches

Dossier racine : `/Users/Javid/Documents/Projects/spaces-v1/ticketing/`.

1. **Scaffolding Django de base** (faible)
   `manage.py`, `config/{settings.py,urls.py,wsgi.py,asgi.py}`,
   `requirements.txt` (Django, django-htmx, gunicorn, psycopg2-binary,
   whitenoise, Faker, pytest, pytest-django), `.gitignore`, `.env.example`.
   Settings mirroring `n8n-automation/web/config/settings.py` (§2) +
   `django_htmx` dans `INSTALLED_APPS`/`MIDDLEWARE`. Pas de dépendance
   précédente.

2. **Docker dev/prod** (moyenne)
   `Dockerfile` (stage Python, sans Tailwind pour l'instant),
   `entrypoint.sh` (wait Postgres → migrate → collectstatic → runserver/
   gunicorn selon `$@`), `docker-compose.yml` (services `web` + `db`
   Postgres avec healthcheck, bind-mount code), `docker-compose.prod.yml`
   (overlay sans bind-mount/ports, `gunicorn --workers 3`), `.dockerignore`.
   Dépend de l'étape 1 (settings lisant les env vars Postgres).

3. **Pipeline Tailwind** (moyenne)
   Stage Docker additionnel téléchargeant le binaire standalone
   `tailwindcss` et compilant `static/src/input.css` →
   `static/dist/tailwind.css` (copié dans le stage final) ; `templates/
   base.html` (nav, layout, lien vers le CSS compilé, inclusion du script
   `django-htmx` pour le header CSRF — voir §5). Dépend de l'étape 2
   (Dockerfile multi-stage).

4. **App `tickets` — modèles** (moyenne)
   `tickets/models.py` : `Category`, `TicketStatus`/`TicketPriority`
   (`TextChoices`), `Ticket` (title, description, status, priority, category
   FK, assigned_to FK `auth.User` nullable, reporter_name, created_at,
   updated_at, méthode `change_status()` qui loggue dans
   `TicketStatusHistory`), `TicketComment`, `TicketStatusHistory`.
   Migrations. Dépend de l'étape 1.

5. **Admin Django** (faible)
   `tickets/admin.py` : `Category`, `Ticket` (list_display/list_filter sur
   status/priority/category/assigned_to), `TicketComment` et
   `TicketStatusHistory` en inline read-only sur `Ticket`. Dépend de
   l'étape 4.

6. **Formulaires** (faible-moyenne)
   `tickets/forms.py` : `TicketForm` (création), `TicketCommentForm`, et un
   petit formulaire de filtres GET (status/priority/category) pour la liste.
   Dépend de l'étape 4.

7. **Vues + URLs** (élevée — cœur HTMX de la tâche)
   `tickets/views.py` + `tickets/urls.py` :
   - `ticket_list` (page complète au 1er chargement ; si `request.htmx`,
     renvoie uniquement le partial `_ticket_table.html` filtré par query
     params — déclenché par `hx-get` sur les contrôles de filtre) ;
   - `ticket_create` (formulaire classique POST/redirect/GET, pas de HTMX
     requis ici) ;
   - `ticket_detail` (ticket + historique + commentaires) ;
   - `ticket_update_status` (POST HTMX uniquement, renvoie le partial statut
     + nouvelle ligne d'historique) ;
   - `comment_create` (POST HTMX uniquement, renvoie le partial commentaires
     mis à jour).
   Toutes les vues "partial-only" doivent vérifier `request.htmx` et
   refuser/rediriger sinon (cf. risque §5). Dépend des étapes 4 et 6.

8. **Templates** (moyenne-élevée)
   `templates/tickets/{list.html,_ticket_table.html,create.html,
   detail.html,_status_panel.html,_comments.html}` + nav dans `base.html`.
   Dépend de l'étape 7.

9. **Commande de données de démo** (moyenne)
   `tickets/management/commands/seed_demo_data.py` (Faker : ~6 catégories,
   ~5 agents, ~40 tickets avec statuts/priorités variés, commentaires et
   historique de statut cohérent, idempotent, option `--flush`). Branchement
   dans `entrypoint.sh` après `migrate`. Dépend de l'étape 4.

10. **Suite de tests (scope, pas l'implémentation)** (moyenne — portée
    seulement, écriture déléguée à `test-architect`/implémentation)
    `tickets/tests/{test_models.py,test_views_list.py,test_views_create.py,
    test_views_detail_htmx.py,test_seed_command.py}` + `pytest.ini`/
    `conftest.py`. Couverture attendue détaillée en §6. Dépend des étapes
    4, 6, 7, 9.

11. **README du repo** (faible)
    Install/run local (`docker compose up`), stack technique, lien vers la
    démo une fois déployée (placeholder). Dépend de toutes les étapes de
    code.

12. **Création du repo GitHub public** (faible)
    `/create-github-repo` sur `spaces-v1/ticketing`, visibilité `public`.
    Dépend de l'étape 11 (code + README prêts).

13. **Playbooks Ansible Hostinger** (moyenne)
    `spaces-v1/ansible/playbooks/deploy-ticketing.yml` (upload `.env`,
    `docker compose -f docker-compose.yml -f docker-compose.prod.yml up
    --build -d`, mirroring `deploy-n8n-automation.yml`) et
    `caddy-add-ticketing.yml` (connect réseau `proxy`, site Caddy
    `reverse_proxy ticketing-web-1:8000`, reload). Dépend de l'étape 2 (
    structure compose figée) et doit être rejoué après tout redéploiement
    qui recrée le conteneur `web` (cf. §5).

14. **Déploiement + DNS** (faible, exécution)
    `/deploy-project` (zip+copie) → playbook `deploy-ticketing.yml` →
    playbook `caddy-add-ticketing.yml` → `/hostinger-dns ticketing A
    145.223.85.13`. Dépend des étapes 12 et 13.

## 5. Risques & edge cases

- **CSRF + HTMX** : les requêtes `hx-post` n'incluent pas le cookie CSRF par
  défaut dans le body — prévoir dans `base.html` un listener
  `htmx:configRequest` (ou `hx-headers` global) injectant le token. À
  vérifier dès l'étape 7/8, sinon tous les POST HTMX échouent silencieusement
  en 403.
- **Accès direct aux partials** : `_ticket_table.html`, `_status_panel.html`,
  `_comments.html` ne doivent jamais être servis comme page complète si
  `request.htmx` est faux (cf. tâche 7) — sinon un lien direct affiche du
  HTML cassé (pas de `<html>`/nav).
- **Double-soumission de changement de statut** : clic HTMX répété → ne pas
  créer de doublon d'historique si `new_status == status` actuel (vérifier
  dans `Ticket.change_status()`).
- **Spam public (pas d'auth, cf. hypothèse 3.1)** : accepté comme compromis
  de démo publique ; pas de mitigation prévue dans ce plan au-delà de
  longueurs max sur les champs texte libres.
- **Idempotence du seed** (cf. hypothèse 3.4) : sans le garde-fou
  "no-op si tickets existants", chaque redémarrage de conteneur dupliquerait
  les données de démo.
- **Réseau Docker `proxy` perdu après recréation du conteneur** (cf. §2,
  risque déjà documenté pour `n8n-automation`) : rejouer systématiquement
  `caddy-add-ticketing.yml` après tout `docker compose up --build` en prod,
  pas uniquement au premier déploiement.
- **Pin de version du binaire Tailwind standalone** (cf. hypothèse 3.3) :
  figer une version exacte dans le Dockerfile pour éviter un build cassé si
  l'URL de téléchargement change de format.
- **Propagation DNS** : 5–30 min après `/hostinger-dns` avant que
  `ticketing.javid-space.cloud` résolve — attendu, pas un bug (cf. doc
  `/hostinger-dns`).
- **Rollback** : en cas d'échec de déploiement, `docker compose down` côté
  serveur sur `/data/projects/ticketing` + ne pas pointer le DNS tant que le
  smoke test (§6) n'est pas vert ; le code reste sur GitHub/local, aucune
  perte possible.

## 6. Stratégie de validation

- **Statique** : `python manage.py check` et `makemigrations --check
  --dry-run` (via `docker compose run --rm web ...`) après les étapes 4 et
  9.
- **Tests automatisés** (portée définie tâche 10, écriture par
  `test-architect` ou à l'implémentation) :
  - `test_models.py` : transition de statut crée bien une
    `TicketStatusHistory`, pas de doublon si statut inchangé.
  - `test_views_list.py` : filtres combinés (statut+priorité+catégorie),
    réponse partial (header `HX-Request`) vs page complète.
  - `test_views_create.py` : validation du formulaire, redirection après
    création.
  - `test_views_detail_htmx.py` : `ticket_update_status` et `comment_create`
    refusent les requêtes non-HTMX, renvoient le bon partial sinon.
  - `test_seed_command.py` : idempotence (2e exécution sans `--flush` ne
    change pas le nombre de tickets), `--flush` régénère.
  Exécution : `docker compose run --rm web pytest`.
- **Manuel (dev)** : `docker compose up`, parcourir `/tickets/` (filtres sans
  reload réseau visible dans les devtools), créer un ticket, changer son
  statut inline, ajouter un commentaire sans reload, vérifier `/admin/`.
- **Manuel (post-déploiement)** : `curl -I
  https://ticketing.javid-space.cloud/tickets/` → 200 ; CSS Tailwind bien
  servi (page stylée, pas de HTML nu) ; `/admin/` accessible ; `docker
  network inspect proxy` sur le serveur confirme le conteneur
  `ticketing-web-1` attaché.

## 7. Definition of Done

- Modèles, migrations, admin fonctionnels ; jeu de données de démo non vide
  généré automatiquement au démarrage du conteneur.
- Les 3 interactions HTMX (filtres liste, changement de statut, ajout de
  commentaire) fonctionnent sans rechargement de page, vérifié manuellement.
- Suite de tests (tâche 10) exécutée, rapport "X/Y tests passent" obtenu via
  `test-architect` — des tests encore rouges ne bloquent pas mais sont
  rapportés.
- Repo GitHub public `javid-mougamadou/ticketing` créé et à jour.
- Déployé et accessible publiquement sur
  `https://ticketing.javid-space.cloud` (DNS A + Caddy + conteneurs prod up),
  `/admin/` fonctionnel.
- README présent avec instructions de lancement local.
- Ajout au portfolio Malt/GitHub (badge, `spaces.json`) explicitement hors
  scope de ce plan (à faire après déploiement, cf. énoncé).
