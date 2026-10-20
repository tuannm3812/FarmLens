import pytest

from farmlens.location import in_nsw
from farmlens.config import PRESETS


@pytest.mark.parametrize("point", list(PRESETS.values()) + [(-33.87, 151.21), (-31.55, 159.08)])
def test_nsw_mainland_and_lord_howe_are_accepted(point):
    assert in_nsw(*point)


@pytest.mark.parametrize("point", [(-35.28,149.13), (-37.81,144.96), (-27.47,153.03), (-33,156), (0,0), (float('nan'),148)])
def test_act_other_states_ocean_and_invalid_points_are_rejected(point):
    assert not in_nsw(*point)
