from pathlib import Path
import re

def test_frontend_has_no_browser_persistence_calls():
    root=Path(__file__).resolve().parents[2]/"frontend"/"src"
    pattern=re.compile(r"(?:localStorage|sessionStorage)\s*\.\s*(?:setItem|getItem|removeItem|clear)\s*\(|indexedDB\s*\.\s*(?:open|deleteDatabase)\s*\(",re.I)
    hits=[]
    for path in root.rglob("*"):
        if path.suffix.lower() in {".ts",".tsx",".js",".jsx"}:
            if pattern.search(path.read_text(encoding="utf-8",errors="ignore")): hits.append(path.name)
    assert not hits, hits
