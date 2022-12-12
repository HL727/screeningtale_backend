# About project

This project consists of 2 services

- An API using the Python framework [`FastAPI`](https://fastapi.tiangolo.com/)
  - Accessable at:
    - [`localhost:80/docs`](http://localhost:80/docs) in development.
    - [`api.[ourdomain]/docs`](https://api.ourdomain.com/docs) in production.
- An in-memory database using [`Redis`](https://redis.io/commands/#).

The development-config in `docker-compose.override.yml` also includes a service for inspecting the `Redis` database

- [`Redis-Insight`](https://docs.redislabs.com/latest/ri/installing/install-docker/)
  - Accessable at [`localhost:8001`](http://localhost:8001)
    Paste `"redis://redis"` into the field `Host` to auto-fill credentials.
    [Complete guide here.](https://developer.redislabs.com/explore/redisinsight/getting-started/?_ga=2.119900877.4344574.1627490266-1838434173.1622979283#step-4-add-redis-database)

---

# How to start project

Install [`docker`](https://docs.docker.com/docker-for-windows/wsl/) and [`poetry`](https://python-poetry.org/), preferably in a WSL enviroment.

[`Docker`](https://docs.docker.com/docker-for-windows/wsl/) is used for starting up the development enviroment, while [`poetry`](https://python-poetry.org/) is used for managing `python` packages. `Poetry` is not necessary to start developing, however it is quite useful in order to get type annotations, import declarations and linting inside VSCode.

---

## How to start development enviroment

While in the project root folder use the command:

> `docker-compose up`

Docker will create an enviroment for you with dependencies included. The current service-declaration inside the `docker-compose.yml` file is overridden using a file called `docker-compose.override.yml`. This override starts a single thread FastAPI-service with reloading enabled, suitable for development.

If you want to run the service in an enviroment closer to production you must specify which exact `docker-compose.yml` file to use. Without override (production-build):

> `docker-compose` -f docker-compose.yml `up`

---

## How to initalize poetry

Move into directory `./backend/app/`. With poetry installed, run the command

> `poetry install`

Poetry will then fetch all dependencies (and strict subdependencies of dependencies) declared in the `poetry.lock` and `pyproject.toml` files. Poetry is used as it manages packages version-specific, and also allows development dependencies.

### VSCode linting and typing using Poetry enviroment

Activate `Poetry` using `poetry shell` inside the directory `./backend/app/` where Poetry was initially configured. This will activate the Python enviroment.

Next up there are two ways enable `Poetry` inside your VSCode-editor.

- The easiest way:
  - With the Poetry enviroment activated using `poetry shell`. Run the command
    > code .
  - This will open VSCode in the current directory with `Poetry` enabled as the selected `Python Interpreter` (hopefully 🤞)
- The manual way

  - With the Poetry enviroment activated using `poetry shell`. Run the command
    > poetry show -v
  - This will return the path to the `Poetry` enviroment. Copy this path.
  - In `VSCode` run the command (`Ctrl` + `P` to access command-panel):

    > Python: Select Interpreter

    and paste the path to your Poetry virtual enviroment.

  - You may need to run the command

    > Python: Restart Language Server

    inside VSCode, for the changes to take place.

**Let us also enable our linter-configuration inside VSCode.**

Inside VSCode settings (`Ctrl` + `,` to access settings), search for `"python black"` and set the `"Python > Formatter: Provider"` to `"black"`.

I also recommend to enable formatting on save. Simply search for `"format on save"` and enable the setting `"Editor: Format On Save"`.

# Deployment

This project is designed to be deployed in a Docker Swarm cluster with Traefik as a load-balancer in front. The final deployment will therefore consist of two Docker stacks, namely:

- Our-service stack defined in `docker-compose.yml`
- A separate Traefik load-balancer

## Docker commands

Script to push docker-backend image to dockerhub:

> TAG=prod bash ./scripts/build-push.sh

Script to build docker images locally:

> TAG=prod bash ./scripts/build.sh

Script to deploy service locally:

> DOMAIN=ourdomain.com TRAEFIK_TAG=ourdomain.com STACK_NAME=ourdomain-com TAG=prod bash ./scripts/deploy.sh

Script to pull docker image in vps:

> docker pull danielschiotz/screeningtale-backend:prod

> docker pull danielschiotz/screeningtale-celery-backend:prod

Script to copy code from image to files in vps (get container code with docker ps after running deploy script):

> docker cp d1b010c6008d:/app/. ./backend/app


## Clustering database
The structure of our queries make a clustering of the database effective for increased performance. When the database is recently filled, run the commands below in pgAdmin. The CLUSTER command may take several hours and introduces an extensive block on the database.

> CLUSTER historical USING ix_historical_country_date;

> ANALYZE historical;

To maintain the clustering, we should also recluster every now and then. With a fill-factor of 90, the clustering shouldn't start degrading before a year (10% increase) has gone since last clustering. Reclustering is done with the following commands:

> CLUSTER historical;

> ANALYZE historical;

## Setting up a VPS

Run commands

> apt update

> apt upgrade

Create user with privileges

> adduser `yournewusername`

> _#_ usermod -aG sudo `yournewusername`

Switch user to new user

> su `yournewusername`

### Install docker on VPS

- Link to [documentation](https://docs.docker.com/engine/install/ubuntu/)

### Install docker-compose

- Link to [documentation](https://docs.docker.com/compose/install/#install-compose-on-linux-systems)

## Installing Traefik load-balancer

To set up our load-balancer we will follow the steps from [dockerswarm.rocks](https://dockerswarm.rocks/traefik/).

---

We will start by creating a network called `traefik-public`. This network will be referenced inside our `docker-compose.yml`.

> docker network create --driver=overlay traefik-public

Next up we will determine which `node` will be used to store our HTTPS-certificates from `Let's Encrypt`. First up we are extracting out a node identification (from our current VPS/node).

> export NODE_ID=$(docker info -f '{{.Swarm.NodeID}}')

Then we'll manually add a label to our node. This label is used in `traefik.yml` under `"volume:"`.

> docker node update --label-add traefik-public.traefik-public-certificates=true $NODE_ID

---

`Let's Encrypt` needs our email to hand out certificates, so let's export it as a variable.

> export EMAIL=admin@example.com

> export DOMAIN=traefik.ourdomain.com

---

To limit access to `Traefik`'s dashboard and API, we'll use `Basic HTTP Authentication` with the credentials username and password given.

> export USERNAME=admin

> export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)

---

Finally we'll deploy our load-balancer onto our swarm using [docker stack deploy](https://docs.docker.com/engine/reference/commandline/stack_deploy/).

> docker stack deploy -c traefik.yml traefik

We can assert that the service is running by running the command `

> docker service ls

## Scaling services in production

To scale a service while in production run the command `docker service scale SERVICE=REPLICAS` from a manager node in the swarm.

For example with 4 instances of our `backend`-service:

> docker service scale `[STACK_NAME]_backend`=4

(To get the servicename run the command `docker service ls`.)

---

For our FastAPI applications there is no significant advantage to scale up a service with number of replicas exceeding the amount of nodes in the swarm, since [`gunicorn`](https://gunicorn.org/) (our HTTP server) uses multiple workers scaled automatically by CPU core-count (full config found in the file `gunicorn.conf.py`).

# Database migrations

Database migrations is handled by alembic. Commands for reference:

> docker-compose exec backend bash

> alembic revision --autogenerate -m "Did something"

> alembic upgrade head
