# Implementasi Solusi Basis Data untuk Aplikasi Real-Time

Laporan capstone pertemuan ke-14 mata kuliah Sistem Basis Data Modern.

## 1. Studi Kasus
Sistem ini mensimulasikan monitor event untuk aplikasi real-time. Contohnya adalah notifikasi order baru, perubahan status layanan, atau aktivitas pengguna yang harus diterima oleh beberapa client dengan cepat.

## 2. Analisis Kebutuhan

### Kebutuhan fungsional
- Client dapat mengirim event baru.
- Event disimpan secara persisten ke database.
- Client dapat membaca 50 event terbaru.
- Semua client aktif menerima event baru tanpa memuat ulang halaman.

### Kebutuhan nonfungsional
- Respons API cepat untuk operasi sederhana.
- Data tetap konsisten dan tidak hilang saat halaman dimuat ulang.
- Sistem dapat melayani beberapa koneksi browser secara bersamaan.

## 3. Pemilihan Teknologi
SQLite dipilih sebagai penyimpanan persisten karena ringan, mendukung transaksi, dan tidak memerlukan server database terpisah. SQLite WAL digunakan agar proses baca dan tulis memiliki konkurensi yang lebih baik.

Server-Sent Events (SSE) dipilih untuk komunikasi satu arah dari server ke browser. Pendekatan ini sesuai untuk notifikasi dan monitor event karena implementasinya sederhana serta browser menyediakan API `EventSource`.

## 4.1 Pemetaan Materi Pertemuan ke-14

| Topik materi | Implementasi dalam project |
|---|---|
| Analisis kebutuhan real-time | Kebutuhan fungsional dan nonfungsional dirumuskan untuk monitor event. |
| NoSQL dan In-Memory Database | Redis disediakan pada `benchmark.py` sebagai pembanding in-memory. |
| Integrasi dan sinkronisasi data | SSE mengirim event baru ke seluruh client aktif. |
| Caching, indexing, dan pemodelan data | Index SQLite, WAL, pembatasan data, dan model tabel event diterapkan. |
| Polyglot persistence | SQLite digunakan untuk data persisten dan Redis disiapkan sebagai opsi in-memory/cache. |

Implementasi utama menggunakan SQLite dan SSE agar dapat dijalankan tanpa server tambahan. Redis merupakan komponen opsional yang dapat diaktifkan untuk eksperimen in-memory dan pengembangan skala lebih besar.

## 4. Alur Implementasi
1. Browser mengirim `POST /api/events`.
2. Server memvalidasi `title` dan `detail`.
3. Server menyimpan event ke SQLite menggunakan parameterized query.
4. Server mengirim event ke seluruh koneksi SSE aktif.
5. Browser menampilkan event baru secara langsung.

## 5. Hasil Pengujian Fungsional
Pengujian lokal berhasil dilakukan dengan hasil:

- `GET /` mengembalikan HTTP 200.
- `POST /api/events` mengembalikan HTTP 201.
- Event tersimpan dan dapat dibaca kembali melalui `GET /api/events`.
- Browser menerima event melalui endpoint `/api/stream`.

## 6. Hasil Benchmark SQLite
Pengujian dilakukan dengan 1.000 record pada komputer pengembang. Angka dapat berubah sesuai spesifikasi perangkat.

| Operasi | Rata-rata latency |
|---|---:|
| Insert | 0,0069 ms |
| Read | 0,1515 ms |
| Update | 0,0500 ms |
| Delete | 0,0290 ms |

Benchmark menjalankan operasi CRUD dan menggunakan index pada kolom `city`. Redis disediakan sebagai opsi pembanding pada `benchmark.py`, tetapi hasil Redis harus diambil ketika Redis Server aktif.

## 7. Bottleneck dan Optimasi
Potensi bottleneck utama adalah jumlah koneksi SSE aktif, penulisan database secara bersamaan, dan ukuran event yang terlalu besar. Optimasi yang diterapkan adalah:

- SQLite WAL untuk memperbaiki akses baca/tulis bersamaan.
- Index untuk membantu pencarian data.
- Batas 50 event pada endpoint daftar.
- Validasi dan pembatasan panjang input.
- Penghapusan koneksi SSE yang sudah terputus.

## 8. Kesimpulan
Implementasi ini menunjukkan penerapan solusi basis data untuk aplikasi real-time pada level prototipe. SQLite menangani penyimpanan konsisten, sedangkan SSE menyebarkan perubahan secara langsung ke client. Untuk skala industri yang lebih besar, sistem dapat dikembangkan dengan Redis Pub/Sub, PostgreSQL, autentikasi, reverse proxy, dan pengujian beban multi-client.
