# Subgraphs api

Middleware for decentralized subgraph queries for Curve, Convex, Votium


Running for development:

Create an `.env` file with the following variables:

```
API_ENV= ('dev' or 'prod')
REDIS_PASSWORD= (Redis DB Passwrod)
GRAPH_API_KEY= (API Key for decentralized subgraphs)
PG_USER= (Postgres username)
PG_PASS = (Postgres password)
PG_DATABASE = (Postgres DB name)
PG_HOST = (Postgres DB Host)
PGA_MAIL = (PGAdmin email)
PGA_PASS = (PGAdmin password)
```

And for letsencrypt with production deployment:

```
EMAIL=admin@xxx.xxx
DOMAIN=xxx.xxx
```

Then run:

```
cp docker-compose.override.yaml.sample docker-compose.override.yaml
sudo docker-compose up
```
