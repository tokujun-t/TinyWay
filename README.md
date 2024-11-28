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
SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiZXhhbXBsZVVzZXJEYXRhIiwiZXhwIjoxNzMyODIxMDIzfQ.gZNSp-R8O8LbyYVNVgXCfQFLfVp1ciVF_a8SGZm09Ic
```

Some suggestions:

APIs usually start with a underscore. You can control the routing
of these URLs through nginx or apisix to implement a mechanism to
prevent illegal access.