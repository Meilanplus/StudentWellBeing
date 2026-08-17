\
CARA MENJALANKAN DALAM VS CODE (WINDOWS)

1. Ekstrak ZIP dan buka folder ini dalam VS Code.
2. Buka Terminal > New Terminal.
3. Jalankan satu demi satu:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

4. Tetapkan API key:

$env:DEEPSEEK_API_KEY="MASUKKAN_API_KEY_ANDA"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"

5. Jalankan:

python main.py

6. Laporan muncul dalam folder reports.

EDIT DATA
- Buka data/student_screening.csv menggunakan Excel.
- Kekalkan nama lajur pada baris pertama.
- Simpan semula sebagai CSV UTF-8.

PENTING
- Jangan masukkan API key dalam main.py.
- Gunakan data dummy semasa pembangunan.
- Output bukan diagnosis dan mesti disemak oleh manusia.
