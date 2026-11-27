const prisma = require('../db');

const userSelect = { id: true, nama: true, email: true, password: true };

async function create(user) {
  return prisma.user.create({
    data: { nama: user.nama, email: user.email, password: user.password },
    select: userSelect,
  });
}

async function findByEmail(email) {
  return prisma.user.findUnique({ where: { email }, select: userSelect });
}

async function findById(id) {
  return prisma.user.findUnique({ where: { id }, select: userSelect });
}

async function updateProfile(id, nama, email) {
  await prisma.user.update({ where: { id }, data: { nama, email } });
}

async function updatePassword(id, hashedPassword) {
  await prisma.user.update({ where: { id }, data: { password: hashedPassword } });
}

module.exports = { create, findByEmail, findById, updateProfile, updatePassword };
