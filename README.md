# Antenna Management API

API REST de pilotage du réseau mobile : gestion des antennes et des interventions terrain.

---

## Prérequis

- Docker & Docker Compose **ou** Python 3.11+ avec PostgreSQL local
- `curl` (pour les exemples ci-dessous)

---

## Lancement avec Docker Compose (recommandé)

```bash
docker-compose up --build
```

L'application démarre sur **http://localhost:8000**. Les migrations Alembic et le seed de données de démonstration (5 antennes) s'exécutent automatiquement au démarrage — les exemples curl ci-dessous fonctionnent donc immédiatement.

Documentation interactive : **http://localhost:8000/docs**

---

## Lancement manuel (venv)

```bash
# 1. Créer et activer le virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre DATABASE_URL et API_KEY

# 4. Appliquer les migrations
alembic upgrade head

# 5. Insérer les données de démonstration
python3 -m app.seed

# 6. Démarrer l'API
uvicorn app.main:app --reload
```

---

## Variables d'environnement

| Variable       | Exemple                                                          | Description                 |
| -------------- | ---------------------------------------------------------------- | --------------------------- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/antennas` | URL de connexion PostgreSQL |
| `API_KEY`      | `changeme-super-secret-key`                                      | Clé d'authentification API  |

---

## Exécuter les tests

Les tests requièrent une base `antennas_test` (même hôte que `DATABASE_URL`) :

```bash
# Créer la base de test (une seule fois)
createdb antennas_test
# ou via Docker : docker exec -it <db-container> psql -U postgres -c "CREATE DATABASE antennas_test;"

# Lancer la suite de tests
pytest -v
```

---

## Exemples curl

### Lister les antennes (route publique)

```bash
curl http://localhost:8000/api/v1/antennas
```

Avec filtres et pagination :

```bash
curl "http://localhost:8000/api/v1/antennas?city=Paris&status=UP&limit=10&offset=0"
```

### Créer une intervention (route protégée)

```bash
curl -X POST http://localhost:8000/api/v1/intervention \
  -H "Authorization: Bearer changeme-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "antenna_id": 1,
    "description": "Panne secteur — remplacement carte alimentation",
    "technician_identity": "Jean Dupont",
    "priority": "HIGH"
  }'
```

L'antenne passe automatiquement à `DOWN`.

### Clôturer une intervention (route protégée)

Utilisez l'`id` renvoyé par le `POST` précédent (`2` en suivant ce déroulé — l'intervention `1` est celle du seed, déjà clôturée) :

```bash
curl -X PATCH http://localhost:8000/api/v1/intervention/2/close \
  -H "Authorization: Bearer changeme-super-secret-key"
```

L'antenne repasse automatiquement à `UP`.

### Tentative sans authentification (→ 401)

```bash
curl -X POST http://localhost:8000/api/v1/intervention \
  -H "Content-Type: application/json" \
  -d '{"antenna_id": 1, "description": "test", "technician_identity": "X", "priority": "LOW"}'
```

---

## Note technique

### Choix du framework et de l'ORM

**FastAPI** a été retenu pour sa performance native en I/O asynchrone (ASGI), sa validation automatique via Pydantic et la génération OpenAPI sans configuration supplémentaire. **SQLAlchemy 2.0 async** avec **asyncpg** permet de tirer parti de l'async bout-en-bout, depuis la requête HTTP jusqu'à la base de données.

### Stratégie anti-double-intervention simultanée

La protection contre la double intervention active repose sur deux mécanismes complémentaires :

1. **Index partiel unique PostgreSQL** (défense au niveau base) :

   ```sql
   CREATE UNIQUE INDEX uq_one_active_intervention
   ON interventions (antenna_id)
   WHERE ended_at IS NULL;
   ```

   Cet index garantit qu'une seule ligne avec `ended_at IS NULL` peut exister par `antenna_id`. Même en cas de requêtes concurrentes atteignant simultanément la base, PostgreSQL rejette la seconde insertion avec une `IntegrityError`. C'est le filet de sécurité ultime, indépendant du code applicatif.

2. **`SELECT ... FOR UPDATE`** (défense au niveau applicatif) :
   Avant chaque insertion, le service verrouille la ligne de l'éventuelle intervention active existante. Cela sérialise les transactions concurrentes et renvoie une erreur métier explicite (`409 Conflict`) avant même d'atteindre la contrainte SQL.

Cette combinaison couvre à la fois la concurrence au niveau applicatif (lock pessimiste) et les cas extrêmes de race condition au niveau base (contrainte unique partielle).
