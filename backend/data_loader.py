"""
Veri Yükleme Modülü
Data dizinindeki JSON veri dosyalarını yükler ve parse eder
"""
import json
from pathlib import Path
from typing import Dict, List, Any

def load_json_data(filename: str = None) -> Dict[str, Any]:
    """
    JSON veri dosyalarını yükler
    
    Args:
        filename: Belirli bir dosya adı (opsiyonel). None ise tüm dosyaları yükler.
    
    Returns:
        Eğer filename belirtilmişse, o dosyanın içeriği. 
        Yoksa employees, departments ve projects verilerini içeren dictionary

    Raises:
        FileNotFoundError: Veri dosyaları eksikse
        json.JSONDecodeError: JSON dosyaları geçersizse
    """
    data_dir = Path(__file__).parent / "data"
    
    # Belirli bir dosya istenmişse
    if filename:
        try:
            return json.loads((data_dir / filename).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Veri dosyasında geçersiz JSON: {e}", e.doc, e.pos)
    
    # Tüm dosyaları yükle
    try:
        employees = json.loads((data_dir / "employees.json").read_text(encoding="utf-8"))
        departments = json.loads((data_dir / "departments.json").read_text(encoding="utf-8"))
        projects = json.loads((data_dir / "projects.json").read_text(encoding="utf-8"))
        
        # Procedures dosyası varsa ekle
        procedures = []
        procedures_path = data_dir / "procedures.json"
        if procedures_path.exists():
            try:
                procedures = json.loads(procedures_path.read_text(encoding="utf-8"))
            except:
                procedures = []
        
        return {
            "employees": employees, 
            "departments": departments, 
            "projects": projects,
            "procedures": procedures
        }
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {e}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Veri dosyasında geçersiz JSON: {e}", e.doc, e.pos)

def find_employees_by_department(dept_name: str) -> List[str]:
    """
    Departman adına göre çalışanları bulur

    Args:
        dept_name: Aranacak departman adı

    Returns:
        Belirtilen departmandaki çalışan isimlerinin listesi
    """
    data_dir = Path(__file__).parent / "data"
    try:
        with open(data_dir / "employees.json", "r", encoding="utf-8") as f:
            employees = json.load(f)
        return [e.get("name", "") for e in employees if isinstance(e, dict) and e.get("department", "").lower() == dept_name.lower()]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return []
