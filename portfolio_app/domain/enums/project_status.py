from enum import Enum


class ProjectStatus(str, Enum):
    DEVAM_EDIYOR = "DEVAM_EDIYOR"
    TAMAMLANDI   = "TAMAMLANDI"
    BEKLEMEDE    = "BEKLEMEDE"
    IPTAL        = "IPTAL"

    def label(self) -> str:
        labels = {
            self.DEVAM_EDIYOR: "Devam Ediyor",
            self.TAMAMLANDI:   "Tamamlandı",
            self.BEKLEMEDE:    "Beklemede",
            self.IPTAL:        "İptal",
        }
        return labels[self]

    def color_key(self) -> str:
        colors = {
            self.DEVAM_EDIYOR: "info",
            self.TAMAMLANDI:   "success",
            self.BEKLEMEDE:    "warning",
            self.IPTAL:        "error",
        }
        return colors[self]
