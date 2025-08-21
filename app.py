import csv
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- Konfigurasi dan Fungsi Helper untuk CSV ---

# Nama file untuk menyimpan data
CSV_FILE = '/var/data/transactions.csv'
# Nama kolom untuk file CSV kita
FIELDNAMES = ['id', 'deskripsi', 'jumlah', 'jenis']
nama_user = "Budi"

def read_transactions():
    """Membaca semua transaksi dari file CSV."""
    try:
        with open(CSV_FILE, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            transactions = []
            for row in reader:
                # Konversi tipe data yang sesuai
                row['id'] = int(row['id'])
                row['jumlah'] = int(row['jumlah'])
                transactions.append(row)
            return transactions
    except FileNotFoundError:
        # Jika file tidak ditemukan, kembalikan list kosong
        return []

def write_transaction(new_transaction):
    """Menulis satu transaksi baru ke file CSV."""
    # Gunakan mode 'a' (append) untuk menambahkan data di akhir file
    with open(CSV_FILE, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        
        # Cek apakah file kosong. Jika ya, tulis header dulu.
        csvfile.seek(0, 2) # Pindah ke akhir file
        if csvfile.tell() == 0:
            writer.writeheader()
            
        writer.writerow(new_transaction)

# --- Akhir Fungsi Helper ---


# Muat data dari CSV saat aplikasi pertama kali dijalankan
riwayat_transaksi = read_transactions()


@app.route('/')
def home():
    # Hitung saldo saat ini
    total_pemasukan = sum(t['jumlah'] for t in riwayat_transaksi if t['jenis'] == 'pemasukan')
    total_pengeluaran = sum(t['jumlah'] for t in riwayat_transaksi if t['jenis'] == 'pengeluaran')
    saldo = total_pemasukan - total_pengeluaran
    
    return render_template(
        'index.html',
        user_name=nama_user,
        transactions=riwayat_transaksi,
        saldo=saldo # Kirim saldo ke template
    )

@app.route('/tambah', methods=['POST'])
def tambah_transaksi():
    deskripsi = request.form['deskripsi']
    jumlah = int(request.form['jumlah'])
    jenis = request.form['jenis']
    
    # Dapatkan ID terakhir dan tambahkan 1
    if riwayat_transaksi:
        id_baru = riwayat_transaksi[-1]['id'] + 1
    else:
        id_baru = 1
        
    transaksi_baru = {
        'id': id_baru,
        'deskripsi': deskripsi,
        'jumlah': jumlah,
        'jenis': jenis
    }
    
    # Simpan ke file CSV
    write_transaction(transaksi_baru)
    
    # Tambahkan ke list di memori juga agar tampilan langsung update
    riwayat_transaksi.append(transaksi_baru)
    
    return redirect(url_for('home'))