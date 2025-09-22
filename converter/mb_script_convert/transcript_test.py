from .transcript import Metadata


def test_merge_metadata():
    m1 = Metadata(episode_title="Panopticon")
    m2 = Metadata(season=4)
    m1.merge(m2)

    assert m1 == Metadata(episode_title="Panopticon", season=4)
