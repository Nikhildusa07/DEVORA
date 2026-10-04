def test_devora_basic():
    project_name = "DEVORA"

    assert project_name == "DEVORA"


def test_requirement_is_valid():
    requirement = "Add a student attendance feature"

    assert requirement.strip() != ""


def test_invalid_requirement():
    requirement = ""

    assert requirement.strip() == ""