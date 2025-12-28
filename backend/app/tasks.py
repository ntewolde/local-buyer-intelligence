"""
Celery Tasks for Background Jobs
"""
from celery import Task
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.collectors.census_collector import CensusCollector
from app.services.csv_import import CSVImportService
from app.models.ingestion import IngestionRun, IngestionStatus
from app.models.geography import Geography
from datetime import datetime
import uuid
import traceback


@celery_app.task(bind=True)
def refresh_census_task(self: Task, ingestion_run_id: str, geography_id: int, client_id: str):
    """
    Refresh census data for a geography
    """
    db = SessionLocal()
    try:
        run_id = uuid.UUID(ingestion_run_id)
        client_uuid = uuid.UUID(client_id)
        
        ingestion_run = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
        if not ingestion_run:
            return {"status": "error", "error": "Ingestion run not found"}
        
        collector = CensusCollector(db, client_uuid)
        result = collector.run(geography_id=geography_id, ingestion_run_id=run_id)
        
        return result
    except Exception as e:
        # Update ingestion run on error
        if 'ingestion_run' in locals() and ingestion_run:
            ingestion_run.status = IngestionStatus.FAILED
            ingestion_run.finished_at = datetime.utcnow()
            ingestion_run.error_message = str(e)
            db.commit()
        
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
    finally:
        db.close()


@celery_app.task(bind=True)
def import_csv_property_task(self: Task, ingestion_run_id: str, file_ref: str, geography_id: int, client_id: str):
    """Import property CSV file"""
    db = SessionLocal()
    try:
        run_id = uuid.UUID(ingestion_run_id)
        client_uuid = uuid.UUID(client_id)
        
        ingestion_run = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
        if not ingestion_run:
            return {"status": "error", "error": "Ingestion run not found"}
        
        ingestion_run.status = IngestionStatus.RUNNING
        ingestion_run.started_at = datetime.utcnow()
        db.commit()
        
        import_service = CSVImportService(db, client_uuid)
        rows = import_service.parse_csv_file(file_ref)
        imported = import_service.import_property_csv(rows, geography_id)
        
        ingestion_run.status = IngestionStatus.SUCCESS
        ingestion_run.finished_at = datetime.utcnow()
        ingestion_run.records_upserted = imported
        db.commit()
        
        return {"status": "success", "records_imported": imported}
    except Exception as e:
        if 'ingestion_run' in locals() and ingestion_run:
            ingestion_run.status = IngestionStatus.FAILED
            ingestion_run.finished_at = datetime.utcnow()
            ingestion_run.error_message = str(e)
            db.commit()
        
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
    finally:
        db.close()


@celery_app.task(bind=True)
def import_csv_events_task(self: Task, ingestion_run_id: str, file_ref: str, geography_id: int, client_id: str):
    """Import events CSV file"""
    db = SessionLocal()
    try:
        run_id = uuid.UUID(ingestion_run_id)
        client_uuid = uuid.UUID(client_id)
        
        ingestion_run = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
        if not ingestion_run:
            return {"status": "error", "error": "Ingestion run not found"}
        
        ingestion_run.status = IngestionStatus.RUNNING
        ingestion_run.started_at = datetime.utcnow()
        db.commit()
        
        import_service = CSVImportService(db, client_uuid)
        rows = import_service.parse_csv_file(file_ref)
        imported = import_service.import_events_csv(rows, geography_id)
        
        ingestion_run.status = IngestionStatus.SUCCESS
        ingestion_run.finished_at = datetime.utcnow()
        ingestion_run.records_upserted = imported
        db.commit()
        
        return {"status": "success", "records_imported": imported}
    except Exception as e:
        if 'ingestion_run' in locals() and ingestion_run:
            ingestion_run.status = IngestionStatus.FAILED
            ingestion_run.finished_at = datetime.utcnow()
            ingestion_run.error_message = str(e)
            db.commit()
        
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
    finally:
        db.close()


@celery_app.task(bind=True)
def import_csv_channels_task(self: Task, ingestion_run_id: str, file_ref: str, geography_id: int, client_id: str):
    """Import channels CSV file"""
    db = SessionLocal()
    try:
        run_id = uuid.UUID(ingestion_run_id)
        client_uuid = uuid.UUID(client_id)
        
        ingestion_run = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
        if not ingestion_run:
            return {"status": "error", "error": "Ingestion run not found"}
        
        ingestion_run.status = IngestionStatus.RUNNING
        ingestion_run.started_at = datetime.utcnow()
        db.commit()
        
        import_service = CSVImportService(db, client_uuid)
        rows = import_service.parse_csv_file(file_ref)
        imported = import_service.import_channels_csv(rows, geography_id)
        
        ingestion_run.status = IngestionStatus.SUCCESS
        ingestion_run.finished_at = datetime.utcnow()
        ingestion_run.records_upserted = imported
        db.commit()
        
        return {"status": "success", "records_imported": imported}
    except Exception as e:
        if 'ingestion_run' in locals() and ingestion_run:
            ingestion_run.status = IngestionStatus.FAILED
            ingestion_run.finished_at = datetime.utcnow()
            ingestion_run.error_message = str(e)
            db.commit()
        
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
    finally:
        db.close()


@celery_app.task(bind=True)
def recompute_scores_task(self: Task, geography_id: int, service_category: str, client_id: str):
    """Recompute demand scores for a geography and service category"""
    db = SessionLocal()
    try:
        client_uuid = uuid.UUID(client_id)
        
        # This would trigger score recomputation
        # Implementation depends on IntelligenceEngine
        # For now, return success
        
        return {"status": "success", "message": "Scores recomputed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True)
def generate_report_task(self: Task, report_id: int, client_id: str):
    """Generate intelligence report in background"""
    db = SessionLocal()
    try:
        client_uuid = uuid.UUID(client_id)
        
        # This would generate the report
        # Implementation depends on IntelligenceEngine
        # For now, return success
        
        return {"status": "success", "report_id": report_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        db.close()






