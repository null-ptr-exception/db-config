#!/usr/bin/env python3
"""Generate sample source YAML configs with randomized instances."""

import random
from pathlib import Path

import yaml

SITES = [
    "us-west-1", "us-west-2", "us-east-1", "us-east-2",
    "eu-west-1", "eu-central-1",
    "ap-southeast-1", "ap-northeast-1", "ap-south-1", "sa-east-1",
]
STAGES = ["test", "staging", "production"]
OWNERS = ["app-a", "app-b", "app-c", "app-d", "app-e"]
INSTANCE_TYPES = ["small", "medium", "large"]
STORAGE_SIZES = {"small": "10Gi", "medium": "50Gi", "large": "100Gi"}

DB_TYPES = {
    "mariadb": {"count": 50, "versions": ["10.11", "11.4"]},
    "mongodb": {"count": 30, "versions": ["6.0", "7.0"]},
    "redis":   {"count": 20, "versions": ["7.0", "7.2"]},
}

random.seed(42)


def generate_instances():
    num_sites = random.randint(1, len(SITES))
    sites = random.sample(SITES, num_sites)
    instances = []
    for site in sorted(sites):
        num_stages = random.randint(1, len(STAGES))
        stages = random.sample(STAGES, num_stages)
        for stage in sorted(stages, key=STAGES.index):
            itype = random.choice(INSTANCE_TYPES)
            instances.append({
                "site": site,
                "stage": stage,
                "instance_type": itype,
                "storage_size": STORAGE_SIZES[itype],
            })
    return instances


def generate_config(db_type: str, count: int, versions: list[str]) -> dict:
    resources = []
    for i in range(1, count + 1):
        name = f"{db_type}-{i:03d}"
        resource = {
            "name": name,
            "owner": random.choice(OWNERS),
            "lifecycle": "production",
            "version": random.choice(versions),
            "instances": generate_instances(),
        }
        resources.append(resource)
    return {"resources": resources}


def main():
    repo_root = Path(__file__).resolve().parent.parent

    total_resources = 0
    total_instances = 0

    for db_type, opts in DB_TYPES.items():
        config = generate_config(db_type, opts["count"], opts["versions"])
        path = repo_root / f"{db_type}-config.yaml"
        path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))

        n_resources = len(config["resources"])
        n_instances = sum(len(r["instances"]) for r in config["resources"])
        total_resources += n_resources
        total_instances += n_instances
        print(f"{path.name}: {n_resources} resources, {n_instances} instances")

    print(f"\nTotal: {total_resources} resources, {total_instances} instances")


if __name__ == "__main__":
    main()
