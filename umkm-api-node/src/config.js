require('dotenv').config();

function getOrDefault(key, def) {
  const v = process.env[key];
  return v && v !== '' ? v : def;
}

module.exports = {
  jwtSecret: process.env.JWT_SECRET,
  port: getOrDefault('PORT', '8080'),
  uploadDir: getOrDefault('UPLOAD_DIR', './uploads'),
};
