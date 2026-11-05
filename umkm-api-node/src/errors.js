class AppError extends Error {
  constructor(message, code, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

class InvalidInputError extends AppError {
  constructor(message = 'input tidak valid') {
    super(message, 'BAD_REQUEST', 400);
  }
}

class NotFoundError extends AppError {
  constructor(message = 'data tidak ditemukan') {
    super(message, 'NOT_FOUND', 404);
  }
}

class ConflictError extends AppError {
  constructor(message = 'data sudah ada') {
    super(message, 'CONFLICT', 409);
  }
}

class ForbiddenError extends AppError {
  constructor(message = 'tidak memiliki akses') {
    super(message, 'FORBIDDEN', 403);
  }
}

module.exports = {
  AppError,
  InvalidInputError,
  NotFoundError,
  ConflictError,
  ForbiddenError,
};
