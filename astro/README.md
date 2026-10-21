# Optional Astro setup

This is documentation, not a ready-to-run Astro project.

1. Install Docker Desktop and the Astro CLI.
2. Create a separate folder and run `astro dev init` in that folder.
3. Copy `dags/people_counting_dag.py` into the Astro project's `dags/`.
4. Install DVC, MLflow, pandas, scikit-learn, PyYAML and joblib in the
   Astro container (using its requirements.txt).
5. Mount this ML project at `/usr/local/airflow/ml_project` inside the
   Airflow containers, or change the path in the DAG.
6. Run `astro dev start` from the Astro project.

Without steps 4 and 5, the DAG cannot execute the ML pipeline.
Airflow schedules the pipeline; DVC decides which stages need rerunning.
