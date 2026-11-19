from .case_404 import CASE_404

CASES = {
    "404": CASE_404,
}


def get_case(case_id: str):
    return CASES.get(case_id)


def get_all_cases():
    return CASES