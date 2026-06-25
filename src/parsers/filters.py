import re


def normalize_value(value: str):
    if not value:
        return None
    value = value.strip()
    if value in ["-", "—", ""]:
        return None
    return value

def extract_participants(text: str):
    matches = re.findall(r"[А-ЯЁ][а-яё]+\s[А-Я]\.", text)
    return matches if matches else None


def extract_date(text: str):
    match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
    return match.group(0) if match else None

def extract_status(text: str):

    text = text.lower()

    if "заверш" in text:
        return "Завершён"

    if "работе" in text:
        return "В работе"

    return None

def build_filters_from_protocol(parsed_meeting: dict) -> dict:
    """
    Из структурированного протокола -> фильтры для Chroma
    """

    filters = {}

    project = normalize_value(parsed_meeting.get("project"))
    if project:
        filters["project"] = project

    date = parsed_meeting.get("date")
    if date:
        filters["date"] = date

    participants = parsed_meeting.get("participants")
    if participants:
        filters["participants"] = {"$in": participants}

    status = parsed_meeting.get("status")
    if status:
        filters["status"] = status

    return filters


def build_filters_from_query(query: str) -> dict:
    """
    Из пользовательского запроса -> фильтры поиска
    """

    filters = {}

    date = extract_date(query)
    if date:
        filters["date"] = date

    participants = extract_participants(query)
    if participants:
        filters["participants"] = {"$in": participants}

    status = extract_status(query)

    if status:
        filters["status"] = status

    return filters


def merge_filters(*filters_list):
    """
    Объединение фильтров (MVP-safe)
    """
    result = {}

    for f in filters_list:
        if not f:
            continue

        for k, v in f.items():
            # простая стратегия: последнее значение приоритетнее
            result[k] = v

    return result if result else None