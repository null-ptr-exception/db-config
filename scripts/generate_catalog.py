#!/usr/bin/env python3
"""Transform simplified DB config files into Backstage catalog entities."""

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
        if config and "resources" in config:
            configs.append((db_type, config))
    return configs


def resource_to_entities(db_type: str, resource: dict) -> list[dict]:
    """Convert a simplified resource into a Backstage Resource + Instance entities."""
    name = resource["name"]
    owner = resource["owner"]

    resource_entity = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Resource",
        "metadata": {"name": name},
        "spec": {
            "type": db_type,
            "lifecycle": resource["lifecycle"],
            "system": owner,
            "owner": f"group:default/{owner}-devs",
        },
    }

    instance_entities = []
    for inst in resource.get("instances", []):
        site = inst["site"]
        stage = inst["stage"]
        instance_name = f"{name}-{site}-{stage}"

        properties = {}
        version = inst.get("version") or resource.get("version")
        if version:
            properties["version"] = version

        metadata = {"name": instance_name}
        if "maintenance" in inst:
            metadata["annotations"] = {"maintenance/scheduled": inst["maintenance"]}

        instance_entity = {
            "apiVersion": "dbms.io/v1alpha1",
            "kind": "Instance",
            "metadata": metadata,
            "spec": {
                "target": f"resource:default/{name}",
                "site": f"site:default/{site}",
                "stage": stage,
            },
        }
        if properties:
            instance_entity["spec"]["properties"] = properties

        instance_entities.append(instance_entity)

    return [resource_entity] + instance_entities


def generate_catalog(repo_root: Path, output_dir: Path):
    """Generate per-type Backstage catalog YAML files."""
    configs = load_configs(repo_root)

    for db_type, config in configs:
        entities = []
        for resource in config["resources"]:
            entities.extend(resource_to_entities(db_type, resource))

        documents = []
        for entity in entities:
            documents.append(yaml.dump(entity, default_flow_style=False, sort_keys=False))

        output_path = output_dir / f"{db_type}.yaml"
        output_path.write_text("---\n".join(documents))
        print(f"Generated {output_path} ({len(entities)} entities)")


def main():
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = repo_root / "output"
    output_dir.mkdir(exist_ok=True)
    generate_catalog(repo_root, output_dir)


if __name__ == "__main__":
    main()
