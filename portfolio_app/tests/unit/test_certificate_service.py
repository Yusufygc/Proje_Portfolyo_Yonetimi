"""tests/unit/test_certificate_service.py — Sertifika servisi unit testleri."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import pytest
from unittest.mock import MagicMock

from services.certificate_service import CertificateService
from domain.exceptions.domain_exceptions import ValidationError, NotFoundError


@pytest.fixture
def cert_service(cert_repo):
    storage = MagicMock()
    return CertificateService(cert_repo, storage)


def test_create_cert_success(cert_service):
    cert = cert_service.create({"name": "Python Sertifikası", "issuer": "Udemy"})
    assert cert.id is not None
    assert cert.name == "Python Sertifikası"


def test_create_cert_empty_name_raises(cert_service):
    with pytest.raises(ValidationError):
        cert_service.create({"name": ""})


def test_get_all(cert_service):
    cert_service.create({"name": "Cert A"})
    cert_service.create({"name": "Cert B"})
    certs = cert_service.get_all()
    assert len(certs) >= 2


def test_delete_cert(cert_service):
    cert = cert_service.create({"name": "Silinecek Cert"})
    cert_service.delete(cert.id)
    with pytest.raises(NotFoundError):
        cert_service.get_by_id(cert.id)
