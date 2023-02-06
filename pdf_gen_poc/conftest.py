from django.core.cache import cache
from pytest import fixture


@fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    This enables database access for all unit tests. The alternative is to mark those that need it with @mark.django_db,
    but at this point, most tests need it, so we enable it globally. The performance impact should be minute.
    """
    pass


@fixture(autouse=True)
def clear_cache_after_test_run():
    yield cache.clear()
