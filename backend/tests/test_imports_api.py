import io
from app.models.geography import Geography

def test_property_csv_import_rejects_pii(client, client_token, db, test_client_account):
    # Create a geography for the test
    geography = Geography(
        name="Test Geography",
        client_id=test_client_account.id,
        type="CITY",
        state_code="GA"
    )
    db.add(geography)
    db.commit()
    db.refresh(geography)
    
    csv_data = "zip_code,email\n30043,test@test.com"
    res = client.post(
        f"/api/v1/import/property?geography_id={geography.id}",
        files={"file": ("bad.csv", io.BytesIO(csv_data.encode()), "text/csv")},
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code == 400

def test_property_csv_import_accepts_valid(client, client_token, db, test_client_account):
    # Create a geography for the test
    geography = Geography(
        name="Test Geography",
        client_id=test_client_account.id,
        type="CITY",
        state_code="GA"
    )
    db.add(geography)
    db.commit()
    db.refresh(geography)
    
    csv_data = "zip_code,property_type\n30043,SINGLE_FAMILY"
    res = client.post(
        f"/api/v1/import/property?geography_id={geography.id}",
        files={"file": ("good.csv", io.BytesIO(csv_data.encode()), "text/csv")},
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code in (200, 202)

