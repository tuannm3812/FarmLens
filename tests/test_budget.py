import pytest
from farmlens.budget import assess_budget, budget_metadata


def row(**kwargs):
    return {'crop_id':'wheat','yield_t_ha':3,'price_aud_t':300,
            'variable_aud_ha':500,'selling_aud_t':20,'irrigation_aud_ha':100,**kwargs}


def test_budget_accounts_for_yield_based_selling_and_irrigation_costs():
    got=assess_budget({'rows':[row()]})['rows'][0]
    assert got['revenue_aud_ha']==900
    assert got['cost_aud_ha']==660
    assert got['margin_aud_ha']==240
    assert got['break_even_price_aud_t']==220
    assert got['break_even_yield_t_ha']==pytest.approx(600/280)
    assert got['sensitivity']['low']==pytest.approx(-72)
    assert got['sensitivity']['high']==pytest.approx(624)


def test_missing_and_zero_inputs_are_distinct():
    assert assess_budget({'rows':[row(yield_t_ha=None)]})['rows'][0]['status']=='incomplete'
    got=assess_budget({'rows':[row(yield_t_ha=0)]})['rows'][0]
    assert got['margin_aud_ha']==-600 and got['break_even_price_aud_t'] is None
    assert got['revenue_aud_ha']==0
    assert assess_budget({'rows':[row(price_aud_t=20)]})['rows'][0]['break_even_yield_t_ha'] is None


def test_zero_contribution_and_zero_fixed_costs_break_even_at_any_yield():
    got = assess_budget({'rows':[row(
        price_aud_t=20, selling_aud_t=20, variable_aud_ha=0, irrigation_aud_ha=0,
    )]})['rows'][0]
    assert got['margin_aud_ha'] == 0
    assert got['break_even_yield_t_ha'] is None
    assert got['break_even_yield_any'] is True
    assert assess_budget({'rows':[row(price_aud_t=20)]})['rows'][0]['break_even_yield_any'] is False


@pytest.mark.parametrize('field,value', [('yield_t_ha',-1),('price_aud_t',float('nan')),
    ('variable_aud_ha',True),('irrigation_aud_ha',float('inf')),('selling_aud_t','20'),
    ('yield_t_ha',31),('crop_id','olives')])
def test_invalid_inputs_are_rejected(field,value):
    with pytest.raises(ValueError):assess_budget({'rows':[row(**{field:value})]})


def test_duplicate_crops_and_missing_costs_do_not_produce_comparison():
    with pytest.raises(ValueError):assess_budget({'rows':[row(),row()]})
    r=row();del r['selling_aud_t']
    assert assess_budget({'rows':[r]})['rows'][0]['status']=='incomplete'


def test_archived_examples_reproduce_published_base_margins_and_retain_provenance():
    meta=budget_metadata()
    rows=[dict(crop_id=k,**v['example']) for k,v in meta['profiles'].items()]
    got={r['crop_id']:r for r in assess_budget({'rows':rows})['rows']}
    assert got['wheat']['margin_aud_ha']==pytest.approx(118.59)
    assert got['barley']['margin_aud_ha']==pytest.approx(58.86)
    assert got['canola']['margin_aud_ha']==pytest.approx(265.39)
    assert all(p['year']==2012 and p['region']=='Central West NSW' for p in meta['profiles'].values())
