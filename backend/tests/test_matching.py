import json
import unittest
from datetime import date

from app.services.matchscore import score_candidate


class MatchingTests(unittest.TestCase):
    def test_full_match_scores_100(self):
        profile = {
            "languages_json": json.dumps([{"id": "latvian", "name": "Latvian", "level": "C1"}]),
            "licenses_json": json.dumps(["forklift"]),
            "skill_ids_json": json.dumps(["mig_welding"]),
            "availability": "Immediate",
            "resume_data_json": json.dumps({
                "driving_licenses": ["B"],
                "work_experiences": [{
                    "occupation_id": "welder_mig",
                    "start_date": "2022-01-01",
                    "end_date": "2025-01-01",
                }],
            }),
        }
        job = {
            "occupation_id": "welder_mig",
            "experience_level": "2_years",
            "required_from": "2025-02-01",
            "languages_json": json.dumps([{"id": "latvian", "level": "B2", "mandatory": True}]),
            "licenses_json": json.dumps([{"id": "B", "mandatory": True}]),
            "skills_json": json.dumps([{"id": "mig_welding", "mandatory": True}]),
        }

        result = score_candidate(profile, job, date(2025, 1, 1))

        self.assertEqual(result["score"], 100)
        self.assertEqual(result["label"], "excellent")
        self.assertFalse(any(flag["type"] == "required_missing" for flag in result["flags"]))

    def test_mandatory_requirement_adds_flag_without_zeroing_score(self):
        profile = {
            "languages_json": "[]",
            "licenses_json": "[]",
            "skill_ids_json": "[]",
            "resume_data_json": json.dumps({
                "work_experiences": [{"occupation_id": "welder_mig"}],
            }),
        }
        job = {
            "occupation_id": "welder_mig",
            "experience_level": "no_experience",
            "languages_json": "[]",
            "licenses_json": json.dumps([{"id": "C", "mandatory": True}]),
            "skills_json": "[]",
        }

        result = score_candidate(profile, job, date(2025, 1, 1))

        self.assertEqual(result["score"], 85)
        self.assertEqual(result["flags"][0]["type"], "required_missing")

    def test_experience_and_skills_have_higher_priority(self):
        base_profile = {
            "languages_json": "[]",
            "licenses_json": "[]",
            "skill_ids_json": "[]",
            "availability": "Immediate",
            "resume_data_json": json.dumps({
                "work_experiences": [{"occupation_id": "welder_mig"}],
            }),
        }
        missing_experience = score_candidate(base_profile, {
            "occupation_id": "welder_mig",
            "experience_level": "2_years",
        }, date(2025, 1, 1))
        missing_skill = score_candidate(base_profile, {
            "experience_level": "no_experience",
            "skills_json": json.dumps([{"id": "mig_welding", "mandatory": True}]),
        }, date(2025, 1, 1))
        missing_language = score_candidate(base_profile, {
            "experience_level": "no_experience",
            "languages_json": json.dumps([{"id": "latvian", "level": "B2", "mandatory": True}]),
        }, date(2025, 1, 1))
        missing_credential = score_candidate(base_profile, {
            "experience_level": "no_experience",
            "licenses_json": json.dumps([{"id": "B", "mandatory": True}]),
        }, date(2025, 1, 1))

        self.assertEqual(missing_experience["score"], 70)
        self.assertEqual(missing_skill["score"], 70)
        self.assertEqual(missing_language["score"], 85)
        self.assertEqual(missing_credential["score"], 85)

    def test_candidate_outside_occupation_keeps_score_and_flag(self):
        profile = {
            "resume_data_json": json.dumps({
                "work_experiences": [{"occupation_id": "electrician"}],
            }),
        }
        job = {
            "occupation_id": "welder_mig",
            "experience_level": "no_experience",
            "skills_json": "[]",
        }

        result = score_candidate(profile, job, date(2025, 1, 1))

        self.assertFalse(result["excluded"])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["breakdown"]["experience"]["points"], 0)
        self.assertEqual(result["breakdown"]["skills"]["points"], 0)
        self.assertEqual(result["flags"][0]["type"], "outside_occupation")

    def test_recent_short_jobs_receive_stability_penalty(self):
        profile = {
            "languages_json": "[]",
            "licenses_json": "[]",
            "skill_ids_json": "[]",
            "resume_data_json": json.dumps({
                "work_experiences": [
                    {"start_date": "2024-01-01", "end_date": "2024-04-01"},
                    {"start_date": "2024-05-01", "end_date": "2024-08-01"},
                    {"start_date": "2024-09-01", "end_date": "2024-12-01"},
                ],
            }),
        }
        job = {"experience_level": "no_experience"}

        result = score_candidate(profile, job, date(2025, 1, 1))

        self.assertEqual(result["score"], 90)
        self.assertTrue(any(flag["type"] == "stability" for flag in result["flags"]))


if __name__ == "__main__":
    unittest.main()
