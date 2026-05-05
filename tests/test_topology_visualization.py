"""Unit tests for topology page naming and resource-group coloring."""

import unittest
from pathlib import Path

import pandas as pd

from modules.network_graph import build_base_graph, apply_resource_group_coloring


class TestTopologyPageNaming(unittest.TestCase):
    """Validate Topology tab naming consistency in app router."""

    def test_app_routes_topology_tab(self):
        """Router should include Topology tab and renamed page path."""
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        content = app_path.read_text(encoding="utf-8")

        self.assertIn('st.Page("pages/4_Topology.py",  title="Topology"', content)
        self.assertNotIn('st.Page("pages/4_Network.py",   title="Network"', content)


class TestResourceGroupColoring(unittest.TestCase):
    """Validate resource-group overlay coloring for topology visualization."""

    def test_color_overlay_assigns_group_palette(self):
        """Nodes in same resource group should share color; different groups should differ."""
        inventory_df = pd.DataFrame(
            [
                {
                    "id": "/subscriptions/s/resourceGroups/rg-a/providers/Microsoft.Storage/storageAccounts/sa1",
                    "name": "sa1",
                    "type": "Microsoft.Storage/storageAccounts",
                    "service_category": "Storage",
                    "resource_group": "rg-a",
                    "provisioning_state": "Succeeded",
                },
                {
                    "id": "/subscriptions/s/resourceGroups/rg-a/providers/Microsoft.Storage/storageAccounts/sa2",
                    "name": "sa2",
                    "type": "Microsoft.Storage/storageAccounts",
                    "service_category": "Storage",
                    "resource_group": "rg-a",
                    "provisioning_state": "Succeeded",
                },
                {
                    "id": "/subscriptions/s/resourceGroups/rg-b/providers/Microsoft.Web/sites/app1",
                    "name": "app1",
                    "type": "Microsoft.Web/sites",
                    "service_category": "Web",
                    "resource_group": "rg-b",
                    "provisioning_state": "Succeeded",
                },
            ]
        )

        base_graph = build_base_graph(inventory_df)
        colored_graph, color_map = apply_resource_group_coloring(base_graph, inventory_df)

        node_sa1 = "/subscriptions/s/resourceGroups/rg-a/providers/Microsoft.Storage/storageAccounts/sa1"
        node_sa2 = "/subscriptions/s/resourceGroups/rg-a/providers/Microsoft.Storage/storageAccounts/sa2"
        node_app1 = "/subscriptions/s/resourceGroups/rg-b/providers/Microsoft.Web/sites/app1"

        self.assertEqual(colored_graph.nodes[node_sa1]["color"], colored_graph.nodes[node_sa2]["color"])
        self.assertNotEqual(colored_graph.nodes[node_sa1]["color"], colored_graph.nodes[node_app1]["color"])

        self.assertIn("rg-a", color_map)
        self.assertIn("rg-b", color_map)


if __name__ == "__main__":
    unittest.main()
