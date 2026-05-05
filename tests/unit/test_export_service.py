"""tests/unit/test_export_service.py"""

import pytest
from unittest.mock import MagicMock

from services.export_service import ExportService
from services.dto.export_config import ExportConfig
from services.interfaces.i_exporter import IExporter


class DummyExporter(IExporter):
    def get_format_name(self) -> str:
        return "Dummy Format"
        
    def get_file_extension(self) -> str:
        return ".dummy"
        
    def export(self, info, projects, skills, edu, exp, certs, config) -> bytes:
        return b"dummy_content"


def test_export_service_registration():
    svc = ExportService()
    exporter = DummyExporter()
    svc.register_exporter("dummy", exporter)
    
    formats = svc.get_available_formats()
    assert len(formats) == 1
    assert formats[0]["key"] == "dummy"
    assert formats[0]["ext"] == ".dummy"


def test_export_service_export_success():
    svc = ExportService()
    svc.register_exporter("dummy", DummyExporter())
    
    result = svc.export("dummy", None, [], [], [], [], [], ExportConfig())
    assert result == b"dummy_content"


def test_export_service_export_not_found():
    svc = ExportService()
    with pytest.raises(ValueError, match="Bilinmeyen export formatı"):
        svc.export("unknown", None, [], [], [], [], [], ExportConfig())


def test_suggest_improvements_empty():
    svc = ExportService()
    class DummyInfo:
        pass
        
    suggestions = svc.suggest_improvements(DummyInfo(), [], [], [], [])
    assert len(suggestions) > 0
    assert any("teknik beceri eklemeniz" in s for s in suggestions)
    assert any("en az 3 proje" in s for s in suggestions)
    assert any("GitHub" in s for s in suggestions)
