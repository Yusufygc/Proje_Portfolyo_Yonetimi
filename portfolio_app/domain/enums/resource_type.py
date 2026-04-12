from enum import Enum


class ResourceType(str, Enum):
    KURS  = "KURS"
    VIDEO = "VIDEO"
    REPO  = "REPO"
    NOT   = "NOT"
    PLAN  = "PLAN"

    def label(self) -> str:
        labels = {
            self.KURS:  "Kurs",
            self.VIDEO: "Video",
            self.REPO:  "Repo",
            self.NOT:   "Not",
            self.PLAN:  "Plan",
        }
        return labels[self]

    def icon_name(self) -> str:
        icons = {
            self.KURS:  "book-open",
            self.VIDEO: "play-circle",
            self.REPO:  "code",
            self.NOT:   "file-text",
            self.PLAN:  "map",
        }
        return icons[self]


class ResourceStatus(str, Enum):
    PLANLI     = "PLANLI"
    DEVAM_EDIYOR = "DEVAM_EDIYOR"
    TAMAMLANDI = "TAMAMLANDI"

    def label(self) -> str:
        labels = {
            self.PLANLI:       "Planlı",
            self.DEVAM_EDIYOR: "Devam Ediyor",
            self.TAMAMLANDI:   "Tamamlandı",
        }
        return labels[self]
