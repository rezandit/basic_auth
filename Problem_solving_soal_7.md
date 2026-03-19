Sistem A (internal) mengirim data user ke Sistem B (external API), tapi sering gagal karena timeout.
Pertanyaan:
1.	Bagaimana cara menangani retry?
•	Gunakan strategi Exponential Backoff untuk memberikan jeda waktu yang meningkat secara bertahap sebelum mencoba mengirim ulang data

2.	Bagaimana memastikan data tidak duplicate?
•	Implementasi unique ID 

3.	Tools apa yang bisa digunakan untuk monitoring?
•	Sentry untuk pelacakan error secara real-time atau Prometheus untuk memantau performa dan latency 
