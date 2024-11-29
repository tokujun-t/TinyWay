# TinyWay

## API
See [sample.http](sample.http)

## Depoly

Pull the project, then use a reverse proxy to map domain names,
add identity verification logic, etc.

We recommend that one domain name corresponds to one instance.

```dotenv
REDIS_HOST=localhost
INDEX_REDIRECT_URL=https://www.stayforge.io
```

Some suggestions:

APIs usually start with a underscore. You can control the routing
of these URLs through nginx or apisix to implement a mechanism to
prevent illegal access.