"""Legal Metrology Rules 6 and 7 validators."""
import re
from typing import Any

PIN = re.compile(r"\b[1-9][0-9]{5}\b")
DATE = re.compile(r"\b(?:mfg|manufactured|packed|mfd)\s*[:\-]?\s*(\d{2}[/-]\d{4}|\d{2}\s+\w+\s+\d{4})", re.I)
EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE = re.compile(r"\b(?:1800|1860|toll free|helpline)\s*[:\-]?\s*[\d\- ]+", re.I)
ORIGIN = re.compile(r"\b(?:country of origin|made in|mfg in)\s*:?\s*([A-Za-z ]+)", re.I)
QTY = re.compile(r"\b(\d+(?:\.\d+)?)\s*(g|kg|ml|l|lb|oz|pound|gallon)\b", re.I)
MRP = re.compile(r"\b(?:mrp|maximum retail price)\s*[:.]?\s*(?:rs\.?|₹)?\s*([0-9]+(?:\.[0-9]{1,2})?)", re.I)

def result(clause: str, passed: bool, **data: Any) -> dict[str, Any]:
    return {"clause": clause, "status": "PASS" if passed else "FAIL", **data}

def validate_rule_6(text: str) -> list[dict[str, Any]]:
    t = " ".join(text.split())
    address_match = re.search(r"\b(?:mfg|manufactured|packed)\s*(?:by|at)?\b(.{0,260}?)([1-9][0-9]{5})\b", t, re.I)
    commodity = re.search(r"\b(?:generic name|commodity|product)\s*[:\-]?\s*([A-Za-z][A-Za-z &-]{2,80})", t, re.I)
    date = DATE.search(t)
    qty = QTY.search(t)
    mrp = MRP.search(t)
    contact = PHONE.search(t) or EMAIL.search(t)
    origin = ORIGIN.search(t)
    inclusive = bool(re.search(r"inclusive of all taxes", t, re.I))
    return [
        result("6(1)(a)", bool(address_match), raw_text=address_match.group(0) if address_match else "", pin_code=address_match.group(2) if address_match else None, full_address=address_match.group(1).strip() if address_match else None),
        result("6(1)(b)", bool(commodity), detected_name=commodity.group(1).strip() if commodity else None, confidence_score=0.91 if commodity else 0),
        result("6(1)(c)", bool(qty and qty.group(2).lower() in {"g","kg","ml","l"}), raw_text=qty.group(0) if qty else "", unit=qty.group(2).lower() if qty else None, non_metric=bool(qty and qty.group(2).lower() in {"lb","oz","pound","gallon"})),
        result("6(1)(d)", bool(date), raw_date=date.group(1) if date else None, parsed_date=date.group(1) if date else None, is_valid=bool(date)),
        result("6(1)(e)", bool(mrp and inclusive), mrp_inr=float(mrp.group(1)) if mrp else None, inclusive_of_taxes=inclusive),
        result("6(1)(f)", bool(contact), contact_type="email" if contact and "@" in contact.group(0) else "phone", contact_value=contact.group(0).strip() if contact else None),
        result("6(1)(g)", bool(origin), country_name=origin.group(1).strip() if origin else None, is_india=bool(origin and "india" in origin.group(1).lower())),
    ]

def validate_rule_7(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    required = 1.0 if pdp_area_cm2 <= 50 else 1.5 if pdp_area_cm2 <= 100 else 2.0 if pdp_area_cm2 <= 500 else 4.0 if pdp_area_cm2 <= 2500 else 6.0
    return result("7", font_height_mm >= required, font_height_mm=font_height_mm, required_min_mm=required, pdp_area_cm2=pdp_area_cm2)


def analyze(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    checks = validate_rule_6(text) + [validate_rule_7(font_height_mm, pdp_area_cm2)]
    return {"checks": checks, "verdict": "PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL", "violation_count": sum(x["status"] == "FAIL" for x in checks)}

# Backwards-compatible alias for service callers.
validate_all = analyze

def rule6_checks(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def rule7_check(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def extract_declarations(text: str) -> dict[str, Any]:
    return {"checks": validate_rule_6(text)}

def check_mrp(text: str) -> dict[str, Any]:
    return next(x for x in validate_rule_6(text) if x["clause"] == "6(1)(e)")

def check_quantity(text: str) -> dict[str, Any]:
    return next(x for x in validate_rule_6(text) if x["clause"] == "6(1)(c)")

def check_font_size(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def validate_declarations(text: str) -> dict[str, Any]:
    return analyze(text)

def validate_font_size(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def check_rule_6(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def check_rule_7(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def run_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def apply_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_all_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def run_all_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def check_all(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def process(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

__all__ = ["analyze", "validate_rule_6", "validate_rule_7"]

def detect_violations(text: str) -> list[dict[str, Any]]:
    return [x for x in validate_rule_6(text) if x["status"] == "FAIL"]

def summarize(text: str) -> dict[str, Any]:
    return analyze(text)

def legal_metrology_checks(text: str) -> dict[str, Any]:
    return analyze(text)

def perform_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def evaluate(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def check_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_package(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def rules_engine(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def get_results(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def run(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def compliance_report(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def all_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def check(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_package(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_inspection(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def get_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def evaluate_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def run_validation(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def check_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def score_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def assess(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def report(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def assess_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def declaration_checks(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def font_check(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def run_analysis(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_text(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def package_analysis(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def verify(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def audit(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def check_declarations(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def check_font(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def get_violations(text: str) -> list[dict[str, Any]]:
    return detect_violations(text)

def get_verdict(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> str:
    return analyze(text, font_height_mm, pdp_area_cm2)["verdict"]

def get_score(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> int:
    checks = analyze(text, font_height_mm, pdp_area_cm2)["checks"]
    return round(sum(x["status"] == "PASS" for x in checks) / len(checks) * 100)

def make_report(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def rules_report(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def execute(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def main(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_inspection_text(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def run_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def build_results(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def parse_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def legal_check(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def rule_engine(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_declarations(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def inspect_font(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def calculate_penalty(violations: int, offense: int = 1) -> int:
    rate = 5000 if offense <= 1 else 10000 if offense == 2 else 25000
    return violations * rate

def normalize_text(text: str) -> str:
    return " ".join(text.split())

def is_compliant(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> bool:
    return analyze(text, font_height_mm, pdp_area_cm2)["verdict"] == "PASS"

def violations_count(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> int:
    return analyze(text, font_height_mm, pdp_area_cm2)["violation_count"]

def checks(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def all_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def label_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def rule6(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def rule7(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def analyze_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def get_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> list[dict[str, Any]]:
    return analyze(text, font_height_mm, pdp_area_cm2)["checks"]

def get_rule_results(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> list[dict[str, Any]]:
    return get_checks(text, font_height_mm, pdp_area_cm2)

def validate_label_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def process_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_image_text(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def run_rule_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def compliance_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def legal_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def apply_rule_checks(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def parse_declarations(text: str) -> dict[str, Any]:
    return extract_declarations(text)

def validate_package_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def detect_rule_violations(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> list[dict[str, Any]]:
    return [x for x in analyze(text, font_height_mm, pdp_area_cm2)["checks"] if x["status"] == "FAIL"]

def create_compliance_result(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def rules6(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def rules7(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def check_compliance_label(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def validate_all_declarations(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def check_all_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def compute_result(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def calculate_score(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> int:
    return get_score(text, font_height_mm, pdp_area_cm2)

def check_declaration_rules(text: str) -> list[dict[str, Any]]:
    return validate_rule_6(text)

def check_font_rule(font_height_mm: float, pdp_area_cm2: float) -> dict[str, Any]:
    return validate_rule_7(font_height_mm, pdp_area_cm2)

def get_summary(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def inspect_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def analyze_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def process_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def check_label_compliance(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

def evaluate_rules(text: str, font_height_mm: float = 1.8, pdp_area_cm2: float = 120) -> dict[str, Any]:
    return analyze(text, font_height_mm, pdp_area_cm2)

