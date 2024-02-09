<div align="center">
    <h1>Vindex</h1>
</div>

> "If there were no cruise missiles, Backfire bombers, Foxbats and Fencers, you wouldn't need the F-14. But these threats do exist, and the F-14 is the only aircraft that can effectively counter them... and survive." - Grumman Aerospace Corporation, 1970s

Vindex is a Discord bot written using discord.py, made for DCS communities.

## Install

Install the bot by cloning the repository, and using `pip install .` or `pdm install`.

## Setup

To setup a Vindex instance, you need to set a few important environment variables.
The bot runs thanks to Prisma and PostgreSQL. You first need to install and setup a correct installation of PostgreSQL first.

The environment variables that are necessary are:

- `VINDEX_TOKEN` : The token that will be used for the bot to connect.
- `VINDEX_DB_URL` : The URL to use to connect to the database. See [Prisma documentation directly](https://www.prisma.io/docs/orm/prisma-schema/overview/data-sources).

## Technologies

Vindex is proud of the technologies it uses.

- PDM
- discord.py
- PostgreSQL
- Prisma
- Click/Rich
- pygettext3/Babel
