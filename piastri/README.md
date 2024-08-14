# Project Structure

This repository contains the following files and directories:

- `src`: Directory for Python scripts
- `docs`: Directory for reference and EDA materials such as Jupyter notebooks
- `functions`: Directory for Python files defining functions imported in scripts saved to `src` directory
- `init-db.sql`: File containing SQL queries to create Postgres schemas, tables, and indexes
- `requirements.txt`: File specifying Python dependencies
- `Dockerfile`: File configuring the Docker container to utilize in this project
- `docker-compose.yml`: File building a Postgres database with `init-db.sql` and running an ETL script in the `src` directory