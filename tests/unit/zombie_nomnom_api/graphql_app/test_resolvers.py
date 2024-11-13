from zombie_nomnom_api.graphql_app.resolvers import hello


def test_hello__when_resolving_value__is_french():
    value = hello(None, None)
    assert value == "Bonjour"
