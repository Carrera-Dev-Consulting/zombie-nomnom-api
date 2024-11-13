import pytest

from zombie_nomnom_api.graphql_app.dependencies import bootstrap


@pytest.fixture
def di_container():
    return bootstrap()
