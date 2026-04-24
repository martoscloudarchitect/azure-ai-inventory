"""Unit tests for modules/inventory_optimizer.py"""

import unittest
from datetime import datetime, timedelta

from modules import inventory_optimizer as opt
from modules.constants import (
    CRITICAL_RESOURCE_TYPES,
    PROFILE_RESOURCE_FILTERS,
    RESOURCE_TYPE_PRIORITIES,
    SAMPLING_THRESHOLD_MIN,
)


class TestTokenEstimation(unittest.TestCase):
    """Test token estimation functions."""

    def test_estimate_token_count_empty(self):
        """Empty text should estimate to 0 tokens."""
        result = opt.estimate_token_count("")
        self.assertEqual(result, 0)

    def test_estimate_token_count_small(self):
        """Small text should estimate to small token count."""
        # "hello" is about 5 bytes, should be ~1 token
        result = opt.estimate_token_count("hello")
        self.assertGreater(result, 0)
        self.assertLess(result, 10)

    def test_estimate_token_count_1kb(self):
        """~1 KB should estimate to ~224 tokens."""
        text = "x" * 1024  # Exactly 1024 bytes
        result = opt.estimate_token_count(text)
        # Should be approximately 224 tokens (224 tokens/KB ratio)
        # Allow ±10 token variance
        self.assertGreater(result, 214)
        self.assertLess(result, 234)

    def test_estimate_prompt_tokens(self):
        """Prompt estimation should combine system + user."""
        system = "You are an expert."
        user = "Analyze the following data: " + "x" * 1000
        result = opt.estimate_prompt_tokens(system, user)
        # Should be greater than 0
        self.assertGreater(result, 0)
        # Should be less than 10K (sanity check)
        self.assertLess(result, 10000)


class TestSamplingThreshold(unittest.TestCase):
    """Test sampling threshold logic."""

    def test_should_sample_small_inventory(self):
        """Small inventory (< threshold) should not need sampling."""
        small = [{"type": "Microsoft.Compute/virtualMachines"} for _ in range(50)]
        result = opt.should_sample(small)
        self.assertFalse(result)

    def test_should_sample_at_threshold(self):
        """Inventory exactly at threshold should sample."""
        at_threshold = [{"type": "Microsoft.Compute/virtualMachines"}
                       for _ in range(SAMPLING_THRESHOLD_MIN + 1)]
        result = opt.should_sample(at_threshold)
        self.assertTrue(result)

    def test_should_sample_large_inventory(self):
        """Large inventory should need sampling."""
        large = [{"type": "Microsoft.Compute/virtualMachines"} for _ in range(500)]
        result = opt.should_sample(large)
        self.assertTrue(result)

    def test_should_sample_empty(self):
        """Empty inventory should not sample."""
        result = opt.should_sample([])
        self.assertFalse(result)


class TestTargetSamplePercentage(unittest.TestCase):
    """Test target sample percentage calculation."""

    def test_target_small_inventory(self):
        """Small inventory: keep 100%."""
        result = opt.get_target_sample_percentage(50)
        self.assertEqual(result, 1.0)

    def test_target_medium_inventory(self):
        """100–300 resources: keep 80%."""
        result = opt.get_target_sample_percentage(200)
        self.assertEqual(result, 0.8)

    def test_target_large_inventory(self):
        """300–500 resources: keep 60%."""
        result = opt.get_target_sample_percentage(400)
        self.assertEqual(result, 0.6)

    def test_target_very_large_inventory(self):
        """500+ resources: keep 40%."""
        result = opt.get_target_sample_percentage(1000)
        self.assertEqual(result, 0.4)


class TestResourcePriority(unittest.TestCase):
    """Test resource priority calculation."""

    def test_priority_vm(self):
        """VMs should have high priority."""
        vm = {"type": "Microsoft.Compute/virtualMachines"}
        priority = opt.get_resource_priority(vm)
        self.assertGreater(priority, 100)

    def test_priority_database(self):
        """Databases should have high priority."""
        db = {"type": "Microsoft.Sql/servers/databases"}
        priority = opt.get_resource_priority(db)
        self.assertGreater(priority, 90)

    def test_priority_managed_identity(self):
        """Managed identities should have low priority."""
        mi = {"type": "Microsoft.ManagedIdentity/userAssignedIdentities"}
        priority = opt.get_resource_priority(mi)
        self.assertLess(priority, 50)

    def test_priority_unknown(self):
        """Unknown types should get default priority."""
        unknown = {"type": "Microsoft.Unknown/unknownType"}
        priority = opt.get_resource_priority(unknown)
        self.assertGreater(priority, 0)
        self.assertLess(priority, 100)

    def test_priority_without_type(self):
        """Resources without type should get default priority."""
        no_type = {}
        priority = opt.get_resource_priority(no_type)
        self.assertGreater(priority, 0)


class TestCriticalResourceDetection(unittest.TestCase):
    """Test critical resource detection."""

    def test_is_critical_vm(self):
        """VMs should be critical."""
        vm = {"type": "Microsoft.Compute/virtualMachines"}
        result = opt.is_critical_resource(vm)
        self.assertTrue(result)

    def test_is_critical_database(self):
        """Databases should be critical."""
        db = {"type": "Microsoft.Sql/servers/databases"}
        result = opt.is_critical_resource(db)
        self.assertTrue(result)

    def test_is_critical_managed_identity(self):
        """Managed identities should NOT be critical."""
        mi = {"type": "Microsoft.ManagedIdentity/userAssignedIdentities"}
        result = opt.is_critical_resource(mi)
        self.assertFalse(result)

    def test_is_critical_partial_match(self):
        """Partial type matches should work."""
        # Any resource starting with "Microsoft.Compute" should match
        compute = {"type": "Microsoft.Compute/disks"}
        # Note: disks are not in CRITICAL_RESOURCE_TYPES, so should be False
        # But let's verify the logic works
        result = opt.is_critical_resource(compute)
        # This should be False because disks are not explicitly critical
        self.assertFalse(result)


class TestProfileFiltering(unittest.TestCase):
    """Test profile-specific filtering."""

    def create_mixed_inventory(self):
        """Create a sample inventory with various resource types."""
        return [
            {"type": "Microsoft.Compute/virtualMachines", "name": "vm-1"},
            {"type": "Microsoft.Storage/storageAccounts", "name": "storage-1"},
            {"type": "Microsoft.Sql/servers/databases", "name": "db-1"},
            {"type": "Microsoft.Network/virtualNetworks", "name": "vnet-1"},
            {"type": "Microsoft.ManagedIdentity/userAssignedIdentities", "name": "identity-1"},
            {"type": "Microsoft.Insights/components", "name": "appinsights-1"},
        ]

    def test_filter_architecture_keeps_all(self):
        """Architecture profile should keep all resources."""
        inventory = self.create_mixed_inventory()
        result = opt.apply_profile_filter(inventory, "architecture")
        self.assertEqual(len(result), len(inventory))

    def test_filter_security_prioritizes_vms_and_storage(self):
        """Security profile should prioritize VMs and storage."""
        inventory = self.create_mixed_inventory()
        result = opt.apply_profile_filter(inventory, "security")
        # Result should be same size but reordered
        self.assertEqual(len(result), len(inventory))
        # First few should be relevant types (VMs, storage, etc.)
        first_types = [r.get("type") for r in result[:3]]
        self.assertTrue(any("Compute" in t or "Storage" in t for t in first_types))

    def test_filter_networking_prioritizes_vnets(self):
        """Networking profile should prioritize network resources."""
        inventory = self.create_mixed_inventory()
        result = opt.apply_profile_filter(inventory, "networking")
        # VNet should be early in the list
        type_list = [r.get("type") for r in result]
        vnet_index = next((i for i, t in enumerate(type_list)
                          if "Network/virtualNetworks" in t), -1)
        self.assertGreater(vnet_index, -1)
        # Should be in first half of list
        self.assertLess(vnet_index, len(result) / 2)

    def test_filter_governance_keeps_all(self):
        """Governance profile needs full view."""
        inventory = self.create_mixed_inventory()
        result = opt.apply_profile_filter(inventory, "governance")
        self.assertEqual(len(result), len(inventory))

    def test_filter_unknown_profile_keeps_all(self):
        """Unknown profile should keep all resources."""
        inventory = self.create_mixed_inventory()
        result = opt.apply_profile_filter(inventory, "unknown_profile")
        self.assertEqual(len(result), len(inventory))


class TestSampling(unittest.TestCase):
    """Test inventory sampling."""

    def create_sample_inventory(self, size=100):
        """Create a sample inventory of given size."""
        now = datetime.now()
        inventory = []
        types = [
            "Microsoft.Compute/virtualMachines",
            "Microsoft.Sql/servers/databases",
            "Microsoft.Storage/storageAccounts",
            "Microsoft.ManagedIdentity/userAssignedIdentities",
            "Microsoft.Insights/diagnosticSettings",
        ]
        for i in range(size):
            resource = {
                "type": types[i % len(types)],
                "name": f"resource-{i}",
                "id": f"/subscriptions/sub/resourceGroups/rg/providers/{types[i % len(types)]}/{i}",
                "properties": {
                    "modificationTime": (now - timedelta(days=size - i)).isoformat(),
                }
            }
            inventory.append(resource)
        return inventory

    def test_sample_small_inventory_unchanged(self):
        """Small inventory should not be sampled."""
        small = self.create_sample_inventory(50)
        result = opt.sample_inventory(small)
        self.assertEqual(len(result), len(small))

    def test_sample_large_inventory_reduces_size(self):
        """Large inventory should be reduced."""
        large = self.create_sample_inventory(300)
        result = opt.sample_inventory(large, profile="architecture")
        # Should be smaller than original
        self.assertLess(len(result), len(large))
        # But not tiny
        self.assertGreater(len(result), len(large) * 0.5)

    def test_sample_preserves_critical_resources(self):
        """Sampling should keep all critical resources."""
        # Create inventory with mostly non-critical resources
        inventory = self.create_sample_inventory(200)
        # Add a few critical VMs at the end
        for i in range(5):
            inventory.append({
                "type": "Microsoft.Compute/virtualMachines",
                "name": f"critical-vm-{i}",
                "id": f"/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/{i}",
                "properties": {"modificationTime": datetime.now().isoformat()},
            })

        result = opt.sample_inventory(inventory, profile="architecture")
        # Should contain all critical VMs
        critical_vms_in_result = [r for r in result
                                  if r.get("name", "").startswith("critical-vm")]
        self.assertEqual(len(critical_vms_in_result), 5)

    def test_sample_respects_target_percentage(self):
        """Sampling should respect target percentage."""
        large = self.create_sample_inventory(500)
        target_pct = 0.5
        result = opt.sample_inventory(large, target_percentage=target_pct)
        # Should be approximately target size (allow ±10% variance due to critical resources)
        expected_size = int(len(large) * target_pct)
        tolerance = int(len(large) * 0.1)  # ±10%
        self.assertGreater(len(result), expected_size - tolerance)
        self.assertLessEqual(len(result), expected_size + tolerance)

    def test_sample_empty_inventory(self):
        """Empty inventory should remain empty."""
        result = opt.sample_inventory([])
        self.assertEqual(len(result), 0)


class TestSamplingReport(unittest.TestCase):
    """Test sampling report generation."""

    def test_report_generation(self):
        """Sampling report should show reduction stats."""
        original = [{"type": "Microsoft.Compute/virtualMachines"} for _ in range(100)]
        sampled = [{"type": "Microsoft.Compute/virtualMachines"} for _ in range(60)]
        
        report = opt.get_sampling_report(original, sampled)
        
        self.assertEqual(report["original_count"], 100)
        self.assertEqual(report["sampled_count"], 60)
        self.assertEqual(report["resources_dropped"], 40)
        self.assertEqual(report["reduction_percentage"], 40.0)
        self.assertTrue(report["sampled"])

    def test_report_no_sampling(self):
        """Report when no sampling occurs."""
        original = [{"type": "Microsoft.Compute/virtualMachines"} for _ in range(100)]
        
        report = opt.get_sampling_report(original, original)
        
        self.assertEqual(report["original_count"], 100)
        self.assertEqual(report["sampled_count"], 100)
        self.assertEqual(report["resources_dropped"], 0)
        self.assertEqual(report["reduction_percentage"], 0.0)
        self.assertFalse(report["sampled"])


class TestInventoryToJson(unittest.TestCase):
    """Test inventory JSON conversion."""

    def test_inventory_to_json(self):
        """Inventory should convert to valid JSON."""
        inventory = [
            {"type": "Microsoft.Compute/virtualMachines", "name": "vm-1"},
            {"type": "Microsoft.Storage/storageAccounts", "name": "storage-1"},
        ]
        result = opt.inventory_to_json_string(inventory)
        
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        
        self.assertIn("inventory", parsed)
        self.assertEqual(len(parsed["inventory"]), 2)
        self.assertEqual(parsed["inventory"][0]["name"], "vm-1")

    def test_inventory_to_json_empty(self):
        """Empty inventory should convert to JSON with empty list."""
        result = opt.inventory_to_json_string([])
        
        import json
        parsed = json.loads(result)
        
        self.assertEqual(len(parsed["inventory"]), 0)


if __name__ == "__main__":
    unittest.main()
