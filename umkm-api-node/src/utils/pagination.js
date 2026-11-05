const DEFAULT_LIMIT = 10;
const MAX_LIMIT = 100;

// normalizePagination memastikan page minimal 1 dan limit berada pada rentang wajar.
// Dipanggil dengan nilai mentah dari query string (bertipe string atau undefined).
function normalizePagination(rawPage, rawLimit) {
  let page = parseInt(rawPage, 10);
  let limit = parseInt(rawLimit, 10);

  if (!Number.isInteger(page) || page < 1) page = 1;
  if (!Number.isInteger(limit) || limit <= 0) limit = DEFAULT_LIMIT;
  if (limit > MAX_LIMIT) limit = MAX_LIMIT;

  return { page, limit };
}

module.exports = { normalizePagination };
