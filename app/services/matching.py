from rapidfuzz import process, fuzz
import re

CONFIDENCE_THRESHOLDS = {
    'auto_approve': 95,
    'needs_review': 75,
}

# Common OCR errors specifically for Rwandan names or general text
OCR_CORRECTIONS = {
    r'\b0\b': 'O',
    r'rn': 'm',
    r'\bl\b': 'I',
    r'1': 'I',
}

def normalize_name(name: str) -> str:
    """Clean a single name string for matching."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)  # remove punctuation
    name = re.sub(r'\s+', ' ', name)     # collapse spaces
    for pattern, replacement in OCR_CORRECTIONS.items():
        name = re.sub(pattern, replacement, name)
    return name

def match_name(ocr_name: str, candidates: list[str]) -> dict:
    """
    Match one OCR name against an official student list.
    Returns { matched, score, status }
    """
    if not candidates:
        return {'matched': None, 'score': 0, 'status': 'unrecognized'}

    normalized_ocr = normalize_name(ocr_name)
    normalized_candidates = {normalize_name(c): c for c in candidates}

    # Use token_sort_ratio as primary because names often come in different orders
    result = process.extractOne(
        normalized_ocr,
        list(normalized_candidates.keys()),
        scorer=fuzz.token_sort_ratio
    )

    if not result:
        return {'matched': None, 'score': 0, 'status': 'unrecognized'}

    matched_normalized, score, _ = result
    matched_original = normalized_candidates[matched_normalized]

    if score >= CONFIDENCE_THRESHOLDS['auto_approve']:
        status = 'auto_approved'
    elif score >= CONFIDENCE_THRESHOLDS['needs_review']:
        status = 'needs_review'
    else:
        status = 'unrecognized'

    return {'matched': matched_original, 'score': score, 'status': status}

def match_all(ocr_names: list[str], candidates: list[str]) -> list[dict]:
    """Match a full OCR name list against the official student roster."""
    return [
        {'ocr_raw': name, **match_name(name, candidates)}
        for name in ocr_names
    ]
