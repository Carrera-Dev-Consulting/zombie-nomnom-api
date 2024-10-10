from zombie_nomnom_api.server import _version, fastapi_app


def test_server__when_module_loaded__sets_fastapi_version_to_version_in_file():
    assert fastapi_app.version == _version
