// crudDocs membuat dokumentasi Swagger untuk 5 endpoint CRUD sekaligus.
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
