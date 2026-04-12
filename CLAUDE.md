# CLAUDE.md — Developer Portfolio Management System

> Bu dosya Claude Code için yazılmış yaşayan bir proje rehberidir.
> Her önemli karardan önce bu dosyayı oku. Her iterasyon sonunda güncelle.

---

## 1. Proje Özeti

**Ne:** PySide6 ile geliştirilmiş masaüstü portföy yönetim uygulaması.  
**Kim için:** Yusuf — tek geliştirici, tek kullanıcı (admin = uygulama sahibi).  
**Ne değil:** Multi-user SaaS platformu, web uygulaması, başkalarının kullanacağı sistem.

### Vizyon
Geliştiricinin projelerini, sertifikalarını, vizyonunu ve kişisel bilgilerini sergileyen bir vitrin + bu içerikleri yöneten gizli bir admin paneli. Vitrin dışarıya açık; admin paneli tamamen gizli — URL yok, menü yok, iz yok.

---

## 2. Kritik Mimari Kararlar

### 2.1 Uygulama İki Bağımsız Alandan Oluşur

```
[VİTRİN]  →  Dışardan gelen ziyaretçinin gördüğü alan
[ADMIN]   →  Sadece Yusuf'un yönettiği gizli alan
```

**Vitrin özellikleri:**
- Hakkımda, Projelerim, Vizyon & Misyon, Sertifikalarım — tek sayfa, aşağı kaydırmalı
- Sabit navbar — tıklanınca smooth scroll ile ilgili bölüme gider
- Bölümler arası arka plan gradyan geçişleri (animasyonlu)
- Silver, blue, white tonları — modern, glass ve gradyan yapılar

**Admin paneli özellikleri:**
- Açılır/kapanır sidebar
- Proje CRUD + proje içinde görev/fikir/tasarım task'leri + ilerleme takibi
- Kişisel bilgi düzenleme
- Sertifika CRUD
- Kaynak/plan sayfası: kurs, video, repo linki, notlar, planlar

> ⚠️ Admin paneline erişim için gizli klavye kısayolu veya gizli tıklama combo'su kullanılacak. Login formu görünür olmamalı.

### 2.2 Mimari: Katmanlı + MVP Hybrid

```
Presentation  →  PySide6 Views + QML (karmaşık animasyonlar için)
Controller    →  View-Model koordinasyonu, input validation
Service       →  İş kuralları, use-case orkestrasyonu
Domain        →  Entity, Enum, Exception (saf Python, Qt bağımlılığı yok)
Infrastructure → DB, dosya sistemi, dışa aktarım
```

**Katman kuralı:** Her katman yalnızca bir alt katmanla konuşur. View → Repository doğrudan erişim **yasaktır**.

**DI akışı:** `main.py → DI Container → Repositories → Services → Controllers → Views → MainWindow`

### 2.3 Neden Bu Mimari?

Benim raporumda multi-user admin paneli (kullanıcı CRUD, içerik moderasyonu, istatistik) önerilmişti. **Bu gereksiz karmaşıklık** — sen tek kullanıcısın, moderasyon yapılacak başka kullanıcı yok. O bölümler budandı.

Senin raporunda Authentication modülü (kayıt, şifre sıfırlama) isteniyordu. **Gereksiz** — single-user uygulamada kayıt formu anlamsız. Basit PIN/şifre koruması yeterli, o da sadece admin giriş noktasını korur.

---

## 3. Klasör Yapısı

```
portfolio_app/
├── main.py                    # Giriş noktası, DI setup, gizli admin trigger
├── config.py                  # Tüm sabitler: DB path, tema, limitler, sürüm
├── di_container.py            # Dependency Injection container
│
├── presentation/
│   ├── showcase/              # VİTRİN — dışarıdan görülen
│   │   ├── main_window.py     # Tek sayfa scroll yapısı
│   │   ├── navbar.py          # Sabit üst bar
│   │   ├── sections/
│   │   │   ├── about_section.py
│   │   │   ├── projects_section.py
│   │   │   ├── vision_section.py
│   │   │   └── certificates_section.py
│   │   └── widgets/           # ProjectCard, CertCard, vb.
│   │
│   ├── admin/                 # ADMİN — gizli panel
│   │   ├── admin_window.py    # Admin ana penceresi
│   │   ├── sidebar.py         # Açılır/kapanır sidebar
│   │   └── pages/
│   │       ├── dashboard_page.py
│   │       ├── projects_page.py       # CRUD + task yönetimi
│   │       ├── personal_info_page.py
│   │       ├── certificates_page.py   # CRUD
│   │       └── resources_page.py      # Kurs/video/repo/not/plan
│   │
│   └── shared/                # Her iki alanda ortak widget'lar
│       ├── toast.py
│       ├── confirm_dialog.py
│       └── loading_overlay.py
│
├── controllers/
│   ├── showcase_controller.py
│   ├── project_controller.py
│   ├── certificate_controller.py
│   ├── personal_info_controller.py
│   └── resource_controller.py
│
├── services/
│   ├── project_service.py
│   ├── certificate_service.py
│   ├── personal_info_service.py
│   ├── resource_service.py
│   └── interfaces/            # ABC tanımları — her service için IService
│
├── domain/
│   ├── models/
│   │   ├── project.py
│   │   ├── certificate.py
│   │   ├── personal_info.py
│   │   ├── resource.py
│   │   └── task.py            # Proje task'leri
│   ├── enums/
│   │   ├── project_status.py
│   │   ├── task_type.py       # GÖREV / FİKİR / TASARIM
│   │   └── resource_type.py   # KURS / VİDEO / REPO
│   └── exceptions/
│       └── domain_exceptions.py
│
├── infrastructure/
│   ├── database/
│   │   ├── db_manager.py      # Bağlantı + migration runner
│   │   └── migrations/        # 001_initial.sql, 002_xxx.sql
│   ├── repositories/
│   │   ├── project_repository.py
│   │   ├── certificate_repository.py
│   │   ├── personal_info_repository.py
│   │   └── resource_repository.py
│   └── storage/
│       └── image_storage.py   # Görsel kaydetme/okuma/silme
│
├── styles/
│   ├── theme_engine.py        # Runtime QSS şablon işleyici
│   ├── constants.py           # Renkler, font boyutları, spacing — MERKEZ
│   ├── themes/
│   │   └── silver_blue.qss    # Ana tema
│   └── components/            # button.qss, card.qss, sidebar.qss, navbar.qss
│
├── resources/
│   ├── icons/                 # .svg ikonlar (bundled — internet gerektirmez)
│   └── fonts/                 # Gömülü fontlar
│
├── data/                      # Runtime veri (git'e ekleme!)
│   ├── portfolio.db
│   └── images/
│       ├── projects/
│       └── profile/
│
├── logs/                      # Uygulama logları
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
└── docs/
    └── decisions/             # Önemli mimari kararlar (ADR)
```

---

## 4. Veritabanı

### 4.1 SQLite — Tek Dosya

`data/portfolio.db` — sunucu yok, bağlantı yok, yedek = tek dosya kopyası.

### 4.2 Tablolar

```sql
-- Kişisel bilgiler (tek satır, id=1)
personal_info (id, full_name, title, bio, avatar_path, github_url, linkedin_url, website_url, email, vision_text, mission_text, updated_at)

-- Projeler
projects (id, title, short_description, full_description, status, github_url, demo_url, start_date, end_date, is_featured, display_order, created_at)

-- Proje görselleri
project_images (id, project_id, image_path, caption, display_order)

-- Proje teknoloji etiketleri
project_tags (id, project_id, tag_name)

-- Proje task'leri (GÖREV / FİKİR / TASARIM)
project_tasks (id, project_id, type, title, description, status, display_order, created_at)

-- Sertifikalar
certificates (id, name, issuer, date, verification_url, image_path, display_order)

-- Kaynaklar (kurs, video, repo, not, plan)
resources (id, type, title, url, notes, status, related_project_id, created_at)

-- Migration takibi
schema_migrations (version, applied_at)
```

### 4.3 Migration Sistemi

`db_manager.py` her açılışta `migrations/` klasörünü tarar, eksik versiyonları sırayla uygular. Geriye dönüş (rollback) şimdilik yok — yedek al, gerek olursa sıfırla.

---

## 5. Tasarım Sistemi

### 5.1 Renk Paleti (constants.py'de tanımlı — hiçbir widget'ta hardcode renk olmaz)

```python
# styles/constants.py
COLORS = {
    # Arka planlar
    "bg_primary":    "#0F1923",   # Koyu lacivert-siyah
    "bg_secondary":  "#162030",
    "bg_card":       "#1C2A3A",
    "bg_glass":      "rgba(28, 42, 58, 0.7)",

    # Silver/Blue/White ton sistemi
    "accent_blue":   "#4A9EFF",
    "accent_silver": "#B0BEC5",
    "text_primary":  "#E8EDF2",
    "text_secondary":"#8CA0B3",
    "white":         "#FFFFFF",

    # Gradyanlar (vitrin bölüm geçişleri)
    "grad_about":       "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F1923, stop:1 #162030)",
    "grad_projects":    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #162030, stop:1 #0D1F2D)",
    "grad_vision":      "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D1F2D, stop:1 #111827)",
    "grad_certs":       "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #111827, stop:1 #0F1923)",

    # Durum renkleri
    "success":       "#4CAF7D",
    "warning":       "#F59E0B",
    "error":         "#EF4444",
}
```

### 5.2 İkon Stratejisi — SVG Bundled

İnternet bağlantısı olmadan çalışması şart. Strateji:

1. `resources/icons/` klasörüne gerekli tüm `.svg` dosyaları kopyalanır
2. PyInstaller build'de bu klasör bundle'a dahil edilir
3. Runtime'da `QIcon` ile yüklenir — CDN, FontAwesome online bağlantısı YOK

**QtAwesome kullanma** — online bağlantı riski var, bundle'a gömülmesi zahmetli. Yerine curated SVG set kullan (Heroicons veya Feather Icons — MIT lisanslı, offline).

```python
# resources/icon_manager.py
class IconManager:
    _cache: dict[str, QIcon] = {}
    
    @classmethod
    def get(cls, name: str) -> QIcon:
        if name not in cls._cache:
            path = get_resource_path(f"resources/icons/{name}.svg")
            cls._cache[name] = QIcon(path)
        return cls._cache[name]
```

### 5.3 Animasyonlar

**QML kullan** karmaşık animasyonlar için:
- Vitrin bölüm geçişlerindeki gradyan animasyonları → QML `SequentialAnimation`
- Glass card hover efektleri → QML `Behavior on opacity`
- Sidebar açılıp kapanma → `QPropertyAnimation` (PySide6 yeterli)
- Scroll-triggered bölüm reveal → `QPropertyAnimation` + `QScrollArea` event

**Kural:** Animasyon süresi 200-400ms arası. 600ms üzeri = yavaş hissettir, kullanma.

### 5.4 QML — Ne Zaman, Ne Zaman Değil

| Kullan | Kullanma |
|--------|----------|
| Karmaşık animasyon sekansları | Form widget'ları |
| Particle/shader efektleri | Tablo/liste görünümleri |
| Smooth gradient geçişler | Admin CRUD sayfaları |
| Glass morphism kartlar | Basit buton/label |

---

## 6. Tasarım Kalıpları

| Pattern | Nerede | Neden |
|---------|--------|-------|
| Repository | Tüm DB erişimi | DB değişirse sadece infra katmanı etkilenir |
| Strategy | Görsel export (gelecekte) | Yeni format = yeni strateji sınıfı |
| Observer (Signals/Slots) | UI güncellemeleri | Qt'nin native mekanizması |
| Dependency Injection | Service bağımlılıkları | Test edilebilirlik, gevşek bağ |
| Factory | Widget üretimi | ProjectCardFactory, TaskCardFactory |
| Decorator | Admin erişim kontrolü | `@require_admin` — her admin işlemde doğrula |
| Singleton | DB bağlantısı, IconManager | Tek bağlantı, tek cache |

---

## 7. EXE Paketleme — PyInstaller

### 7.1 Path Yapılandırması (Kritik)

EXE içinde kaynak dosyalara erişim için tüm path'ler `get_resource_path()` üzerinden geçmeli:

```python
# config.py
import sys
import os

def get_resource_path(relative_path: str) -> str:
    """PyInstaller bundle veya normal çalışma için doğru path döner."""
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS  # PyInstaller temp dizini
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def get_data_path(relative_path: str) -> str:
    """Kullanıcı verisi (DB, görseller) — EXE yanında kalır."""
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "data", relative_path)
```

**Kural:** `resources/` → `get_resource_path()` | `data/` → `get_data_path()`

### 7.2 Virüs Damgasını Önleme

Windows Defender ve antivirüs yazılımları PyInstaller EXE'lerini sık sık yanlış pozitif işaretler. Önlemler:

1. **UPX kullanma:** `--noupx` flag'i ekle — UPX compression virüs imzasına benzer
2. **Code signing:** Ücretsiz self-signed sertifika bile tetikleyiciyi azaltır (signtool.exe)
3. **onefile yerine onedir:** `--onedir` ile tek EXE yerine klasör yapısı — daha az şüphe
4. **spec dosyası:** `pyinstaller portfolio.spec` — `--hidden-import` listesini manuel yönet
5. **VirusTotal testi:** Her release öncesi kontrol et

```python
# portfolio.spec (PyInstaller)
a = Analysis(
    ['main.py'],
    datas=[
        ('resources/', 'resources/'),
        ('styles/', 'styles/'),
    ],
    hiddenimports=['PySide6.QtSvg', 'PySide6.QtXml'],
    ...
)
exe = EXE(a.pure, ..., upx=False, ...)  # UPX KAPALI
```

---

## 8. Loglama

```python
# infrastructure/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Konsol (geliştirme)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # Dosya (production) — max 5MB, 3 yedek
    file_handler = RotatingFileHandler(
        get_data_path("../logs/app.log"),
        maxBytes=5_000_000, backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
```

**Loglama kuralı:** Her service ve repository başında `logger = logging.getLogger(__name__)`. Exception'lar `logger.exception()` ile loglanır (stack trace dahil).

---

## 9. Test Stratejisi

Her adım test edilerek ilerlenir. Feature eklenince test yazılır, test yazılmadan feature kapanmaz.

| Tür | Araç | Kapsam |
|-----|------|--------|
| Unit | pytest | Service, domain model, repository (in-memory DB) |
| Integration | pytest + SQLite test DB | CRUD akışları, migration |
| UI | pytest-qt | Kritik widget render, form submit |
| Manuel | Checklist | Her iterasyon sonunda görsel kontrol |

```python
# tests/conftest.py
@pytest.fixture
def test_db():
    """Her test için temiz in-memory SQLite."""
    manager = DBManager(":memory:")
    manager.run_migrations()
    yield manager
    manager.close()
```

---

## 10. Bellek Yönetimi

- Görsel cache: `IconManager` + `QPixmap` cache — aynı görsel tekrar diskten okunmaz
- Büyük listeler: `QAbstractListModel` + virtual scrolling — tüm kartları aynı anda render etme
- Ağır işlemler (görsel resize, gelecekte PDF export): `QThread` + `QThreadPool`
- Widget silme: `deleteLater()` kullan, Python GC'ye bırakma
- Admin sayfaları arası geçişte eski sayfayı `hide()` + yeni sayfayı `show()` — her geçişte yeniden oluşturma

---

## 11. Geliştirme Ortamı

```bash
# Kurulum
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# requirements.txt
PySide6>=6.6.0
Pillow>=10.0.0
pytest>=7.0.0
pytest-qt>=4.0.0
```

**venv kuralı:** `venv/` dizini `.gitignore`'da. `requirements.txt` her yeni paket eklenince güncellenir.

---

## 12. Git Commit Stratejisi

Her tamamlanan adımdan sonra Türkçe açıklamalı commit:

```
[alan]: kısa açıklama

[vitrin]: hakkımda bölümü eklendi
[admin]: proje CRUD sayfası tamamlandı
[db]: sertifikalar tablosu migrasyonu eklendi
[style]: silver-blue tema constants.py'a taşındı
[fix]: görsel yükleme path hatası düzeltildi
[test]: proje servisi unit testleri yazıldı
[refactor]: repository arayüzleri ABC'ye çıkarıldı
[docs]: animasyon kararı ADR'ye eklendi
```

**Branch stratejisi:** `main` (stabil) → `develop` (aktif) → `feature/alan-ozellik`

---

## 13. İterasyon Planı

| İterasyon | Kapsam | Çıktı |
|-----------|--------|-------|
| IT-1: İskelet | Klasör yapısı, DI container, DB + migration, constants/theme | Çalışan boş pencere |
| IT-2: Vitrin | Tek sayfa scroll yapısı, navbar, 4 bölüm iskelet, gradyan geçişler | Görsel vitrin |
| IT-3: Admin Giriş | Gizli admin trigger, admin penceresi, sidebar | Gizli admin erişimi |
| IT-4: Projeler | Proje CRUD, task yönetimi, proje kartı widget | Proje yönetimi |
| IT-5: Kişisel + Sertifika | Kişisel bilgi düzenleme, sertifika CRUD | Profil yönetimi |
| IT-6: Kaynaklar | Kurs/video/repo/not/plan sayfası | Kaynak deposu |
| IT-7: Polish | Animasyonlar, glass efektler, QML entegrasyonu, performans | Release candidate |
| IT-8: EXE | PyInstaller paketleme, virüs testi, dağıtım | Dağıtılabilir EXE |

---

## 14. Kesin Yasaklar

```
❌ View içinde doğrudan SQL sorgusu — katman ihlali
❌ Widget içinde hardcode renk (#FFFFFF gibi) — constants.py kullan
❌ Görselleri DB'de BLOB olarak saklamak — dosya yolu sakla
❌ Çalışan kodu büyük refactor etmek — küçük, cerrahi değişiklikler
❌ Test yazmadan feature tamamlandı demek
❌ get_resource_path() kullanmadan dosya yolu oluşturmak
❌ Exception'ı yakalay, logla, sessizce yut — hepsini yap, sadece loglayıp geçme yok
❌ Tek god class — sorumluluk ayrımına dikkat
```

---

## 15. Yapılacaklar — Başlangıç Sırası

1. `portfolio.spec` + `requirements.txt` + `.gitignore` + `venv`
2. `config.py` + `get_resource_path()` + `get_data_path()`
3. `styles/constants.py` — tüm renk paleti
4. `infrastructure/database/db_manager.py` + `migrations/001_initial.sql`
5. `di_container.py` + `main.py` iskelet
6. İlk boş vitrin penceresi — pencere açılıyor mu testi
7. Buradan iterasyonlar başlar

---

*Bu dosya yaşayan bir dokümandır. Her önemli karardan sonra güncelle. Güncellemeler commit mesajına `[docs]: CLAUDE.md güncellendi` şeklinde ekle.*
