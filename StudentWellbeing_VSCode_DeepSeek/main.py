import csv
import os
from pathlib import Path
from typing import Dict, List
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "student_screening.csv"
REPORT_DIR = BASE_DIR / "reports"


def normalise_yes_no(value: str) -> bool:
    return str(value).strip().lower() in {"ya", "yes", "y", "true", "1"}


def safe_int(value: str, minimum: int = 0, maximum: int = 3) -> int:
    number = int(value)
    if not minimum <= number <= maximum:
        raise ValueError(f"Skor mesti antara {minimum} dan {maximum}.")
    return number


def safe_float(value: str, minimum: float = 0, maximum: float = 100) -> float:
    number = float(value)
    if not minimum <= number <= maximum:
        raise ValueError(f"Nilai mesti antara {minimum} dan {maximum}.")
    return number


def calculate_screening(student: Dict[str, str]) -> Dict[str, object]:
    w1 = normalise_yes_no(student["whooley_q1"])
    w2 = normalise_yes_no(student["whooley_q2"])
    yes_count = int(w1) + int(w2)
    g1 = safe_int(student["gad2_q1"])
    g2 = safe_int(student["gad2_q2"])
    total = g1 + g2
    return {
        "whooley_q1": "Ya" if w1 else "Tidak",
        "whooley_q2": "Ya" if w2 else "Tidak",
        "whooley_yes_count": yes_count,
        "whooley_status": "Positif" if yes_count >= 1 else "Negatif",
        "gad2_q1": g1,
        "gad2_q2": g2,
        "gad2_total": total,
        "gad2_status": "Positif" if total >= 3 else "Negatif",
        "attendance_percentage": safe_float(student["attendance_percentage"]),
    }


def detect_safety_flags(student: Dict[str, str]) -> List[str]:
    text = " ".join([student.get("discipline_details", ""), student.get("teacher_observation", ""), student.get("parent_feedback", "")]).lower()
    keyword_map = {
        "senjata atau pisau": ["pisau", "senjata"],
        "keganasan serius": ["memukul guru", "serangan", "mencederakan orang"],
        "risiko mencederakan diri": ["mencederakan diri", "self-harm"],
        "risiko bunuh diri": ["bunuh diri", "suicide", "mahu mati"],
    }
    return [label for label, words in keyword_map.items() if any(word in text for word in words)]


def build_student_context(student: Dict[str, str]) -> str:
    s = calculate_screening(student)
    flags = detect_safety_flags(student)
    return f"""
DATA MURID
ID: {student['student_id']}
Nama: {student['student_name']}
Kelas: {student['class_name']}

KEPUTUSAN DIKIRA OLEH SISTEM
WHOOLEY Q1: {s['whooley_q1']}
WHOOLEY Q2: {s['whooley_q2']}
Bilangan jawapan Ya: {s['whooley_yes_count']}
Status WHOOLEY: {s['whooley_status']}
GAD-2 Q1: {s['gad2_q1']}
GAD-2 Q2: {s['gad2_q2']}
Jumlah GAD-2: {s['gad2_total']}/6
Status GAD-2: {s['gad2_status']}

DATA KONTEKS
Kehadiran: {s['attendance_percentage']}%
Sebab ketidakhadiran: {student['absence_reason']}
Salah laku: {student['discipline_details']}
Pemerhatian guru: {student['teacher_observation']}
Intervensi terdahulu: {student['previous_intervention']}
Maklum balas penjaga: {student['parent_feedback']}
Bendera keselamatan: {flags if flags else 'Tiada'}

Sediakan laporan berdasarkan data ini. Jangan ubah pengiraan sistem.
"""


def load_students() -> List[Dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def create_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY belum ditetapkan dalam terminal VS Code.")
    return OpenAI(api_key=api_key, base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))


def generate_report(client: OpenAI, student: Dict[str, str]) -> str:
    system_prompt = (BASE_DIR / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")
    rules = (BASE_DIR / "knowledge" / "screening_rules.txt").read_text(encoding="utf-8")
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        messages=[
            {"role": "system", "content": system_prompt + "\n\nRUJUKAN WAJIB:\n" + rules},
            {"role": "user", "content": build_student_context(student)},
        ],
        temperature=0.2,
        stream=False,
    )
    return response.choices[0].message.content or ""


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    client = create_client()
    for student in load_students():
        try:
            report = generate_report(client, student)
            output = REPORT_DIR / f"{student['student_id']}_report.txt"
            output.write_text(report, encoding="utf-8")
            print(f"Siap: {output.name}")
        except Exception as error:
            print(f"Gagal memproses {student.get('student_id', 'Unknown')}: {error}")


if __name__ == "__main__":
    main()
