from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from json import JSONDecodeError, loads
from typing import Any, TypeVar


# Версия алгоритма сохраняется вместе с результатом.
# Это позволяет отличать старые расчёты от новых после изменения логики.
ALGORITHM_VERSION = "matching_v8"

# Максимальные веса категорий.
# До штрафа стабильности сумма положительных весов равна 100.
EXPERIENCE_WEIGHT = 30
LANGUAGE_WEIGHT = 15
AVAILABILITY_WEIGHT = 10
CREDENTIAL_WEIGHT = 15
SKILL_WEIGHT = 30

# Числовые ранги CEFR нужны для сравнения фактического
# языкового уровня кандидата с требуемым уровнем вакансии.
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

# Требуемый уровень опыта переводится в минимальное число месяцев.
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

# Границы уровней используются, чтобы определить:
# кандидат находится ровно на один уровень ниже требования или ещё ниже.
EXPERIENCE_BANDS = tuple(EXPERIENCE_MONTHS.values())

# Текстовые значения доступности переводятся в задержку относительно даты расчёта.
AVAILABILITY_OFFSETS = {
    "immediate": 0,
    "1 week notice": 7,
    "2 weeks notice": 14,
    "1 month notice": 30,
}

# TypeVar связывает тип fallback с типом результата parse_json.
# Если fallback — список, функция типизируется как возвращающая список.
T = TypeVar("T")


def parse_json(value: Any, fallback: T) -> T:
    """
    Безопасно преобразует JSON-строку в ожидаемый тип.

    Тип fallback одновременно задаёт ожидаемый тип результата:
    [] означает list, {} означает dict.

    При пустом, некорректном или неподходящем значении
    возвращается сам fallback.
    """
    # Если значение уже имеет нужный тип, JSON разбирать не требуется.
    if isinstance(value, type(fallback)):
        return value

    # Пустое значение или значение не строкового типа считаем некорректным.
    if not isinstance(value, str) or not value.strip():
        return fallback

    try:
        parsed = loads(value)
    except (TypeError, JSONDecodeError):
        return fallback

    # Даже корректный JSON должен иметь ожидаемый тип.
    return parsed if isinstance(parsed, type(fallback)) else fallback


def get_value(source: Any, name: str, default: Any = None) -> Any:
    """
    Читает поле как из словаря, так и из ORM-объекта.

    Это позволяет одинаково работать с dict, dataclass
    и объектами моделей базы данных.
    """
    return (
        source.get(name, default)
        if isinstance(source, dict)
        else getattr(source, name, default)
    )


def normalize_text(value: Any) -> str:
    """
    Нормализует текст для точного регистронезависимого сравнения.

    strip удаляет пробелы по краям,
    casefold надёжнее lower для Unicode.
    """
    return str(value or "").strip().casefold()


def normalize_requirements(value: Any) -> list[dict]:
    """
    Приводит требования вакансии к единому формату:

    {
        "id": str,
        "label": str,
        "mandatory": bool,
        "level": str
    }

    Поддерживаются как простые строки, так и словари.
    """
    result = []

    for item in parse_json(value, []):
        # Простая строка превращается в необязательное требование.
        if isinstance(item, str):
            identifier = item.strip()
            if identifier:
                result.append({
                    "id": identifier,
                    "label": identifier,
                    "mandatory": False,
                    "level": "",
                })
            continue

        # Все неподдерживаемые типы пропускаются.
        if not isinstance(item, dict):
            continue

        # id может прийти под разными именами из frontend или старых данных.
        identifier = str(
            item.get("id")
            or item.get("value")
            or item.get("name")
            or ""
        ).strip()

        if identifier:
            result.append({
                "id": identifier,
                "label": str(
                    item.get("label")
                    or item.get("name")
                    or identifier
                ).strip(),
                "mandatory": bool(
                    item.get("mandatory")
                    or item.get("is_mandatory")
                ),
                "level": str(item.get("level") or "").strip(),
            })

    return result


def normalize_ids(values: Any) -> set[str]:
    """
    Извлекает нормализованные id из списка строк или словарей.

    Используется для навыков, лицензий и сертификатов.
    set исключает дубликаты и ускоряет проверку совпадения.
    """
    return {
        normalize_text(
            item
            if isinstance(item, str)
            else item.get("id") or item.get("name")
        )
        for item in values
        if isinstance(item, (str, dict))
        and normalize_text(
            item
            if isinstance(item, str)
            else item.get("id") or item.get("name")
        )
    }


def parse_date(value: Any) -> date | None:
    """
    Поддерживает форматы YYYY-MM-DD и DD.MM.YYYY.

    Неизвестный или некорректный формат возвращает None.
    """
    text = str(value or "").strip()

    for pattern in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            pass

    return None


def add_months(value: date, months: int) -> date:
    """
    Сдвигает дату на заданное число месяцев.

    Если исходный день отсутствует в целевом месяце,
    используется последний доступный день месяца.
    """
    index = value.month - 1 + months
    year = value.year + index // 12
    month = index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])

    return date(year, month, day)


def months_between(start: date, end: date) -> int:
    """
    Возвращает число полных месяцев между датами.

    Для любого положительного интервала возвращается минимум 1 месяц.
    """
    if end <= start:
        return 0

    months = (
        (end.year - start.year) * 12
        + end.month
        - start.month
        - (end.day < start.day)
    )

    return max(months, 1)


def merge_intervals(
    intervals: list[tuple[date, date]],
) -> list[tuple[date, date]]:
    """
    Объединяет пересекающиеся интервалы работы.

    Это предотвращает двойной учёт одного и того же месяца,
    если кандидат одновременно указал несколько пересекающихся работ.
    """
    merged: list[list[date]] = []

    for start, end in sorted(intervals):
        # Новый непересекающийся период добавляется отдельно.
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            # Пересекающийся период расширяет предыдущий интервал.
            merged[-1][1] = max(merged[-1][1], end)

    return [(start, end) for start, end in merged]


def resume_data(profile: Any) -> dict:
    """
    Возвращает resume_data_json кандидата как словарь.

    Некорректный JSON заменяется пустым словарём.
    """
    return parse_json(
        get_value(profile, "resume_data_json", {}),
        {},
    )


def work_experiences(profile: Any) -> list[dict]:
    """
    Возвращает только корректные записи опыта работы.
    """
    return [
        item
        for item in resume_data(profile).get("work_experiences", [])
        if isinstance(item, dict)
    ]


def relevant_experience_months(
    profile: Any,
    job: Any,
    as_of: date,
) -> int:
    """
    Рассчитывает релевантный опыт кандидата в месяцах.

    Правила:
    1. Основное совпадение выполняется по occupation_id.
    2. category используется как fallback для старых записей.
    3. Последние 24 месяца учитываются полностью.
    4. Более старый опыт учитывается с коэффициентом 0.5.
    5. Пересекающиеся периоды сначала объединяются.
    """
    occupation = normalize_text(get_value(job, "occupation_id"))
    category = normalize_text(get_value(job, "category"))

    # Всё, что старше 24 месяцев относительно даты расчёта,
    # получает половинный вес.
    boundary = add_months(as_of, -24)
    intervals = []

    for entry in work_experiences(profile):
        entry_occupation = normalize_text(entry.get("occupation_id"))
        entry_category = normalize_text(entry.get("job_category"))

        # occupation_id имеет приоритет.
        # Если его нет в старой записи, используется category.
        relevant = (
            entry_occupation == occupation
            if occupation and entry_occupation
            else bool(category and entry_category == category)
        )

        start = parse_date(entry.get("start_date"))

        # Для текущей работы концом периода считается дата расчёта.
        end = (
            as_of
            if entry.get("current")
            else parse_date(entry.get("end_date"))
        )

        # Некорректные или отрицательные интервалы не учитываются.
        if relevant and start and end and end > start:
            intervals.append((start, min(end, as_of)))

    weighted = 0.0

    for start, end in merge_intervals(intervals):
        # Старая часть периода учитывается наполовину.
        older_end = min(end, boundary)
        if older_end > start:
            weighted += months_between(start, older_end) * 0.5

        # Недавняя часть периода учитывается полностью.
        recent_start = max(start, boundary)
        if end > recent_start:
            weighted += months_between(recent_start, end)

    return round(weighted)


def matches_occupation(profile: Any, job: Any) -> bool:
    """
    Проверяет точное совпадение occupation_id вакансии
    хотя бы с одной записью опыта кандидата.

    Если occupation_id вакансии не указан,
    исключение по профессии не применяется.
    """
    required = normalize_text(get_value(job, "occupation_id"))

    return not required or any(
        normalize_text(entry.get("occupation_id")) == required
        for entry in work_experiences(profile)
    )


def experience_score(
    profile: Any,
    job: Any,
    as_of: date,
) -> tuple[int, dict]:
    """
    Начисляет баллы за релевантный опыт.

    Полное соответствие: 30 баллов.
    На один уровень ниже: 15 баллов.
    Ещё ниже: 0 баллов.
    """
    required = EXPERIENCE_MONTHS.get(
        str(get_value(job, "experience_level") or ""),
        0,
    )
    actual = relevant_experience_months(profile, job, as_of)

    detail = {
        "required_months": required,
        "actual_months": actual,
    }

    # Отсутствие требования к опыту даёт полный вес категории.
    if not required or actual >= required:
        return EXPERIENCE_WEIGHT, detail

    required_band = max(
        index
        for index, value in enumerate(EXPERIENCE_BANDS)
        if value <= required
    )
    actual_band = max(
        index
        for index, value in enumerate(EXPERIENCE_BANDS)
        if value <= actual
    )

    points = (
        EXPERIENCE_WEIGHT // 2
        if actual_band == required_band - 1
        else 0
    )

    return points, detail


def language_score(
    profile: Any,
    job: Any,
) -> tuple[int, dict, list[dict], list[dict]]:
    """
    Рассчитывает соответствие языковым требованиям.

    Требуемый уровень или выше: 100%.
    На один CEFR-уровень ниже: 50%.
    Более чем на один уровень ниже: 0%.
    """
    required = normalize_requirements(
        get_value(job, "languages_json")
    )

    # Если языков нет в требованиях, кандидат получает все 15 баллов.
    if not required:
        return (
            LANGUAGE_WEIGHT,
            {"required": 0, "matched": 0},
            [],
            [],
        )

    # Языки кандидата переводятся в словарь:
    # нормализованный id языка -> числовой ранг CEFR.
    candidate = {
        normalize_text(
            item.get("id") or item.get("name")
        ): CEFR_RANK.get(
            str(item.get("level") or "").upper(),
            0,
        )
        for item in parse_json(
            get_value(profile, "languages_json"),
            [],
        )
        if isinstance(item, dict)
    }

    ratios = []
    red = []
    green = []

    for item in required:
        expected = CEFR_RANK.get(
            item["level"].upper(),
            0,
        )
        actual = candidate.get(
            normalize_text(item["id"]),
            0,
        )

        ratio = (
            1
            if actual >= expected
            else 0.5
            if actual == expected - 1
            else 0
        )

        ratios.append(ratio)

        # Обязательный язык с недостаточным уровнем создаёт красный флаг.
        if item["mandatory"] and ratio < 1:
            red.append(
                flag(
                    "required_missing",
                    "language",
                    item["label"],
                )
            )

        # Уровень выше требуемого создаёт зелёный флаг.
        if expected and actual > expected:
            green.append(
                flag(
                    "exceeds_requirement",
                    "language",
                    item["label"],
                )
            )

    detail = {
        "required": len(required),
        "matched": sum(
            ratio == 1
            for ratio in ratios
        ),
    }

    points = round(
        LANGUAGE_WEIGHT
        * sum(ratios)
        / len(ratios)
    )

    return points, detail, red, green


def resolve_availability(
    value: Any,
    as_of: date,
) -> date | None:
    """
    Преобразует доступность кандидата в календарную дату.

    Поддерживает текстовые notice-периоды
    и точные даты двух форматов.
    """
    text = normalize_text(value)

    if text in AVAILABILITY_OFFSETS:
        return as_of + timedelta(
            days=AVAILABILITY_OFFSETS[text]
        )

    return parse_date(value)


def availability_score(
    profile: Any,
    job: Any,
    as_of: date,
) -> tuple[int, dict]:
    """
    Начисляет баллы за доступность кандидата.

    Вовремя: 10 баллов.
    Задержка до 14 дней: 5 баллов.
    Более поздний выход или неизвестная дата: 0 баллов.
    """
    required = parse_date(
        get_value(job, "required_from")
    )

    # Без даты начала вакансии начисляется полный вес категории.
    if not required:
        return (
            AVAILABILITY_WEIGHT,
            {
                "required_from": None,
                "candidate_from": None,
            },
        )

    candidate = resolve_availability(
        get_value(profile, "availability"),
        as_of,
    )

    points = (
        AVAILABILITY_WEIGHT
        if candidate and candidate <= required
        else AVAILABILITY_WEIGHT // 2
        if candidate
        and candidate <= required + timedelta(days=14)
        else 0
    )

    return points, {
        "required_from": required.isoformat(),
        "candidate_from": (
            candidate.isoformat()
            if candidate
            else None
        ),
    }


def flag(
    kind: str,
    field: str,
    value: Any,
) -> dict:
    """
    Создаёт флаг единого формата.
    """
    return {
        "type": kind,
        "field": field,
        "value": value,
    }


def requirement_score(
    required_value: Any,
    candidate_values: Any,
    weight: int,
    field: str,
    include_extras: bool = False,
) -> tuple[int, dict, list[dict], list[dict]]:
    """
    Общий скоринг требований по точному id.

    Используется для навыков, лицензий и сертификатов.
    Общая функция устраняет дублирование логики.
    """
    required = normalize_requirements(required_value)

    # Отсутствие требований автоматически даёт полный вес категории.
    if not required:
        return (
            weight,
            {"required": 0, "matched": 0},
            [],
            [],
        )

    candidate = normalize_ids(candidate_values)

    matched = [
        item
        for item in required
        if normalize_text(item["id"]) in candidate
    ]
    missing = [
        item
        for item in required
        if normalize_text(item["id"]) not in candidate
    ]

    # Красные флаги создаются только для обязательных требований.
    red = [
        flag(
            "required_missing",
            field,
            item["label"],
        )
        for item in missing
        if item["mandatory"]
    ]

    # Дополнительные элементы считаются относительно уже совпавших.
    extras = len(
        candidate
        - {
            normalize_text(item["id"])
            for item in matched
        }
    )

    green = (
        [
            flag(
                "exceeds_requirement",
                field,
                extras,
            )
        ]
        if include_extras and extras
        else []
    )

    detail = {
        "required": len(required),
        "matched": len(matched),
    }

    # Баллы распределяются пропорционально количеству совпадений.
    points = round(
        weight
        * len(matched)
        / len(required)
    )

    return points, detail, red, green


def credentials_score(
    profile: Any,
    job: Any,
) -> tuple[int, dict, list[dict], list[dict]]:
    """
    Рассчитывает баллы за лицензии, сертификаты
    и водительские права.
    """
    values = [
        *parse_json(
            get_value(profile, "licenses_json"),
            [],
        ),
        *resume_data(profile).get(
            "driving_licenses",
            [],
        ),
    ]

    return requirement_score(
        get_value(job, "licenses_json"),
        values,
        CREDENTIAL_WEIGHT,
        "credential",
        include_extras=True,
    )


def skills_score(
    profile: Any,
    job: Any,
) -> tuple[int, dict, list[dict]]:
    """
    Рассчитывает баллы за навыки.

    Используется та же общая логика,
    что и для лицензий.
    """
    points, detail, red, _ = requirement_score(
        get_value(job, "skills_json"),
        parse_json(
            get_value(profile, "skill_ids_json"),
            [],
        ),
        SKILL_WEIGHT,
        "skill",
    )

    return points, detail, red


def stability_penalty(
    profile: Any,
    as_of: date,
) -> tuple[int, dict | None]:
    """
    Рассчитывает штраф за частую смену работы.

    Анализируются только последние 36 месяцев.
    Для применения штрафа требуется минимум 2 места работы.

    Средний стаж меньше 6 месяцев: -10.
    Средний стаж меньше 12 месяцев: -5.
    Иначе: 0.
    """
    boundary = add_months(as_of, -36)
    tenures = []

    for entry in work_experiences(profile):
        start = parse_date(entry.get("start_date"))
        end = (
            as_of
            if entry.get("current")
            else parse_date(entry.get("end_date"))
        )

        if (
            start
            and end
            and end > boundary
            and end > start
        ):
            tenures.append(
                months_between(
                    max(start, boundary),
                    min(end, as_of),
                )
            )

    # Одного места работы недостаточно для оценки стабильности.
    if len(tenures) < 2:
        return 0, None

    average = sum(tenures) / len(tenures)

    penalty = (
        -10
        if average < 6
        else -5
        if average < 12
        else 0
    )

    detail = {
        "average_tenure_months": round(
            average,
            1,
        ),
        "jobs_considered": len(tenures),
    }

    return (
        penalty,
        detail if penalty else None,
    )


def score_candidate(
    profile: Any,
    job: Any,
    as_of: date | None = None,
) -> dict:
    """
    Главная точка входа алгоритма MatchScore.

    Порядок работы:
    1. Определяется дата расчёта.
    2. Проверяется occupation_id.
    3. Независимо рассчитываются пять категорий.
    4. Применяется штраф стабильности.
    5. Итог ограничивается диапазоном 0-100.
    6. Формируются breakdown и flags.
    """
    calculation_date = (
        as_of
        or datetime.now(timezone.utc).date()
    )

    # Категория 1:
    # неподходящая профессия фиксируется флагом и обнуляет итоговый score,
    # но не блокирует расчёт breakdown и отправку отклика.
    outside_occupation_flag = (
        flag(
            "outside_occupation",
            "occupation_id",
            get_value(
                job,
                "occupation_id",
            )
            or "",
        )
        if not matches_occupation(profile, job)
        else None
    )

    # Категория 2:
    # каждая часть рассчитывается независимо.
    experience, experience_detail = experience_score(
        profile,
        job,
        calculation_date,
    )
    languages, language_detail, language_red, language_green = (
        language_score(
            profile,
            job,
        )
    )
    availability, availability_detail = availability_score(
        profile,
        job,
        calculation_date,
    )
    credentials, credential_detail, credential_red, credential_green = (
        credentials_score(
            profile,
            job,
        )
    )
    skills, skill_detail, skill_red = skills_score(
        profile,
        job,
    )
    penalty, stability_detail = stability_penalty(
        profile,
        calculation_date,
    )

    if outside_occupation_flag:
        experience = 0
        skills = 0

    # Итог всегда ограничивается диапазоном от 0 до 100.
    raw_score = max(
        0,
        min(
            100,
            experience
            + languages
            + availability
            + credentials
            + skills
            + penalty,
        ),
    )
    score = 0 if outside_occupation_flag else raw_score

    # Текстовая категория зависит только от итогового балла.
    label = (
        "excellent"
        if score >= 90
        else "good"
        if score >= 70
        else "partial"
        if score >= 50
        else "weak"
    )

    # Флаги объясняют сильные и слабые стороны,
    # но сами по себе дополнительно баллы не меняют.
    flags = [
        *([outside_occupation_flag] if outside_occupation_flag else []),
        *language_red,
        *credential_red,
        *skill_red,
        *language_green,
        *credential_green,
    ]

    if stability_detail:
        flags.append(
            flag(
                "stability",
                "work_history",
                stability_detail[
                    "average_tenure_months"
                ],
            )
        )

    return {
        "score": score,
        "label": label,
        "excluded": False,
        "algorithm_version": ALGORITHM_VERSION,
        "breakdown": {
            "experience": {
                "points": experience,
                "max_points": EXPERIENCE_WEIGHT,
                **experience_detail,
            },
            "languages": {
                "points": languages,
                "max_points": LANGUAGE_WEIGHT,
                **language_detail,
            },
            "availability": {
                "points": availability,
                "max_points": AVAILABILITY_WEIGHT,
                **availability_detail,
            },
            "credentials": {
                "points": credentials,
                "max_points": CREDENTIAL_WEIGHT,
                **credential_detail,
            },
            "skills": {
                "points": skills,
                "max_points": SKILL_WEIGHT,
                **skill_detail,
            },
            "stability_penalty": {
                "points": penalty,
                "max_points": 0,
                **(stability_detail or {}),
            },
        },
        "flags": flags,
    }
