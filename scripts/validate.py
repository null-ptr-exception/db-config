#!/usr/bin/env python3
"""Validate all *-config.yaml files against the JSON schema."""

import json
import sys
from pathlib import Path

import jsonschema
import yaml


def main():
    repo_root = Path(__file__).resolve().parent.parent
    schema_path = repo_root / "schema" / "db-config.schema.json"

    with open(schema_path) as f:
        schema = json.load(f)

    config_files = sorted(repo_root.glob("*-config.yaml"))
    if not config_files:
        print("ERROR: No config files found")
        sys.exit(1)

    errors = []
    for path in config_files:
        with open(path) as f:
            config = yaml.safe_load(f)

        try:
            jsonschema.validate(config, schema)
            print(f"PASS: {path.name}")
        except jsonschema.ValidationError as e:
            print(f"FAIL: {path.name}: {e.message}")
            errors.append((path.name, e.message))

    if errors:
        sys.exit(1)

    print(f"\nAll {len(config_files)} config files valid.")


if __name__ == "__main__":
    main()
