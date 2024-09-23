# piastri Project Directory

This project contains files dedicated to answering a specific question: how did Oscar Piastri’s rookie Formula 1 season compare to others in recent history?

The Medium blog post, the first in a series, elaborates on the purpose and objectives

This [Medium blog post](https://medium.com/@anthonydalke/oscar-piastri-star-in-the-making-c8d803d4f1f7), the first in a series, elaborates on the purpose and objectives.

## Project Structure

This repository contains the following files and directories:

- `src`: Directory for Python scripts
- `docs`: Directory for reference and EDA materials such as Jupyter notebooks
- `functions`: Directory for Python files defining functions imported in scripts saved to `src` directory
- `init-db.sql`: File containing SQL queries to create Postgres schemas, tables, and indexes
- `requirements.txt`: File specifying Python dependencies
- `Dockerfile`: File configuring the Docker container to utilize in this project
- `docker-compose.yml`: File building a Postgres database with `init-db.sql` and running an ETL script in the `src` directory

## Installation

1. Clone the repository:
```sh
git clone https://github.com/AnthonyDalke/f1data
cd f1data
```

2. Install Docker locally if not already installed

3. Create a `.env` file with values for key variables
```
POSTGRES_PASSWORD=<Define a password for the Postgres database the container will create>
POSTGRES_USER=<Define a username for the Postgres DB - e.g., 'f1_db'>
POSTGRES_DB=<Define a name for the Postgres DB - e.g., 'db'>
POSTGRES_HOST=<Define a host for the Postgres DB - e.g., 'db'>
POSTGRES_PORT=<Define a port for the Postgres DB - e.g., '5432'>
YEAR_START=<Specify the first year of data to pull>
YEAR_END=<Specify the final year of data to pull>
EMAIL_PW=<After configuring an app password for your email account, such as the following guide for Gmail explains, enter the app password https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237>
```

4. Build image and run container
```
docker-compose up --build
```

5. Download a SQL client like DBeaver to connect to and query data from the Postgres DB

## Contact
If you have any questions or feedback, feel free to contact me directly, at anthony.dalke@gmail.com. Thank you for visiting!