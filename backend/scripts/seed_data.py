# -*- coding: utf-8 -*-
"""
Module: Seed Initial Data Script
Description: Loads employees, projects, departments, and procedures from JSON files into database as Documents
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from core.database import sync_engine, init_database
from core.config import get_settings
from models.document_model import Document
from services.document_service import document_service

settings = get_settings()


def load_json_data():
    """Load initial data from JSON files into database"""
    print("\n" + "=" * 60)
    print("Seeding Initial Data (Employees, Projects, Departments, Procedures)")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\nERROR: Database not configured. Set DATABASE_URL in .env")
        return False
    
    data_dir = Path(__file__).parent.parent / "data"
    
    # Map JSON files to document types
    file_mapping = {
        "employees.json": "employee",
        "projects.json": "project",
        "departments.json": "department",
        "procedures.json": "procedure"
    }
    
    total_loaded = 0
    total_skipped = 0
    
    with Session(sync_engine) as session:
        for filename, doc_type in file_mapping.items():
            file_path = data_dir / filename
            
            if not file_path.exists():
                print(f"[SKIP] File not found: {filename}")
                continue
            
            print(f"\nLoading {filename}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    print(f"[SKIP] {filename} is not a list")
                    continue
                
                loaded_count = 0
                skipped_count = 0
                
                for item in data:
                    # Check if document already exists
                    # Use a unique identifier - for employees/projects use id, for others use name
                    unique_id = item.get("id") or item.get("name")
                    if unique_id:
                        existing = session.exec(
                            select(Document).where(
                                Document.doc_type == doc_type,
                                Document.body.contains({"id": unique_id})
                            )
                        ).first()
                        
                        if existing:
                            skipped_count += 1
                            continue
                    
                    # Create document body
                    doc_body = {
                        "data": item,
                        "source": filename
                    }
                    
                    # Determine title
                    title = item.get("name") or item.get("title") or f"{doc_type.title()} {unique_id}"
                    
                    # Create document body
                    doc_body = {
                        "data": item,
                        "source": filename
                    }
                    
                    # Determine department
                    department = item.get("department") if doc_type != "department" else item.get("name")
                    
                    # Create document
                    document = Document(
                        doc_type=doc_type,
                        body=doc_body,
                        title=title,
                        department=department,
                        uploaded_by=None,  # System document
                        chunk_count=1
                    )
                    
                    session.add(document)
                    loaded_count += 1
                
                session.commit()
                
                print(f"  [OK] Loaded {loaded_count} {doc_type}(s), skipped {skipped_count} existing")
                total_loaded += loaded_count
                total_skipped += skipped_count
                
            except Exception as e:
                print(f"  [FAIL] Error loading {filename}: {e}")
                session.rollback()
                continue
    
    print("\n" + "=" * 60)
    print(f"Summary: {total_loaded} documents loaded, {total_skipped} skipped")
    print("=" * 60)
    
    if total_loaded > 0:
        print("\n[SUCCESS] Initial data loaded!")
        print("\nNote: Run RAG service initialization to index these documents in FAISS")
        return True
    else:
        print("\n[WARNING] No new documents loaded")
        return False


def main():
    """Main function"""
    success = load_json_data()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

