from .schema import Query


@Query.hello
def hello(_, __):
    return "Bonjour"
