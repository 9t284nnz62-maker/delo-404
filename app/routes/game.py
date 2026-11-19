from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..data import get_case

bp = Blueprint("game", __name__, url_prefix="/case")


# ---------- Работа с прогрессом (пока в сессии, позже — в БД) ----------
def _progress_key(case_id: str) -> str:
    return f"studied_{case_id}"


def _get_studied(case_id: str) -> set[str]:
    return set(session.get(_progress_key(case_id), []))


# ---------- Маршруты ----------
@bp.route("/<case_id>")
def case_view(case_id: str):
    case = get_case(case_id)
    if not case:
        abort(404)

    studied = _get_studied(case_id)
    available = [m for m in case["materials"].values() if m.get("available")]
    total_available = len(available)
    studied_available = sum(1 for m in available if m["id"] in studied)
    progress_pct = int(studied_available / total_available * 100) if total_available else 0

    return render_template(
        "case.html",
        case=case,
        studied=studied,
        progress={
            "pct": progress_pct,
            "studied": studied_available,
            "total": total_available,
        },
    )


@bp.route("/<case_id>/study/<material_id>", methods=["POST"])
def study_material(case_id: str, material_id: str):
    case = get_case(case_id)
    if not case:
        abort(404)

    material = case["materials"].get(material_id)
    if not material or not material.get("available"):
        abort(404)

    studied = _get_studied(case_id)
    studied.add(material_id)
    session[_progress_key(case_id)] = list(studied)
    session.modified = True

    return redirect(
        url_for("game.case_view", case_id=case_id, tab="evidence") + f"#m-{material_id}"
    )


@bp.route("/<case_id>/reset", methods=["POST"])
def reset_case(case_id: str):
    session.pop(_progress_key(case_id), None)
    return redirect(url_for("game.case_view", case_id=case_id))


@bp.route("/<case_id>/accuse", methods=["GET", "POST"])
def accuse(case_id: str):
    case = get_case(case_id)
    if not case:
        abort(404)

    if request.method == "POST":
        accused_id = request.form.get("suspect", "")
        studied = _get_studied(case_id)
        key_evidence = set(case["key_evidence"])

        if not key_evidence.issubset(studied):
            return render_template(
                "accuse.html",
                case=case,
                studied=studied,
                error="Вы ещё не изучили все ключевые улики. Соберите доказательства.",
            )

        correct = accused_id == case["solution"]["accused"]
        return render_template(
            "result.html",
            case=case,
            accused_id=accused_id,
            correct=correct,
        )

    return render_template(
        "accuse.html",
        case=case,
        studied=_get_studied(case_id),
    )