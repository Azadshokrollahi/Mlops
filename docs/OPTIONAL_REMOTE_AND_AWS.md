# Optional remote tools

## DagsHub + DVC
This 10-row example deliberately commits the tiny CSV to Git so GitHub
Actions can run without data-storage credentials. DVC still manages the
generated pipeline outputs and the stage dependency graph.

For a large real dataset, use `dvc add data/raw/people_count.csv`, configure
a DagsHub DVC remote, then `dvc push`. GitHub Actions must authenticate and
run `dvc pull` before `dvc repro`. Do not commit credentials.

## DagsHub + MLflow
The default MLflow store is local `mlruns/`. To track remotely, set the
environment variables `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`,
and `MLFLOW_TRACKING_PASSWORD` using the endpoint and credentials supplied
by DagsHub. Rerun `dvc repro -f evaluate`. Do not commit access tokens.

## Docker Hub
GitHub Actions CD publishes `YOUR_USER/people-counting-api:v1` when you
configure `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets.
It does NOT deploy to AWS.

## AWS
On a configured server with Docker, you could `docker pull` the published
image and `docker run` it. Proper authentication, HTTPS, networking,
secrets, observability and security are required before public deployment.
