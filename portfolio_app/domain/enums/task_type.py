from enum import Enum


class TaskType(str, Enum):
    GOREV   = "GOREV"
    FIKIR   = "FIKIR"
    TASARIM = "TASARIM"

    def label(self) -> str:
        labels = {
            self.GOREV:   "Görev",
            self.FIKIR:   "Fikir",
            self.TASARIM: "Tasarım",
        }
        return labels[self]


class TaskStatus(str, Enum):
    BEKLIYOR     = "BEKLIYOR"
    DEVAM_EDIYOR = "DEVAM_EDIYOR"
    TAMAMLANDI   = "TAMAMLANDI"

    def label(self) -> str:
        labels = {
            self.BEKLIYOR:     "Bekliyor",
            self.DEVAM_EDIYOR: "Devam Ediyor",
            self.TAMAMLANDI:   "Tamamlandı",
        }
        return labels[self]
