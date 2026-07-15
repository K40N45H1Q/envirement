import json
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from typing import Any


ALGORITHM_VERSION = "matching_v1"
EXPERIENCE_WEIGHT = 30
LANGUAGE_WEIGHT = 20
AVAILABILITY_WEIGHT = 20
CREDENTIAL_WEIGHT = 20
SKILL_WEIGHT = 10

CEFR_RANK = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
    "NATIVE": 7,
    "MOTHER TONGUE": 7,
    "РОДНОЙ": 7,
    "DZIMTĀ": 7,
}

EXPERIENCE_MONTHS = {
    "no_experience": 0,
    "1_year": 12,
    "2_years": 24,
    "3_years": 36,
    "4_years": 48,
    "5_years": 60,
    "7_years": 84,
    "10_years": 120,
}

EXPERIENCE_BANDS = (0, 12, 24, 36, 48, 60, 84, 120)


def parse_json(value: Any, fallback):
    if isinstance(value, type(fallback)):
        return value
    if not isinstance(value, str) or not value.strip():
        return fallback
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, type(fallback)) else fallback
    except (TypeError, json.JSONDecodeError):
        return fallback


def get_value(source: Any, name: str, default=None):
    if isinstance(source, dict):
        return source.get(name, default)
    return getattr(source, name, default)


def normalize_text(value: Any) -> str:
    return str(value or "").strip().casefold()


def normalize_requirement_list(value: Any) -> list[dict]:
    result = []
    for item in parse_json(value, []):
        if isinstance(item, str):
            clean = item.strip()
            if clean:
                result.append({"id": clean, "label": clean, "mandatory": False})
            continue
        if not isinstance(item, dict):
            continue
        identifier = str(item.get("id") or item.get("value") or item.get("name") or "").strip()
        if not identifier:
            continue
        result.append({
            "id": identifier,
            "label": str(item.get("label") or item.get("name") or identifier).strip(),
            "mandatory": bool(item.get("mandatory") or item.get("is_mandatory")),
            "level": str(item.get("level") or "").strip(),
        })
    return result


def parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    for pattern in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def months_between(start: date, end: date) -> int:
    if end <= start:
        return 0
    months = (end.year - start.year) * 12 + end.month - start.month
    if end.day < start.day:
        months -= 1
    return max(months, 1)


def merge_intervals(intervals: list[tuple[date, date]]) -> list[tuple[date, date]]:
    merged = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def relevant_experience_months(profile: Any, job: Any, as_of: date) -> int:
    resume_data = parse_json(get_value(profile, "resume_data_json", {}), {})
    occupation_id = normalize_text(get_value(job, "occupation_id"))
    category = normalize_text(get_value(job, "category"))
    recent_boundary = add_months(as_of, -24)
    intervals = []

    for entry in resume_data.get("work_experiences", []):
        if not isinstance(entry, dict):
            continue
        entry_occupation = normalize_text(entry.get("occupation_id"))
        entry_category = normalize_text(entry.get("job_category"))
        is_relevant = bool(occupation_id and entry_occupation == occupation_id)
        if occupation_id and not entry_occupation:
            is_relevant = bool(category and entry_category == category)
        if not occupation_id:
            is_relevant = bool(category and entry_category == category)
        if not is_relevant:
            continue
        start = parse_date(entry.get("start_date"))
        end = as_of if entry.get("current") else parse_date(entry.get("end_date"))
        if start and end and end > start:
            intervals.append((start, min(end, as_of)))

    weighted_months = 0.0
    for start, end in merge_intervals(intervals):
        older_end = min(end, recent_boundary)
        if older_end > start:
            weighted_months += months_between(start, older_end) * 0.5
        recent_start = max(start, recent_boundary)
        if end > recent_start:
            weighted_months += months_between(recent_start, end)
    return round(weighted_months)


def experience_score(profile: Any, job: Any, as_of: date) -> tuple[int, dict]:
    required = EXPERIENCE_MONTHS.get(str(get_value(job, "experience_level") or ""), 0)
    actual = relevant_experience_months(profile, job, as_of)
    if required <= 0:
        return EXPERIENCE_WEIGHT, {"required_months": 0, "actual_months": actual}
    required_band = max(index for index, value in enumerate(EXPERIENCE_BANDS) if value <= required)
    actual_band = max(index for index, value in enumerate(EXPERIENCE_BANDS) if value <= actual)
    points = EXPERIENCE_WEIGHT if actual >= required else 15 if actual_band == required_band - 1 else 0
    return points, {"required_months": required, "actual_months": actual}


def language_score(profile: Any, job: Any) -> tuple[int, dict, list[dict], list[dict]]:
    required = normalize_requirement_list(get_value(job, "languages_json"))
    if not required:
        return LANGUAGE_WEIGHT, {"required": 0, "matched": 0}, [], []
    candidate = {
        normalize_text(item.get("id") or item.get("name")): CEFR_RANK.get(str(item.get("level") or "").upper(), 0)
        for item in parse_json(get_value(profile, "languages_json"), [])
        if isinstance(item, dict)
    }
    ratios = []
    red_flags = []
    green_flags = []
    for requirement in required:
        key = normalize_text(requirement["id"])
        expected = CEFR_RANK.get(requirement["level"].upper(), 0)
        actual = candidate.get(key, 0)
        ratio = 1 if actual >= expected else 0.5 if actual == expected - 1 else 0
        ratios.append(ratio)
        if requirement["mandatory"] and ratio < 1:
            red_flags.append({"type": "required_missing", "field": "language", "value": requirement["label"]})
        if expected and actual > expected:
            green_flags.append({"type": "exceeds_requirement", "field": "language", "value": requirement["label"]})
    points = round(LANGUAGE_WEIGHT * sum(ratios) / len(ratios))
    return points, {"required": len(required), "matched": sum(1 for value in ratios if value == 1)}, red_flags, green_flags


def resolve_availability(value: Any, as_of: date) -> date | None:
    text = normalize_text(value)
    offsets = {
        "immediate": 0,
        "1 week notice": 7,
        "2 weeks notice": 14,
        "1 month notice": 30,
    }
    if text in offsets:
        return as_of + timedelta(days=offsets[text])
    return parse_date(value)


def availability_score(profile: Any, job: Any, as_of: date) -> tuple[int, dict]:
    required = parse_date(get_value(job, "required_from"))
    if not required:
        return AVAILABILITY_WEIGHT, {"required_from": None, "candidate_from": None}
    candidate = resolve_availability(get_value(profile, "availability"), as_of)
    if not candidate:
        points = 0
    elif candidate <= required:
        points = AVAILABILITY_WEIGHT
    elif candidate <= required + timedelta(days=14):
        points = AVAILABILITY_WEIGHT // 2
    else:
        points = 0
    return points, {
        "required_from": required.isoformat(),
        "candidate_from": candidate.isoformat() if candidate else None,
    }


def credentials_score(profile: Any, job: Any) -> tuple[int, dict, list[dict], list[dict]]:
    required = normalize_requirement_list(get_value(job, "licenses_json"))
    if not required:
        return CREDENTIAL_WEIGHT, {"required": 0, "matched": 0}, [], []
    resume_data = parse_json(get_value(profile, "resume_data_json", {}), {})
    values = [*parse_json(get_value(profile, "licenses_json"), []), *resume_data.get("driving_licenses", [])]
    candidate = {
        normalize_text(item if isinstance(item, str) else item.get("id") or item.get("name"))
        for item in values
    }
    matched = [item for item in required if normalize_text(item["id"]) in candidate]
    missing = [item for item in required if normalize_text(item["id"]) not in candidate]
    red_flags = [
        {"type": "required_missing", "field": "credential", "value": item["label"]}
        for item in missing if item["mandatory"]
    ]
    extras = max(0, len(candidate) - len(matched))
    green_flags = ([{"type": "exceeds_requirement", "field": "credential", "value": str(extras)}] if extras else [])
    points = round(CREDENTIAL_WEIGHT * len(matched) / len(required))
    return points, {"required": len(required), "matched": len(matched)}, red_flags, green_flags


def skills_score(profile: Any, job: Any) -> tuple[int, dict, list[dict]]:
    required = normalize_requirement_list(get_value(job, "skills_json"))
    if not required:
        return SKILL_WEIGHT, {"required": 0, "matched": 0}, []
    candidate = {
        normalize_text(item if isinstance(item, str) else item.get("id") or item.get("name"))
        for item in parse_json(get_value(profile, "skill_ids_json"), [])
    }
    matched = [item for item in required if normalize_text(item["id"]) in candidate]
    missing = [item for item in required if normalize_text(item["id"]) not in candidate]
    red_flags = [
        {"type": "required_missing", "field": "skill", "value": item["label"]}
        for item in missing if item["mandatory"]
    ]
    points = round(SKILL_WEIGHT * len(matched) / len(required))
    return points, {"required": len(required), "matched": len(matched)}, red_flags


def stability_penalty(profile: Any, as_of: date) -> tuple[int, dict | None]:
    resume_data = parse_json(get_value(profile, "resume_data_json", {}), {})
    boundary = add_months(as_of, -36)
    tenures = []
    for entry in resume_data.get("work_experiences", []):
        if not isinstance(entry, dict):
            continue
        start = parse_date(entry.get("start_date"))
        end = as_of if entry.get("current") else parse_date(entry.get("end_date"))
        if not start or not end or end <= boundary or end <= start:
            continue
        tenures.append(months_between(max(start, boundary), min(end, as_of)))
    if len(tenures) < 2:
        return 0, None
    average = sum(tenures) / len(tenures)
    penalty = -10 if average < 6 else -5 if average < 12 else 0
    detail = {"average_tenure_months": round(average, 1), "jobs_considered": len(tenures)}
    return penalty, detail if penalty else None


def score_candidate(profile: Any, job: Any, as_of: date | None = None) -> dict:
    calculation_date = as_of or datetime.now(timezone.utc).date()
    experience, experience_detail = experience_score(profile, job, calculation_date)
    languages, language_detail, language_red, language_green = language_score(profile, job)
    availability, availability_detail = availability_score(profile, job, calculation_date)
    credentials, credential_detail, credential_red, credential_green = credentials_score(profile, job)
    skills, skill_detail, skill_red = skills_score(profile, job)
    penalty, stability_detail = stability_penalty(profile, calculation_date)
    score = max(0, min(100, experience + languages + availability + credentials + skills + penalty))
    label = "excellent" if score >= 90 else "good" if score >= 70 else "partial" if score >= 50 else "weak"
    flags = [*language_red, *credential_red, *skill_red, *language_green, *credential_green]
    if stability_detail:
        flags.append({"type": "stability", "field": "work_history", "value": stability_detail["average_tenure_months"]})
    return {
        "score": score,
        "label": label,
        "algorithm_version": ALGORITHM_VERSION,
        "breakdown": {
            "experience": {"points": experience, **experience_detail},
            "languages": {"points": languages, **language_detail},
            "availability": {"points": availability, **availability_detail},
            "credentials": {"points": credentials, **credential_detail},
            "skills": {"points": skills, **skill_detail},
            "stability_penalty": {"points": penalty, **(stability_detail or {})},
        },
        "flags": flags,
    }
