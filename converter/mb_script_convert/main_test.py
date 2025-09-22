from pathlib import Path

from .main import make_output_path


def test_make_output_path(tmp_path: Path):
    input_base = Path("input_base")
    input1 = input_base / Path("foo.pdf")
    input2 = input_base / Path("bar.pdf")
    input3 = input_base / Path("sub/baz.pdf")

    existing_output = tmp_path / "bar" / "index.html"
    existing_output.parent.mkdir(parents=True, exist_ok=True)
    existing_output.touch()

    assert make_output_path(input1, input_base, tmp_path) == tmp_path / "foo.html"
    assert (
        make_output_path(input2, input_base, tmp_path)
        == tmp_path / "bar" / "index.html"
    )
    assert (
        make_output_path(input3, input_base, tmp_path) == tmp_path / "sub" / "baz.html"
    )
