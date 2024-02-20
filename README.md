# Vindex

> "If there were no cruise missiles, Backfire bombers, Foxbats and Fencers, you wouldn't need the F-14. But these threats do exist, and the F-14 is the only aircraft that can effectively counter them... and survive." - Grumman Aerospace Corporation, 1970s

Vindex is a Discord bot written using discord.py, made for DCS communities.

## Install

Install the bot by cloning the repository, and using `pip install .` or `pdm install`.

## Setup an instance

Vindex uses [Docker](https://www.docker.com/products/docker-desktop/) to run.
While it has been first thought to not be built with it, it soon became a necessary switch to properly setup the bot, which uses the `prisma` CLI tool, but that could potentially be not available as expected without Docker.

### Prerequirements

You need to pass the set the following environment variable, you can do so using an `.env` file, which will be loaded automatically.

- `VINDEX_TOKEN` : Your bot's token.

### Using Docker

Docker provides supplementary environment variables to set:

#### Required

- `POSTGRES_PASSWORD` : This password will be used to connect to your database.
The password is only set the first time the database is created and not at each initilization. In case you forgot the password, remove the corresponding volume (Supposedly called `vindex_db`)
  - Expected type: `String`

#### Optional

##### Regarding the database

- `POSTGRES_USER`: The user used to connect to the PostgresSQL database. By default, `vindex`.
- `POSTGRES_DB`: The name of the database that will be created. By default, `Vindex`.
- `POSTGRES_PORT`: The port to use to connect to Postgres. The bot will automatically use that port if set. Do know that this port will still not be exposed on the internet. By default, `5432`.
- `DB_VOLUME_STUB`: A stub name for the name of the volume that will be given to where your database will be stored. This will result in something like `vindex_{stub}`, where `{stub}` will be the name you have set. By default, `db` (Result in `vindex_db`).

##### Regarding the bot

- `VINDEX_LOG_LEVEL` : Defines the level of log you wish to use when running the bot. Expected type: **Number**, from `0` to `50`.
- `VINDEX_PRISMA_GENERATE` : Generate the Prisma client & models before starting the bot. This should already be done when building the image, but its might be required for some odd cases. **Number**. `0` will deactivate. `1` or any other value will enable.
- `VINDEX_PRISMA_PUSH` : Push the tables to the database for development purposes. Please, I beg you, do not use this for production... Expected type: **Number**. `0` will deactivate. `1` or any other value will enable.
- `VINDEX_PRISMA_GENERATE` : Run migrations before starting the bot. This can only be done when the database is running. (hence, not possible during image build). Expected type: **Number**. `0` will deactivate. `1` or any other value will enable.

After that, you can launch a bot instance using the following command in your terminal:

`docker compose up`

### Without Docker

> ⚠️ This is not the recommended way to go in a production environment.

The bot can be setup without Docker by hosting a PostgreSQL daemon by yourself.

- Ensure you have a PostgreSQL database hosted.
- Set the following environment variables:
  - `VINDEX_DB_URL` : The URL used to connect to the database. See [Prisma documentation directly](https://www.prisma.io/docs/orm/prisma-schema/overview/data-sources).
- Install requirements using `pdm install` (Recommended)
  - If you do not wish to use PDM, feel free to use `pip install . -e` instead.
- Launch the bot using `pdm run python -m vindex`
  - Remove `pdm run` if you do not use PDM.

## Technologies

Vindex is proud of the technologies it uses.

- PDM
- Docker
- discord.py
- PostgreSQL
- Prisma
- Rich
- pygettext3/Babel
