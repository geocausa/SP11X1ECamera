#!/usr/bin/env python3
"""Synthetic negative gate tests: metadata only, no hardware, no photos."""
import copy
import importlib.util
import unittest
from pathlib import Path

MOD = Path(__file__).with_name("preflight.py")
spec = importlib.util.spec_from_file_location("rear_pix_preflight", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def sample():
    unified = m.read_json(m.IG)
    front = m.read_json(m.HY / "DISCOVERY.json")
    front_result = m.read_json(m.HY / "RESULT.json")
    stats = m.read_json(m.Z)
    rear = m.read_json(m.LR)
    props = {(p, prop): m.dt_get(p, prop, kind)
             for p in [m.REAR, m.FRONT, m.CAMSS]
             for prop, kind in [("compatible", "s")]}
    for endpoint in m.ENDPOINTS.values():
        for prop in ("phandle", "remote-endpoint", "bus-type", "data-lanes"):
            props[(endpoint, prop)] = m.dt_get(endpoint, prop)
    return unified, front, front_result, stats, rear, props

class RearPixGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = sample()

    def evaluate(self, mutate=None):
        u, f, fr, s, r, props = copy.deepcopy(self.fixture)
        if mutate:
            mutate(u, f, fr, s, r, props)
        return m.check(u, f, fr, s, r, lambda path, prop, kind="x": props[(path, prop)])

    def test_accepted_source_evidence(self):
        result = self.evaluate()
        self.assertEqual(result["rear_native_PIX_frames_proven"], 0)
        self.assertIn("NOT_HARDWARE_PROVEN", result["gate"])

    def test_reject_front_route_substituted_for_rear(self):
        with self.assertRaisesRegex(m.GateError, "rear RAW route"):
            self.evaluate(lambda u, f, fr, s, r, p: u.__setitem__("rear_route", u["front_route"]))

    def test_reject_front_bayer_substituted_for_rear(self):
        with self.assertRaisesRegex(m.GateError, "rear RAW transport"):
            self.evaluate(lambda u, f, fr, s, r, p:
                          r["rear_ov13858"].__setitem__("raw_format", f["format"]))

    def test_reject_incorrect_rear_endpoint(self):
        with self.assertRaisesRegex(m.GateError, "nonreciprocal"):
            self.evaluate(lambda u, f, fr, s, r, p:
                          p.__setitem__((m.ENDPOINTS["rear_camss"], "remote-endpoint"), "dead"))

    def test_reject_wrong_rear_bus(self):
        with self.assertRaisesRegex(m.GateError, "bus mismatch"):
            self.evaluate(lambda u, f, fr, s, r, p:
                          p.__setitem__((m.ENDPOINTS["rear_sensor"], "bus-type"), "1"))

    def test_reject_missing_front_hardware_proof(self):
        with self.assertRaisesRegex(m.GateError, "front bounded PIX"):
            self.evaluate(lambda u, f, fr, s, r, p: fr.__setitem__("frames", 0))

    def test_reject_unpaired_stats(self):
        with self.assertRaisesRegex(m.GateError, "paired hardware 3A"):
            self.evaluate(lambda u, f, fr, s, r, p:
                          s.__setitem__("paired_tlbg_stats3a_identity_exact", False))

if __name__ == "__main__":
    unittest.main(verbosity=2)
