"""controllers/certificate_controller.py — Sertifika CRUD koordinasyonu."""

import logging

from PySide6.QtCore import QObject, Signal

from services.certificate_service import CertificateService
from domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class CertificateController(QObject):
    certificates_changed = Signal()
    error_occurred       = Signal(str)

    def __init__(self, service: CertificateService):
        super().__init__()
        self._service = service

    def get_all(self):
        return self._service.get_all()

    def get_by_id(self, cert_id: int):
        return self._service.get_by_id(cert_id)

    def create(self, data: dict):
        try:
            cert = self._service.create(data)
            self.certificates_changed.emit()
            return cert
        except DomainException as e:
            logger.exception("Sertifika oluşturma hatası")
            self.error_occurred.emit(str(e))
            return None

    def update(self, cert_id: int, data: dict):
        try:
            cert = self._service.update(cert_id, data)
            self.certificates_changed.emit()
            return cert
        except DomainException as e:
            logger.exception("Sertifika güncelleme hatası")
            self.error_occurred.emit(str(e))
            return None

    def delete(self, cert_id: int):
        try:
            self._service.delete(cert_id)
            self.certificates_changed.emit()
        except DomainException as e:
            logger.exception("Sertifika silme hatası")
            self.error_occurred.emit(str(e))
