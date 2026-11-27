"""Halaman ../swagger-generate.html: dokumentasi Swagger dibuat otomatis dari route Express.

Memakai swagger-autogen, padanan `swag init` di versi Go.
"""

SCRIPT_AWAL = """const swaggerAutogen = require('swagger-autogen')({ openapi: '3.0.3', autoHeaders: false });

const doc = {
  info: { title: 'API Project', version: '1.0.0', description: 'Dibuat otomatis dari route Express' },
  servers: [{ url: '/' }],
};

// argumen: file hasil, file yang berisi route, keterangan tambahan
swaggerAutogen('./src/docs/swagger-output.json', ['./src/app.js'], doc);
"""

SCRIPT_LENGKAP = """const swaggerAutogen = require('swagger-autogen')({ openapi: '3.0.3', autoHeaders: false });

const email = 'budi@test.com';
const password = 'rahasia123';

const doc = {
  info: { title: 'API Project', version: '1.0.0', description: 'Dibuat otomatis dari route Express' },
  servers: [{ url: '/' }],
  // semua endpoint mengirim token; yang publik dikecualikan lewat komentar
  security: [{ bearerAuth: [] }],
  components: {
    securitySchemes: {
      bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
    },
    // cukup tulis contohnya, tipe datanya disimpulkan otomatis
    schemas: {
      Register: { nama: 'Budi Tester', email, password },
      Login: { email, password },
      Profil: { nama: 'Budi Baru', email },
      Password: { password_lama: password, password_baru: 'rahasiabaru456' },
    },
  },
};

// argumen: file hasil, file yang berisi route, keterangan tambahan
swaggerAutogen('./src/docs/swagger-output.json', ['./src/app.js'], doc);
"""

APP_REQUIRE = """// baris lama: const swaggerSpec = require('./docs/swagger');
const swaggerSpec = require('./docs/swagger-output.json');
"""

APP_IGNORE = """// health check
app.get('/healthz', (req, res) => {
  // #swagger.ignore = true
  res.sendStatus(200);
});
"""

APP_IGNORE_SWAGGER = """app.get('/swagger/index.html', (req, res) => {
  // #swagger.ignore = true
  res.redirect('/swagger/');
});
"""


def komentar(fungsi, baris):
    isi = "".join("    %s\n" % b for b in baris)
    return "async function %s(req, res, next) {\n  /*\n%s  */\n  // ...isi fungsi yang lama tetap\n" % (fungsi, isi)


def badan(skema):
    return [
        "#swagger.requestBody = {",
        "  required: true,",
        "  content: { 'application/json': { schema: { $ref: '#/components/schemas/%s' } } }" % skema,
        "}",
    ]


def balas(*pasangan):
    return ["#swagger.responses[%d] = { description: '%s' }" % x for x in pasangan]


def kepala(tag, ringkas):
    return ["#swagger.tags = ['%s']" % tag, "#swagger.summary = '%s'" % ringkas]


HANDLER = [
    komentar("register", kepala("Auth", "Daftar akun baru") + ["#swagger.security = []"] + badan("Register")
             + balas((201, "Akun dibuat"), (400, "Isian tidak valid"), (409, "Email sudah terdaftar"))),
    komentar("login", kepala("Auth", "Masuk dan dapatkan token") + ["#swagger.security = []"] + badan("Login")
             + balas((200, "Berhasil, respons berisi token"), (401, "Email atau password salah"),
                     (429, "Terlalu banyak percobaan"))),
    komentar("profile", kepala("Profil", "Lihat profil sendiri") + balas((200, "Data profil"))),
    komentar("updateProfile", kepala("Profil", "Ubah nama dan email") + badan("Profil")
             + balas((200, "Profil diubah"), (400, "Isian tidak valid"), (409, "Email sudah terdaftar"))),
    komentar("updatePassword", kepala("Profil", "Ubah password") + badan("Password")
             + balas((200, "Password diubah"), (400, "Password lama salah atau password baru terlalu pendek"))),
]

CONTOH_CRUD = komentar("create", kepala("Barang", "Tambah barang") + [
    "#swagger.requestBody = {",
    "  required: true,",
    "  content: { 'application/json': { example: { nama: 'Kopi', stok: 10 } } }",
    "}",
] + balas((201, "Data dibuat"), (400, "Isian tidak valid")))

CONTOH_UPLOAD = """/*
  #swagger.requestBody = {
    required: true,
    content: {
      'multipart/form-data': {
        schema: { type: 'object', properties: { foto: { type: 'string', format: 'binary' } } }
      }
    }
  }
*/
"""


def build(page, p, h3, ul, box, card, table, c):
    ulang = card("terminal", "npm run swagger")
    sections = [
        ("Apa Bedanya",
         p("<strong>swagger-autogen</strong> membaca <code>src/app.js</code> beserta handler yang dipakainya, lalu menulis file dokumentasi sendiri. Perannya sama dengan <code>swag init</code> di versi Go.")
         + table(["", '<a href="swagger.html">Tulis sendiri</a>', "Generate (halaman ini)"], [
             ["Daftar endpoint", "Diketik satu per satu", "Dibaca dari route"],
             ["Isi body", "Diketik", "Nama field terbaca dari <code>req.body</code>; contohnya lewat komentar"],
             ["Setelah API berubah", "Ubah file dokumentasi", "Jalankan <code>npm run swagger</code>"],
             ["File dokumentasi", c("src/docs/swagger.js"), c("src/docs/swagger-output.json")],
         ])
         + box("note", "Pilih salah satu", "Hasil keduanya sama-sama tampil di <code>/swagger/</code>. Yang dipakai ditentukan satu baris <code>require</code> di <code>app.js</code>.")),
        ("Syarat Awal",
         p('Project Express-mu sudah punya modul user, bisa dijalankan dengan <code>npm run dev</code>, dan <code>/swagger/</code> sudah tampil. Itu terpenuhi kalau kamu mengikuti <a href="00-fondasi.html">Fondasi Modul User</a> atau <a href="../pertemuan-09a.html">Pertemuan 9a</a>.')
         + p('Belum ada <code>swagger-ui-express</code>? Kerjakan dulu <a href="swagger.html#s3">langkah 1</a> dan <a href="swagger.html#s5">langkah 3 di tutorial manual</a>.')),
        ("Langkah 1: Install",
         p("Di folder project:")
         + card("terminal", "npm install --save-exact --save-dev swagger-autogen@2.23.7\nmkdir -p scripts")),
        ("Langkah 2: Buat Script Generator",
         p("Buat file baru <code>scripts/generate-swagger.js</code>:")
         + card("scripts/generate-swagger.js", SCRIPT_AWAL)
         + p('Lalu di <code>package.json</code>, tambahkan satu baris di bagian <code>scripts</code>:')
         + card("package.json — di dalam scripts", '"swagger": "node scripts/generate-swagger.js",')),
        ("Langkah 3: Generate",
         ulang
         + p("Terminal menampilkan <code>Swagger-autogen: Success</code> dan muncul file <code>src/docs/swagger-output.json</code>. File ini <strong>jangan diedit manual</strong> karena ditimpa setiap kali generate.")),
        ("Langkah 4: Pakai Hasilnya",
         p("Di bagian atas <code>src/app.js</code>, ganti baris <code>require</code> Swagger:")
         + card("src/app.js — ganti satu baris", APP_REQUIRE)
         + p("Route bantu tidak perlu ikut didokumentasikan. Masih di <code>app.js</code>, ganti route <code>/healthz</code> dan <code>/swagger/index.html</code> menjadi:")
         + card("src/app.js — health check", APP_IGNORE)
         + card("src/app.js — pengalihan swagger", APP_IGNORE_SWAGGER)
         + card("terminal", "npm run swagger\nnpm run dev")
         + box("verify", "Checkpoint", "Buka <code>http://localhost:8080/swagger/</code>. Semua route muncul dalam satu kelompok <strong>default</strong>, dan body register sudah berisi <code>nama</code>, <code>email</code>, <code>password</code> dengan nilai <code>any</code>.")),
        ("Langkah 5: Token & Contoh Isian",
         p("Ganti seluruh isi <code>scripts/generate-swagger.js</code>. Tambahannya: jenis token (supaya tombol <em>Authorize</em> berfungsi) dan contoh isian.")
         + card("scripts/generate-swagger.js", SCRIPT_LENGKAP)),
        ("Langkah 6: Komentar di Handler",
         p("Kelompok, judul, contoh body, dan balasan diatur lewat komentar <code>#swagger</code>. Buka <code>src/handlers/authHandler.js</code>, tempel tiap komentar <strong>di dalam</strong> fungsinya, tepat setelah baris <code>async function</code>. Komentar di luar fungsi diabaikan.")
         + "".join(card("src/handlers/authHandler.js", x) for x in HANDLER)
         + table(["Komentar", "Fungsi"], [
             [c("#swagger.tags"), "Nama kelompok."], [c("#swagger.summary"), "Judul singkat."],
             [c("#swagger.security = []"), "Endpoint publik, tanpa token."],
             [c("#swagger.requestBody"), "Contoh isian, diambil dari <code>schemas</code> di script."],
             [c("#swagger.responses[409]"), "Keterangan satu status balasan."],
         ])
         + ulang
         + p("Muat ulang halaman <code>/swagger/</code>.")
         + box("verify", "Coba", "Register → <code>201</code>. Login → <code>200</code>, salin <code>token</code>. Klik <strong>Authorize</strong>, tempel token tanpa kata <code>Bearer</code>. <strong>GET /api/profile</strong> → <code>200</code>.")),
        ("CRUD Project-mu",
         p('Setelah mengikuti <a href="index.html">tutorial project</a>, jalankan <code>npm run swagger</code>: lima endpoint CRUD langsung terbaca, termasuk <code>{id}</code>, <code>q</code>, <code>page</code>, dan <code>limit</code>.')
         + p("Yang <strong>tidak</strong> terbaca adalah isi body, karena handler meneruskan <code>req.body</code> utuh ke service. Tambahkan komentar pada fungsi <code>create</code> (dan <code>update</code>) di handler-mu. Ganti <code>Barang</code> dan contohnya dengan <em>contoh body</em> dari halaman project-mu.")
         + card("src/handlers/…Handler.js — contoh", CONTOH_CRUD)
         + p("Untuk <code>update</code>, ganti judulnya dan pakai status <code>200</code>. Beri <code>#swagger.tags</code> yang sama pada kelima fungsi supaya mengelompok.")
         + box("warn", "Tutorial project mengganti app.js", "Bagian Route di halaman project meminta mengganti seluruh <code>src/app.js</code>, sehingga baris <code>require</code> kembali ke <code>./docs/swagger</code>. Ulangi langkah 4. Bagian Swagger di halaman project (cara manual) boleh dilewati.")
         + h3("Upload file")
         + p("Kalau route-mu menerima file (misalnya di proyek UMKM), tulis komentar ini di dalam handler-nya:")
         + card("contoh — upload file", CONTOH_UPLOAD)),
        ("Kebiasaan Sehari-hari",
         ul(["Setiap menambah atau mengubah route dan komentar, jalankan <code>npm run swagger</code>. Kalau <code>npm run dev</code> sedang menyala, server restart sendiri; tinggal muat ulang halaman.",
             "Ikut sertakan <code>swagger-output.json</code> dalam commit. Server membutuhkannya, sedangkan <code>swagger-autogen</code> hanya terpasang di komputer development."])
         + p("Opsional, supaya generate otomatis setiap kali memulai <code>npm run dev</code>:")
         + card("package.json — di dalam scripts", '"predev": "npm run swagger",')),
        ("Troubleshooting",
         table(["Gejala", "Penyebab", "Solusi"], [
             [c("Cannot find module './docs/swagger-output.json'"), "Belum pernah generate.", c("npm run swagger")],
             [c("Cannot find module 'swagger-autogen'"), "Paket belum terpasang.", "Ulangi langkah 1."],
             [c("'#swagger.requestBody' out of structure"), "Kurung di komentar tidak lengkap. Terminal <strong>tetap menulis Success</strong>.", "Perbaiki kurungnya, generate lagi. Baca selalu seluruh keluaran terminal."],
             ["Komentar tidak berpengaruh", "Ditulis di luar fungsi, atau belum generate.", "Pindahkan ke dalam fungsi."],
             ["Endpoint baru tidak muncul", "Belum generate, atau route tidak terhubung dari <code>app.js</code>.", c("npm run swagger")],
             ["Body berisi <code>any</code> atau kosong", "Belum ada komentar <code>requestBody</code>.", "Lihat langkah 6."],
             ["Sudah Authorize tetap <code>401</code>", "Script belum berisi <code>security</code>, atau token kedaluwarsa.", "Ulangi langkah 5, login lagi."],
             ["Tampilan masih yang lama", "<code>app.js</code> masih memanggil <code>./docs/swagger</code>.", "Ulangi langkah 4."],
         ])),
        ("Checklist",
         ul(["<code>npm run swagger</code> selesai tanpa pesan <code>out of structure</code>.",
             "<code>/swagger/</code> menampilkan kelompok Auth dan Profil dengan contoh isian.",
             "Tanpa token, <code>GET /api/profile</code> membalas <code>401</code>; setelah Authorize, <code>200</code>.",
             "Di server produksi, route <code>/swagger</code> dimatikan atau dilindungi."])),
    ]
    return page("Generate Swagger Otomatis di Node.js", "Tutorial &middot; Dokumentasi API",
                "Satu perintah untuk membuat dokumentasi API dari route Express, memakai swagger-autogen.", sections)
