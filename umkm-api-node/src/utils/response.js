function ok(res, status, data) {
  res.status(status).json({ data });
}

function paginated(res, status, data, page, limit, total) {
  res.status(status).json({ data, meta: { page, limit, total } });
}

module.exports = { ok, paginated };
