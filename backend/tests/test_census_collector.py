import responses
import uuid
from app.collectors.census_collector import CensusCollector

@responses.activate
def test_census_collector_ingests_data(db):
    responses.add(
        responses.GET,
        "https://api.census.gov/data/2022/acs/acs5",
        json=[["NAME","B01003_001E"],["30043",1000]],
        status=200
    )
    collector = CensusCollector(db, uuid.uuid4())
    data = collector.collect(zip_codes=["30043"])
    assert data is not None



