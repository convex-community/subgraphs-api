# Subgraphs api

Middleware for decentralized subgraph queries for Curve, Convex, Votium


Running for development:

Create an `.env` file with the following variables:

```
DB_ENDPOINT= (Cosmos db endpoint: https://xxxx.azure.com:443)
DB_KEY= (Database key)
```

And for production deployment:

```
EMAIL=admin@xxx.xxx
DOMAIN=xxx.xxx
```

Then run:

```
cp docker-compose.override.yaml.sample docker-compose.override.yaml
sudo docker-compose up
```