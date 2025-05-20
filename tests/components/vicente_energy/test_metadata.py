import json
import os
import pathlib

import yaml

REPO_ROOT = pathlib.Path(__file__).parents[3]
CC = REPO_ROOT / "custom_components" / "vicente_energy"


def test_manifest_exists_and_valid():
    with open(os.path.join(CC, "manifest.json")) as manifest_file:
        manifest = json.load(manifest_file)
    for key in [
        "domain",
        "name",
        "version",
        "documentation",
        "config_flow",
        "iot_class",
        "homeassistant",
    ]:
        assert key in manifest


def test_services_declared():
    with open(os.path.join(CC, "services.yaml")) as services_file:
        services = yaml.safe_load(services_file)
    assert "set_power_level" in services
    assert "reset_history" in services
