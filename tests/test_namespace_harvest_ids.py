from scripts.namespace_harvest_ids import namespaced_question_id, rewrite_question_ids


def test_namespaced_question_id_uses_pdf_name_and_global_question_number() -> None:
    assert (
        namespaced_question_id("2023_tier1_prepp_2023-07-14_shift1", 42)
        == "harvest_2023_tier1_prepp_2023-07-14_shift1_q42"
    )


def test_rewrite_question_ids_sets_question_and_resolved_ids() -> None:
    data = {
        "questions": [
            {"question_id": "264330", "resolved_question_id": "old", "global_question_number": 1},
            {"question_id": None, "global_question_number": "2"},
        ]
    }

    changed = rewrite_question_ids(data, "paper_a")

    assert changed == 4
    assert data["questions"][0]["question_id"] == "harvest_paper_a_q1"
    assert data["questions"][0]["resolved_question_id"] == "harvest_paper_a_q1"
    assert data["questions"][1]["question_id"] == "harvest_paper_a_q2"
    assert data["questions"][1]["resolved_question_id"] == "harvest_paper_a_q2"
