from route_graph_repair_design import components, repair


def test_h233_known_answer_repair() -> None:
    assert repair(3, ((0, 2), (1, 2)))["minimum_new_pair_types"] == 0
    b_repair = repair(3, ((0, 1),))
    assert b_repair["minimum_new_pair_types"] == 1
    assert b_repair["selected_edges"] in ([[0, 2]], [[1, 2]])


def test_empty_context_requires_spanning_tree() -> None:
    for k in range(2, 12):
        result = repair(k, ())
        assert result["minimum_new_pair_types"] == k - 1
        assert len(result["selected_edges"]) == k - 1


def test_allowable_edge_failure_is_fail_closed() -> None:
    result = repair(4, ((0, 1),), ((2, 3),))
    assert result["feasible"] is False
    assert result["minimum_new_pair_types"] is None
    assert result["selected_edges"] == []


def test_costed_quotient_selects_cheapest_policy_bridges() -> None:
    costs = {(0, 2): 7, (1, 2): 2, (2, 3): 3, (0, 3): 11}
    result = repair(4, ((0, 1),), tuple(costs), costs)
    assert result["selected_edges"] == [[1, 2], [2, 3]]
    assert result["total_cost"] == 5


def test_repeated_edges_do_not_change_components() -> None:
    assert components(4, ((0, 1), (1, 2))) == components(
        4, ((0, 1), (0, 1), (1, 2), (1, 2))
    )
