.PHONY: build up down logs clean

build:
\tdocker compose build

up:
\tdocker compose up -d

down:
\tdocker compose down

logs:
\tdocker compose logs -f

clean:
\tdocker compose down -v --remove-orphans
\tdocker image prune -f
