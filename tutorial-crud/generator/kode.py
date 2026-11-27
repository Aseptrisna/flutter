"""Pembuat kode: fondasi (modul user, disalin dari umkm-api-node) dan CRUD per project."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "umkm-api-node")


def read(path):
    with open(os.path.join(SRC, path), encoding="utf-8") as f:
        return f.read()


def sub(text, old, new):
    assert text.count(old) == 1, "pola tidak ditemukan tepat 1 kali: " + old[:70]
    return text.replace(old, new)


# ---------------------------------------------------------------- file tambahan fondasi
VALIDATE_JS = """const { InvalidInputError } = require('../errors');

const MAKS_INT = 2147483647; // batas kolom Int di PostgreSQL
const POLA_TANGGAL = /^\\d{4}-\\d{2}-\\d{2}$/;

function gagal(pesan) {
  throw new InvalidInputError(pesan);
}

// Satu pemeriksa untuk tiap tipe kolom. Mengembalikan nilai yang siap disimpan.
const pemeriksa = {
  teks(nama, nilai, aturan) {
    if (typeof nilai !== 'string' || nilai.trim() === '') gagal(`${nama} harus berupa teks`);
    if (aturan.max && nilai.trim().length > aturan.max) gagal(`${nama} maksimal ${aturan.max} karakter`);
    return nilai.trim();
  },
  bulat(nama, nilai, aturan) {
    const min = aturan.min ?? 0;
    if (!Number.isInteger(nilai) || nilai < min || nilai > MAKS_INT) {
      gagal(`${nama} harus bilangan bulat minimal ${min}`);
    }
    return nilai;
  },
  angka(nama, nilai, aturan) {
    if (typeof nilai !== 'number' || nilai < aturan.min || nilai > aturan.max) {
      gagal(`${nama} harus angka antara ${aturan.min} dan ${aturan.max}`);
    }
    return nilai;
  },
  boolean(nama, nilai) {
    if (typeof nilai !== 'boolean') gagal(`${nama} harus true atau false`);
    return nilai;
  },
  tanggal(nama, nilai) {
    const pesan = `${nama} harus tanggal berformat YYYY-MM-DD`;
    if (typeof nilai !== 'string' || !POLA_TANGGAL.test(nilai)) gagal(pesan);
    const tanggal = new Date(`${nilai}T00:00:00Z`);
    // tanggal mustahil seperti 2026-02-30 bergeser atau tidak valid
    if (Number.isNaN(tanggal.getTime()) || tanggal.toISOString().slice(0, 10) !== nilai) gagal(pesan);
    return tanggal;
  },
  pilihan(nama, nilai, aturan) {
    if (!aturan.opsi.includes(nilai)) gagal(`${nama} harus salah satu dari: ${aturan.opsi.join(', ')}`);
    return nilai;
  },
};

// validate memeriksa body sesuai aturan, lalu mengembalikan HANYA kolom yang
// terdaftar. Kolom lain yang dikirim klien (misalnya user_id) otomatis dibuang.
function validate(body, aturan) {
  const hasil = {};
  for (const [nama, a] of Object.entries(aturan)) {
    const nilai = body ? body[nama] : undefined;
    if (nilai === undefined || nilai === null || nilai === '') {
      if (a.wajib) gagal(`${nama} wajib diisi`);
      hasil[nama] = a.tipe === 'boolean' ? false : null;
    } else {
      hasil[nama] = pemeriksa[a.tipe](nama, nilai, a);
    }
  }
  return hasil;
}

// parseId mengubah :id dari URL menjadi angka yang aman.
function parseId(value) {
  const id = Number(value);
  if (!Number.isInteger(id) || id < 1 || id > MAKS_INT) gagal('id tidak valid');
  return id;
}

module.exports = { validate, parseId };
"""

CRUD_DOCS_JS = """// crudDocs membuat dokumentasi Swagger untuk 5 endpoint CRUD sekaligus.
function crudDocs({ tag, path, properties, required }) {
  const security = [{ bearerAuth: [] }];
  const contoh = { id: 1, user_id: 1 };
  for (const [nama, p] of Object.entries(properties)) contoh[nama] = p.example;

  const json = (example) => ({ 'application/json': { example } });
  const reply = (description, data) => ({ description, content: json({ data }) });
  const gagal = (description, code) => ({
    description,
    content: json({ error: { message: description, code } }),
  });

  const body = {
    required: true,
    content: { 'application/json': { schema: { type: 'object', required, properties } } },
  };
  const id = [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }];
  const query = ['q', 'page', 'limit'].map((name) => ({
    name,
    in: 'query',
    schema: { type: name === 'q' ? 'string' : 'integer' },
  }));

  const salahInput = gagal('input tidak valid', 'BAD_REQUEST');
  const tanpaToken = gagal('token tidak valid', 'UNAUTHORIZED');
  const bukanPemilik = gagal('Anda bukan pemilik data ini', 'FORBIDDEN');
  const tidakAda = gagal('data tidak ditemukan', 'NOT_FOUND');
  const base = { tags: [tag], security };

  return {
    tag: { name: tag, description: 'Data milik pengguna yang login' },
    paths: {
      [`/${path}`]: {
        get: {
          ...base,
          summary: 'Daftar data milik sendiri',
          parameters: query,
          responses: { 200: reply('Daftar data', [contoh]), 401: tanpaToken },
        },
        post: {
          ...base,
          summary: 'Tambah data',
          requestBody: body,
          responses: { 201: reply('Data dibuat', contoh), 400: salahInput, 401: tanpaToken },
        },
      },
      [`/${path}/{id}`]: {
        get: {
          ...base,
          summary: 'Detail data',
          parameters: id,
          responses: { 200: reply('Detail', contoh), 403: bukanPemilik, 404: tidakAda },
        },
        put: {
          ...base,
          summary: 'Ubah data (kirim semua kolom)',
          parameters: id,
          requestBody: body,
          responses: { 200: reply('Data diubah', contoh), 400: salahInput, 403: bukanPemilik, 404: tidakAda },
        },
        delete: {
          ...base,
          summary: 'Hapus data',
          parameters: id,
          responses: {
            200: reply('Terhapus', { message: 'data berhasil dihapus' }),
            403: bukanPemilik,
            404: tidakAda,
          },
        },
      },
    },
  };
}

module.exports = crudDocs;
"""

PENANDA_ROUTE = "// --- route project-mu ---\n"


def foundation_files():
    """Semua file fondasi. File modul user diambil apa adanya dari umkm-api-node."""
    schema = read("prisma/schema.prisma")
    user_model = schema[schema.index("model User {"):schema.index("model Umkm {")]
    user_model = sub(user_model, "  umkm Umkm?\n\n", "")
    header = schema[schema.index("generator client"):schema.index("model User {")]

    config = sub(read("src/config.js"), "  uploadDir: getOrDefault('UPLOAD_DIR', './uploads'),\n", "")

    eh = read("src/middleware/errorHandler.js")
    eh = sub(eh, "const { InvalidFileTypeError } = require('../utils/upload');\n\n", "")
    a = eh.index("  // Error dari multer")
    b = eh.index("  // Body JSON yang rusak")
    eh = eh[:a] + eh[b:]

    swagger = read("src/docs/swagger.js")
    swagger = sub(swagger, "title: 'UMKM API (Node.js)',", "title: 'API Project',")

    app = read("src/app.js")
    for old in ["const path = require('path');\n",
                "const { uploadSingle } = require('./utils/upload');\n",
                "const config = require('./config');\n",
                "const umkmHandler = require('./handlers/umkmHandler');\n",
                "const produkHandler = require('./handlers/produkHandler');\n"]:
        app = sub(app, old, "")
    a = app.index("// umkm\n")
    b = app.index("// health check")
    app = app[:a] + PENANDA_ROUTE + "\n" + app[b:]

    pkg = json.loads(read("package.json"))
    pkg["name"] = "api-project"
    pkg["description"] = "REST API project mahasiswa — Express + Prisma + PostgreSQL"
    del pkg["dependencies"]["multer"]

    env = "".join(l for l in read(".env.example").splitlines(True) if not l.startswith("UPLOAD_DIR"))

    files = {
        "package.json": json.dumps(pkg, indent=2, ensure_ascii=False) + "\n",
        ".env.example": env,
        ".gitignore": "node_modules/\n.env\n",
        "prisma/schema.prisma": "// Skema database. User dipakai semua project; tambahkan tabelmu di bawahnya.\n\n"
                                + header + user_model.rstrip() + "\n",
        "src/config.js": config,
        "src/db.js": read("src/db.js"),
        "src/errors.js": read("src/errors.js"),
        "src/utils/response.js": read("src/utils/response.js"),
        "src/utils/pagination.js": read("src/utils/pagination.js"),
        "src/utils/validate.js": VALIDATE_JS,
        "src/middleware/auth.js": read("src/middleware/auth.js"),
        "src/middleware/rateLimit.js": read("src/middleware/rateLimit.js"),
        "src/middleware/errorHandler.js": eh,
        "src/repositories/userRepository.js": read("src/repositories/userRepository.js"),
        "src/services/authService.js": read("src/services/authService.js"),
        "src/handlers/authHandler.js": read("src/handlers/authHandler.js"),
        "src/docs/swagger.js": swagger,
        "src/docs/crud.js": CRUD_DOCS_JS,
        "src/app.js": app,
        "server.js": read("server.js"),
    }
    return files


# ---------------------------------------------------------------- CRUD per project
def camel(model):
    return model[0].lower() + model[1:]


def snake(model):
    return "".join(("_" if c.isupper() and i else "") + c.lower() for i, c in enumerate(model))


def js(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(value, list):
        return "[" + ", ".join(js(v) for v in value) + "]"
    return repr(value)


def prisma_type(kind, required, extra):
    q = "" if required else "?"
    if kind == "teks":
        return "String" + q, ("@db.VarChar(%d)" % extra["max"]) if "max" in extra else ""
    if kind == "pilihan":
        return "String", "@db.VarChar(%d)" % extra["max"]
    if kind == "bulat":
        return "Int" + q, ""
    if kind == "angka":
        return "Decimal" + q, "@db.Decimal(%d, %d)" % extra["presisi"]
    if kind == "boolean":
        return "Boolean", "@default(false)"
    if kind == "tanggal":
        return "DateTime" + q, "@db.Date"
    raise ValueError(kind)


def schema_prisma(p):
    base = foundation_files()["prisma/schema.prisma"]
    acc = camel(p["model"])
    base = sub(base, '\n  @@map("users")', '\n  %s %s[]\n\n  @@map("users")' % (acc, p["model"]))
    rows = [("id", "Int", "@id @default(autoincrement())"), ("user_id", "Int", "")]
    for name, kind, required, _, extra in p["kolom"]:
        t, attr = prisma_type(kind, required, extra)
        rows.append((name, t, attr))
    rows.append(("created_at", "DateTime", "@default(now()) @db.Timestamp(6)"))
    w1 = max(len(r[0]) for r in rows)
    w2 = max(len(r[1]) for r in rows)
    body = "".join(("  %s %s %s" % (n.ljust(w1), t.ljust(w2), a)).rstrip() + "\n" for n, t, a in rows)
    model = ("model %s {\n%s\n  user User @relation(fields: [user_id], references: [id], onDelete: Cascade)\n\n"
             "  @@index([user_id])\n  @@map(\"%s\")\n}\n") % (p["model"], body, snake(p["model"]))
    return base + "\n" + model


def repository(p):
    acc = camel(p["model"])
    cols = ["id", "user_id"] + [k[0] for k in p["kolom"]]
    maps = []
    for name, kind, required, _, _x in p["kolom"]:
        if kind == "angka":
            maps.append("    %s: row.%s === null ? null : Number(row.%s)," % (name, name, name))
        if kind == "tanggal":
            maps.append("    %s: row.%s && row.%s.toISOString().slice(0, 10)," % (name, name, name))
    if maps:
        mapper = ("// mapRow mengubah tipe dari Prisma menjadi bentuk JSON yang ramah klien:\n"
                  "// Decimal -> angka biasa, tanggal -> teks YYYY-MM-DD.\n"
                  "function mapRow(row) {\n  if (!row) return row;\n  return {\n    ...row,\n%s\n  };\n}\n\n") % "\n".join(maps)
        wrap = lambda x: "mapRow(%s)" % x
        many = "  return rows.map(mapRow);\n"
    else:
        mapper = ""
        wrap = lambda x: x
        many = "  return rows;\n"
    return f"""const prisma = require('../db');

// Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
const kolom = {{
{chr(10).join('  %s: true,' % c for c in cols)}
}};

{mapper}// Selalu dibatasi user_id, supaya pengguna hanya melihat datanya sendiri.
function buildWhere(userId, q) {{
  const where = {{ user_id: userId }};
  if (q) where.{p['cari']} = {{ contains: q, mode: 'insensitive' }};
  return where;
}}

async function create(data) {{
  return {wrap(f'await prisma.{acc}.create({{ data, select: kolom }})')};
}}

async function findAllByUser(userId, q, limit, offset) {{
  const rows = await prisma.{acc}.findMany({{
    where: buildWhere(userId, q),
    orderBy: {{ id: 'desc' }},
    take: limit,
    skip: offset,
    select: kolom,
  }});
{many}}}

async function countByUser(userId, q) {{
  return prisma.{acc}.count({{ where: buildWhere(userId, q) }});
}}

async function findById(id) {{
  return {wrap(f'await prisma.{acc}.findUnique({{ where: {{ id }}, select: kolom }})')};
}}

async function update(id, data) {{
  return {wrap(f'await prisma.{acc}.update({{ where: {{ id }}, data, select: kolom }})')};
}}

async function remove(id) {{
  await prisma.{acc}.delete({{ where: {{ id }} }});
}}

module.exports = {{ create, findAllByUser, countByUser, findById, update, remove }};
"""


def rules(p):
    lines = []
    for name, kind, required, _, extra in p["kolom"]:
        parts = ["tipe: " + js(kind), "wajib: " + js(required)]
        for k in ("min", "max"):
            if k in extra and not (kind == "pilihan" and k == "max"):
                parts.append("%s: %s" % (k, js(extra[k])))
        if "opsi" in extra:
            parts.append("opsi: " + js(extra["opsi"]))
        lines.append("  %s: { %s }," % (name, ", ".join(parts)))
    return "\n".join(lines)


def service(p):
    acc = camel(p["model"])
    return f"""const {acc}Repository = require('../repositories/{acc}Repository');
const {{ normalizePagination }} = require('../utils/pagination');
const {{ validate }} = require('../utils/validate');
const {{ NotFoundError, ForbiddenError }} = require('../errors');

// Aturan tiap kolom. Samakan dengan schema.prisma.
const aturan = {{
{rules(p)}
}};

async function list(userId, q, rawPage, rawLimit) {{
  const {{ page, limit }} = normalizePagination(rawPage, rawLimit);
  const offset = (page - 1) * limit;

  const data = await {acc}Repository.findAllByUser(userId, q, limit, offset);
  const total = await {acc}Repository.countByUser(userId, q);
  return {{ data, total, page, limit }};
}}

// authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
async function authorizeOwner(userId, id) {{
  const data = await {acc}Repository.findById(id);
  if (!data) throw new NotFoundError('data tidak ditemukan');
  if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
  return data;
}}

async function create(userId, body) {{
  const data = validate(body, aturan);
  // user_id diambil dari token, bukan dari isian klien
  return {acc}Repository.create({{ ...data, user_id: userId }});
}}

async function update(userId, id, body) {{
  await authorizeOwner(userId, id);
  return {acc}Repository.update(id, validate(body, aturan));
}}

async function remove(userId, id) {{
  await authorizeOwner(userId, id);
  await {acc}Repository.remove(id);
}}

module.exports = {{ list, detail: authorizeOwner, create, update, remove }};
"""


def handler(p):
    acc = camel(p["model"])
    def fn(name, body):
        return f"""async function {name}(req, res, next) {{
  try {{
{body}
  }} catch (err) {{
    next(err);
  }}
}}
"""
    parts = [
        fn("list", f"""    const q = typeof req.query.q === 'string' ? req.query.q : '';
    const {{ data, total, page, limit }} = await {acc}Service.list(req.userId, q, req.query.page, req.query.limit);
    paginated(res, 200, data, page, limit, total);"""),
        fn("detail", f"""    ok(res, 200, await {acc}Service.detail(req.userId, parseId(req.params.id)));"""),
        fn("create", f"""    ok(res, 201, await {acc}Service.create(req.userId, req.body));"""),
        fn("update", f"""    ok(res, 200, await {acc}Service.update(req.userId, parseId(req.params.id), req.body));"""),
        fn("remove", f"""    await {acc}Service.remove(req.userId, parseId(req.params.id));
    ok(res, 200, {{ message: 'data berhasil dihapus' }});"""),
    ]
    return (f"""const {acc}Service = require('../services/{acc}Service');
const {{ ok, paginated }} = require('../utils/response');
const {{ parseId }} = require('../utils/validate');

""" + "\n".join(parts) + "\nmodule.exports = { list, detail, create, update, remove };\n")


def app_js(p):
    app = foundation_files()["src/app.js"]
    acc, path = camel(p["model"]), p["path"]
    app = sub(app, "const authHandler = require('./handlers/authHandler');\n",
              "const authHandler = require('./handlers/authHandler');\nconst %sHandler = require('./handlers/%sHandler');\n" % (acc, acc))
    routes = PENANDA_ROUTE + "".join(
        "app.%s('/api/%s%s', requireAuth, %sHandler.%s);\n" % (m, path, s, acc, f)
        for m, s, f in [("get", "", "list"), ("get", "/:id", "detail"), ("post", "", "create"),
                        ("put", "/:id", "update"), ("delete", "/:id", "remove")])
    return sub(app, PENANDA_ROUTE, routes)


def openapi_prop(kind, example, extra):
    t = {"teks": "string", "pilihan": "string", "bulat": "integer", "angka": "number",
         "boolean": "boolean", "tanggal": "string"}[kind]
    parts = ["type: " + js(t)]
    if kind == "tanggal":
        parts.append("format: 'date'")
    if kind == "pilihan":
        parts.append("enum: " + js(extra["opsi"]))
    if kind == "teks" and "max" in extra:
        parts.append("maxLength: %d" % extra["max"])
    parts.append("example: " + js(example))
    return "{ %s }" % ", ".join(parts)


def docs_js(p):
    props = "\n".join("    %s: %s," % (n, openapi_prop(k, ex, x)) for n, k, _, ex, x in p["kolom"])
    required = js([n for n, _, w, _, _ in p["kolom"] if w])
    return f"""const crudDocs = require('./crud');

module.exports = crudDocs({{
  tag: {js(p['judul'])},
  path: {js(p['path'])},
  properties: {{
{props}
  }},
  required: {required},
}});
"""


def swagger_append(p):
    acc = camel(p["model"])
    return f"""// --- modul {p['path']} ---
const {acc} = require('./{acc}');
module.exports.tags.push({acc}.tag);
Object.assign(module.exports.paths, {acc}.paths);
"""


def project_files(p):
    acc = camel(p["model"])
    return [
        ("prisma/schema.prisma", schema_prisma(p)),
        (f"src/repositories/{acc}Repository.js", repository(p)),
        (f"src/services/{acc}Service.js", service(p)),
        (f"src/handlers/{acc}Handler.js", handler(p)),
        ("src/app.js", app_js(p)),
        (f"src/docs/{acc}.js", docs_js(p)),
    ]


def example_body(p):
    return {n: ex for n, _, _, ex, _ in p["kolom"]}
