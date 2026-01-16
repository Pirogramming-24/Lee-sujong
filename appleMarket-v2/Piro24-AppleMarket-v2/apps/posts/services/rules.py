import re

def _to_grams(value: float, unit: str) -> float:
    unit = unit.lower()
    if unit == "mg":
        return round(value / 1000.0, 3)
    return round(value, 3)

def _find_amount(t: str, keys: list[str]):
    for k in keys:
        m = re.search(rf'{k}\s*([0-9]+(?:\.[0-9]+)?)\s*(mg|g)\b', t)
        if m:
            return _to_grams(float(m.group(1)), m.group(2))
    return None

import re

def extract_nutrition(ocr_text: str) -> dict:
    t = ocr_text.replace(" ", "").lower()

    kcal = None
    m = re.search(r'([0-9]+(?:\.[0-9]+)?)kcal', t)
    if m:
        kcal = float(m.group(1))

    def find_g(name):
        m = re.search(rf'{name}([0-9]+(?:\.[0-9]+)?)(mg|g)', t)
        if not m:
            return None
        val = float(m.group(1))
        unit = m.group(2)
        return round(val/1000, 3) if unit == "mg" else round(val, 3)

    return {
        "calories_kcal": kcal,
        "carbs_g": find_g("탄수화물"),
        "protein_g": find_g("단백질"),
        "fat_g": find_g("지방"),
    }
