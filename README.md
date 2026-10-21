# People Counting MLOps: Complete 10-Row Project

This project is a **hands-on educational example** using 10 artificial rows.
It shows how Python, DVC, MLflow, Pytest, Flask, Docker, Docker Compose,
GitHub Actions, Docker Hub, and optional Airflow/Astro fit together.

**Important:** A model trained on 8 synthetic rows and tested on 2 rows
is NOT a scientifically meaningful occupancy-estimation model.

## 1. Project workflow and connections

```text
data/raw/people_count.csv (10 rows)
    |
    | src/prepare.py
    v
data/processed/train.csv (8) + test.csv (2)
    |
    | src/train.py reads params.yaml
    v
models/model.joblib
    |
    | src/evaluate.py + test.csv
    +---> metrics/metrics.json
    +---> mlruns/ (MLflow experiment)
    |
    | src/predict.py
    v
app.py (Flask: /health, /predict)
    |
    | Dockerfile
    v
Docker image -> Docker Compose -> running API
    |
    | GitHub Actions CD
    v
Docker Hub (stores the image, does not deploy it)
```

**DVC:** `dvc.yaml` defines prepare/train/evaluate dependencies.
`dvc repro` runs the required stages and generates `dvc.lock`.
**MLflow:** logs hyperparameters, MAE, RMSE and artifacts from evaluation.
**Pytest:** checks the input data and basic API behavior.
**GitHub Actions CI:** tests and runs the pipeline after pushes/PRs.
**GitHub Actions CD:** manually builds and publishes a Docker image.
**Airflow:** optionally schedules the DVC pipeline.
**Astro:** optionally runs an Airflow environment in Docker.

## 2. Prerequisites (Windows)

Use **Miniconda Prompt** (CMD), not PowerShell, for the following commands.
Install Miniconda, Git, and optionally VS Code. Docker Desktop is needed
only for the Docker steps. You do not need Airflow/Astro for the first run.

Unzip to `C:\MLOps\people_counting_mlops_10_rows`.

```cmd
cd /d C:\MLOps\people_counting_mlops_10_rows
conda create -n people-mlops python=3.11 -y
conda activate people-mlops
python -m pip install -r requirements.txt
```

`requirements.txt` lists the training/development libraries. The smaller
`requirements-api.txt` is used when building the inference Docker image.

## 3. Dataset: exactly 10 rows

File: `data/raw/people_count.csv`

```csv
co2_ppm,pir_motion,people_count
420,0,0
450,1,1
480,2,1
520,3,2
560,4,2
610,5,3
650,6,3
700,7,4
760,8,4
820,9,5
```

`co2_ppm` and `pir_motion` are model **inputs**.
`people_count` is the **target**.
For learning, we use the first 8 rows to train and the last 2 to test.

## 4. Run the Python files one by one

All commands below assume you are in the project root with the Conda
environment active.

```cmd
python -m src.prepare
```

`src/prepare.py` reads the raw CSV, checks columns/values, and writes
`data/processed/train.csv` (8 rows) and `test.csv` (2 rows).

```cmd
type data\processed\train.csv
type data\processed\test.csv
python -m src.train
```

`src/train.py` reads `train.csv` and `params.yaml`, fits a
`RandomForestRegressor`, and saves `models/model.joblib`.

```cmd
python -m src.evaluate
type metrics\metrics.json
```

`src/evaluate.py` loads the saved model, predicts the two test rows,
calculates MAE and RMSE, writes `metrics.json`, and logs an MLflow run.
MAE is the average absolute prediction error. RMSE penalizes large errors
more strongly. The actual values depend on the model output.

```cmd
python -m src.predict
```

`src/predict.py` loads `model.joblib` and predicts from one input pair
(CO2=760, PIR=8). It rounds the result to a nonnegative integer.

## 5. Test the code

```cmd
python -m pytest -q
```

`tests/test_data.py` checks that there are 10 rows, correct column names,
nonnegative labels, a working health endpoint, and a 400 response for an
invalid prediction request. Tests do not prove model accuracy.

## 6. Initialize Git and DVC

```cmd
git init
git branch -M main
dvc init
dvc repro
dvc metrics show
```

`dvc init` creates `.dvc/`. `dvc repro` reads the included `dvc.yaml`:

- **prepare**: raw CSV + `prepare.py` -> `train.csv`, `test.csv`
- **train**: train CSV + `train.py` + `params.yaml` -> `model.joblib`
- **evaluate**: test CSV + model + `evaluate.py` -> `metrics.json` + MLflow

DVC generates `dvc.lock` to record the pipeline state. It also ignores
DVC-managed generated outputs in Git. Running `dvc repro` again without
changes should skip unchanged stages.

**Try a change:** edit `params.yaml` and change `n_estimators: 10` to
`n_estimators: 20`. Then:

```cmd
dvc repro
dvc metrics show
```

DVC should rerun train and evaluate, but skip unchanged preparation.
To force evaluation (and a new MLflow run), use:

```cmd
dvc repro -f evaluate
```

**Why no `data/raw/people_count.csv.dvc`?** This project intentionally
commits the **tiny** raw CSV to Git so GitHub Actions can work without
remote-storage credentials. DVC still tracks the pipeline and its generated
outputs. For large real datasets, use `dvc add`, a remote such as DagsHub,
and `dvc push`. Then CI/CD must authenticate and run `dvc pull` first.
See `docs/OPTIONAL_REMOTE_AND_AWS.md`.

## 7. Open MLflow

Open a SECOND Miniconda Prompt:

```cmd
conda activate people-mlops
cd /d C:\MLOps\people_counting_mlops_10_rows
mlflow ui --backend-store-uri ./mlruns --port 5001
```

Open http://127.0.0.1:5001 in your browser.
Select the `people-counting-10-rows` experiment to compare model parameters,
MAE, RMSE, and artifacts. `mlruns/` is local and ignored by Git.

## 8. Run the Flask API

Make sure `models/model.joblib` exists.

```cmd
python app.py
```

Keep this terminal open. In another Miniconda Prompt:

```cmd
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d "{\"co2_ppm\":760,\"pir_motion\":8}"
```

`app.py` accepts JSON, validates sensor values, calls
`src/predict.py`, and returns `{"predicted_people": ...}`.
The prediction is computed, not hard-coded.
Press **Ctrl+C** in the Flask terminal before running Docker on port 5000.

## 9. Build and run Docker

Start Docker Desktop first. Run `dvc repro` to generate the model if needed.

```cmd
docker build -t people-counting-api:v1 .
docker run --rm -p 5000:5000 people-counting-api:v1
```

The **Dockerfile** starts from Python 3.11, installs inference libraries,
copies `app.py`, `src/`, and `models/model.joblib`, and starts Gunicorn.
The **image** is a packaged application. The **container** runs it.
`-p 5000:5000` maps host port 5000 to the container's port 5000.
Visit http://127.0.0.1:5000/health and test the prediction again.
Press **Ctrl+C** to stop.

`.dockerignore` excludes training data, Git history, and other files that
the API does not need. The model is intentionally included in the image.

## 10. Docker Compose

`compose.yaml` records the image/build and port configuration.
Instead of a long `docker run` command:

```cmd
docker compose up --build
```

Visit http://127.0.0.1:5000/health.
Stop with Ctrl+C and clean up:

```cmd
docker compose down
```

If port 5000 is already in use, stop the local Flask server or change the
host port in `compose.yaml` from `"5000:5000"` to `"5001:5000"`.

## 11. Git and GitHub

```cmd
git add .
git commit -m "Initial 10-row MLOps example"
```

If Git asks for your identity:

```cmd
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Create an empty GitHub repository, then:

```cmd
git remote add origin https://github.com/YOUR_USER/people_counting_mlops_10_rows.git
git push -u origin main
```

Git versions code and the tiny example CSV. DVC manages the generated
pipeline artifacts and dependencies.

## 12. GitHub Actions CI

File: `.github/workflows/ci.yml`.

After `git push`, GitHub Actions:
1. Downloads the source code and 10-row CSV.
2. Installs Python and `requirements.txt`.
3. Runs `python -m pytest -q`.
4. Runs `dvc init --no-scm`, then `dvc repro` and `dvc metrics show`.

Find the results at GitHub repository > **Actions** > CI workflow.
The temporary GitHub runner starts without your local `.dvc/` state;
`--no-scm` initializes a new workspace for that CI run.

## 13. GitHub Actions CD and Docker Hub

File: `.github/workflows/cd.yml`.

First create a Docker Hub account and a repository named
`people-counting-api`. Generate a Docker Hub access token.

In GitHub repository > Settings > Secrets and variables > Actions,
create these two **repository secrets**:

- `DOCKERHUB_USERNAME`: your Docker Hub username.
- `DOCKERHUB_TOKEN`: Docker Hub access token with write permission.

Open GitHub > Actions > **CD - Publish Docker image** > **Run workflow**.

The workflow tests, runs the DVC training pipeline, logs in to Docker Hub,
builds the Docker image, and publishes `YOUR_USER/people-counting-api:v1`.
**Publishing is not deployment.** Docker Hub stores the image, but does
not start the API on AWS.

On another machine with Docker:

```cmd
docker pull YOUR_USER/people-counting-api:v1
docker run --rm -p 5000:5000 YOUR_USER/people-counting-api:v1
```

## 14. Optional Airflow and Astro

File: `dags/people_counting_dag.py`.

This optional DAG schedules `dvc repro` at 02:00 daily in the DAG timezone.
Airflow decides **when** to run the job; DVC decides **which stages** run.

The DAG is NOT runnable without an Airflow environment. To use Astro,
install Astro CLI and Docker Desktop, create a separate Astro project with
`astro dev init`, copy the DAG, install ML/DVC dependencies in Airflow,
and mount this ML project into the container at
`/usr/local/airflow/ml_project`. Then use `astro dev start`.
See `astro/README.md` for details.

## 15. All files and their responsibilities

| File / folder | What it does |
|---|---|
| `data/raw/people_count.csv` | 10 synthetic examples |
| `src/prepare.py` | Split 8 train / 2 test |
| `data/processed/train.csv` | Generated training data |
| `data/processed/test.csv` | Generated test data |
| `src/train.py` | Train Random Forest |
| `params.yaml` | Random Forest parameters |
| `models/model.joblib` | Generated trained model |
| `src/evaluate.py` | Evaluate and log MLflow experiment |
| `metrics/metrics.json` | Generated MAE and RMSE |
| `mlruns/` | Generated local MLflow runs |
| `src/predict.py` | Predict with saved model |
| `app.py` | Flask API with /health and /predict |
| `tests/test_data.py` | Five Pytest checks |
| `dvc.yaml` | Pipeline stages, inputs, outputs |
| `dvc.lock` | Generated DVC pipeline lock |
| `.dvc/` | Generated DVC settings |
| `Dockerfile` | Build recipe for API image |
| `.dockerignore` | Exclude unneeded files from Docker build |
| `compose.yaml` | Run API container with Compose |
| `.github/workflows/ci.yml` | GitHub automated tests and pipeline |
| `.github/workflows/cd.yml` | Publish image to Docker Hub |
| `dags/people_counting_dag.py` | Optional scheduled Airflow pipeline |
| `astro/README.md` | Optional Astro setup requirements |
| `docs/OPTIONAL_REMOTE_AND_AWS.md` | DagsHub and AWS notes |
| `requirements.txt` | Python training/dev dependencies |
| `requirements-api.txt` | Python inference dependencies |
| `.gitignore` | Git ignore rules |
| `pytest.ini` | Pytest discovery settings |
| `README.md` | This step-by-step guide |

## 16. Quick start: commands in order

```cmd
cd /d C:\MLOps\people_counting_mlops_10_rows
conda create -n people-mlops python=3.11 -y
conda activate people-mlops
python -m pip install -r requirements.txt
python -m pytest -q
git init
git branch -M main
dvc init
dvc repro
dvc metrics show
python -m src.predict
python app.py
```

Use a second terminal for `curl`, and stop Flask before using Docker.

## 17. Troubleshooting

- `conda` not recognized: use **Miniconda Prompt**.
- `dvc` not recognized: activate the environment and install requirements.
- `model.joblib` missing: run `dvc repro` first.
- Port 5000 busy: stop Flask or the existing container.
- Docker daemon unavailable: start Docker Desktop.
- DVC skipped evaluation: no dependencies changed; use
  `dvc repro -f evaluate` to force a new MLflow run.
- MLflow UI empty: run evaluation and point the UI to `./mlruns`.
- Astro DAG fails: install ML dependencies and mount the project path.

**Security:** The API is unauthenticated and intended for local learning.
Do not expose it directly to the public internet.
