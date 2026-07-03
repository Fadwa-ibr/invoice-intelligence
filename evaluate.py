import json
from extract import extract_invoice
from validator import validate_invoice
import time

TEXT_FIELDS = ["vendor_name", "invoice_number", "currency"]
NUM_FIELDS = ["subtotal", "vat_amount", "grand_total"]


def same_text(a, b):
    return (str(a).strip().lower() if a else None) == (str(b).strip().lower() if b else None)


def same_num(a, b):
    try:
        return abs(float(a) - float(b)) <= 0.01
    except (TypeError, ValueError):
        return False

def extract_with_retry(path, attempts=4):
    """Retry on rate limits (429) and busy servers (503) with a cool-down wait."""
    for attempt in range(1, attempts + 1):
        try:
            return extract_invoice(path)
        except Exception as e:
            print(f"  API busy ({type(e).__name__}) - waiting 45s, retry {attempt}/{attempts}")
            time.sleep(45)
    raise RuntimeError(f"Gave up on {path} after {attempts} attempts")

CACHE_FILE = "test_data/extractions_cache.json"

def load_cache():
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def main():
    with open("test_data/ground_truth.json", encoding="utf-8") as f:
        manifest = json.load(f)

    scores = {f: 0 for f in TEXT_FIELDS + NUM_FIELDS + ["line_item_count"]}
    caught, missed, false_positives = [], [], []
    seen = set()
    cache = load_cache()
    for entry in manifest:
        truth = entry["data"]
        print(f"Evaluating {entry['file']} ...")
        if entry["file"] in cache:
            extracted = cache[entry["file"]]  # already done - no API call
        else:
            time.sleep(15)
            extracted = extract_with_retry(entry["file"])
            cache[entry["file"]] = extracted
            save_cache(cache)

        for f in TEXT_FIELDS:
            scores[f] += same_text(extracted.get(f), truth.get(f))
        for f in NUM_FIELDS:
            scores[f] += same_num(extracted.get(f), truth.get(f))
        scores["line_item_count"] += len(extracted.get("line_items") or []) == len(truth["line_items"])

        issues = validate_invoice(extracted)
        key = (str(extracted.get("vendor_name")).lower(), str(extracted.get("invoice_number")))
        if key in seen:
            issues.append("DUPLICATE")
        seen.add(key)

        expected = entry["expected_issues"]
        for exp in expected:
            (caught if any(exp in i for i in issues) else missed).append((entry["file"], exp))
        if not expected and issues:
            false_positives.append((entry["file"], issues))

    n = len(manifest)
    print("\n===== EXTRACTION ACCURACY =====")
    for f, score in scores.items():
        print(f"{f:20s} {score}/{n}  ({100 * score / n:.0f}%)")

    print("\n===== VALIDATOR PERFORMANCE =====")
    print(f"Planted errors caught: {len(caught)}/{len(caught) + len(missed)}")
    for f, exp in missed:
        print(f"  MISSED: {exp} in {f}")
    print(f"False positives: {len(false_positives)}")
    for f, iss in false_positives:
        print(f"  FALSE ALARM in {f}: {iss}")


if __name__ == "__main__":
    main()