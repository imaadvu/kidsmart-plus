from core.dedupe import near_duplicate_indices


def test_near_duplicate_indices_simple():
    texts = [
        "Creative Writing for Kids in Melbourne",
        "Kids Creative Writing - Melbourne",
        "Advanced Robotics Workshop",
    ]
    sup = near_duplicate_indices(texts, threshold=0.3)
    # Should suppress one of the first two
    assert any(i in sup for i in (0, 1))
    # The robotics item should remain
    assert 2 not in sup

