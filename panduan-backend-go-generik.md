# Panduan Tahapan Membangun Backend Golang (REST API) — Generik & Bisa Dikustomisasi

Panduan ini adalah **versi umum** dari tutorial Go + PostgreSQL di `pertemuan-04` (studi kasus UMKM). Isinya tahapan yang sama persis strukturnya, tapi ditulis dengan **placeholder** sehingga bisa dipakai untuk **topik proyek apa pun** yang dipilih mahasiswa di `pertemuan-10` (perpustakaan, parkir, laundry, inventaris, booking lapangan, dll).

Cara pakai: setiap kali muncul tanda `[ENTITAS]`, `[ENTITAS_ANAK]`, atau `[FIELD]`, ganti dengan nama sesuai domain proyekmu. Contoh pemetaan dari studi kasus UMKM:

| Placeholder | Contoh di UMKM (pertemuan-04) | Contoh di proyek lain |
|---|---|---|
| `[ENTITAS_UTAMA]` | `umkm` | `buku`, `kendaraan`, `kamar_kos`, `pelanggan_laundry` |
| `[ENTITAS_ANAK]` | `produk` | `peminjaman`, `transaksi_parkir`, `pesanan` |
| `[ENTITAS_PEMILIK]` | `user` (pemilik UMKM) | `user` (anggota, admin, member) |

---

## 01 Tahap 0 — Menentukan Kontrak Sebelum Menulis Kode

Sebelum membuka VS Code, jawab dulu pertanyaan ini di atas kertas (atau dokumen):

1. **Entitas apa saja** yang ada di proyekmu, dan relasinya (one-to-one, one-to-many, many-to-many)? Gambarkan seperti diagram ERD di `pertemuan-09`.
2. **Siapa saja role pengguna**? (misal: admin, member, tamu) — ini menentukan middleware otorisasi yang dibutuhkan.
3. **Endpoint apa saja** yang dibutuhkan untuk setiap entitas (daftar method + path)?
4. **Data apa yang sensitif** (password, foto KTP, dsb) sehingga butuh hashing/enkripsi/akses terbatas?
5. **Ada file upload?** (foto produk, foto profil, dokumen) — tentukan format yang diizinkan dan batas ukurannya.

Tuliskan dalam tabel kontrak endpoint seperti di `pertemuan-04` bagian 9.1, misalnya:

| Method | Path | Auth | Deskripsi |
|---|---|---|---|
| POST | `/auth/register` | Tidak | Registrasi pengguna |
| POST | `/auth/login` | Tidak | Login, hasilkan JWT |
| GET | `/[entitas-utama]` | Ya | Daftar milik pengguna yang login |
| POST | `/[entitas-utama]` | Ya | Buat baru |
| GET | `/[entitas-utama]/:id` | Ya | Detail satu |
| PUT | `/[entitas-utama]/:id` | Ya (pemilik) | Update |
| DELETE | `/[entitas-utama]/:id` | Ya (pemilik) | Hapus |
| POST | `/[entitas-utama]/:id/[entitas-anak]` | Ya (pemilik) | Tambah entitas anak |

**Aturan penting:** tahap ini wajib selesai dulu sebelum menulis kode apa pun. Mengubah struktur database di tengah jalan jauh lebih mahal daripada mengubah rancangan di atas kertas.

---

## 02 Tahap 1 — Setup Project

Langkah ini identik untuk proyek apa pun (sama seperti `pertemuan-04` bagian 08), hanya nama modul yang berubah:

```bash
mkdir [nama-project]-api && cd [nama-project]-api
go mod init github.com/[username-github]/[nama-project]-api
```

Buat struktur folder standar (menengah — cocok untuk proyek 1 semester):

```
[nama-project]-api/
├── cmd/
│   ├── api/
│   │   └── main.go          # entry point server
│   └── migrate/
│       └── main.go          # tool migration sendiri
├── internal/
│   ├── config/               # load .env
│   ├── domain/                # struct entity + error domain
│   ├── repository/            # akses database (interface + implementasi)
│   ├── service/                # logika bisnis / aturan domain
│   ├── handler/                # HTTP handler + DTO request/response
│   └── middleware/             # auth JWT, logging, recovery, CORS
├── migrations/                 # file .sql migration
├── docs/                        # hasil generate Swagger
├── uploads/                     # folder penyimpanan file upload (lokal, dev only)
├── .env.example
├── .gitignore
├── go.mod
├── Makefile
└── README.md
```

Kenapa strukturnya tetap seperti ini walau entitasnya beda-beda? Karena ini **memisahkan tanggung jawab**, bukan memisahkan "fitur per mahasiswa". Alurnya selalu:

```
request HTTP → handler → service → repository → database
```

> Jangan membuat folder `utils/` atau `helpers/` generik berisi campuran fungsi tidak berhubungan — itu kebiasaan buruk yang bikin kode susah ditelusuri. Beri nama paket sesuai fungsinya (`validator/`, `hashing/`, dsb) jika memang perlu dipisah.

Install dependency inti (sesuaikan dengan pilihan tim, ini default yang dipakai `pertemuan-04`):

```bash
go get github.com/jackc/pgx/v5
go get github.com/jackc/pgx/v5/pgxpool
go get github.com/golang-jwt/jwt/v5
go get golang.org/x/crypto/bcrypt
go get github.com/joho/godotenv
go get -tool github.com/golang-migrate/migrate/v4
```

---

## 03 Tahap 2 — Desain Database & Migration

1. Gambar ERD final (lihat [[go-umkm-api]] di materi referensi, bagian "Desain Database" di `pertemuan-09`).
2. Tulis `Ref:` relasi antar tabel (lihat penjelasan DBML sebelumnya) supaya foreign key-nya jelas sejak awal.
3. Buat file migration dengan nama berurutan di `migrations/`:

```sql
-- migrations/000001_create_[entitas_pemilik].up.sql
CREATE TABLE [entitas_pemilik] (
    id          BIGSERIAL PRIMARY KEY,
    nama        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- migrations/000002_create_[entitas_utama].up.sql
CREATE TABLE [entitas_utama] (
    id                BIGSERIAL PRIMARY KEY,
    [entitas_pemilik]_id BIGINT NOT NULL UNIQUE
        REFERENCES [entitas_pemilik](id) ON DELETE CASCADE,
    nama              VARCHAR(150) NOT NULL,
    -- [FIELD] tambahkan kolom sesuai domain, misal: alamat, kategori, dsb.
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- migrations/000003_create_[entitas_anak].up.sql
CREATE TABLE [entitas_anak] (
    id               BIGSERIAL PRIMARY KEY,
    [entitas_utama]_id BIGINT NOT NULL
        REFERENCES [entitas_utama](id) ON DELETE CASCADE,
    -- [FIELD] field spesifik entitas anak
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Jangan lupa pasangan `.down.sql` untuk tiap migration (untuk rollback):

```sql
-- migrations/000003_create_[entitas_anak].down.sql
DROP TABLE IF EXISTS [entitas_anak];
```

4. Jalankan migration dengan tool `cmd/migrate/main.go` yang sama persis seperti di `pertemuan-04` bagian 10.1 — tool-nya generik, tidak tergantung nama tabel.

> **Checklist sebelum lanjut:** tabel sudah terbentuk? Foreign key benar arahnya? `UNIQUE` sudah dipasang di kolom yang memang harus unik (contoh: satu pemilik hanya satu `[entitas_utama]`)?

---

## 04 Tahap 3 — Domain & Konfigurasi

`internal/domain/[entitas_utama].go` — struct murni, tanpa logika:

```go
package domain

import "time"

type [EntitasUtama] struct {
    ID               int64     `json:"id"`
    [EntitasPemilik]ID int64   `json:"-"`
    Nama             string    `json:"nama"`
    // [FIELD] tambahkan field sesuai domain
    CreatedAt        time.Time `json:"created_at"`
}

var (
    Err[EntitasUtama]NotFound = errors.New("[entitas_utama] tidak ditemukan")
    ErrForbidden              = errors.New("tidak berhak mengakses data ini")
)
```

`internal/config/config.go` — load `.env` sekali di awal, generik untuk proyek apa pun:

```go
package config

type Config struct {
    Port        string
    DatabaseURL string
    JWTSecret   string
    UploadDir   string
}

func Load() (*Config, error) {
    _ = godotenv.Load()
    cfg := &Config{
        Port:        getEnv("PORT", "8080"),
        DatabaseURL: os.Getenv("DATABASE_URL"),
        JWTSecret:   os.Getenv("JWT_SECRET"),
        UploadDir:   getEnv("UPLOAD_DIR", "./uploads"),
    }
    if cfg.DatabaseURL == "" || cfg.JWTSecret == "" {
        return nil, fmt.Errorf("DATABASE_URL dan JWT_SECRET wajib diisi di .env")
    }
    return cfg, nil
}

func getEnv(key, fallback string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return fallback
}
```

---

## 05 Tahap 4 — Repository (Akses Database)

Interface didefinisikan di sisi pemakai (service), tapi untuk proyek kuliah cukup satu file per entitas di `repository/`. Pola query-nya **selalu sama**, hanya nama tabel dan kolom yang berubah:

```go
package repository

type [EntitasUtama]Repository interface {
    Create(ctx context.Context, e *domain.[EntitasUtama]) error
    GetByID(ctx context.Context, id int64) (*domain.[EntitasUtama], error)
    GetByOwnerID(ctx context.Context, ownerID int64) (*domain.[EntitasUtama], error)
    Update(ctx context.Context, e *domain.[EntitasUtama]) error
    Delete(ctx context.Context, id int64) error
}

type [entitasUtama]PgRepo struct {
    db *pgxpool.Pool
}

func New[EntitasUtama]Repository(db *pgxpool.Pool) [EntitasUtama]Repository {
    return &[entitasUtama]PgRepo{db: db}
}

func (r *[entitasUtama]PgRepo) Create(ctx context.Context, e *domain.[EntitasUtama]) error {
    query := `INSERT INTO [entitas_utama] ([entitas_pemilik]_id, nama)
              VALUES ($1, $2) RETURNING id, created_at`
    return r.db.QueryRow(ctx, query, e.[EntitasPemilik]ID, e.Nama).
        Scan(&e.ID, &e.CreatedAt)
}

func (r *[entitasUtama]PgRepo) GetByID(ctx context.Context, id int64) (*domain.[EntitasUtama], error) {
    var e domain.[EntitasUtama]
    query := `SELECT id, [entitas_pemilik]_id, nama, created_at
              FROM [entitas_utama] WHERE id = $1`
    err := r.db.QueryRow(ctx, query, id).
        Scan(&e.ID, &e.[EntitasPemilik]ID, &e.Nama, &e.CreatedAt)
    if errors.Is(err, pgx.ErrNoRows) {
        return nil, domain.Err[EntitasUtama]NotFound
    }
    if err != nil {
        return nil, fmt.Errorf("get [entitas_utama] %d: %w", id, err)
    }
    return &e, nil
}
```

**Pola ini berlaku untuk entitas apa pun** — kalau butuh CRUD baru (misal `[ENTITAS_ANAK]`), tinggal duplikasi pola yang sama dengan nama tabel/kolom berbeda. Inilah yang dimaksud "generik": bukan satu kode yang dipakai untuk semua tabel (itu over-engineering untuk level tugas kuliah), melainkan **pola yang konsisten** yang gampang ditiru ulang.

---

## 06 Tahap 5 — Service (Aturan Bisnis)

Di sinilah letak logika yang **spesifik untuk tiap proyek** — ini bagian yang paling banyak kustomisasinya:

```go
package service

type [EntitasUtama]Service struct {
    repo repository.[EntitasUtama]Repository
}

func New[EntitasUtama]Service(repo repository.[EntitasUtama]Repository) *[EntitasUtama]Service {
    return &[EntitasUtama]Service{repo: repo}
}

func (s *[EntitasUtama]Service) Create(ctx context.Context, ownerID int64, nama string) (*domain.[EntitasUtama], error) {
    if strings.TrimSpace(nama) == "" {
        return nil, fmt.Errorf("%w: nama wajib diisi", domain.ErrInvalidInput)
    }

    // [ATURAN BISNIS] contoh: cek apakah pemilik sudah punya [entitas_utama]
    existing, err := s.repo.GetByOwnerID(ctx, ownerID)
    if err != nil && !errors.Is(err, domain.Err[EntitasUtama]NotFound) {
        return nil, err
    }
    if existing != nil {
        return nil, fmt.Errorf("%w: pengguna sudah memiliki [entitas_utama]", domain.ErrConflict)
    }

    e := &domain.[EntitasUtama]{[EntitasPemilik]ID: ownerID, Nama: nama}
    if err := s.repo.Create(ctx, e); err != nil {
        return nil, fmt.Errorf("create [entitas_utama]: %w", err)
    }
    return e, nil
}
```

Contoh **aturan bisnis khas** yang biasa muncul di proyek mahasiswa (ganti sesuai domain):

- Peminjaman buku: tidak boleh pinjam jika masih ada buku yang belum dikembalikan.
- Parkir: hitung tarif berdasarkan selisih waktu masuk-keluar.
- Booking lapangan: cegah bentrok jadwal (overlap time slot).
- Laundry: status pesanan hanya boleh berubah sesuai urutan (diterima → diproses → selesai).

Pola penanganannya sama: **validasi di awal method service**, lempar error domain (`ErrInvalidInput`, `ErrConflict`, `ErrForbidden`), baru dipetakan ke kode HTTP di handler.

---

## 07 Tahap 6 — Middleware (Auth JWT & Lainnya)

Middleware ini **100% dapat dipakai ulang tanpa perubahan** di proyek apa pun, karena tidak bergantung pada entitas:

```go
package middleware

func Auth(jwtSecret string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            header := r.Header.Get("Authorization")
            if !strings.HasPrefix(header, "Bearer ") {
                writeError(w, http.StatusUnauthorized, "token tidak ditemukan")
                return
            }
            tokenStr := strings.TrimPrefix(header, "Bearer ")
            claims := &Claims{}
            token, err := jwt.ParseWithClaims(tokenStr, claims, func(t *jwt.Token) (interface{}, error) {
                return []byte(jwtSecret), nil
            })
            if err != nil || !token.Valid {
                writeError(w, http.StatusUnauthorized, "token tidak valid")
                return
            }
            ctx := context.WithValue(r.Context(), userIDKey, claims.UserID)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

Middleware tambahan yang perlu disesuaikan **hanya jika proyekmu punya role berbeda**:

```go
func RequireRole(allowed ...string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            role := RoleFromContext(r.Context())
            if !slices.Contains(allowed, role) {
                writeError(w, http.StatusForbidden, "tidak punya akses")
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
```

Pakai di router: `router.With(middleware.RequireRole("admin")).Delete(...)`.

Middleware lain yang sebaiknya selalu ada (generik, lihat checklist produksi di bawah): `Logging`, `Recovery` (menangkap panic agar server tidak mati), `CORS`.

---

## 08 Tahap 7 — Handler & Routing

Pola handler **identik** dengan `pertemuan-04` bagian 10.8–10.9, hanya nama struct dan field yang berubah:

```go
func (h *[EntitasUtama]Handler) Create(w http.ResponseWriter, r *http.Request) {
    ownerID := middleware.UserIDFromContext(r.Context())

    var req struct {
        Nama string `json:"nama" validate:"required"`
    }
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "body tidak valid")
        return
    }

    e, err := h.svc.Create(r.Context(), ownerID, req.Nama)
    switch {
    case errors.Is(err, domain.ErrConflict):
        writeError(w, http.StatusConflict, err.Error())
        return
    case errors.Is(err, domain.ErrInvalidInput):
        writeError(w, http.StatusBadRequest, err.Error())
        return
    case err != nil:
        h.log.Error("create [entitas_utama]", "err", err)
        writeError(w, http.StatusInternalServerError, "kesalahan server")
        return
    }
    writeJSON(w, http.StatusCreated, e)
}
```

Routing dengan `net/http` (Go 1.22+, bawaan, tanpa framework tambahan):

```go
mux := http.NewServeMux()

mux.HandleFunc("POST /auth/register", authHandler.Register)
mux.HandleFunc("POST /auth/login", authHandler.Login)

mux.Handle("GET /[entitas-utama]", authMW(http.HandlerFunc(entitasHandler.Get)))
mux.Handle("POST /[entitas-utama]", authMW(http.HandlerFunc(entitasHandler.Create)))
mux.Handle("PUT /[entitas-utama]/{id}", authMW(http.HandlerFunc(entitasHandler.Update)))
mux.Handle("DELETE /[entitas-utama]/{id}", authMW(http.HandlerFunc(entitasHandler.Delete)))

mux.Handle("POST /[entitas-utama]/{id}/[entitas-anak]", authMW(http.HandlerFunc(anakHandler.Create)))
```

> Kalau tim lebih nyaman pakai `chi` (routing lebih ringkas untuk path param & grouping), silakan — tapi untuk tugas kuliah skala kecil, `net/http` bawaan Go 1.22+ sudah cukup dan mengurangi dependency.

---

## 09 Tahap 8 — File Upload (jika proyekmu butuh)

Tidak semua proyek butuh upload file — lewati tahap ini kalau tidak relevan. Kalau butuh (foto produk, foto profil, dokumen bukti), polanya generik:

```go
func (h *UploadHandler) UploadFoto(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, 2<<20) // batas 2MB
    file, header, err := r.FormFile("foto")
    if err != nil {
        writeError(w, http.StatusBadRequest, "file tidak ditemukan")
        return
    }
    defer file.Close()

    ext := strings.ToLower(filepath.Ext(header.Filename))
    if ext != ".jpg" && ext != ".jpeg" && ext != ".png" {
        writeError(w, http.StatusBadRequest, "format harus JPG/JPEG/PNG")
        return
    }

    filename := fmt.Sprintf("%d_%d%s", ownerID, time.Now().UnixNano(), ext)
    dst, err := os.Create(filepath.Join(h.uploadDir, filename))
    if err != nil {
        writeError(w, http.StatusInternalServerError, "gagal menyimpan file")
        return
    }
    defer dst.Close()
    io.Copy(dst, file)

    writeJSON(w, http.StatusOK, map[string]string{"url": "/uploads/" + filename})
}
```

**Checklist upload:** batasi ukuran (`MaxBytesReader`), validasi ekstensi **dan** isi file (jangan percaya nama file saja), nama file unik (hindari tabrakan/overwrite), simpan path relatif di database bukan path absolut. Untuk deployment, pertimbangkan simpan di storage eksternal (Cloudinary/S3) karena disk server biasanya tidak persisten di platform gratis.

---

## 10 Tahap 9 — Dokumentasi API dengan Swagger

Sama persis seperti `pertemuan-04` bagian 11 — tool `swaggo/swag` membaca anotasi komentar di atas tiap handler, tidak peduli nama entitasnya apa:

```go
// Create godoc
// @Summary      Buat [entitas_utama] baru
// @Tags         [entitas-utama]
// @Security     BearerAuth
// @Accept       json
// @Produce      json
// @Param        body body CreateRequest true "Data [entitas_utama]"
// @Success      201 {object} Response
// @Failure      400 {object} ErrorResponse
// @Router       /[entitas-utama] [post]
func (h *[EntitasUtama]Handler) Create(w http.ResponseWriter, r *http.Request) { ... }
```

```bash
go install github.com/swaggo/swag/cmd/swag@latest
swag init -g cmd/api/main.go -o docs
```

Buka `http://localhost:8080/swagger/index.html` untuk memverifikasi kontrak endpoint sudah sesuai rancangan tahap 01.

---

## 11 Tahap 10 — Testing

Minimal yang wajib ada per proyek (lihat pola table-driven test di referensi skill backend Go):

1. **Unit test service** dengan fake repository (tidak perlu database asli):
   ```go
   type fake[EntitasUtama]Repo struct{ data map[int64]*domain.[EntitasUtama] }
   // implementasikan semua method interface, baca/tulis ke map in-memory
   ```
2. **Test aturan bisnis spesifik proyek** — ini yang paling penting untuk dinilai, karena membuktikan logika domainmu benar (contoh: test "tidak boleh pinjam buku yang stoknya 0").
3. **Handler test** dengan `httptest.NewRecorder()` untuk memastikan status code dan format JSON respons benar.

Jalankan dengan `go test ./... -v`, dan `go test ./... -race` kalau ada bagian yang menyentuh goroutine/concurrency.

---

## 12 Tahap 11 — Checklist Sebelum Deployment

Checklist ini **sama untuk semua proyek**, tidak peduli domainnya:

- [ ] `.env` tidak ikut ter-commit (`.gitignore` sudah benar), `.env.example` tersedia sebagai referensi.
- [ ] Graceful shutdown (`signal.NotifyContext` + `srv.Shutdown`).
- [ ] Timeout server (`ReadHeaderTimeout`, `WriteTimeout`, dst) sudah diset.
- [ ] Password di-hash dengan bcrypt, bukan disimpan plain text.
- [ ] Query database terparameter (`$1, $2`), tidak ada string concat SQL.
- [ ] CORS dibatasi ke origin yang memang dipakai (frontend/Flutter app), bukan `*` kalau bisa dihindari.
- [ ] Endpoint `/healthz` tersedia untuk cek server hidup.
- [ ] Migration sudah dijalankan di database production (Neon/Railway/dsb), bukan cuma di lokal.
- [ ] Swagger docs sinkron dengan endpoint yang benar-benar diimplementasikan.

### Opsi Deployment untuk Tugas Kuliah (gratis/murah)

| Platform | Cocok untuk | Catatan |
|---|---|---|
| Railway / Render | Backend Go + auto-deploy dari GitHub | Paling mudah untuk pemula |
| Fly.io | Backend Go dengan Dockerfile | Butuh kartu kredit untuk verifikasi, ada free tier |
| Neon | Database PostgreSQL | Sudah dipakai sejak `pertemuan-04` |
| VPS (opsional, untuk yang ingin belajar lebih dalam) | Kontrol penuh | Perlu setup Nginx reverse proxy + systemd service |

---

## 13 Ringkasan: Apa yang Generik, Apa yang Dikustomisasi

| Lapisan | Generik (pola sama) | Dikustomisasi per proyek |
|---|---|---|
| Struktur folder | ✅ Selalu sama | — |
| Config, koneksi DB | ✅ Selalu sama | — |
| Middleware auth JWT | ✅ Bisa dipakai ulang persis | Role tambahan jika ada multi-role |
| Repository (pola query) | ✅ Pola sama | Nama tabel/kolom, query spesifik |
| Service (aturan bisnis) | — | 🔧 Ini jantung keunikan proyekmu |
| Handler & response format | ✅ Pola sama | Field request/response |
| File upload | ✅ Pola sama (jika dipakai) | Jenis file, validasi spesifik |
| Swagger | ✅ Pola sama | Isi anotasi per endpoint |
| Testing | ✅ Pola sama | Skenario aturan bisnis yang diuji |
| Deployment | ✅ Checklist sama | Pilihan platform |

**Pesan utama untuk mahasiswa:** jangan takut proyekmu "beda sendiri" dari contoh UMKM — justru tahap 06 (Service/aturan bisnis) adalah tempat proyekmu seharusnya terlihat beda. Kalau seluruh backend-mu cuma CRUD tanpa aturan bisnis apa pun, itu tanda rancangan di tahap 01 belum cukup dalam — kembali diskusikan dengan dosen pembimbing.
