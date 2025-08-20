# 1. Impor modul-modul yang diperlukan
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 2. Pindahkan data ke luar fungsi agar menjadi "database" sementara kita
nama_user = "Budi"
riwayat_transaksi = [
    {'id': 1, 'deskripsi': 'Gaji Awal', 'jumlah': 5000000, 'jenis': 'pemasukan'}
]

@app.route('/')
def home():
    # Tampilkan halaman utama dengan data terbaru
    return render_template('index.html', user_name=nama_user, transactions=riwayat_transaksi)

# 3. Buat route baru untuk menangani penambahan transaksi
@app.route('/tambah', methods=['POST'])
def tambah_transaksi():
    # Ambil data dari formulir yang dikirim
    deskripsi = request.form['deskripsi']
    jumlah = int(request.form['jumlah']) # Konversi jumlah ke integer
    jenis = request.form['jenis']
    
    # Tentukan ID baru untuk transaksi
    id_baru = len(riwayat_transaksi) + 1
    
    # Buat dictionary untuk transaksi baru
    transaksi_baru = {
        'id': id_baru,
        'deskripsi': deskripsi,
        'jumlah': jumlah,
        'jenis': jenis
    }
    
    # Tambahkan transaksi baru ke "database" kita
    riwayat_transaksi.append(transaksi_baru)
    
    # Arahkan kembali pengguna ke halaman utama
    return redirect(url_for('home'))