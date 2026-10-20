import pytest
from farmlens.soil_factors import soil_group, texture_score, carbon_score
from farmlens.scoring import load_crops, score_crop


@pytest.mark.parametrize("clay,sand,want", [(40,30,"heavy"),(10,80,"light"),(25,40,"medium"),(None,50,None),(25,None,None),(60,60,None),(float('nan'),40,None),(-1,50,None)])
def test_soil_groups_and_invalid_data(clay,sand,want):
    assert soil_group(clay,sand) == want


def test_crop_texture_preferences_are_specific():
    crops={c['id']:c for c in load_crops()}
    assert texture_score(crops['canola'],10,80) == 100
    assert texture_score(crops['barley'],10,80) == 70
    assert texture_score(crops['wheat'],10,80) == 40
    assert texture_score(crops['wheat'],25,40) == 100
    assert texture_score(crops['rice'],45,30) == 100
    assert texture_score(crops['rice'],None,30) is None


@pytest.mark.parametrize("gkg,want", [(0,50),(8,70),(15,90),(20,100),(40,100),(None,None),(-1,None),(float('inf'),None),(1001,None)])
def test_carbon_units_interpolation_and_no_zero_cap(gkg,want):
    assert carbon_score(gkg) == want


def test_texture_and_carbon_change_score_without_overriding_absolute_limits():
    barley=next(c for c in load_crops() if c['id']=='barley')
    base=dict(temperature_c=18,rainfall_mm=800,ph=7,frost_min_c=5,fire_exposure='low')
    good=score_crop(barley,**base,clay_pct=25,sand_pct=40,soc_g_kg=20)
    poor=score_crop(barley,**base,clay_pct=10,sand_pct=80,soc_g_kg=0)
    assert good['total']==100
    assert poor['total']==pytest.approx(93)
    assert poor['subscores']['texture']==70
    assert poor['subscores']['carbon']==50
    assert not poor['zero_capped']
    poor=score_crop(barley,**{**base,'rainfall_mm':0},clay_pct=25,sand_pct=40,soc_g_kg=20)
    assert poor['total']<=20 and poor['zero_capped']
