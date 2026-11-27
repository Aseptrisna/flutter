"""Membuat seluruh tutorial CRUD per project.

Jalankan dari folder ini:  python3 generate.py   (butuh pandoc untuk versi Markdown)
Hasil: ../index.html, ../00-fondasi.html, ../NN-slug.html, ../md/, ../starter/
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import kode  # noqa: E402
from data import PROJECTS  # noqa: E402

OUT = os.path.join(HERE, "..")
ROOT = kode.ROOT

with open(os.path.join(ROOT, "pertemuan-09a.html"), encoding="utf-8") as f:
    TEMPLATE = f.read()
STYLE = re.search(r"<style>.*?</style>", TEMPLATE, re.S).group(0)
FONTS = re.search(r'<link href="https://fonts[^>]+>', TEMPLATE).group(0)
SCRIPT = re.search(r"<script>.*</script>", TEMPLATE, re.S).group(0)
FOOTER = re.search(r'<footer class="site-footer">.*?</footer>', TEMPLATE, re.S).group(0)
FOOTER = re.sub(r'href="(?!https?:|#|\.\./)', 'href="../', FOOTER)


# ---------------------------------------------------------------- potongan HTML
def e(text):
    return html.escape(str(text), quote=False)


def c(text):
    return "<code>%s</code>" % e(text)


def p(text):
    return "    <p>%s</p>\n" % text


def h3(text):
    return "    <h3>%s</h3>\n" % text


def ul(items, tag="ul"):
    return "    <%s>\n%s    </%s>\n" % (tag, "".join("      <li>%s</li>\n" % i for i in items), tag)


def box(kind, label, body):
    return '    <div class="%s"><span class="lbl">%s</span><p>%s</p></div>\n' % (kind, label, body)


def card(tag, code):
    return ('    <div class="codecard"><div class="bar"><span class="dot"></span><span class="dot"></span>'
            '<span class="dot"></span><span class="tag">%s</span></div><pre><code>%s</code></pre></div>\n'
            % (e(tag), e(code.rstrip("\n"))))


def table(head, rows):
    return "    <table>\n      <tr>%s</tr>\n%s    </table>\n" % (
        "".join("<th>%s</th>" % h for h in head),
        "".join("      <tr>%s</tr>\n" % "".join("<td>%s</td>" % x for x in r) for r in rows))


def page(title, kicker, sub, sections, back=("index.html", "Daftar tutorial project")):
    nav = "".join('      <li><a href="#s%d">%s</a></li>\n' % (i, t) for i, (t, _) in enumerate(sections, 1))
    body = "".join('    <h2 id="s%d"><span class="badge">%02d</span>%s</h2>\n%s' % (i, i, t, b)
                   for i, (t, b) in enumerate(sections, 1))
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{e(title)}</title>
{FONTS}
{STYLE}
</head>
<body>
<div class="scrollbar"><div class="scrollbar-fill" id="scrollFill"></div></div>
<div class="site-header-bar">
  <header class="site-header">
    <a class="site-brand" href="../index.html">
      <span class="site-brand-mark">PIV</span>
      <span class="site-brand-text">Pemrograman IV<small>Sistem Informasi &middot; FIK UBL</small></span>
    </a>
    <a class="site-header-cta" href="index.html">Semua Project &rarr;</a>
  </header>
</div>
<div class="shell">
  <nav class="side">
    <div class="brand">SISTEM INFORMASI<br>FAKULTAS ILMU KOMPUTER<br>UNIVERSITAS BANDAR LAMPUNG</div>
    <ol>
{nav}    </ol>
  </nav>
  <main>
    <a class="back" href="{back[0]}">&larr; {back[1]}</a>
    <header>
      <span class="kicker">{kicker}</span>
      <h1>{e(title)}</h1>
      <p class="sub">{sub}</p>
    </header>
{body}    <footer>Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung</footer>
  </main>
</div>
{FOOTER}
{SCRIPT}
</body>
</html>
"""


def filename(pr):
    return "%02d-%s.html" % (pr["no"], pr["slug"])


# ---------------------------------------------------------------- halaman fondasi
def foundation_page():
    files = kode.foundation_files()
    pkg = json.loads(files["package.json"])
    dep = " ".join("%s@%s" % kv for kv in pkg["dependencies"].items())
    dev = " ".join("%s@%s" % kv for kv in pkg["devDependencies"].items())

    def cards(*names):
        return "".join(card(n, files[n]) for n in names)

    s9 = lambda n: '<a href="../pertemuan-09a.html#s%d">Pertemuan 9a Bagian %02d</a>' % (n, n)
    sections = [
        ("Apa yang Dibuat",
         p("Fondasi ini adalah <strong>modul user</strong> dari Pertemuan 9a: register, login, profil, ubah password, dan Swagger. Semua project memakai fondasi yang <strong>sama persis</strong>. Setelah fondasi jalan, kamu menambahkan satu tabel milik project-mu lewat tutorial masing-masing.")
         + p("Pahami dulu konsepnya di " + '<a href="../pertemuan-09a.html">Pertemuan 9a</a>. Halaman ini hanya berisi langkah dan kode.')
         + box("note", "Punya salinan repo materi?", "Folder <code>tutorial-crud/starter/</code> berisi fondasi ini. Salin foldernya, ganti namanya, jalankan <code>npm install</code>, lalu lompat ke bagian 05.")),
        ("Membuat Proyek & Install",
         p("Ganti <code>project-api</code> dengan nama folder untuk project-mu.")
         + card("terminal", "mkdir project-api && cd project-api\nnpm init -y\n\nnpm install --save-exact %s\nnpm install --save-exact --save-dev %s" % (dep, dev))
         + card("terminal — buat folder", "mkdir -p prisma src/docs src/middleware src/utils src/repositories src/services src/handlers")
         + p("Buka <code>package.json</code>, ubah <code>main</code> menjadi <code>server.js</code> dan isi bagian <code>scripts</code> seperti di bawah. Bagian dependency sudah terisi otomatis.")
         + card("package.json", files["package.json"])),
        ("File Konfigurasi & Database",
         p("Penjelasan: %s dan %s." % (s9(5), s9(6)))
         + cards("prisma/schema.prisma", ".env.example", ".gitignore", "src/config.js", "src/db.js")),
        ("Kode Pendukung",
         p("Penjelasan: %s sampai %s. File <code>validate.js</code> dan <code>docs/crud.js</code> disiapkan untuk CRUD project-mu." % (s9(7), s9(8)))
         + cards("src/errors.js", "src/utils/response.js", "src/utils/pagination.js", "src/utils/validate.js",
                 "src/middleware/auth.js", "src/middleware/rateLimit.js", "src/middleware/errorHandler.js")),
        ("Modul User",
         p("Penjelasan per fungsi: %s, %s, dan %s." % (s9(10), s9(11), s9(13)))
         + cards("src/repositories/userRepository.js", "src/services/authService.js", "src/handlers/authHandler.js")),
        ("Swagger, Route & Server",
         p("Penjelasan: %s." % s9(14))
         + cards("src/docs/swagger.js", "src/docs/crud.js", "src/app.js", "server.js")),
        ("Jalankan & Uji",
         box("warn", "Pakai database baru", "Buat database <strong>baru yang kosong</strong> di Neon untuk project-mu. Jangan memakai database latihan UMKM: Prisma akan menemukan tabel lain dan meminta <em>reset</em> yang menghapus data.")
         + card("terminal", "cp .env.example .env      # isi DATABASE_URL dan JWT_SECRET\nnpx prisma migrate dev --name init\nnpm run dev")
         + p("Buka <code>http://localhost:8080/swagger/</code>, lalu uji register, login, <em>Authorize</em>, dan profil seperti di %s." % s9(16))
         + box("verify", "Checkpoint", "Lanjut ke tutorial project-mu hanya kalau <code>GET /profile</code> sudah membalas <code>200</code>. Kembali ke <a href=\"index.html\">daftar project</a>.")),
    ]
    return page("Fondasi: Modul User untuk Semua Project", "Langkah 1 &middot; Sama untuk Semua",
                "Satu fondasi yang sama untuk seluruh mahasiswa sebelum membuat CRUD project masing-masing.", sections)


# ---------------------------------------------------------------- halaman project
TIPE_TAMPIL = {"teks": "teks", "bulat": "bilangan bulat", "angka": "angka desimal",
               "boolean": "true / false", "tanggal": "tanggal (YYYY-MM-DD)", "pilihan": "pilihan"}


def column_rows(pr):
    rows = [[c("id"), "bilangan bulat", "otomatis", "Primary key"],
            [c("user_id"), "bilangan bulat", "dari token", "Pemilik data"]]
    for name, kind, req, example, extra in pr["kolom"]:
        info = []
        if "opsi" in extra:
            info.append("Salah satu: " + ", ".join(c(o) for o in extra["opsi"]))
        else:
            if kind == "teks" and "max" in extra:
                info.append("maks. %d karakter" % extra["max"])
            if "min" in extra:
                info.append("minimal %s" % extra["min"])
            info.append("contoh: " + c(json.dumps(example, ensure_ascii=False)))
        rows.append([c(name), TIPE_TAMPIL[kind], "wajib" if req else "opsional", "; ".join(info)])
    return rows


def project_page(pr):
    files = dict(kode.project_files(pr))
    acc, path, model = kode.camel(pr["model"]), pr["path"], pr["model"]
    repo, svc, hdl, docs = ("src/repositories/%sRepository.js" % acc, "src/services/%sService.js" % acc,
                            "src/handlers/%sHandler.js" % acc, "src/docs/%s.js" % acc)
    body = kode.example_body(pr)
    pretty = json.dumps(body, indent=2, ensure_ascii=False)
    required = [k for k in pr["kolom"] if k[2]]
    first = required[0][0]
    wrong = next(((n, k) for n, k, *_ in pr["kolom"] if k in ("bulat", "angka")), None) \
        or next(((n, k) for n, k, *_ in pr["kolom"] if k in ("boolean", "tanggal", "pilihan")), None)
    bad = {"bulat": 'teks <code>"sepuluh"</code>', "angka": 'teks <code>"seribu"</code>',
           "boolean": 'teks <code>"ya"</code>', "tanggal": "<code>2026-02-30</code>",
           "pilihan": "nilai di luar daftar"}

    negative = [["POST", "Hapus <code>%s</code> dari body" % first, "<code>400</code> %s wajib diisi" % first]]
    if wrong:
        negative.append(["POST", "Isi <code>%s</code> dengan %s" % (wrong[0], bad[wrong[1]]), "<code>400</code>"])
    negative += [
        ["GET /{id}", "id <code>999999</code>", "<code>404</code> data tidak ditemukan"],
        ["GET, PUT, DELETE /{id}", "Login sebagai akun kedua, pakai id milik akun pertama", "<code>403</code>"],
        ["GET (daftar)", "Login sebagai akun kedua", "<code>200</code>, data akun pertama tidak terlihat"],
        ["Semua", "Tanpa token", "<code>401</code>"],
    ]

    curl_body = json.dumps(body, ensure_ascii=False).replace("'", "'\\''")
    note = box("warn", "Perlu dikonfirmasi", pr["catatan"]) if pr["catatan"] else ""
    sections = [
        ("Yang Akan Dibuat",
         note
         + p("CRUD tabel <code>%s</code> untuk project <strong>%s</strong>. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri." % (kode.snake(model), e(pr["judul"])))
         + table(["Endpoint", "Fungsi"], [[c("GET /api/%s" % path), "Daftar milik sendiri, dengan <code>?q=</code>, <code>page</code>, <code>limit</code>"],
                                           [c("GET /api/%s/{id}" % path), "Detail satu data"],
                                           [c("POST /api/%s" % path), "Tambah"],
                                           [c("PUT /api/%s/{id}" % path), "Ubah"],
                                           [c("DELETE /api/%s/{id}" % path), "Hapus"]])
         + box("note", "Syarat sebelum mulai", 'Selesaikan <a href="00-fondasi.html">Fondasi Modul User</a> sampai <code>GET /profile</code> membalas <code>200</code>.')),
        ("Rancangan Tabel",
         table(["Kolom", "Tipe", "Isian", "Keterangan"], column_rows(pr))
         + p("Kolom <code>created_at</code> juga dibuat otomatis. Pencarian <code>?q=</code> mencocokkan kolom <code>%s</code>." % pr["cari"])),
        ("Skema & Migrasi",
         p("Ganti seluruh isi <code>prisma/schema.prisma</code>. Yang baru: <code>model %s</code> dan satu baris relasi <code>%s %s[]</code> di model <code>User</code>." % (model, acc, model))
         + card("prisma/schema.prisma", files["prisma/schema.prisma"])
         + card("terminal", "npx prisma migrate dev --name tambah_%s" % kode.snake(model))
         + p('Hentikan dulu <code>npm run dev</code> saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: <a href="../pertemuan-09a.html#s5">Pertemuan 9a Bagian 05</a>.')),
        ("Repository — Akses Database",
         p("Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi <code>user_id</code>.")
         + card(repo, files[repo])),
        ("Service — Validasi & Hak Akses",
         p("Objek <code>aturan</code> menentukan isian yang sah; <code>validate</code> membuang kolom lain yang dikirim klien. <code>authorizeOwner</code> membalas <code>404</code> bila data tidak ada dan <code>403</code> bila milik orang lain. <code>PUT</code> menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau <code>false</code>).")
         + card(svc, files[svc])),
        ("Handler — Request & Response",
         p("Mengambil input dari <code>req</code>, memanggil service, lalu membalas JSON.")
         + card(hdl, files[hdl])),
        ("Route",
         p("Ganti seluruh isi <code>src/app.js</code>. Tambahannya: satu <code>require</code> handler dan lima route yang semuanya melewati <code>requireAuth</code>.")
         + card("src/app.js", files["src/app.js"])),
        ("Swagger",
         p("Buat file dokumentasi, lalu daftarkan.")
         + card(docs, files[docs])
         + card("src/docs/swagger.js — tambahkan di baris paling bawah", kode.swagger_append(pr))),
        ("Jalankan & Uji",
         card("terminal", "npm run dev")
         + p("Buka <code>http://localhost:8080/swagger/</code>, login, klik <em>Authorize</em>, lalu buka kelompok <strong>%s</strong>." % e(pr["judul"]))
         + ul(["<strong>POST</strong> dengan contoh di bawah → <code>201</code>. Catat <code>id</code>-nya.",
               "<strong>GET daftar</strong> → <code>200</code>, data muncul dan <code>meta.total</code> bertambah.",
               "<strong>GET /{id}</strong> → <code>200</code>.",
               "<strong>PUT /{id}</strong> dengan nilai yang diubah → <code>200</code>.",
               "<strong>DELETE /{id}</strong> → <code>200</code>, lalu GET id yang sama → <code>404</code>."], "ol")
         + card("contoh body", pretty)
         + card("terminal — alternatif tanpa Swagger", "TOKEN=\"tempel-token-hasil-login\"\ncurl -s -X POST http://localhost:8080/api/%s \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '%s'" % (path, curl_body))
         + h3("Uji jalur gagal")
         + table(["Request", "Yang dicoba", "Harus dibalas"], negative)),
        ("Tantangan & Troubleshooting",
         box("note", "Tantangan (kerjakan sendiri)", pr["tantangan"])
         + table(["Gejala", "Penyebab", "Solusi"], [
             ["<code>Cannot find module</code>", "Nama file atau folder berbeda dari tutorial.", "Samakan huruf besar dan kecilnya."],
             ["<code>Cannot read properties of undefined</code> saat query", "Prisma Client belum dibuat ulang.", "<code>npx prisma generate</code>, lalu restart."],
             ["Prisma meminta <em>reset</em>", "Database berisi tabel dari project lain.", "Jawab tidak, pakai database baru."],
             ["Kelompok baru tidak muncul di Swagger", "Baris tambahan di <code>swagger.js</code> belum ada.", "Tambahkan, restart, muat ulang halaman."],
         ])),
    ]
    return page("%s: CRUD %s" % (pr["judul"], path.replace("-", " ").title()), "Project %02d &middot; CRUD 1 Tabel" % pr["no"],
                "Menambahkan tabel milik project <strong>%s</strong> di atas fondasi modul user, memakai Express, Prisma, dan Swagger." % e(pr["judul"]),
                sections)


def index_page():
    rows = [[str(pr["no"]), e(pr["judul"]), c(kode.snake(pr["model"])),
             '<a href="%s">Buka tutorial &rarr;</a>' % filename(pr)] for pr in PROJECTS]
    sections = [
        ("Urutan Belajar", ul([
            '<a href="../pertemuan-09a.html">Pertemuan 9a</a> — pahami konsepnya (studi kasus UMKM).',
            '<a href="00-fondasi.html">Fondasi Modul User</a> — sama untuk semua.',
            "Tutorial project-mu di daftar bawah — CRUD satu tabel.",
        ], "ol")),
        ("Daftar Project", p("Cari berdasarkan nama project yang kamu daftarkan.")
         + table(["No", "Project", "Tabel", "Tutorial"], rows)),
    ]
    return page("Tutorial CRUD per Project", "Praktikum Proyek Sendiri",
                "Fondasi yang sama, tabel yang berbeda untuk setiap project.", sections,
                back=("../index.html", "Kembali ke daftar pertemuan"))


# ---------------------------------------------------------------- Markdown
def to_markdown(source):
    m = re.search(r"<main[^>]*>(.*)</main>", source, re.S).group(1)
    m = re.sub(r'<div class="codecard"><div class="bar">(?:<span class="dot"></span>)*<span class="tag">(.*?)</span></div><pre><code>',
               r"<p>\1</p><pre><code>", m, flags=re.S)
    m = m.replace("</code></pre></div>", "</code></pre>")
    m = re.sub(r'<span class="badge">(.*?)</span>', r"\1 ", m)
    m = re.sub(r'href="([^"#:]+)\.html', lambda g: 'href="%s.%s' % (g.group(1), "html" if g.group(1).startswith("..") else "md"), m)
    m = m.replace('href="../', 'href="../../')
    out = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                         input=m, capture_output=True, text=True, check=True).stdout
    return out


def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    assert len({pr["slug"] for pr in PROJECTS}) == len(PROJECTS), "slug kembar"
    pages = {"index.html": index_page(), "00-fondasi.html": foundation_page()}
    pages.update({filename(pr): project_page(pr) for pr in PROJECTS})
    for name, source in pages.items():
        write(name, source)
        if shutil.which("pandoc"):
            write("md/" + name.replace(".html", ".md"), to_markdown(source))
    for name, source in kode.foundation_files().items():
        write("starter/" + name, source)
    print("halaman:", len(pages), "| file starter:", len(kode.foundation_files()))


if __name__ == "__main__":
    main()
