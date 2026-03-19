# Bagian 5: Problem Solving

## Soal 7: Integrasi Sistem & Penanganan Kegagalan

**Kasus:**
> Sistem A (internal) mengirim data user ke Sistem B (external API), tapi sering gagal karena timeout.

### 1. Bagaimana cara menangani retry?
Untuk menangani kegagalan sementara (*transient failures*) seperti timeout, disarankan menggunakan strategi **Exponential Backoff**.
- **Mekanisme**: Sistem akan mencoba mengirim ulang data setelah kegagalan, namun dengan jeda waktu yang meningkat secara bertahap (misalnya: 4 detik, 8 detik, hingga batas maksimal tertentu).
- **Tujuan**: Memberikan waktu bagi Sistem B untuk pulih dan menghindari penumpukan request (*request flooding*) yang justru dapat memperburuk kondisi server tujuan.
- **Implementasi**: Strategi ini telah diterapkan dalam backend menggunakan library `tenacity` pada fungsi sinkronisasi data eksternal.

### 2. Bagaimana memastikan data tidak duplicate?
Untuk mencegah duplikasi data (*double-entry*) akibat proses pengiriman ulang (retry), dapat diterapkan mekanisme berikut:
- **Idempotency Key**: Sistem A menyertakan ID unik untuk setiap transaksi. Sistem B akan memverifikasi ID tersebut sebelum memproses data; jika ID sudah pernah diproses, Sistem B hanya akan mengembalikan response sukses tanpa menduplikasi data.
- **Database Unique Constraint**: Menerapkan batasan unik (*Unique Constraint*) pada kolom tertentu di database (seperti `email` atau `external_id`) untuk memastikan integritas data di level penyimpanan.

### 3. Tools apa yang bisa digunakan untuk monitoring?
Beberapa alat bantu untuk memantau dan mengaudit kesehatan integrasi sistem meliputi:
- **Sentry**: Fokus pada *Error Tracking* secara real-time. Memberikan notifikasi instan dan detail *stack trace* saat terjadi exception di backend.
- **Prometheus & Grafana**: Digunakan untuk pengumpulan dan visualisasi metrik performa seperti *latency* API, jumlah request sukses/gagal, dan penggunaan resource server.
- **ELK Stack (Elasticsearch, Logstash, Kibana)**: Solusi untuk manajemen log terpusat, memudahkan investigasi jika terjadi masalah yang memerlukan penelusuran histori data.
