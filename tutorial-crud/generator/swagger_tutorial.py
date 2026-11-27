"""Halaman ../swagger.html: tutorial setup Swagger dari awal untuk project yang baru punya modul user.

Potongan kode disusun bertahap; "file lengkap" di akhir halaman digabung otomatis
dari potongan yang sama, jadi keduanya tidak bisa berbeda.
"""

KERANGKA = """// Dokumentasi API dalam format OpenAPI 3.
// Swagger UI membaca objek ini lalu membuat halamannya.
module.exports = {
  openapi: '3.0.3',
  info: {
    title: 'API Project',
    version: '1.0.0',
    description: 'Dokumentasi modul user',
  },
  servers: [{ url: '/api' }],
  tags: [],
  components: { securitySchemes: {} },
  paths: {},
};
"""

APP_JS = """const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./docs/swagger');

// /swagger/index.html dialihkan: file bawaan paket di alamat itu berisi demo "Petstore"
app.get('/swagger/index.html', (req, res) => res.redirect('/swagger/'));
app.use(
  '/swagger',
  swaggerUi.serve,
  swaggerUi.setup(swaggerSpec, { swaggerOptions: { persistAuthorization: true } }),
);
"""

SERVER_JS = """    console.log(`swagger: http://localhost:${config.port}/swagger/`);
"""

REGISTER = """// ---------- register ----------
module.exports.tags.push({ name: 'Auth', description: 'Daftar dan masuk' });

module.exports.paths['/auth/register'] = {
  post: {
    tags: ['Auth'],
    summary: 'Daftar akun baru',
    requestBody: {
      required: true,
      content: {
        'application/json': {
          schema: {
            type: 'object',
            required: ['nama', 'email', 'password'],
            properties: {
              nama: { type: 'string', example: 'Budi Tester' },
              email: { type: 'string', format: 'email', example: 'budi@test.com' },
              password: { type: 'string', format: 'password', example: 'rahasia123' },
            },
          },
        },
      },
    },
    responses: {
      201: { description: 'Akun dibuat' },
      400: { description: 'Isian tidak lengkap atau password kurang dari 6 karakter' },
      409: { description: 'Email sudah terdaftar' },
    },
  },
};
"""

BANTU = """// ---------- fungsi bantu ----------
// Body JSON; semua properti yang ditulis dianggap wajib.
function jsonBody(properties) {
  return {
    required: true,
    content: {
      'application/json': {
        schema: { type: 'object', required: Object.keys(properties), properties },
      },
    },
  };
}

const email = { type: 'string', format: 'email', example: 'budi@test.com' };
const password = { type: 'string', format: 'password', example: 'rahasia123' };
"""

LOGIN = """// ---------- login ----------
module.exports.paths['/auth/login'] = {
  post: {
    tags: ['Auth'],
    summary: 'Masuk dan dapatkan token (maks. 5 kali per menit)',
    requestBody: jsonBody({ email, password }),
    responses: {
      200: { description: 'Berhasil, respons berisi token' },
      401: { description: 'Email atau password salah' },
      429: { description: 'Terlalu banyak percobaan' },
    },
  },
};
"""

PROFIL = """// ---------- token (tombol Authorize) ----------
module.exports.components.securitySchemes.bearerAuth = {
  type: 'http',
  scheme: 'bearer',
  bearerFormat: 'JWT',
};
const butuhToken = [{ bearerAuth: [] }];

// ---------- lihat profil ----------
module.exports.tags.push({ name: 'Profil', description: 'Butuh token' });

module.exports.paths['/profile'] = {
  get: {
    tags: ['Profil'],
    summary: 'Lihat profil sendiri',
    security: butuhToken,
    responses: {
      200: { description: 'Data profil' },
      401: { description: 'Token tidak ada atau tidak valid' },
    },
  },
};
"""

UBAH = """// ---------- ubah profil ----------
// ditambahkan sebagai method kedua pada path /profile yang sudah ada
module.exports.paths['/profile'].put = {
  tags: ['Profil'],
  summary: 'Ubah nama dan email',
  security: butuhToken,
  requestBody: jsonBody({ nama: { type: 'string', example: 'Budi Baru' }, email }),
  responses: {
    200: { description: 'Profil diubah' },
    400: { description: 'Nama dan email wajib diisi' },
    401: { description: 'Token tidak valid' },
    409: { description: 'Email sudah terdaftar' },
  },
};

// ---------- ubah password ----------
module.exports.paths['/profile/password'] = {
  put: {
    tags: ['Profil'],
    summary: 'Ubah password',
    security: butuhToken,
    requestBody: jsonBody({
      password_lama: password,
      password_baru: { ...password, example: 'rahasiabaru456' },
    }),
    responses: {
      200: { description: 'Password diubah' },
      400: { description: 'Password lama salah atau password baru terlalu pendek' },
      401: { description: 'Token tidak valid' },
    },
  },
};
"""

CONTOH_PARAM = """// path parameter: GET /barang/{id}   (di Express ditulis /barang/:id)
// query parameter: GET /barang?q=kopi&page=1
module.exports.paths['/barang/{id}'] = {
  get: {
    tags: ['Barang'],
    summary: 'Detail barang',
    security: butuhToken,
    parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }],
    responses: { 200: { description: 'Detail' }, 404: { description: 'Tidak ditemukan' } },
  },
};

module.exports.paths['/barang'] = {
  get: {
    tags: ['Barang'],
    summary: 'Daftar barang',
    security: butuhToken,
    parameters: [
      { name: 'q', in: 'query', schema: { type: 'string' } },
      { name: 'page', in: 'query', schema: { type: 'integer' } },
    ],
    responses: { 200: { description: 'Daftar' } },
  },
};
"""

CONTOH_UPLOAD = """// upload file: tipe isinya multipart/form-data, file ditandai format binary
module.exports.paths['/barang/{id}/foto'] = {
  put: {
    tags: ['Barang'],
    summary: 'Unggah foto barang',
    security: butuhToken,
    parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }],
    requestBody: {
      required: true,
      content: {
        'multipart/form-data': {
          schema: {
            type: 'object',
            properties: { foto: { type: 'string', format: 'binary' } },
          },
        },
      },
    },
    responses: { 200: { description: 'Foto tersimpan' } },
  },
};
"""

LANGKAH = [KERANGKA, REGISTER, BANTU, LOGIN, PROFIL, UBAH]


def file_lengkap():
    return "\n".join(x.rstrip("\n") + "\n" for x in LANGKAH)


def build(page, p, h3, ul, box, card, table, c):
    tambah = "src/docs/swagger.js — tambahkan di paling bawah"
    ulang = p("Simpan file. <code>npm run dev</code> menyalakan ulang server otomatis; muat ulang halaman <code>/swagger/</code> di browser.")
    sections = [
        ("Apa Itu Swagger",
         p("<strong>Swagger UI</strong> adalah halaman web yang menampilkan daftar endpoint API dan menyediakan tombol untuk mencobanya langsung dari browser, tanpa Postman. Isinya dibaca dari deskripsi berformat <strong>OpenAPI</strong> yang kita tulis.")
         + table(["Istilah", "Arti"], [
             ["OpenAPI", "Aturan penulisan deskripsi API (endpoint, isian, balasan)."],
             ["Swagger UI", "Tampilan web yang membaca deskripsi itu."],
             [c("swagger-ui-express"), "Paket npm yang menyajikan Swagger UI dari server Express."],
             [c("src/docs/swagger.js"), "File deskripsi yang akan kita buat."],
         ])
         + box("note", "Dokumentasi tidak otomatis", "Swagger hanya menampilkan apa yang ditulis di file deskripsi. Ia tidak membuat atau memvalidasi endpoint. Kalau API berubah, deskripsinya ikut diubah. Mau dibuat dari route dengan satu perintah? Lihat <a href=\"swagger-generate.html\">Generate Swagger Otomatis</a>.")),
        ("Syarat Awal",
         p("Project Express-mu sudah punya modul user dan bisa dijalankan dengan <code>npm run dev</code>. Pastikan lima route ini ada di <code>src/app.js</code>:")
         + table(["Route", "Fungsi"], [
             [c("POST /api/auth/register"), "Daftar"], [c("POST /api/auth/login"), "Masuk, menghasilkan token"],
             [c("GET /api/profile"), "Lihat profil"], [c("PUT /api/profile"), "Ubah profil"],
             [c("PUT /api/profile/password"), "Ubah password"],
         ])
         + p('Belum punya? Buat dulu lewat <a href="00-fondasi.html">Fondasi Modul User</a>. Fondasi dan folder <code>starter</code> <strong>sudah berisi Swagger</strong>, jadi halaman ini dipakai untuk memahami cara membuatnya.')
         + box("warn", "Sudah ada src/docs/swagger.js?", "Berarti Swagger sudah terpasang. Jangan ditimpa kalau di dalamnya sudah ada dokumentasi lain; simpan salinannya dulu.")),
        ("Langkah 1: Install Paket",
         p("Hentikan server (<code>Ctrl+C</code>), lalu di folder project:")
         + card("terminal", "npm install --save-exact swagger-ui-express@5.0.1\nmkdir -p src/docs")),
        ("Langkah 2: Buat Kerangka",
         p("Buat file baru <code>src/docs/swagger.js</code>:")
         + card("src/docs/swagger.js", KERANGKA)
         + table(["Bagian", "Fungsi"], [
             [c("openapi"), "Versi format."], [c("info"), "Judul, versi, dan keterangan di bagian atas halaman."],
             [c("servers"), "Awalan semua path. Karena sudah <code>/api</code>, path ditulis tanpa <code>/api</code>."],
             [c("tags"), "Nama kelompok endpoint."], [c("components"), "Definisi yang dipakai ulang, misalnya jenis token."],
             [c("paths"), "Daftar endpoint. Masih kosong."],
         ])),
        ("Langkah 3: Daftarkan di app.js",
         p("Buka <code>src/app.js</code>. Tempel kode berikut <strong>di atas</strong> baris <code>app.use(errorHandler);</code>:")
         + card("src/app.js — tempel di atas app.use(errorHandler)", APP_JS)
         + table(["Baris", "Fungsi"], [
             [c("swaggerUi.serve"), "Mengirim file tampilan (HTML, CSS, JavaScript)."],
             [c("swaggerUi.setup(swaggerSpec, ...)"), "Mengisi tampilan dengan deskripsi kita."],
             [c("persistAuthorization: true"), "Token tetap tersimpan setelah halaman dimuat ulang."],
         ])
         + p("Opsional, supaya alamatnya muncul di terminal, tambahkan baris ini di <code>server.js</code> di bawah pesan <code>server berjalan di port ...</code>:")
         + card("server.js — di dalam app.listen", SERVER_JS)
         + card("terminal — jalankan server", "npm run dev")
         + box("verify", "Checkpoint", "Buka <code>http://localhost:8080/swagger/</code>. Harus tampil judul <strong>API Project</strong> dengan keterangan <em>No operations defined in spec!</em> Itu benar, karena <code>paths</code> masih kosong.")),
        ("Langkah 4: Dokumentasikan Register",
         card(tambah, REGISTER)
         + table(["Bagian", "Arti"], [
             [c("paths['/auth/register']"), "Alamat endpoint."], [c("post"), "Method HTTP."],
             [c("tags"), "Masuk ke kelompok mana."], [c("summary"), "Judul singkat."],
             [c("requestBody"), "Bentuk data yang dikirim."], [c("required"), "Field yang wajib."],
             [c("example"), "Isian contoh yang otomatis muncul saat <em>Try it out</em>."],
             [c("responses"), "Kemungkinan status balasan."],
         ])
         + ulang
         + box("verify", "Coba", "Klik <strong>POST /auth/register</strong> → <em>Try it out</em> → <em>Execute</em>. Harus <code>201</code>. Tekan lagi: harus <code>409</code>.")),
        ("Langkah 5: Fungsi Bantu & Login",
         p("Menulis <code>requestBody</code> sepanjang itu untuk setiap endpoint melelahkan. Buat fungsi bantu:")
         + card(tambah, BANTU)
         + p("Sekarang login jauh lebih pendek:")
         + card(tambah, LOGIN)
         + ulang
         + box("verify", "Coba", "<strong>POST /auth/login</strong> → <em>Execute</em> → <code>200</code>. Salin nilai <code>token</code> dari respons, tanpa tanda kutip.")),
        ("Langkah 6: Token & Lihat Profil",
         card(tambah, PROFIL)
         + table(["Bagian", "Fungsi"], [
             [c("securitySchemes.bearerAuth"), "Memberi tahu Swagger bahwa API memakai header <code>Authorization: Bearer ...</code>. Tombol <em>Authorize</em> sudah ada sejak kerangka; baris ini membuat jendelanya menyediakan kolom token."],
             [c("security: butuhToken"), "Endpoint ini dikirim bersama token (ikon gembok)."],
         ])
         + ulang
         + ul(["<strong>GET /profile</strong> → <em>Execute</em> → <code>401</code> (belum membawa token).",
               "Klik <strong>Authorize</strong>, tempel token <strong>tanpa kata Bearer</strong>, klik <em>Authorize</em>, lalu <em>Close</em>.",
               "<em>Execute</em> lagi → <code>200</code>."], "ol")),
        ("Langkah 7: Ubah Profil & Password",
         card(tambah, UBAH)
         + box("warn", "Perhatikan .put", "Satu path hanya boleh didefinisikan sekali. Method kedua ditambahkan dengan <code>paths['/profile'].put = ...</code>. Kalau ditulis <code>paths['/profile'] = { put: ... }</code>, dokumentasi GET akan tertimpa dan hilang.")
         + ulang
         + box("verify", "Coba", "<strong>PUT /profile</strong> → <code>200</code>. <strong>PUT /profile/password</strong> → <code>200</code>. Setelah itu login memakai password baru <code>rahasiabaru456</code>.")),
        ("Menguji Jalur Gagal",
         table(["Endpoint", "Yang dicoba", "Harus dibalas"], [
             ["register", "Email yang sama dua kali", c("409")], ["register", "Password 3 karakter", c("400")],
             ["login", "Password salah", c("401")], ["login", "Lebih dari 5 kali dalam 1 menit", c("429")],
             ["GET /profile", "<em>Logout</em> di jendela Authorize, lalu <em>Execute</em>", c("401")],
             ["PUT /profile/password", "Password lama salah", c("400")],
         ])
         + p('Kalau balasannya berbeda (misalnya <code>500</code>), yang perlu diperiksa kode API-nya, bukan Swagger. Bandingkan dengan <a href="../pertemuan-09a.html#s11">Pertemuan 9a Bagian 11</a>.')),
        ("Menambah Endpoint Lain",
         p("Polanya selalu sama: tambahkan path, tulis method, lalu muat ulang. Contoh untuk endpoint milikmu sendiri (ganti <code>barang</code>). Dokumentasi hanya berfungsi kalau route-nya memang sudah ada di <code>app.js</code>.")
         + p("Daftarkan dulu kelompoknya dengan <code>module.exports.tags.push({ name: 'Barang' });</code>")
         + h3("Parameter di path dan query")
         + card("contoh — path dan query parameter", CONTOH_PARAM)
         + h3("Upload file")
         + card("contoh — upload file", CONTOH_UPLOAD)
         + p('Untuk CRUD lengkap, tutorial <a href="index.html">project masing-masing</a> memakai fungsi <code>crudDocs</code> yang membuat dokumentasi lima endpoint sekaligus.')),
        ("Troubleshooting",
         table(["Gejala", "Penyebab", "Solusi"], [
             [c("Cannot find module 'swagger-ui-express'"), "Paket belum terpasang.", c("npm install")],
             [c("Cannot find module './docs/swagger'"), "Nama atau lokasi file salah.", "Harus <code>src/docs/swagger.js</code>."],
             ["<code>/swagger/</code> membalas <code>Cannot GET</code>", "Kode di <code>app.js</code> belum ditempel atau server belum di-restart.", "Ulangi langkah 3."],
             [c("jsonBody is not defined") + " atau " + c("butuhToken is not defined"), "Urutan potongan terbalik.", "Fungsi bantu dan <code>butuhToken</code> harus di atas pemakaiannya."],
             ["Endpoint tidak muncul", "File belum disimpan, atau <code>paths</code> tertimpa.", "Simpan, restart, muat ulang."],
             ["Tampil <em>Failed to fetch</em> atau <code>404</code> saat Execute", "Path di dokumentasi berbeda dari route.", "Samakan; ingat <code>servers</code> sudah berisi <code>/api</code>."],
             ["Sudah Authorize tetapi <code>401</code>", "Menempel kata <code>Bearer</code> atau token kedaluwarsa.", "<em>Logout</em>, tempel token saja."],
         ])),
        ("File Lengkap & Checklist",
         p("Isi akhir <code>src/docs/swagger.js</code> setelah semua langkah, untuk dibandingkan:")
         + card("file lengkap — src/docs/swagger.js", file_lengkap())
         + ul(["<code>/swagger/</code> menampilkan 5 endpoint dalam kelompok Auth dan Profil.",
               "Register, login, dan ketiga endpoint profil berhasil dicoba.",
               "Tanpa token, endpoint profil membalas <code>401</code>.",
               "Di server produksi, route <code>/swagger</code> dimatikan atau dilindungi."])),
    ]
    return page("Setup Swagger dari Awal (Modul User)", "Tutorial &middot; Dokumentasi API",
                "Dari project yang baru punya modul user sampai semua endpoint-nya bisa diuji dari browser.", sections)
