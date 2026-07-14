Set-Location -LiteralPath $PSScriptRoot
python scripts\prepare_data.py --input "C:\Users\zyt18\Downloads\scholar-data-full.txt"
python scripts\build_vector_index.py
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
