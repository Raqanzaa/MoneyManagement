# Langkah 1: Gunakan base image Python yang resmi dan ringan
FROM python:3.10-slim

# Langkah 2: Atur direktori kerja di dalam container
WORKDIR /app

# Langkah 3: Salin file requirements.txt terlebih dahulu
COPY requirements.txt .

# Langkah 4: Install semua library yang dibutuhkan
# --no-cache-dir digunakan agar image lebih kecil
RUN pip install --no-cache-dir -r requirements.txt

# Langkah 5: Salin semua sisa kode aplikasi ke dalam container
COPY . .

# Langkah 6: Perintah yang akan dijalankan saat container dimulai
# --host=0.0.0.0 membuat aplikasi bisa diakses dari luar container
CMD ["flask", "run", "--host=0.0.0.0"]