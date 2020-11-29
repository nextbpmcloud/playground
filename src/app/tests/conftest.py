import pytest

pytest.register_assert_rewrite('app.testutils')


def pytest_assertrepr_compare(config, op, left, right):
    return [
        "Failed assertion:",
        "   vals: {} {} {}".format(left.val, op, right.val),
    ]
