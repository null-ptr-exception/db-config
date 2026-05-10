# db-config

GitOps-style Internal Developer Platform for MariaDB instances.

## How it works

1. Apps declare database instances in `mariadb-config.yaml`
2. CI transforms declarations into:
   - **Backstage catalog entries** → pushed to `catalog` branch
   - **MariaDB operator CRDs** → pushed to `deployment` branch

## Config format

```yaml
instances:
  - name: db-1
    owner: app-a
    spec:
      instance_type: small    # small | medium | large
      storage_size: 10Gi
      version: "11.4"         # optional, defaults to 11.4
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Unique instance name (lowercase, alphanumeric + hyphens) |
| `owner` | yes | Owning application or team |
| `spec.instance_type` | yes | Resource tier: `small`, `medium`, `large` |
| `spec.storage_size` | yes | Persistent storage size (e.g. `10Gi`, `1Ti`) |
| `spec.version` | no | MariaDB version, defaults to `11.4` |

### Instance types

| Type | CPU | Memory |
|------|-----|--------|
| small | 1 | 2Gi |
| medium | 2 | 4Gi |
| large | 4 | 8Gi |

## Validation

The config is validated against `schema/mariadb-config.schema.json`.
