from audit_inference_links import validate


def test_broadened_inference_recode_validates():
    counts = validate()
    assert counts["papers"] == 26
    assert counts["held_out_predictive"] >= 6
    assert counts["fixed_benchmark"] >= 4
    assert counts["formal_population_prediction"] == 0
