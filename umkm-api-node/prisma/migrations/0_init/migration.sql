-- CreateTable
CREATE TABLE "users" (
    "id" SERIAL NOT NULL,
    "nama" VARCHAR(100) NOT NULL,
    "email" VARCHAR(150) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "umkm" (
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "nama" VARCHAR(150) NOT NULL,
    "deskripsi" TEXT,
    "alamat" VARCHAR(255),
    "foto" VARCHAR(255),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "umkm_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "produk" (
    "id" SERIAL NOT NULL,
    "umkm_id" INTEGER NOT NULL,
    "nama" VARCHAR(150) NOT NULL,
    "harga" DECIMAL(12,2) NOT NULL DEFAULT 0,
    "deskripsi" TEXT,
    "foto" VARCHAR(255),
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "produk_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "umkm_user_id_key" ON "umkm"("user_id");

-- CreateIndex
CREATE INDEX "produk_umkm_id_idx" ON "produk"("umkm_id");

-- AddForeignKey
ALTER TABLE "umkm" ADD CONSTRAINT "umkm_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "produk" ADD CONSTRAINT "produk_umkm_id_fkey" FOREIGN KEY ("umkm_id") REFERENCES "umkm"("id") ON DELETE CASCADE ON UPDATE CASCADE;

