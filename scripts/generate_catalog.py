#!/usr/bin/env python3
"""Transform simplified DB config files into Backstage catalog entities."""

import glob
import sys
from pathlib import Path

import yaml


def load_configs(repo_root: Path) -> list[tuple[str, dict]]:
    """Load all *-config.yaml files, returning (db_type, config) pairs."""
    configs = []
    for path in sorted(repo_root.glob("*-config.yaml")):
        db_type = path.stem.replace("-config", "")
        with open(path) as f:
            config = yaml.safe_load(f)
        if config and "instances" in config:
            configs.append((db_type, config))
    return configs


def instance_to_catalog_entity(db_type: str, instance: dict) -> dict:
    """Convert a simplified instance definition to a Backstage Resource entity."""
    metadata = {"name": instance["name"]}

    if "description" in instance:
        metadata["description"] = instance["description"]
    if "tags" in instance:
        metadata["tags"] = instance["tags"]
    if "annotations" in instance:
        metadata["annotations"] = instance["annotations"]

    entity = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Resource",
        "metadata": metadata,
        "spec": {
            "type": db_type,
            "lifecycle": instance["lifecycle"],
            "system": instance["system"],
            "owner": f"group:default/{instance['owner']}",
            "properties": {
                "version": instance["spec"]["version"],
                "host": instance["connection"]["host"],
                "port": instance["connection"]["port"],
            },
        },
    }

    return entity


def generate_catalog(repo_root: Path) -> str:
    """Generate the full Backstage catalog YAML from all config files."""
    configs = load_configs(repo_root)
    entities = []

    for db_type, config in configs:
        for instance in config["instances"]:
            entities.append(instance_to_catalog_entity(db_type, instance))

    documents = []
    for entity in entities:
        documents.append(yaml.dump(entity, default_flow_style=False, sort_keys=False))

    return "---\n".join(documents)


def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "output"
    output_dir.mkdir(exist_ok=True)

    catalog_yaml = generate_catalog(repo_root)
    output_path = output_dir / "databases.yaml"
    output_path.write_text(catalog_yaml)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
