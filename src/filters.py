def parse_filter(question: str):

    question_lower = question.lower()

    if "mobileapp" in question_lower:
        return {"project": "MobileApp"}

    if "crm2026" in question_lower:
        return {"project": "CRM2026"}

    if "productx" in question_lower:
        return {"project": "ProductX"}

    return None