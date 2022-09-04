# Subgraphs api

Middleware for decentralized subgraph queries for Curve, Convex, Votium


Running for development:

Create an `.env` file with the following variables:

```
API_ENV= ('dev' or 'prod')
DB_ENDPOINT= (Cosmos db endpoint: https://xxxx.azure.com:443)
DB_KEY= (Database key)
DB_NAME= (Database name)
REDIS_PASSWORD= (Redis DB Passwrod)
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
