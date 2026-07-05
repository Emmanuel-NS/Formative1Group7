"""MongoDB repository for daily pharma sales records."""

from datetime import date, datetime, timezone
from typing import List, Optional

from app.constants import ATC_COLUMNS
from app.database import get_mongo_collection
from app.schemas import RecordCreate, RecordResponse, RecordUpdate


def _doc_to_response(doc: dict) -> RecordResponse:
    """
    Helper function to convert a raw MongoDB document into a RecordResponse schema.
    Args:
        doc (dict): The raw dictionary document from MongoDB.
    Returns:
        RecordResponse: The validated Pydantic response model.
    """
    sale_date = doc["sale_date"]
    if isinstance(sale_date, str):
        sale_date = date.fromisoformat(sale_date)

    return RecordResponse(
        record_id=doc["record_id"],
        sale_date=sale_date,
        total_demand=float(doc["total_demand"]),
        categories={k: float(v) for k, v in doc["categories"].items()},
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


def create_record(payload: RecordCreate) -> RecordResponse:
    """
    Creates a new daily pharma sales record in the database.
    Args:
        payload (RecordCreate): The data required to create a new record.
    Returns:
        RecordResponse: The newly created record.
    Raises:
        ValueError: If a record for the given sale_date already exists.
    """
    collection = get_mongo_collection()
    record_id = payload.sale_date.isoformat()
    if collection.find_one({"record_id": record_id}):
        raise ValueError(f"Record already exists for {payload.sale_date}")

    now = datetime.now(timezone.utc)
    doc = {
        "record_id": record_id,
        "sale_date": record_id,
        "total_demand": sum(payload.categories.values()),
        "categories": payload.categories,
        "source": "pharma_sales_daily",
        "created_at": now,
        "updated_at": now,
    }
    collection.insert_one(doc)
    return _doc_to_response(doc)


def get_record(record_id: str) -> Optional[RecordResponse]:
    """
    Retrieves a single record by its ID or sale date.
    Args:
        record_id (str): The unique identifier (or ISO date string) of the record.
    Returns:
        Optional[RecordResponse]: The record if found, otherwise None.
    """
    collection = get_mongo_collection()
    doc = collection.find_one({"record_id": record_id})
    if not doc and not record_id.isdigit():
        doc = collection.find_one({"sale_date": record_id})
    return _doc_to_response(doc) if doc else None


def update_record(record_id: str, payload: RecordUpdate) -> Optional[RecordResponse]:
    """
    Updates the categories and total demand of an existing record.
     Args:
        record_id (str): The unique identifier of the record to update.
        payload (RecordUpdate): The new data to apply.
    Returns:
        Optional[RecordResponse]: The updated record if successful, otherwise None.
    """
    collection = get_mongo_collection()
    now = datetime.now(timezone.utc)
    result = collection.find_one_and_update(
        {"record_id": record_id},
        {
            "$set": {
                "categories": payload.categories,
                "total_demand": sum(payload.categories.values()),
                "updated_at": now,
            }
        },
        return_document=True,
    )
    return _doc_to_response(result) if result else None


def delete_record(record_id: str) -> bool:
    """
    Deletes a specific record from the database.
    Args:
        record_id (str): The unique identifier of the record to delete.
    Returns:
        bool: True if a record was successfully deleted, False otherwise.
    """
    collection = get_mongo_collection()
    result = collection.delete_one({"record_id": record_id})
    return result.deleted_count > 0


def get_latest_record() -> Optional[RecordResponse]:
    """
    Fetches the most recent sales record based on the sale date.
   Returns:
        Optional[RecordResponse]: The latest record, or None if the collection is empty.
    """
    collection = get_mongo_collection()
    doc = collection.find_one(sort=[("sale_date", -1)])
    return _doc_to_response(doc) if doc else None


def get_records_by_range(start_date: date, end_date: date) -> List[RecordResponse]:
    """
    Retrieves all records within a specific date range, inclusive.
    Args:
        start_date (date): The beginning of the date range.
        end_date (date): The end of the date range.
     Returns:
        List[RecordResponse]: A list of records falling within the specified timeframe.
    """
    collection = get_mongo_collection()
    cursor = collection.find(
        {"sale_date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}}
    ).sort("sale_date", 1)
    return [_doc_to_response(doc) for doc in cursor]
