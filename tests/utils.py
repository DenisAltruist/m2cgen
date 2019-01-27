import contextlib
import shutil
import tempfile

from sklearn.datasets import load_boston
from sklearn.utils import shuffle

from m2cgen import ast


def cmp_exprs(left, right):
    """Recursively compares two ast expressions."""

    if not isinstance(left, ast.Expr) and not isinstance(right, ast.Expr):
        assert left == right
        return True

    if isinstance(left, ast.Expr) and isinstance(right, ast.Expr):
        assert isinstance(left, type(right)), (
            "Expected instance of {}, received {}".format(
                type(right), type(left)))

        # Only compare attributes which don't start with __
        attrs_to_compare = filter(
            lambda attr_name: not attr_name.startswith('__'), dir(left))

        for attr_name in attrs_to_compare:
            assert cmp_exprs(
                getattr(left, attr_name), getattr(right, attr_name))

        return True

    return False


def assert_code_equal(actual, expected):
    assert actual.strip() == expected.strip()


def train_model(estimator, test_fraction=0.1):
    boston = load_boston()

    X, y = shuffle(boston.data, boston.target, random_state=13)

    offset = int(X.shape[0] * (1 - test_fraction))
    X_train, y_train = X[:offset], y[:offset]
    X_test = X[offset:]

    estimator.fit(X_train, y_train)

    y_pred = estimator.predict(X_test)

    return X_test, y_pred


@contextlib.contextmanager
def tmp_dir():
    dirpath = tempfile.mkdtemp()

    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)
