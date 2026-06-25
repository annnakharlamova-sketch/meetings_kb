import re

def parse_meeting(text: str):
    result = {
        "title": None,
        "project": None,
        "date": None,
        "participants": [],
        "topics": [],
        "decisions": [],
        "tasks": [],
        "status": None
    }

    title_match = re.search(
        r"Название встречи:\s*(.+)",
        text
    )

    if title_match:
        result["title"] = title_match.group(1).strip()

    date_match = re.search(
        r"Дата:\s*(.+)",
        text
    )

    if date_match:
        result["date"] = date_match.group(1).strip()

    participants_match = re.search(
        r"Участники:\s*\n?(.+)",
        text
    )

    if participants_match:
        result["participants"] = [
            p.strip()
            for p in participants_match.group(1).split(",")
        ]

    decision_block = re.search(
        r"Решения:(.*?)Поручения:",
        text,
        re.DOTALL
    )

    topics_block = re.search(
        r"Темы:(.*?)Решения:",
        text,
        re.DOTALL
    )

    if topics_block:

        topics_text = topics_block.group(1)

        topics = [
            line.replace("-", "").strip()
            for line in topics_text.split("\n")
            if line.strip()
        ]

        result["topics"] = topics

    if decision_block:
        decisions_text = decision_block.group(1)

        decisions = [
            line.strip()
            for line in decisions_text.split("\n")
            if line.strip()
        ]

        result["decisions"] = decisions

    task_pattern = re.findall(
        r"([А-ЯЁа-яё]+\s+[А-Я]\.)\s*—\s*(.*?)\s*до\s*(\d{2}\.\d{2}\.\d{4})",
        text
    )

    for assignee, task, deadline in task_pattern:

        task = " ".join(task.split())

        result["tasks"].append(
            {
                "assignee": assignee,
                "task": task,
                "deadline": deadline
            }
        )

    project_match = re.search(
        r"Проект:\s*(.+)",
        text
    )

    if project_match:
        project = project_match.group(1).strip()

        # нормализация "пустых" значений
        if project in ["-", "—", "нет", "N/A", "none", "None"]:
            result["project"] = None
        else:
            result["project"] = project

    status_match = re.search(
        r"Статус:\s*(.+)",
        text
    )

    if status_match:
        result["status"] = status_match.group(1).strip()

    return result