# Movie Database Project

This repository contains the Movie Database Project — a collaborative group project where we built a searchable, queryable movie dataset and a small application to explore it. The raw data we used was obtained from Kaggle (see "Data Source" below). This README describes how I collaborated with my team of five, the database systems and schema choices we made, data preparation, and how to run the project locally (including Docker and manual instructions).

---

## Table of Contents
- Project overview
- How I collaborated with a team of 5
- Data source (Kaggle)
- Database systems & design decisions
- Suggested schema (SQL)
- Data cleaning & preprocessing
- How to run (Quick start with Docker, Manual setup)
- Importing Kaggle CSV data examples
- Running the application
- Testing
- Troubleshooting
- Acknowledgements & license

---

## Project overview
The goal of this project is to provide a useful, well-structured movie database to support searches, analytics, and simple visualizations (e.g., top-rated movies, genre breakdown, actor co-appearances). We built an ETL pipeline to ingest CSVs from Kaggle, cleaned and normalized the data, stored it in a database, and added an application layer (API and/or frontend) to query it.

---

## How I collaborated with a team of 5
I worked with four other teammates on this project (5 people total). Our workflow and my contributions:

- Team roles (example split):
  - Product/PM: defined scope, user stories, and test cases
  - Backend devs (2): designed DB schema, ingestion scripts, API
  - Frontend dev (1): built UI for browsing/searching movies
  - DevOps/data engineer (1): Dockerization, CI config, data pipeline

- My personal contributions:
  - Designed and implemented the relational schema and indexing strategy.
  - Wrote CSV import & cleaning scripts (Python) and sample SQL for importing into Postgres and SQLite.
  - Implemented parts of the API (endpoints for movie search, movie details, and rating aggregation).
  - Coordinated weekly sprint meetings, maintained the GitHub board, and performed code reviews for backend PRs.

- Collaboration practices we used:
  - GitHub branches + pull requests for all code; each PR required at least one review.
  - Issues used to track tasks and bugs; a lightweight Kanban board to manage progress.
  - Regular standups (15 min) + one sprint planning session per week.
  - Pair programming when debugging tricky ETL logic or database performance issues.
  - CI runs automated tests and linter on PRs (example: GitHub Actions).

---

## Data source (Kaggle)
The dataset(s) used in this project were downloaded from Kaggle. Typical movie datasets on Kaggle include CSVs like:
- movies.csv (movie id, title, release date, overview, etc.)
- credits.csv (cast and crew data)
- ratings.csv (user ratings)
- links.csv (external ids like TMDB or IMDB)

Be sure to follow the Kaggle dataset license and attribution requirements. We do not include the raw Kaggle CSVs in this repository — you should download them separately and place them into the `data/` directory before running the import steps below.

---

## Database systems & design decisions

We considered multiple database types and used relational DB as our primary store for structured movie data. Summary of choices:

- Relational DB (Postgres recommended)
  - Pros: ACID compliance, rich SQL, joins for normalized data (movies, people, genres).
  - Use-case: primary storage for normalized records; good for analytics and integrity.
  - Indexing: create indexes on frequently searched columns (title, release_date, genre, rating).

- SQLite (local dev)
  - Pros: zero-setup, single-file DB good for demo and tests.
  - Cons: not suited for heavy concurrent loads.

- Graph DB (Neo4j) — optional
  - Pros: ideal for complex relationships (actor co-appearances, recommendations).
  - Use-case: if you need fast graph traversal (e.g., "Find degrees of separation between actors").

- Search engine (Elasticsearch or Meilisearch) — optional
  - Pros: full-text search and fuzzy matching for titles and overviews.
  - Use-case: power the search box for fast fuzzy search over large text fields.

Our implementation defaults to Postgres for production-like runs and SQLite for local demos.

---

## Suggested relational schema (example)
Below is an example normalized schema. Adjust types as required for your DBMS.

```sql
-- movies table
CREATE TABLE movies (
  id              SERIAL PRIMARY KEY,
  kaggle_id       INTEGER,         -- optional original id from Kaggle
  title           TEXT NOT NULL,
  original_title  TEXT,
  overview        TEXT,
  release_date    DATE,
  runtime_minutes INTEGER,
  language        TEXT,
  vote_average    NUMERIC,
  vote_count      INTEGER
);

-- genres table
CREATE TABLE genres (
  id   SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

-- movie_genres (many-to-many)
CREATE TABLE movie_genres (
  movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
  genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
  PRIMARY KEY (movie_id, genre_id)
);

-- people (actors, directors, crew)
CREATE TABLE people (
  id         SERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  external_id TEXT  -- e.g. TMDB or IMDB id
);

-- movie_credits (many-to-many)
CREATE TABLE movie_credits (
  movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
  person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
  role TEXT,        -- e.g., 'actor', 'director', 'writer'
  character TEXT,   -- for actors
  order_in_cast INTEGER,
  PRIMARY KEY (movie_id, person_id, role)
);

-- ratings (if user ratings CSV available)
CREATE TABLE ratings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  movie_kaggle_id INTEGER, -- or reference to movie id after join
  rating NUMERIC,
  rated_at TIMESTAMP
);
```

Indexing suggestions:
- CREATE INDEX ON movies (lower(title));
- CREATE INDEX ON movies (release_date);
- CREATE INDEX ON ratings (movie_kaggle_id);

---

## Data cleaning & preprocessing
Typical steps we performed on the Kaggle CSVs:

1. Remove duplicates and rows with missing key identifiers.
2. Normalize text fields (trim whitespace, unify Unicode, lowercasing for search indexes).
3. Parse dates (normalize `release_date`), and convert runtimes to integers.
4. Extract genres into normalized `genres` table and populate `movie_genres`.
5. Parse credits JSON (Kaggle credits often store cast/crew as JSON strings) into `people` and `movie_credits`.
6. Handle inconsistent IDs: map Kaggle/IMDB/TMDB ids as needed.
7. Optional: deduplicate person names by external ids if available.

We implemented cleaning in Python scripts (example: scripts/clean_and_import.py). Adjust paths and column names to match the dataset you downloaded.

---

## How to run

Prerequisites:
- Git
- Docker & Docker Compose (recommended)
- OR: Local Postgres or SQLite + Python 3.8+/Node.js (depending on the stack used in this repo)
- The Kaggle CSV files placed in `data/` (e.g., data/movies.csv, data/credits.csv, data/ratings.csv)

### Quick start (recommended) — Docker
We provide a Docker-based workflow for quick, consistent local runs.

1. Clone repo:
```bash
git clone https://github.com/ch4ngs4n1ty/Movie-Database-Project.git
cd Movie-Database-Project
```

2. Place Kaggle CSV files into the `data/` directory:
- data/movies.csv
- data/credits.csv
- data/ratings.csv
(Adjust names as needed.)

3. Build and run containers:
```bash
docker-compose up --build
```

4. Import data into Postgres container (example using psql inside container):
```bash
# get into the db container (replace service name with your compose file)
docker-compose exec db bash
psql -U postgres -d moviesdb -f /docker-entrypoint-initdb.d/schema.sql
# run your import script inside container or from host pointing to the db
```

5. Open the app at http://localhost:3000 (or whatever port is configured in the compose file).

Note: If a `docker-compose.yml` is not present in this repo, you can create one using a Postgres service and an app service.

### Manual setup (Postgres)
1. Install Postgres and create a database:
```bash
createdb moviesdb
```

2. Create tables using the SQL schema above or run migrations:
```bash
psql -d moviesdb -f sql/schema.sql
```

3. Install Python dependencies (example):
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Configure environment variables (create `.env`):
```
DATABASE_URL=postgresql://username:password@localhost:5432/moviesdb
FLASK_ENV=development
```

5. Run the import script (example):
```bash
python scripts/import_kaggle_csvs.py --data-dir data/ --database-url "$DATABASE_URL"
```

6. Start the app (example for Flask):
```bash
export FLASK_APP=app
flask run --host=0.0.0.0 --port=5000
```

Or for Node/Express (if applicable):
```bash
npm install
npm run dev
```

### Local demo with SQLite
If you prefer a zero-dependency demo:
1. Create SQLite database:
```bash
sqlite3 movies.db < sql/sqlite_schema.sql
```

2. Import CSV into SQLite (example):
```bash
sqlite3 movies.db
sqlite> .mode csv
sqlite> .import data/movies.csv movies_raw
```

3. Run small Python script to normalize and move data into normalized tables.

---

## Importing Kaggle CSV data — example commands

Postgres COPY (fast):
```sql
-- inside psql
COPY movies(kaggle_id, title, overview, release_date, runtime_minutes, vote_average, vote_count)
FROM '/path/to/data/movies.csv' DELIMITER ',' CSV HEADER;
```

SQLite .import:
```bash
sqlite3 movies.db
.mode csv
.import data/movies.csv movies_temp
```

Python pandas example to read and push to DB:
```python
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('data/movies.csv')
engine = create_engine('postgresql://user:pass@localhost/moviesdb')
df.to_sql('movies_temp', engine, if_exists='replace', index=False)
```

For credits and nested JSON columns, parse with `json.loads()` and expand arrays into rows for the `people` and `movie_credits` tables.

---

## Running tests
If the repo contains tests (e.g., pytest / jest), run them:

Python (pytest):
```bash
pip install -r dev-requirements.txt
pytest
```

Node (jest):
```bash
npm ci
npm test
```

(Adjust commands to match the project's actual test framework.)

---

## Troubleshooting
- "Connection refused" to DB: ensure Postgres is running and `DATABASE_URL` is correct.
- CSV import errors: confirm delimiter and that CSV headers match expected columns.
- Encoding issues: open CSV with utf-8 and normalize Unicode.
- Large CSVs: use streaming parsing (pandas chunksize or csv reader) rather than loading entire file into memory.

---

## Acknowledgements
- Kaggle for datasets used in this project.
- Team members: my teammates (backend, frontend, product, devops) for their contributions.
- Open-source libraries used (e.g., SQLAlchemy, Flask/Express, pandas).

---

## License
Specify your preferred license (e.g., MIT). Also respect the dataset license from Kaggle — the CSVs may have their own terms.

---

If you'd like, I can:
- Generate a ready-to-run Docker Compose example for Postgres + app.
- Create import scripts (Python) tailored to the exact Kaggle dataset you used — tell me the CSV filenames and sample columns.
- Produce a CONTRIBUTING.md describing the PR and review workflow your team used.
