import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from append_verified_grants import append_verified_grants
from validate_grant_schema import GrantValidator


class EligibilityChecksTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[4]
        self.grant = json.loads((root / "grants/newest_grants.json").read_text())["grants"][0]
        self.grant["eligibility"] = {
            "stage": ["all"],
            "team_size_min": None,
            "team_size_max": None,
            "geography": ["GLOBAL"],
            "restrictions": "Individuals aged 18 or older",
            "eligibility_checks": ["Individual applicants must be at least 18"],
        }

    def test_validator_accepts_document_requirements_without_effort_rating(self):
        self.grant["requirements"] = {
            "key_requirements": ["Project proposal"],
            "focus_areas": ["Research"],
        }
        valid, errors, _ = GrantValidator().validate_grant(self.grant)
        self.assertTrue(valid, errors)

    def test_validator_accepts_checks_and_rejects_missing_or_invalid_checks(self):
        valid, errors, _ = GrantValidator().validate_grant(self.grant)
        self.assertTrue(valid, errors)
        for value in (None, []):
            grant = copy.deepcopy(self.grant)
            grant["eligibility"]["eligibility_checks"] = value
            self.assertTrue(GrantValidator().validate_grant(grant)[0])
        for missing in (False, True):
            with self.subTest(missing=missing):
                grant = copy.deepcopy(self.grant)
                if missing:
                    del grant["eligibility"]["eligibility_checks"]
                else:
                    grant["eligibility"]["eligibility_checks"] = "not an array"
                valid, errors, _ = GrantValidator().validate_grant(grant)
                self.assertFalse(valid)
                self.assertTrue(any("eligibility.eligibility_checks" in error for error in errors))

    def test_append_preserves_checks_and_normalizes_null(self):
        for checks, expected in ((["Individual applicants must be at least 18"], ["Individual applicants must be at least 18"]), (None, [])):
            with self.subTest(checks=checks), tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()) / "opencode") as directory:
                staging = Path(directory) / "staging.json"
                target = Path(directory) / "target.json"
                grant = copy.deepcopy(self.grant)
                grant["eligibility"]["eligibility_checks"] = checks
                staging.write_text(json.dumps([grant]))
                target.write_text('{"grants": []}')
                with contextlib.redirect_stdout(io.StringIO()):
                    success, count, errors = append_verified_grants(str(staging), str(target))
                self.assertTrue(success, errors)
                self.assertEqual(count, 1)
                eligibility = json.loads(target.read_text())["grants"][0]["eligibility"]
                self.assertEqual(eligibility["eligibility_checks"], expected)
                self.assertEqual(eligibility.keys(), grant["eligibility"].keys())


if __name__ == "__main__":
    unittest.main()
