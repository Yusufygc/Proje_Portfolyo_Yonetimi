"""services/certificate_service.py — Sertifika iş kuralları."""

import logging

from services.interfaces.i_service import ICertificateService
from infrastructure.repositories.certificate_repository import CertificateRepository
from infrastructure.storage.image_storage import ImageStorage
from domain.models.certificate import Certificate
from domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class CertificateService(ICertificateService):
    def __init__(self, repo: CertificateRepository, storage: ImageStorage):
        self._repo = repo
        self._storage = storage

    def get_all(self) -> list[Certificate]:
        return self._repo.get_all()

    def get_by_id(self, cert_id: int) -> Certificate:
        return self._repo.get_by_id(cert_id)

    def create(self, data: dict) -> Certificate:
        self._validate(data)
        cert = Certificate(
            id=None,
            name=data["name"].strip(),
            issuer=data.get("issuer", "").strip(),
            date=data.get("date") or None,
            verification_url=data.get("verification_url") or None,
            image_path=None,
            display_order=int(data.get("display_order", 0)),
        )
        cert = self._repo.create(cert)
        if data.get("image_source_path"):
            cert.image_path = self._storage.save_cert_image(
                data["image_source_path"], cert.id
            )
            self._repo.update(cert)
        return cert

    def update(self, cert_id: int, data: dict) -> Certificate:
        self._validate(data)
        cert = self._repo.get_by_id(cert_id)
        cert.name = data["name"].strip()
        cert.issuer = data.get("issuer", "").strip()
        cert.date = data.get("date") or None
        cert.verification_url = data.get("verification_url") or None
        cert.display_order = int(data.get("display_order", 0))
        if data.get("image_source_path"):
            if cert.image_path:
                self._storage.delete(cert.image_path)
            cert.image_path = self._storage.save_cert_image(
                data["image_source_path"], cert.id
            )
        return self._repo.update(cert)

    def delete(self, cert_id: int) -> None:
        cert = self._repo.get_by_id(cert_id)
        if cert.image_path:
            self._storage.delete(cert.image_path)
        self._repo.delete(cert_id)

    @staticmethod
    def _validate(data: dict) -> None:
        if not data.get("name", "").strip():
            raise ValidationError("Sertifika adı boş olamaz.")
