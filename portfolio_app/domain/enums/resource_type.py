"""domain/enums/resource_type.py — Kaynak durum ve öncelik enum'ları."""

from enum import Enum


class ResourceStatus(str, Enum):
    PLANLI       = "PLANLI"
    DEVAM_EDIYOR = "DEVAM_EDIYOR"
    TAMAMLANDI   = "TAMAMLANDI"

    def label(self) -> str:
        labels = {
            self.PLANLI:       "Planlı",
            self.DEVAM_EDIYOR: "Devam Ediyor",
            self.TAMAMLANDI:   "Tamamlandı",
        }
        return labels[self]


class ResourcePriority(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"
    URGENT = "URGENT"

    def label(self) -> str:
        labels = {
            self.LOW:    "Düşük",
            self.MEDIUM: "Orta",
            self.HIGH:   "Yüksek",
            self.URGENT: "Acil",
        }
        return labels[self]

    def color(self) -> str:
        colors = {
            self.LOW:    "#8B949E",
            self.MEDIUM: "#2F81F7",
            self.HIGH:   "#D29922",
            self.URGENT: "#EF4444",
        }
        return colors[self]


# Geriye uyumluluk — eski enum hâlâ import edilebilir ama artık kullanılmıyor
# Kaynak türleri artık DB'den dinamik olarak yönetiliyor (resource_types tablosu)
class ResourceType(str, Enum):
    """Eski statik enum — geriye uyumluluk için korunuyor.
    Yeni kod ResourceTypeDynamic kullanmalı."""
    KURS  = "Kurs"
    VIDEO = "Video"
    REPO  = "Repo"
    NOT   = "Not"
    PLAN  = "Plan"

    def label(self) -> str:
        return self.value
