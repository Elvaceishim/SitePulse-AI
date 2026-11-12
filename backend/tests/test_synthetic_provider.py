from app.providers.synthetic import SyntheticRiskProvider


def test_provider_returns_three_sites():
    provider = SyntheticRiskProvider()

    sites = provider.get_sites()

    assert len(sites) == 3


def test_provider_returns_six_assessments():
    provider = SyntheticRiskProvider()

    assessments = provider.get_risk_assessments()

    assert len(assessments) == 6


def test_assessments_reference_existing_sites():
    provider = SyntheticRiskProvider()

    site_ids = {site.id for site in provider.get_sites()}

    for assessment in provider.get_risk_assessments():
        assert assessment.site_id in site_ids


def test_all_provider_data_is_marked_synthetic():
    provider = SyntheticRiskProvider()

    for assessment in provider.get_risk_assessments():
        assert assessment.data_is_synthetic is True


def test_assessments_have_timezone_aware_timestamps():
    provider = SyntheticRiskProvider()

    for assessment in provider.get_risk_assessments():
        assert assessment.observed_at.tzinfo is not None