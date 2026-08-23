# Laporan Proyek Pengembangan Sistem Penyimpanan Data Skalabel

## 1. Latar Belakang
Pertumbuhan data dan perubahan beban kerja membutuhkan sistem penyimpanan yang dapat diperbesar tanpa mengubah seluruh aplikasi. Proyek ini membangun prototipe key-value storage untuk mensimulasikan kebutuhan tersebut.

## 2. Tujuan
- Membangun arsitektur penyimpanan berbasis shard.
- Menyediakan replica untuk meningkatkan ketersediaan data.
- Mengadaptasikan penyimpanan berdasarkan frekuensi akses.
- Mengevaluasi distribusi data dan konsistensi replica.

## 3. Desain Solusi
Routing key menggunakan SHA-256 agar pembagian data stabil. Primary shard ditentukan dari hash, kemudian data ditulis ke beberapa shard berurutan sesuai replication factor. Saat dibaca, sistem memeriksa cache lebih dahulu lalu primary dan replica.

Data panas dipromosikan ke cache setelah mencapai batas akses tertentu. Penyimpanan file dilakukan melalui temporary file dan operasi replace sehingga file shard tidak ditinggalkan dalam kondisi setengah tertulis.

## 4. Implementasi
Komponen utama berada pada `scalable_storage.py`:

- `put(key, value)`: menulis data ke primary dan replica.
- `get(key)`: membaca cache, primary, atau replica.
- `distribution()`: mengukur jumlah data pada setiap shard.
- `replica_consistent(key)`: memeriksa kesamaan data antar replica.

## 5. Skenario Pengujian
Jalankan:

```powershell
python scalable_storage.py --demo --load 1000 --shards 4 --replicas 2
```

Indikator yang diamati:

- jumlah record yang diproses;
- waktu pembacaan;
- cache hit setelah data sering diakses;
- distribusi record per shard;
- status konsistensi replica.

Hasil waktu dapat berbeda bergantung pada perangkat dan kondisi sistem. Keberhasilan ditunjukkan ketika program menampilkan `replica_consistent_order-0=True` dan data tersebar pada shard.

## 6. Pemetaan Materi
| Materi | Implementasi |
|---|---|
| Arsitektur skala industri | Sharding dan routing berbasis hash. |
| NoSQL dan polyglot persistence | Model key-value dan jalur pengembangan Redis/NoSQL. |
| Replikasi dan partisi | Primary shard dan replica shard. |
| Optimasi adaptif | Hot cache berdasarkan access threshold. |
| Project based learning | Prototipe dapat dijalankan dan diuji dengan berbagai beban. |

## 7. Analisis dan Pengembangan
Penambahan shard dapat meningkatkan kapasitas penyimpanan dan paralelisme, tetapi membutuhkan strategi rebalancing. Replica meningkatkan ketersediaan, tetapi menambah biaya tulis. Cache menurunkan latency baca untuk data panas dengan konsekuensi kebutuhan invalidasi cache.

Prototipe ini masih berjalan pada satu node dan file JSON. Untuk penggunaan industri, storage dapat diganti dengan MongoDB/Cassandra, cache dengan Redis, komunikasi antar-node dengan message broker, serta ditambahkan monitoring, autentikasi, backup, dan pengujian beban terdistribusi.

## 8. Kesimpulan
Proyek berhasil membangun solusi penyimpanan data yang memperagakan partisi, replikasi, dan adaptasi berdasarkan pola akses. Solusi ini memenuhi tujuan Sub-CPMK-3.2 pada level C4 sebagai dasar pengembangan sistem penyimpanan yang scalable dan adaptif.
