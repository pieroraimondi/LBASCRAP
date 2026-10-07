"""Regression test per la tolleranza delle righe aggregate LNP."""
from pathlib import Path


def test_parser_no_longer_requires_exactly_one_footer_row():
    source = Path(__file__).with_name('a2_tabellini.py').read_text()
    assert "len(stats) != len(identities) + 1" not in source
    assert "len(stats) < len(identities)" in source
    assert "player_stats = stats[:len(identities)]" in source


if __name__ == '__main__':
    test_parser_no_longer_requires_exactly_one_footer_row()
    print('A2 parser regression: OK')
