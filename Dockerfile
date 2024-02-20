# syntax=docker/dockerfile:1

FROM python:3.12 AS build

ENV VINDEX_PRISMA_GENERATE=0 \
    VINDEX_PRISMA_PUSH=0 \
    VINDEX_PRISMA_MIGRATE=0

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

WORKDIR /app

# Requirements first, should be cached (hopefully)
# Yes. README is a requirement.
COPY README.md pyproject.toml pdm.lock /app/
RUN pip install .

# This will help caching the prisma executable
RUN prisma -v

# Launch Prisma generation, if required
COPY ./prisma /app/prisma
RUN prisma generate

# Install the rest of the package
COPY ./src /app/src/
RUN pip install . --no-deps

CMD ["python", "-m", "vindex"]
