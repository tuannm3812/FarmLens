from copy import deepcopy
import pytest
import requests
from conftest import FakeSession
from farmlens.land_cover import LandCoverClient

POINT=(-32.2569,148.6011)

def test_real_dea_fixture_preserves_pixel_year_and_axis_order(fixture_json,tmp_path):
    session=FakeSession(fixture_json('land_cover_dea.json'))
    client=LandCoverClient(tmp_path,session=session)
    got=client.fetch(*POINT)
    assert got.status=='live'
    assert got.data['class_code']==111 and got.data['label']=='Cultivated vegetation'
    assert got.data['year']==2025 and got.data['resolution_m']==30
    assert got.data['point']=={'lat':-32.2569,'lon':148.6011}
    p=session.calls[0][1]['params']
    assert p['version']=='1.3.0' and p['crs']=='EPSG:4326'
    assert p['layers']=='ga_ls_landcover_c3' and p['time']=='2025-01-01'
    a,b,c,d=map(float,p['bbox'].split(','))
    assert a < -32.2569 < c and b < 148.6011 < d
    assert p['i']==p['j']==1 and p['width']==p['height']==3
    assert client.fetch(*POINT).status=='cached'
    assert len(session.calls)==1
    assert '-32.25690_148.60110' in next(tmp_path.glob('*.json')).name

@pytest.mark.parametrize('damage',['year','axis','code','boolean','multiple','shape'])
def test_wrong_year_point_or_class_never_becomes_observation(fixture_json,tmp_path,damage):
    p=fixture_json('land_cover_dea.json');f=p['features'][0]
    if damage=='year':f['properties']['data'][0]['time']='2020-01-01'
    if damage=='axis':f['geometry']['coordinates']=list(POINT)
    if damage=='code':f['properties']['data'][0]['bands']['level3']=999
    if damage=='boolean':f['properties']['data'][0]['bands']['level3']=True
    if damage=='multiple':p['features'].append(deepcopy(f))
    if damage=='shape':p={}
    got=LandCoverClient(tmp_path,session=FakeSession(p,p)).fetch(*POINT)
    assert got.status=='offline' and got.data['class_code'] is None

@pytest.mark.parametrize('missing',['nodata','empty','no_feature'])
def test_nodata_is_an_explicit_missing_class(fixture_json,tmp_path,missing):
    p=fixture_json('land_cover_dea.json')
    if missing=='nodata':p['features'][0]['properties']['data'][0]['bands']['level3']=255
    if missing=='empty':p['features'][0]['properties']={}
    if missing=='no_feature':p['features']=[]
    got=LandCoverClient(tmp_path,session=FakeSession(p)).fetch(*POINT)
    assert got.status=='live' and got.data['class_code'] is None
    assert got.data['reason']

def test_retry_cache_recovery_and_close_points_do_not_share_class(fixture_json,tmp_path):
    p=fixture_json('land_cover_dea.json')
    client=LandCoverClient(tmp_path,session=FakeSession(requests.Timeout(),p))
    assert client.fetch(*POINT).status=='live'
    client.session=FakeSession(requests.Timeout(),requests.Timeout())
    assert client.fetch(*POINT,refresh=True).data['class_code']==111
    cached=LandCoverClient(tmp_path,cache_only=True)
    assert cached.fetch(*POINT).status=='cached'
    assert cached.fetch(-32.2579,148.6011).status=='offline'
    with pytest.raises(ValueError):cached.fetch(-35.28,149.13)
