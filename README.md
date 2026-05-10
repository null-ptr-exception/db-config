# db-config

GitOps-style Internal Developer Platform for database instances.

## How it works

1. Teams declare database instances in per-type config files on `main`:
   - `mariadb-config.yaml`
   - `mongodb-config.yaml`
   - `redis-config.yaml`
2. CI transforms declarations into:
   - **Backstage catalog entities** → pushed to `catalog` branch
   - **Kubernetes operator CRDs** → pushed to `deployment` branch

## Config format

```yaml
instances:
  - name: mariadb-app-a-prod
    system: app-a
    owner: app-a-devs
    lifecycle: production
    description: Production MariaDB
    tags: [critical, production]
    annotations:                    # optional
      maintenance/scheduled: "20260601"
    spec:
      version: "11.4"
      instance_type: small
      storage_size: 10Gi
    connection:
      host: mariadb01.internal
      port: 3306
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Unique instance name (lowercase, alphanumeric + hyphens) |
| `system` | yes | Backstage system this resource belongs to |
| `owner` | yes | Owning group name (expanded to `group:default/<owner>` in catalog) |
| `lifecycle` | yes | `production`, `staging`, or `development` |
| `description` | no | Human-readable description |
| `tags` | no | List of tags |
| `annotations` | no | Key-value annotations |
| `spec.version` | yes | Database engine version |
| `spec.instance_type` | yes | Resource tier: `small`, `medium`, `large` |
| `spec.storage_size` | yes | Persistent storage size (e.g. `10Gi`, `1Ti`) |
| `connection.host` | yes | Database hostname |
| `connection.port` | yes | Database port |

### Instance types

| Type | CPU | Memory |
|------|-----|--------|
| small | 1 | 2Gi |
| medium | 2 | 4Gi |
| large | 4 | 8Gi |

## Validation

Configs are validated against `schema/db-config.schema.json`.

## Branch structure

| Branch | Content |
|--------|---------|
| `main` | Simplified source-of-truth config files |
| `catalog` | Generated Backstage catalog entities |
| `deployment` | Generated Kubernetes operator CRDs |
