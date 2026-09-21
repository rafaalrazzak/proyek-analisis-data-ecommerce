# Olist E-Commerce Dashboard ✨

Analisis data E-Commerce Public Dataset (Olist Brazil) - submission proyek akhir Dicoding "Belajar Analisis Data dengan Python".

Notebook-nya jawab 4 pertanyaan bisnis: tren order & revenue bulanan, kategori produk paling/paling gak laku, sebaran pelanggan per negara bagian, dan segmentasi pelanggan pakai RFM. Dashboard Streamlit buat eksplorasi hasilnya secara interaktif.

Live demo: lihat `url.txt`

## Struktur Direktori

```
data/            9 csv mentah dari Olist
dashboard/       dashboard.py + data yang sudah diringkas untuk dashboard
notebook.ipynb   seluruh proses analisis, sudah dijalankan (output tersimpan)
```

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

Dashboard baca file csv relatif ke lokasi `dashboard.py`, jadi bisa dijalankan dari mana saja - tapi paling gampang dari dalam folder `dashboard/`:

```
cd dashboard
streamlit run dashboard.py
```

## Catatan teknis

Dataset ini punya dua id yang gampang ketuker: `customer_id` unik per **order**, sedangkan `customer_unique_id` unik per **orang**. Kalau RFM dihitung pakai `customer_id`, Frequency-nya bakal selalu 1 buat semua orang - gak kepake. Notebook dan dashboard di sini pakai `customer_unique_id` supaya angkanya benar.
