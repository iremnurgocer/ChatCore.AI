# backend/data_loader.py
import json
from pathlib import Path

def load_json_data():
    data_dir = Path(__file__).parent / "data"
    employees = json.loads((data_dir / "employees.json").read_text(encoding="utf-8"))
    departments = json.loads((data_dir / "departments.json").read_text(encoding="utf-8"))
    projects = json.loads((data_dir / "projects.json").read_text(encoding="utf-8"))
    return {"employees": employees, "departments": departments, "projects": projects}
def find_employees_by_department(dept_name):
    with open("data/employees.json", "r") as f:
        employees = json.load(f)
    return [e["name"] for e in employees if e["department"].lower() == dept_name.lower()]
