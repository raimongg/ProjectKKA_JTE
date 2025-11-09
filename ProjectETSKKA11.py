import streamlit as st
import pandas as pd
import random
import heapq
from itertools import combinations
import altair as alt
import matplotlib.pyplot as plt

# Konfigurasi halaman
st.set_page_config(
    page_title="Optimasi Rute Pengiriman",
    page_icon="🚚",
    layout="wide"
)

# Data kota dan jarak
# Data kota - diperluas menjadi 52 kota
cities = [
    'Jakarta', 'Tangerang', 'Bogor', 'Bandung', 'Cianjur', 'Serang', 'Cirebon', 
    'Purwakarta', 'Tasikmalaya', 'Purwokerto', 'Tegal', 'Pekalongan', 'Semarang', 
    'Kendal', 'Purbalingga', 'Temanggung', 'Wonosobo', 'Banjarnegara', 'Banyumas',
    'Magelang', 'Boyolali', 'Salatiga', 'Solo', 'Klaten', 'Sragen', 'Yogyakarta',
    'Demak', 'Kudus', 'Jepara', 'Pati', 'Ngawi', 'Madiun', 'Surabaya', 'Kediri',
    'Jombang', 'Mojokerto', 'Sidoarjo', 'Gresik', 'Lamongan', 'Tuban', 'Malang',
    'Tulungagung', 'Trenggalek', 'Pacitan', 'Blitar', 'Batu', 'Probolinggo',
    'Lumajang', 'Jember', 'Situbondo', 'Bondowoso', 'Banyuwangi'
]

# Matriks jarak yang diperluas (dalam km, estimasi jarak antar kota)
distance_matrix = {
    # ... (Matriks Jarak Anda - tidak perlu diubah, biarkan seperti aslinya) ...
    'Jakarta': {'Jakarta': 0, 'Tangerang': 25, 'Bogor': 60, 'Bandung': 150, 'Cianjur': 120, 'Serang': 90, 'Cirebon': 245, 'Purwakarta': 100, 'Tasikmalaya': 270, 'Purwokerto': 395, 'Tegal': 310, 'Pekalongan': 360, 'Semarang': 445, 'Kendal': 420, 'Purbalingga': 380, 'Temanggung': 450, 'Wonosobo': 440, 'Banjarnegara': 400, 'Banyumas': 390, 'Magelang': 475, 'Boyolali': 530, 'Salatiga': 490, 'Solo': 550, 'Klaten': 535, 'Sragen': 570, 'Yogyakarta': 560, 'Demak': 465, 'Kudus': 480, 'Jepara': 510, 'Pati': 500, 'Ngawi': 600, 'Madiun': 650, 'Surabaya': 785, 'Kediri': 710, 'Jombang': 730, 'Mojokerto': 750, 'Sidoarjo': 770, 'Gresik': 800, 'Lamongan': 720, 'Tuban': 680, 'Malang': 850, 'Tulungagung': 690, 'Trenggalek': 720, 'Pacitan': 740, 'Blitar': 700, 'Batu': 830, 'Probolinggo': 900, 'Lumajang': 920, 'Jember': 970, 'Situbondo': 1020, 'Bondowoso': 1000, 'Banyuwangi': 1080},
    'Tangerang': {'Jakarta': 25, 'Tangerang': 0, 'Bogor': 70, 'Bandung': 160, 'Cianjur': 140, 'Serang': 70, 'Cirebon': 260, 'Purwakarta': 120, 'Tasikmalaya': 285, 'Purwokerto': 410, 'Tegal': 325, 'Pekalongan': 375, 'Semarang': 460, 'Kendal': 435, 'Purbalingga': 395, 'Temanggung': 465, 'Wonosobo': 455, 'Banjarnegara': 415, 'Banyumas': 405, 'Magelang': 490, 'Boyolali': 545, 'Salatiga': 505, 'Solo': 565, 'Klaten': 550, 'Sragen': 585, 'Yogyakarta': 575, 'Demak': 480, 'Kudus': 495, 'Jepara': 525, 'Pati': 515, 'Ngawi': 615, 'Madiun': 665, 'Surabaya': 800, 'Kediri': 725, 'Jombang': 745, 'Mojokerto': 765, 'Sidoarjo': 785, 'Gresik': 815, 'Lamongan': 735, 'Tuban': 695, 'Malang': 865, 'Tulungagung': 705, 'Trenggalek': 735, 'Pacitan': 755, 'Blitar': 715, 'Batu': 845, 'Probolinggo': 915, 'Lumajang': 935, 'Jember': 985, 'Situbondo': 1035, 'Bondowoso': 1015, 'Banyuwangi': 1095},
    'Bogor': {'Jakarta': 60, 'Tangerang': 70, 'Bogor': 0, 'Bandung': 130, 'Cianjur': 80, 'Serang': 120, 'Cirebon': 270, 'Purwakarta': 110, 'Tasikmalaya': 240, 'Purwokerto': 420, 'Tegal': 340, 'Pekalongan': 390, 'Semarang': 475, 'Kendal': 450, 'Purbalingga': 410, 'Temanggung': 480, 'Wonosobo': 470, 'Banjarnegara': 430, 'Banyumas': 420, 'Magelang': 505, 'Boyolali': 560, 'Salatiga': 520, 'Solo': 580, 'Klaten': 565, 'Sragen': 600, 'Yogyakarta': 590, 'Demak': 495, 'Kudus': 510, 'Jepara': 540, 'Pati': 530, 'Ngawi': 630, 'Madiun': 680, 'Surabaya': 815, 'Kediri': 740, 'Jombang': 760, 'Mojokerto': 780, 'Sidoarjo': 800, 'Gresik': 830, 'Lamongan': 750, 'Tuban': 710, 'Malang': 880, 'Tulungagung': 720, 'Trenggalek': 750, 'Pacitan': 770, 'Blitar': 730, 'Batu': 860, 'Probolinggo': 930, 'Lumajang': 950, 'Jember': 1000, 'Situbondo': 1050, 'Bondowoso': 1030, 'Banyuwangi': 1110},
    'Bandung': {'Jakarta': 150, 'Tangerang': 160, 'Bogor': 130, 'Bandung': 0, 'Cianjur': 60, 'Serang': 200, 'Cirebon': 150, 'Purwakarta': 65, 'Tasikmalaya': 120, 'Purwokerto': 340, 'Tegal': 260, 'Pekalongan': 310, 'Semarang': 420, 'Kendal': 395, 'Purbalingga': 325, 'Temanggung': 425, 'Wonosobo': 390, 'Banjarnegara': 350, 'Banyumas': 335, 'Magelang': 450, 'Boyolali': 505, 'Salatiga': 465, 'Solo': 520, 'Klaten': 505, 'Sragen': 540, 'Yogyakarta': 470, 'Demak': 440, 'Kudus': 455, 'Jepara': 485, 'Pati': 475, 'Ngawi': 570, 'Madiun': 620, 'Surabaya': 740, 'Kediri': 665, 'Jombang': 685, 'Mojokerto': 705, 'Sidoarjo': 725, 'Gresik': 755, 'Lamongan': 675, 'Tuban': 635, 'Malang': 800, 'Tulungagung': 645, 'Trenggalek': 675, 'Pacitan': 695, 'Blitar': 655, 'Batu': 780, 'Probolinggo': 850, 'Lumajang': 870, 'Jember': 920, 'Situbondo': 970, 'Bondowoso': 950, 'Banyuwangi': 1030},
    'Cianjur': {'Jakarta': 120, 'Tangerang': 140, 'Bogor': 80, 'Bandung': 60, 'Cianjur': 0, 'Serang': 180, 'Cirebon': 200, 'Purwakarta': 100, 'Tasikmalaya': 150, 'Purwokerto': 380, 'Tegal': 300, 'Pekalongan': 350, 'Semarang': 460, 'Kendal': 435, 'Purbalingga': 365, 'Temanggung': 465, 'Wonosobo': 430, 'Banjarnegara': 390, 'Banyumas': 375, 'Magelang': 490, 'Boyolali': 545, 'Salatiga': 505, 'Solo': 560, 'Klaten': 545, 'Sragen': 580, 'Yogyakarta': 510, 'Demak': 480, 'Kudus': 495, 'Jepara': 525, 'Pati': 515, 'Ngawi': 610, 'Madiun': 660, 'Surabaya': 780, 'Kediri': 705, 'Jombang': 725, 'Mojokerto': 745, 'Sidoarjo': 765, 'Gresik': 795, 'Lamongan': 715, 'Tuban': 675, 'Malang': 840, 'Tulungagung': 685, 'Trenggalek': 715, 'Pacitan': 735, 'Blitar': 695, 'Batu': 820, 'Probolinggo': 890, 'Lumajang': 910, 'Jember': 960, 'Situbondo': 1010, 'Bondowoso': 990, 'Banyuwangi': 1070},
    'Serang': {'Jakarta': 90, 'Tangerang': 70, 'Bogor': 120, 'Bandung': 200, 'Cianjur': 180, 'Serang': 0, 'Cirebon': 310, 'Purwakarta': 170, 'Tasikmalaya': 330, 'Purwokerto': 460, 'Tegal': 375, 'Pekalongan': 425, 'Semarang': 510, 'Kendal': 485, 'Purbalingga': 445, 'Temanggung': 515, 'Wonosobo': 505, 'Banjarnegara': 465, 'Banyumas': 455, 'Magelang': 540, 'Boyolali': 595, 'Salatiga': 555, 'Solo': 615, 'Klaten': 600, 'Sragen': 635, 'Yogyakarta': 625, 'Demak': 530, 'Kudus': 545, 'Jepara': 575, 'Pati': 565, 'Ngawi': 665, 'Madiun': 715, 'Surabaya': 850, 'Kediri': 775, 'Jombang': 795, 'Mojokerto': 815, 'Sidoarjo': 835, 'Gresik': 865, 'Lamongan': 785, 'Tuban': 745, 'Malang': 915, 'Tulungagung': 755, 'Trenggalek': 785, 'Pacitan': 805, 'Blitar': 765, 'Batu': 895, 'Probolinggo': 965, 'Lumajang': 985, 'Jember': 1035, 'Situbondo': 1085, 'Bondowoso': 1065, 'Banyuwangi': 1145},
    'Cirebon': {'Jakarta': 245, 'Tangerang': 260, 'Bogor': 270, 'Bandung': 150, 'Cianjur': 200, 'Serang': 310, 'Cirebon': 0, 'Purwakarta': 100, 'Tasikmalaya': 190, 'Purwokerto': 180, 'Tegal': 100, 'Pekalongan': 150, 'Semarang': 235, 'Kendal': 210, 'Purbalingga': 165, 'Temanggung': 240, 'Wonosobo': 230, 'Banjarnegara': 190, 'Banyumas': 175, 'Magelang': 265, 'Boyolali': 320, 'Salatiga': 280, 'Solo': 335, 'Klaten': 320, 'Sragen': 355, 'Yogyakarta': 285, 'Demak': 255, 'Kudus': 270, 'Jepara': 300, 'Pati': 290, 'Ngawi': 385, 'Madiun': 435, 'Surabaya': 555, 'Kediri': 480, 'Jombang': 500, 'Mojokerto': 520, 'Sidoarjo': 540, 'Gresik': 570, 'Lamongan': 490, 'Tuban': 450, 'Malang': 615, 'Tulungagung': 460, 'Trenggalek': 490, 'Pacitan': 510, 'Blitar': 470, 'Batu': 595, 'Probolinggo': 665, 'Lumajang': 685, 'Jember': 735, 'Situbondo': 785, 'Bondowoso': 765, 'Banyuwangi': 845},
    'Purwakarta': {'Jakarta': 100, 'Tangerang': 120, 'Bogor': 110, 'Bandung': 65, 'Cianjur': 100, 'Serang': 170, 'Cirebon': 100, 'Purwakarta': 0, 'Tasikmalaya': 170, 'Purwokerto': 310, 'Tegal': 230, 'Pekalongan': 280, 'Semarang': 390, 'Kendal': 365, 'Purbalingga': 295, 'Temanggung': 395, 'Wonosobo': 360, 'Banjarnegara': 320, 'Banyumas': 305, 'Magelang': 420, 'Boyolali': 475, 'Salatiga': 435, 'Solo': 490, 'Klaten': 475, 'Sragen': 510, 'Yogyakarta': 440, 'Demak': 410, 'Kudus': 425, 'Jepara': 455, 'Pati': 445, 'Ngawi': 540, 'Madiun': 590, 'Surabaya': 710, 'Kediri': 635, 'Jombang': 655, 'Mojokerto': 675, 'Sidoarjo': 695, 'Gresik': 725, 'Lamongan': 645, 'Tuban': 605, 'Malang': 770, 'Tulungagung': 615, 'Trenggalek': 645, 'Pacitan': 665, 'Blitar': 625, 'Batu': 750, 'Probolinggo': 820, 'Lumajang': 840, 'Jember': 890, 'Situbondo': 940, 'Bondowoso': 920, 'Banyuwangi': 1000},
    'Tasikmalaya': {'Jakarta': 270, 'Tangerang': 285, 'Bogor': 240, 'Bandung': 120, 'Cianjur': 150, 'Serang': 330, 'Cirebon': 190, 'Purwakarta': 170, 'Tasikmalaya': 0, 'Purwokerto': 220, 'Tegal': 250, 'Pekalongan': 300, 'Semarang': 385, 'Kendal': 360, 'Purbalingga': 205, 'Temanggung': 390, 'Wonosobo': 280, 'Banjarnegara': 240, 'Banyumas': 215, 'Magelang': 415, 'Boyolali': 470, 'Salatiga': 430, 'Solo': 485, 'Klaten': 470, 'Sragen': 505, 'Yogyakarta': 350, 'Demak': 405, 'Kudus': 420, 'Jepara': 450, 'Pati': 440, 'Ngawi': 535, 'Madiun': 585, 'Surabaya': 705, 'Kediri': 630, 'Jombang': 650, 'Mojokerto': 670, 'Sidoarjo': 690, 'Gresik': 720, 'Lamongan': 640, 'Tuban': 600, 'Malang': 765, 'Tulungagung': 610, 'Trenggalek': 640, 'Pacitan': 660, 'Blitar': 620, 'Batu': 745, 'Probolinggo': 815, 'Lumajang': 835, 'Jember': 885, 'Situbondo': 935, 'Bondowoso': 915, 'Banyuwangi': 995},
    'Purwokerto': {'Jakarta': 395, 'Tangerang': 410, 'Bogor': 420, 'Bandung': 340, 'Cianjur': 380, 'Serang': 460, 'Cirebon': 180, 'Purwakarta': 310, 'Tasikmalaya': 220, 'Purwokerto': 0, 'Tegal': 95, 'Pekalongan': 145, 'Semarang': 230, 'Kendal': 205, 'Purbalingga': 25, 'Temanggung': 170, 'Wonosobo': 90, 'Banjarnegara': 50, 'Banyumas': 15, 'Magelang': 195, 'Boyolali': 250, 'Salatiga': 210, 'Solo': 265, 'Klaten': 250, 'Sragen': 285, 'Yogyakarta': 215, 'Demak': 250, 'Kudus': 265, 'Jepara': 295, 'Pati': 285, 'Ngawi': 315, 'Madiun': 365, 'Surabaya': 485, 'Kediri': 410, 'Jombang': 430, 'Mojokerto': 450, 'Sidoarjo': 470, 'Gresik': 500, 'Lamongan': 420, 'Tuban': 380, 'Malang': 545, 'Tulungagung': 390, 'Trenggalek': 420, 'Pacitan': 440, 'Blitar': 400, 'Batu': 525, 'Probolinggo': 595, 'Lumajang': 615, 'Jember': 665, 'Situbondo': 715, 'Bondowoso': 695, 'Banyuwangi': 775},
    'Tegal': {'Jakarta': 310, 'Tangerang': 325, 'Bogor': 340, 'Bandung': 260, 'Cianjur': 300, 'Serang': 375, 'Cirebon': 100, 'Purwakarta': 230, 'Tasikmalaya': 250, 'Purwokerto': 95, 'Tegal': 0, 'Pekalongan': 50, 'Semarang': 135, 'Kendal': 110, 'Purbalingga': 80, 'Temanggung': 160, 'Wonosobo': 135, 'Banjarnegara': 105, 'Banyumas': 90, 'Magelang': 170, 'Boyolali': 225, 'Salatiga': 185, 'Solo': 240, 'Klaten': 225, 'Sragen': 260, 'Yogyakarta': 190, 'Demak': 155, 'Kudus': 170, 'Jepara': 200, 'Pati': 190, 'Ngawi': 290, 'Madiun': 340, 'Surabaya': 460, 'Kediri': 385, 'Jombang': 405, 'Mojokerto': 425, 'Sidoarjo': 445, 'Gresik': 475, 'Lamongan': 395, 'Tuban': 355, 'Malang': 520, 'Tulungagung': 365, 'Trenggalek': 395, 'Pacitan': 415, 'Blitar': 375, 'Batu': 500, 'Probolinggo': 570, 'Lumajang': 590, 'Jember': 640, 'Situbondo': 690, 'Bondowoso': 670, 'Banyuwangi': 750},
    'Pekalongan': {'Jakarta': 360, 'Tangerang': 375, 'Bogor': 390, 'Bandung': 310, 'Cianjur': 350, 'Serang': 425, 'Cirebon': 150, 'Purwakarta': 280, 'Tasikmalaya': 300, 'Purwokerto': 145, 'Tegal': 50, 'Pekalongan': 0, 'Semarang': 85, 'Kendal': 60, 'Purbalingga': 130, 'Temanggung': 110, 'Wonosobo': 110, 'Banjarnegara': 135, 'Banyumas': 140, 'Magelang': 120, 'Boyolali': 175, 'Salatiga': 135, 'Solo': 190, 'Klaten': 175, 'Sragen': 210, 'Yogyakarta': 140, 'Demak': 105, 'Kudus': 120, 'Jepara': 150, 'Pati': 140, 'Ngawi': 240, 'Madiun': 290, 'Surabaya': 410, 'Kediri': 335, 'Jombang': 355, 'Mojokerto': 375, 'Sidoarjo': 395, 'Gresik': 425, 'Lamongan': 345, 'Tuban': 305, 'Malang': 470, 'Tulungagung': 315, 'Trenggalek': 345, 'Pacitan': 365, 'Blitar': 325, 'Batu': 450, 'Probolinggo': 520, 'Lumajang': 540, 'Jember': 590, 'Situbondo': 640, 'Bondowoso': 620, 'Banyuwangi': 700},
    'Semarang': {'Jakarta': 445, 'Tangerang': 460, 'Bogor': 475, 'Bandung': 420, 'Cianjur': 460, 'Serang': 510, 'Cirebon': 235, 'Purwakarta': 390, 'Tasikmalaya': 385, 'Purwokerto': 230, 'Tegal': 135, 'Pekalongan': 85, 'Semarang': 0, 'Kendal': 25, 'Purbalingga': 215, 'Temanggung': 50, 'Wonosobo': 85, 'Banjarnegara': 180, 'Banyumas': 225, 'Magelang': 75, 'Boyolali': 90, 'Salatiga': 50, 'Solo': 100, 'Klaten': 90, 'Sragen': 125, 'Yogyakarta': 120, 'Demak': 30, 'Kudus': 50, 'Jepara': 80, 'Pati': 75, 'Ngawi': 155, 'Madiun': 205, 'Surabaya': 325, 'Kediri': 250, 'Jombang': 270, 'Mojokerto': 290, 'Sidoarjo': 310, 'Gresik': 340, 'Lamongan': 260, 'Tuban': 220, 'Malang': 390, 'Tulungagung': 230, 'Trenggalek': 260, 'Pacitan': 280, 'Blitar': 240, 'Batu': 370, 'Probolinggo': 440, 'Lumajang': 460, 'Jember': 510, 'Situbondo': 560, 'Bondowoso': 540, 'Banyuwangi': 620},
    'Kendal': {'Jakarta': 420, 'Tangerang': 435, 'Bogor': 450, 'Bandung': 395, 'Cianjur': 435, 'Serang': 485, 'Cirebon': 210, 'Purwakarta': 365, 'Tasikmalaya': 360, 'Purwokerto': 205, 'Tegal': 110, 'Pekalongan': 60, 'Semarang': 25, 'Kendal': 0, 'Purbalingga': 190, 'Temanggung': 60, 'Wonosobo': 95, 'Banjarnegara': 155, 'Banyumas': 200, 'Magelang': 65, 'Boyolali': 100, 'Salatiga': 60, 'Solo': 110, 'Klaten': 100, 'Sragen': 135, 'Yogyakarta': 105, 'Demak': 40, 'Kudus': 55, 'Jepara': 85, 'Pati': 80, 'Ngawi': 165, 'Madiun': 215, 'Surabaya': 335, 'Kediri': 260, 'Jombang': 280, 'Mojokerto': 300, 'Sidoarjo': 320, 'Gresik': 350, 'Lamongan': 270, 'Tuban': 230, 'Malang': 400, 'Tulungagung': 240, 'Trenggalek': 270, 'Pacitan': 290, 'Blitar': 250, 'Batu': 380, 'Probolinggo': 450, 'Lumajang': 470, 'Jember': 520, 'Situbondo': 570, 'Bondowoso': 550, 'Banyuwangi': 630},
    'Purbalingga': {'Jakarta': 380, 'Tangerang': 395, 'Bogor': 410, 'Bandung': 325, 'Cianjur': 365, 'Serang': 445, 'Cirebon': 165, 'Purwakarta': 295, 'Tasikmalaya': 205, 'Purwokerto': 25, 'Tegal': 80, 'Pekalongan': 130, 'Semarang': 215, 'Kendal': 190, 'Purbalingga': 0, 'Temanggung': 155, 'Wonosobo': 65, 'Banjarnegara': 35, 'Banyumas': 20, 'Magelang': 180, 'Boyolali': 235, 'Salatiga': 195, 'Solo': 250, 'Klaten': 235, 'Sragen': 270, 'Yogyakarta': 200, 'Demak': 235, 'Kudus': 250, 'Jepara': 280, 'Pati': 270, 'Ngawi': 300, 'Madiun': 350, 'Surabaya': 470, 'Kediri': 395, 'Jombang': 415, 'Mojokerto': 435, 'Sidoarjo': 455, 'Gresik': 485, 'Lamongan': 405, 'Tuban': 365, 'Malang': 530, 'Tulungagung': 375, 'Trenggalek': 405, 'Pacitan': 425, 'Blitar': 385, 'Batu': 510, 'Probolinggo': 580, 'Lumajang': 600, 'Jember': 650, 'Situbondo': 700, 'Bondowoso': 680, 'Banyuwangi': 760},
    'Temanggung': {'Jakarta': 450, 'Tangerang': 465, 'Bogor': 480, 'Bandung': 425, 'Cianjur': 465, 'Serang': 515, 'Cirebon': 240, 'Purwakarta': 395, 'Tasikmalaya': 390, 'Purwokerto': 170, 'Tegal': 160, 'Pekalongan': 110, 'Semarang': 50, 'Kendal': 60, 'Purbalingga': 155, 'Temanggung': 0, 'Wonosobo': 35, 'Banjarnegara': 120, 'Banyumas': 165, 'Magelang': 30, 'Boyolali': 60, 'Salatiga': 40, 'Solo': 85, 'Klaten': 75, 'Sragen': 110, 'Yogyakarta': 85, 'Demak': 70, 'Kudus': 85, 'Jepara': 115, 'Pati': 110, 'Ngawi': 140, 'Madiun': 190, 'Surabaya': 310, 'Kediri': 235, 'Jombang': 255, 'Mojokerto': 275, 'Sidoarjo': 295, 'Gresik': 325, 'Lamongan': 245, 'Tuban': 205, 'Malang': 375, 'Tulungagung': 215, 'Trenggalek': 245, 'Pacitan': 265, 'Blitar': 225, 'Batu': 355, 'Probolinggo': 425, 'Lumajang': 445, 'Jember': 495, 'Situbondo': 545, 'Bondowoso': 525, 'Banyuwangi': 605},
    'Wonosobo': {'Jakarta': 440, 'Tangerang': 455, 'Bogor': 470, 'Bandung': 390, 'Cianjur': 430, 'Serang': 505, 'Cirebon': 230, 'Purwakarta': 360, 'Tasikmalaya': 280, 'Purwokerto': 90, 'Tegal': 135, 'Pekalongan': 110, 'Semarang': 85, 'Kendal': 95, 'Purbalingga': 65, 'Temanggung': 35, 'Wonosobo': 0, 'Banjarnegara': 55, 'Banyumas': 75, 'Magelang': 60, 'Boyolali': 95, 'Salatiga': 70, 'Solo': 115, 'Klaten': 105, 'Sragen': 140, 'Yogyakarta': 110, 'Demak': 105, 'Kudus': 120, 'Jepara': 150, 'Pati': 145, 'Ngawi': 170, 'Madiun': 220, 'Surabaya': 340, 'Kediri': 265, 'Jombang': 285, 'Mojokerto': 305, 'Sidoarjo': 325, 'Gresik': 355, 'Lamongan': 275, 'Tuban': 235, 'Malang': 405, 'Tulungagung': 245, 'Trenggalek': 275, 'Pacitan': 295, 'Blitar': 255, 'Batu': 385, 'Probolinggo': 455, 'Lumajang': 475, 'Jember': 525, 'Situbondo': 575, 'Bondowoso': 555, 'Banyuwangi': 635},
    'Banjarnegara': {'Jakarta': 400, 'Tangerang': 415, 'Bogor': 430, 'Bandung': 350, 'Cianjur': 390, 'Serang': 465, 'Cirebon': 190, 'Purwakarta': 320, 'Tasikmalaya': 240, 'Purwokerto': 50, 'Tegal': 105, 'Pekalongan': 135, 'Semarang': 180, 'Kendal': 155, 'Purbalingga': 35, 'Temanggung': 120, 'Wonosobo': 55, 'Banjarnegara': 0, 'Banyumas': 45, 'Magelang': 145, 'Boyolali': 200, 'Salatiga': 160, 'Solo': 215, 'Klaten': 200, 'Sragen': 235, 'Yogyakarta': 165, 'Demak': 200, 'Kudus': 215, 'Jepara': 245, 'Pati': 235, 'Ngawi': 265, 'Madiun': 315, 'Surabaya': 435, 'Kediri': 360, 'Jombang': 380, 'Mojokerto': 400, 'Sidoarjo': 420, 'Gresik': 450, 'Lamongan': 370, 'Tuban': 330, 'Malang': 495, 'Tulungagung': 340, 'Trenggalek': 370, 'Pacitan': 390, 'Blitar': 350, 'Batu': 475, 'Probolinggo': 545, 'Lumajang': 565, 'Jember': 615, 'Situbondo': 665, 'Bondowoso': 645, 'Banyuwangi': 725},
    'Banyumas': {'Jakarta': 390, 'Tangerang': 405, 'Bogor': 420, 'Bandung': 335, 'Cianjur': 375, 'Serang': 455, 'Cirebon': 175, 'Purwakarta': 305, 'Tasikmalaya': 215, 'Purwokerto': 15, 'Tegal': 90, 'Pekalongan': 140, 'Semarang': 225, 'Kendal': 200, 'Purbalingga': 20, 'Temanggung': 165, 'Wonosobo': 75, 'Banjarnegara': 45, 'Banyumas': 0, 'Magelang': 190, 'Boyolali': 245, 'Salatiga': 205, 'Solo': 260, 'Klaten': 245, 'Sragen': 280, 'Yogyakarta': 210, 'Demak': 245, 'Kudus': 260, 'Jepara': 290, 'Pati': 280, 'Ngawi': 310, 'Madiun': 360, 'Surabaya': 480, 'Kediri': 405, 'Jombang': 425, 'Mojokerto': 445, 'Sidoarjo': 465, 'Gresik': 495, 'Lamongan': 415, 'Tuban': 375, 'Malang': 540, 'Tulungagung': 385, 'Trenggalek': 415, 'Pacitan': 435, 'Blitar': 395, 'Batu': 520, 'Probolinggo': 590, 'Lumajang': 610, 'Jember': 660, 'Situbondo': 710, 'Bondowoso': 690, 'Banyuwangi': 770},
    'Magelang': {'Jakarta': 475, 'Tangerang': 490, 'Bogor': 505, 'Bandung': 450, 'Cianjur': 490, 'Serang': 540, 'Cirebon': 265, 'Purwakarta': 420, 'Tasikmalaya': 415, 'Purwokerto': 195, 'Tegal': 170, 'Pekalongan': 120, 'Semarang': 75, 'Kendal': 65, 'Purbalingga': 180, 'Temanggung': 30, 'Wonosobo': 60, 'Banjarnegara': 145, 'Banyumas': 190, 'Magelang': 0, 'Boyolali': 40, 'Salatiga': 25, 'Solo': 65, 'Klaten': 55, 'Sragen': 90, 'Yogyakarta': 45, 'Demak': 95, 'Kudus': 110, 'Jepara': 140, 'Pati': 135, 'Ngawi': 120, 'Madiun': 170, 'Surabaya': 290, 'Kediri': 215, 'Jombang': 235, 'Mojokerto': 255, 'Sidoarjo': 275, 'Gresik': 305, 'Lamongan': 225, 'Tuban': 185, 'Malang': 355, 'Tulungagung': 195, 'Trenggalek': 225, 'Pacitan': 245, 'Blitar': 205, 'Batu': 335, 'Probolinggo': 405, 'Lumajang': 425, 'Jember': 475, 'Situbondo': 525, 'Bondowoso': 505, 'Banyuwangi': 585},
    'Boyolali': {'Jakarta': 530, 'Tangerang': 545, 'Bogor': 560, 'Bandung': 505, 'Cianjur': 545, 'Serang': 595, 'Cirebon': 320, 'Purwakarta': 475, 'Tasikmalaya': 470, 'Purwokerto': 250, 'Tegal': 225, 'Pekalongan': 175, 'Semarang': 90, 'Kendal': 100, 'Purbalingga': 235, 'Temanggung': 60, 'Wonosobo': 95, 'Banjarnegara': 200, 'Banyumas': 245, 'Magelang': 40, 'Boyolali': 0, 'Salatiga': 30, 'Solo': 30, 'Klaten': 25, 'Sragen': 50, 'Yogyakarta': 60, 'Demak': 110, 'Kudus': 125, 'Jepara': 155, 'Pati': 150, 'Ngawi': 80, 'Madiun': 130, 'Surabaya': 250, 'Kediri': 175, 'Jombang': 195, 'Mojokerto': 215, 'Sidoarjo': 235, 'Gresik': 265, 'Lamongan': 185, 'Tuban': 145, 'Malang': 315, 'Tulungagung': 155, 'Trenggalek': 185, 'Pacitan': 205, 'Blitar': 165, 'Batu': 295, 'Probolinggo': 365, 'Lumajang': 385, 'Jember': 435, 'Situbondo': 485, 'Bondowoso': 465, 'Banyuwangi': 545},
    'Salatiga': {'Jakarta': 490, 'Tangerang': 505, 'Bogor': 520, 'Bandung': 465, 'Cianjur': 505, 'Serang': 555, 'Cirebon': 280, 'Purwakarta': 435, 'Tasikmalaya': 430, 'Purwokerto': 210, 'Tegal': 185, 'Pekalongan': 135, 'Semarang': 50, 'Kendal': 60, 'Purbalingga': 195, 'Temanggung': 40, 'Wonosobo': 70, 'Banjarnegara': 160, 'Banyumas': 205, 'Magelang': 25, 'Boyolali': 30, 'Salatiga': 0, 'Solo': 50, 'Klaten': 45, 'Sragen': 75, 'Yogyakarta': 65, 'Demak': 70, 'Kudas': 85, 'Jepara': 115, 'Pati': 110, 'Ngawi': 105, 'Madiun': 155, 'Surabaya': 275, 'Kediri': 200, 'Jombang': 220, 'Mojokerto': 240, 'Sidoarjo': 260, 'Gresik': 290, 'Lamongan': 210, 'Tuban': 170, 'Malang': 340, 'Tulungagung': 180, 'Trenggalek': 210, 'Pacitan': 230, 'Blitar': 190, 'Batu': 320, 'Probolinggo': 390, 'Lumajang': 410, 'Jember': 460, 'Situbondo': 510, 'Bondowoso': 490, 'Banyuwangi': 570},
    'Solo': {'Jakarta': 550, 'Tangerang': 565, 'Bogor': 580, 'Bandung': 520, 'Cianjur': 560, 'Serang': 615, 'Cirebon': 335, 'Purwakarta': 490, 'Tasikmalaya': 485, 'Purwokerto': 265, 'Tegal': 240, 'Pekalongan': 190, 'Semarang': 100, 'Kendal': 110, 'Purbalingga': 250, 'Temanggung': 85, 'Wonosobo': 115, 'Banjarnegara': 215, 'Banyumas': 260, 'Magelang': 65, 'Boyolali': 30, 'Salatiga': 50, 'Solo': 0, 'Klaten': 20, 'Sragen': 35, 'Yogyakarta': 65, 'Demak': 120, 'Kudus': 135, 'Jepara': 165, 'Pati': 155, 'Ngawi': 75, 'Madiun': 110, 'Surabaya': 220, 'Kediri': 145, 'Jombang': 165, 'Mojokerto': 185, 'Sidoarjo': 205, 'Gresik': 235, 'Lamongan': 155, 'Tuban': 115, 'Malang': 290, 'Tulungagung': 125, 'Trenggalek': 155, 'Pacitan': 175, 'Blitar': 135, 'Batu': 270, 'Probolinggo': 340, 'Lumajang': 360, 'Jember': 410, 'Situbondo': 460, 'Bondowoso': 440, 'Banyuwangi': 520},
    'Klaten': {'Jakarta': 535, 'Tangerang': 550, 'Bogor': 565, 'Bandung': 505, 'Cianjur': 545, 'Serang': 600, 'Cirebon': 320, 'Purwakarta': 475, 'Tasikmalaya': 470, 'Purwokerto': 250, 'Tegal': 225, 'Pekalongan': 175, 'Semarang': 90, 'Kendal': 100, 'Purbalingga': 235, 'Temanggung': 75, 'Wonosobo': 105, 'Banjarnegara': 200, 'Banyumas': 245, 'Magelang': 55, 'Boyolali': 25, 'Salatiga': 45, 'Solo': 20, 'Klaten': 0, 'Sragen': 40, 'Yogyakarta': 30, 'Demak': 110, 'Kudus': 125, 'Jepara': 155, 'Pati': 145, 'Ngawi': 90, 'Madiun': 125, 'Surabaya': 235, 'Kediri': 160, 'Jombang': 180, 'Mojokerto': 200, 'Sidoarjo': 220, 'Gresik': 250, 'Lamongan': 170, 'Tuban': 130, 'Malang': 305, 'Tulungagung': 140, 'Trenggalek': 170, 'Pacitan': 190, 'Blitar': 150, 'Batu': 285, 'Probolinggo': 355, 'Lumajang': 375, 'Jember': 425, 'Situbondo': 475, 'Bondowoso': 455, 'Banyuwangi': 535},
    'Sragen': {'Jakarta': 570, 'Tangerang': 585, 'Bogor': 600, 'Bandung': 540, 'Cianjur': 580, 'Serang': 635, 'Cirebon': 355, 'Purwakarta': 510, 'Tasikmalaya': 505, 'Purwokerto': 285, 'Tegal': 260, 'Pekalongan': 210, 'Semarang': 125, 'Kendal': 135, 'Purbalingga': 270, 'Temanggung': 110, 'Wonosobo': 140, 'Banjarnegara': 235, 'Banyumas': 280, 'Magelang': 90, 'Boyolali': 50, 'Salatiga': 75, 'Solo': 35, 'Klaten': 40, 'Sragen': 0, 'Yogyakarta': 85, 'Demak': 145, 'Kudus': 160, 'Jepara': 190, 'Pati': 175, 'Ngawi': 60, 'Madiun': 85, 'Surabaya': 195, 'Kediri': 130, 'Jombang': 150, 'Mojokerto': 170, 'Sidoarjo': 190, 'Gresik': 220, 'Lamongan': 140, 'Tuban': 100, 'Malang': 275, 'Tulungagung': 110, 'Trenggalek': 140, 'Pacitan': 160, 'Blitar': 120, 'Batu': 255, 'Probolinggo': 325, 'Lumajang': 345, 'Jember': 395, 'Situbondo': 445, 'Bondowoso': 425, 'Banyuwangi': 505},
    'Yogyakarta': {'Jakarta': 560, 'Tangerang': 575, 'Bogor': 590, 'Bandung': 470, 'Cianjur': 510, 'Serang': 625, 'Cirebon': 285, 'Purwakarta': 440, 'Tasikmalaya': 350, 'Purwokerto': 215, 'Tegal': 190, 'Pekalongan': 140, 'Semarang': 120, 'Kendal': 105, 'Purbalingga': 200, 'Temanggung': 85, 'Wonosobo': 110, 'Banjarnegara': 165, 'Banyumas': 210, 'Magelang': 45, 'Boyolali': 60, 'Salatiga': 65, 'Solo': 65, 'Klaten': 30, 'Sragen': 85, 'Yogyakarta': 0, 'Demak': 140, 'Kudus': 155, 'Jepara': 185, 'Pati': 170, 'Ngawi': 115, 'Madiun': 155, 'Surabaya': 325, 'Kediri': 200, 'Jombang': 220, 'Mojokerto': 240, 'Sidoarjo': 310, 'Gresik': 340, 'Lamongan': 260, 'Tuban': 220, 'Malang': 330, 'Tulungagung': 170, 'Trenggalek': 200, 'Pacitan': 220, 'Blitar': 180, 'Batu': 310, 'Probolinggo': 380, 'Lumajang': 400, 'Jember': 450, 'Situbondo': 500, 'Bondowoso': 480, 'Banyuwangi': 560},
    'Demak': {'Jakarta': 465, 'Tangerang': 480, 'Bogor': 495, 'Bandung': 440, 'Cianjur': 480, 'Serang': 530, 'Cirebon': 255, 'Purwakarta': 410, 'Tasikmalaya': 405, 'Purwokerto': 250, 'Tegal': 155, 'Pekalongan': 105, 'Semarang': 30, 'Kendal': 40, 'Purbalingga': 235, 'Temanggung': 70, 'Wonosobo': 105, 'Banjarnegara': 200, 'Banyumas': 245, 'Magelang': 95, 'Boyolali': 110, 'Salatiga': 70, 'Solo': 120, 'Klaten': 110, 'Sragen': 145, 'Yogyakarta': 140, 'Demak': 0, 'Kudus': 25, 'Jepara': 55, 'Pati': 50, 'Ngawi': 175, 'Madiun': 225, 'Surabaya': 295, 'Kediri': 270, 'Jombang': 240, 'Mojokerto': 260, 'Sidoarjo': 280, 'Gresik': 310, 'Lamongan': 230, 'Tuban': 190, 'Malang': 360, 'Tulungagung': 250, 'Trenggalek': 280, 'Pacitan': 300, 'Blitar': 260, 'Batu': 340, 'Probolinggo': 410, 'Lumajang': 430, 'Jember': 480, 'Situbondo': 530, 'Bondowoso': 510, 'Banyuwangi': 590},
    'Kudus': {'Jakarta': 480, 'Tangerang': 495, 'Bogor': 510, 'Bandung': 455, 'Cianjur': 495, 'Serang': 545, 'Cirebon': 270, 'Purwakarta': 425, 'Tasikmalaya': 420, 'Purwokerto': 265, 'Tegal': 170, 'Pekalongan': 120, 'Semarang': 50, 'Kendal': 55, 'Purbalingga': 250, 'Temanggung': 85, 'Wonosobo': 120, 'Banjarnegara': 215, 'Banyumas': 260, 'Magelang': 110, 'Boyolali': 125, 'Salatiga': 85, 'Solo': 135, 'Klaten': 125, 'Sragen': 160, 'Yogyakarta': 155, 'Demak': 25, 'Kudus': 0, 'Jepara': 30, 'Pati': 35, 'Ngawi': 190, 'Madiun': 240, 'Surabaya': 280, 'Kediri': 255, 'Jombang': 225, 'Mojokerto': 245, 'Sidoarjo': 265, 'Gresik': 295, 'Lamongan': 215, 'Tuban': 175, 'Malang': 345, 'Tulungagung': 265, 'Trenggalek': 295, 'Pacitan': 315, 'Blitar': 275, 'Batu': 325, 'Probolinggo': 395, 'Lumajang': 415, 'Jember': 465, 'Situbondo': 515, 'Bondowoso': 495, 'Banyuwangi': 575},
    'Jepara': {'Jakarta': 510, 'Tangerang': 525, 'Bogor': 540, 'Bandung': 485, 'Cianjur': 525, 'Serang': 575, 'Cirebon': 300, 'Purwakarta': 455, 'Tasikmalaya': 450, 'Purwokerto': 295, 'Tegal': 200, 'Pekalongan': 150, 'Semarang': 80, 'Kendal': 85, 'Purbalingga': 280, 'Temanggung': 115, 'Wonosobo': 150, 'Banjarnegara': 245, 'Banyumas': 290, 'Magelang': 140, 'Boyolali': 155, 'Salatiga': 115, 'Solo': 165, 'Klaten': 155, 'Sragen': 190, 'Yogyakarta': 185, 'Demak': 55, 'Kudus': 30, 'Jepara': 0, 'Pati': 40, 'Ngawi': 220, 'Madiun': 270, 'Surabaya': 310, 'Kediri': 285, 'Jombang': 255, 'Mojokerto': 275, 'Sidoarjo': 295, 'Gresik': 325, 'Lamongan': 245, 'Tuban': 205, 'Malang': 375, 'Tulungagung': 295, 'Trenggalek': 325, 'Pacitan': 345, 'Blitar': 305, 'Batu': 355, 'Probolinggo': 425, 'Lumajang': 445, 'Jember': 495, 'Situbondo': 545, 'Bondowoso': 525, 'Banyuwangi': 605},
    'Pati': {'Jakarta': 500, 'Tangerang': 515, 'Bogor': 530, 'Bandung': 475, 'Cianjur': 515, 'Serang': 565, 'Cirebon': 290, 'Purwakarta': 445, 'Tasikmalaya': 440, 'Purwokerto': 285, 'Tegal': 190, 'Pekalongan': 140, 'Semarang': 75, 'Kendal': 80, 'Purbalingga': 270, 'Temanggung': 110, 'Wonosobo': 145, 'Banjarnegara': 235, 'Banyumas': 280, 'Magelang': 135, 'Boyolali': 150, 'Salatiga': 110, 'Solo': 155, 'Klaten': 145, 'Sragen': 175, 'Yogyakarta': 170, 'Demak': 50, 'Kudus': 35, 'Jepara': 40, 'Pati': 0, 'Ngawi': 210, 'Madiun': 260, 'Surabaya': 300, 'Kediri': 275, 'Jombang': 245, 'Mojokerto': 265, 'Sidoarjo': 285, 'Gresik': 315, 'Lamongan': 235, 'Tuban': 195, 'Malang': 365, 'Tulungagung': 285, 'Trenggalek': 315, 'Pacitan': 335, 'Blitar': 295, 'Batu': 345, 'Probolinggo': 415, 'Lumajang': 435, 'Jember': 485, 'Situbondo': 535, 'Bondowoso': 515, 'Banyuwangi': 595},
    'Ngawi': {'Jakarta': 600, 'Tangerang': 615, 'Bogor': 630, 'Bandung': 570, 'Cianjur': 610, 'Serang': 665, 'Cirebon': 385, 'Purwakarta': 540, 'Tasikmalaya': 535, 'Purwokerto': 315, 'Tegal': 290, 'Pekalongan': 240, 'Semarang': 155, 'Kendal': 165, 'Purbalingga': 300, 'Temanggung': 140, 'Wonosobo': 170, 'Banjarnegara': 265, 'Banyumas': 310, 'Magelang': 120, 'Boyolali': 80, 'Salatiga': 105, 'Solo': 75, 'Klaten': 90, 'Sragen': 60, 'Yogyakarta': 115, 'Demak': 175, 'Kudus': 190, 'Jepara': 220, 'Pati': 210, 'Ngawi': 0, 'Madiun': 50, 'Surabaya': 165, 'Kediri': 100, 'Jombang': 120, 'Mojokerto': 140, 'Sidoarjo': 160, 'Gresik': 190, 'Lamongan': 110, 'Tuban': 70, 'Malang': 245, 'Tulungagung': 80, 'Trenggalek': 110, 'Pacitan': 130, 'Blitar': 90, 'Batu': 225, 'Probolinggo': 295, 'Lumajang': 315, 'Jember': 365, 'Situbondo': 415, 'Bondowoso': 395, 'Banyuwangi': 475},
    'Madiun': {'Jakarta': 650, 'Tangerang': 665, 'Bogor': 680, 'Bandung': 620, 'Cianjur': 660, 'Serang': 715, 'Cirebon': 435, 'Purwakarta': 590, 'Tasikmalaya': 585, 'Purwokerto': 365, 'Tegal': 340, 'Pekalongan': 290, 'Semarang': 205, 'Kendal': 215, 'Purbalingga': 350, 'Temanggung': 190, 'Wonosobo': 220, 'Banjarnegara': 315, 'Banyumas': 360, 'Magelang': 170, 'Boyolali': 130, 'Salatiga': 155, 'Solo': 110, 'Klaten': 125, 'Sragen': 85, 'Yogyakarta': 155, 'Demak': 225, 'Kudus': 240, 'Jepara': 270, 'Pati': 260, 'Ngawi': 50, 'Madiun': 0, 'Surabaya': 145, 'Kediri': 70, 'Jombang': 90, 'Mojokerto': 110, 'Sidoarjo': 130, 'Gresik': 160, 'Lamongan': 80, 'Tuban': 95, 'Malang': 215, 'Tulungagung': 50, 'Trenggalek': 80, 'Pacitan': 100, 'Blitar': 60, 'Batu': 195, 'Probolinggo': 265, 'Lumajang': 285, 'Jember': 335, 'Situbondo': 385, 'Bondowoso': 365, 'Banyuwangi': 445},
    'Surabaya': {'Jakarta': 785, 'Tangerang': 800, 'Bogor': 815, 'Bandung': 740, 'Cianjur': 780, 'Serang': 850, 'Cirebon': 555, 'Purwakarta': 710, 'Tasikmalaya': 705, 'Purwokerto': 485, 'Tegal': 460, 'Pekalongan': 410, 'Semarang': 325, 'Kendal': 335, 'Purbalingga': 470, 'Temanggung': 310, 'Wonosobo': 340, 'Banjarnegara': 435, 'Banyumas': 480, 'Magelang': 290, 'Boyolali': 250, 'Salatiga': 275, 'Solo': 220, 'Klaten': 235, 'Sragen': 195, 'Yogyakarta': 325, 'Demak': 295, 'Kudus': 280, 'Jepara': 310, 'Pati': 300, 'Ngawi': 165, 'Madiun': 145, 'Surabaya': 0, 'Kediri': 130, 'Jombang': 75, 'Mojokerto': 50, 'Sidoarjo': 25, 'Gresik': 20, 'Lamongan': 60, 'Tuban': 100, 'Malang': 90, 'Tulungagung': 155, 'Trenggalek': 185, 'Pacitan': 240, 'Blitar': 165, 'Batu': 100, 'Probolinggo': 100, 'Lumajang': 170, 'Jember': 220, 'Situbondo': 235, 'Bondowoso': 215, 'Banyuwangi': 295},
    'Kediri': {'Jakarta': 710, 'Tangerang': 725, 'Bogor': 740, 'Bandung': 665, 'Cianjur': 705, 'Serang': 775, 'Cirebon': 480, 'Purwakarta': 635, 'Tasikmalaya': 630, 'Purwokerto': 410, 'Tegal': 385, 'Pekalongan': 335, 'Semarang': 250, 'Kendal': 260, 'Purbalingga': 395, 'Temanggung': 235, 'Wonosobo': 265, 'Banjarnegara': 360, 'Banyumas': 405, 'Magelang': 215, 'Boyolali': 175, 'Salatiga': 200, 'Solo': 145, 'Klaten': 160, 'Sragen': 130, 'Yogyakarta': 200, 'Demak': 270, 'Kudus': 255, 'Jepara': 285, 'Pati': 275, 'Ngawi': 100, 'Madiun': 70, 'Surabaya': 130, 'Kediri': 0, 'Jombang': 55, 'Mojokerto': 80, 'Sidoarjo': 105, 'Gresik': 135, 'Lamongan': 115, 'Tuban': 165, 'Malang': 85, 'Tulungagung': 35, 'Trenggalek': 50, 'Pacitan': 95, 'Blitar': 40, 'Batu': 90, 'Probolinggo': 155, 'Lumajang': 140, 'Jember': 190, 'Situbondo': 240, 'Bondowoso': 220, 'Banyuwangi': 300},
    'Jombang': {'Jakarta': 730, 'Tangerang': 745, 'Bogor': 760, 'Bandung': 685, 'Cianjur': 725, 'Serang': 795, 'Cirebon': 500, 'Purwakarta': 655, 'Tasikmalaya': 650, 'Purwokerto': 430, 'Tegal': 405, 'Pekalongan': 355, 'Semarang': 270, 'Kendal': 280, 'Purbalingga': 415, 'Temanggung': 255, 'Wonosobo': 285, 'Banjarnegara': 380, 'Banyumas': 425, 'Magelang': 235, 'Boyolali': 195, 'Salatiga': 220, 'Solo': 165, 'Klaten': 180, 'Sragen': 150, 'Yogyakarta': 220, 'Demak': 240, 'Kudus': 225, 'Jepara': 255, 'Pati': 245, 'Ngawi': 120, 'Madiun': 90, 'Surabaya': 75, 'Kediri': 55, 'Jombang': 0, 'Mojokerto': 30, 'Sidoarjo': 50, 'Gresik': 80, 'Lamongan': 85, 'Tuban': 125, 'Malang': 120, 'Tulungagung': 75, 'Trenggalek': 95, 'Pacitan': 145, 'Blitar': 85, 'Batu': 105, 'Probolinggo': 160, 'Lumajang': 175, 'Jember': 225, 'Situbondo': 275, 'Bondowoso': 255, 'Banyuwangi': 335},
    'Mojokerto': {'Jakarta': 750, 'Tangerang': 765, 'Bogor': 780, 'Bandung': 705, 'Cianjur': 745, 'Serang': 815, 'Cirebon': 520, 'Purwakarta': 675, 'Tasikmalaya': 670, 'Purwokerto': 450, 'Tegal': 425, 'Pekalongan': 375, 'Semarang': 290, 'Kendal': 300, 'Purbalingga': 435, 'Temanggung': 275, 'Wonosobo': 305, 'Banjarnegara': 400, 'Banyumas': 445, 'Magelang': 255, 'Boyolali': 215, 'Salatiga': 240, 'Solo': 185, 'Klaten': 200, 'Sragen': 170, 'Yogyakarta': 240, 'Demak': 260, 'Kudus': 245, 'Jepara': 275, 'Pati': 265, 'Ngawi': 140, 'Madiun': 110, 'Surabaya': 50, 'Kediri': 80, 'Jombang': 30, 'Mojokerto': 0, 'Sidoarjo': 35, 'Gresik': 55, 'Lamongan': 70, 'Tuban': 110, 'Malang': 95, 'Tulungagung': 100, 'Trenggalek': 120, 'Pacitan': 170, 'Blitar': 110, 'Batu': 80, 'Probolinggo': 135, 'Lumajang': 150, 'Jember': 200, 'Situbondo': 250, 'Bondowoso': 230, 'Banyuwangi': 310},
    'Sidoarjo': {'Jakarta': 770, 'Tangerang': 785, 'Bogor': 800, 'Bandung': 725, 'Cianjur': 765, 'Serang': 835, 'Cirebon': 540, 'Purwakarta': 695, 'Tasikmalaya': 690, 'Purwokerto': 470, 'Tegal': 445, 'Pekalongan': 395, 'Semarang': 310, 'Kendal': 320, 'Purbalingga': 455, 'Temanggung': 295, 'Wonosobo': 325, 'Banjarnegara': 420, 'Banyumas': 465, 'Magelang': 275, 'Boyolali': 235, 'Salatiga': 260, 'Solo': 205, 'Klaten': 220, 'Sragen': 190, 'Yogyakarta': 310, 'Demak': 280, 'Kudus': 265, 'Jepara': 295, 'Pati': 285, 'Ngawi': 160, 'Madiun': 130, 'Surabaya': 25, 'Kediri': 105, 'Jombang': 50, 'Mojokerto': 35, 'Sidoarjo': 0, 'Gresik': 40, 'Lamongan': 70, 'Tuban': 110, 'Malang': 85, 'Tulungagung': 125, 'Trenggalek': 145, 'Pacitan': 195, 'Blitar': 135, 'Batu': 95, 'Probolinggo': 115, 'Lumajang': 140, 'Jember': 190, 'Situbondo': 240, 'Bondowoso': 220, 'Banyuwangi': 300},
    'Gresik': {'Jakarta': 800, 'Tangerang': 815, 'Bogor': 830, 'Bandung': 755, 'Cianjur': 795, 'Serang': 865, 'Cirebon': 570, 'Purwakarta': 725, 'Tasikmalaya': 720, 'Purwokerto': 500, 'Tegal': 475, 'Pekalongan': 425, 'Semarang': 340, 'Kendal': 350, 'Purbalingga': 485, 'Temanggung': 325, 'Wonosobo': 355, 'Banjarnegara': 450, 'Banyumas': 495, 'Magelang': 305, 'Boyolali': 265, 'Salatiga': 290, 'Solo': 235, 'Klaten': 250, 'Sragen': 220, 'Yogyakarta': 340, 'Demak': 310, 'Kudus': 295, 'Jepara': 325, 'Pati': 315, 'Ngawi': 190, 'Madiun': 160, 'Surabaya': 20, 'Kediri': 135, 'Jombang': 80, 'Mojokerto': 55, 'Sidoarjo': 40, 'Gresik': 0, 'Lamongan': 40, 'Tuban': 80, 'Malang': 110, 'Tulungagung': 155, 'Trenggalek': 175, 'Pacitan': 225, 'Blitar': 165, 'Batu': 120, 'Probolinggo': 120, 'Lumajang': 170, 'Jember': 220, 'Situbondo': 270, 'Bondowoso': 250, 'Banyuwangi': 330},
    'Lamongan': {'Jakarta': 720, 'Tangerang': 735, 'Bogor': 750, 'Bandung': 675, 'Cianjur': 715, 'Serang': 785, 'Cirebon': 490, 'Purwakarta': 645, 'Tasikmalaya': 640, 'Purwokerto': 420, 'Tegal': 395, 'Pekalongan': 345, 'Semarang': 260, 'Kendal': 270, 'Purbalingga': 405, 'Temanggung': 245, 'Wonosobo': 275, 'Banjarnegara': 370, 'Banyumas': 415, 'Magelang': 225, 'Boyolali': 185, 'Salatiga': 210, 'Solo': 155, 'Klaten': 170, 'Sragen': 140, 'Yogyakarta': 260, 'Demak': 230, 'Kudus': 215, 'Jepara': 245, 'Pati': 235, 'Ngawi': 110, 'Madiun': 80, 'Surabaya': 60, 'Kediri': 115, 'Jombang': 85, 'Mojokerto': 70, 'Sidoarjo': 70, 'Gresik': 40, 'Lamongan': 0, 'Tuban': 50, 'Malang': 145, 'Tulungagung': 135, 'Trenggalek': 165, 'Pacitan': 200, 'Blitar': 145, 'Batu': 135, 'Probolinggo': 170, 'Lumajang': 200, 'Jember': 250, 'Situbondo': 300, 'Bondowoso': 280, 'Banyuwangi': 360},
    'Tuban': {'Jakarta': 680, 'Tangerang': 695, 'Bogor': 710, 'Bandung': 635, 'Cianjur': 675, 'Serang': 745, 'Cirebon': 450, 'Purwakarta': 605, 'Tasikmalaya': 600, 'Purwokerto': 380, 'Tegal': 355, 'Pekalongan': 305, 'Semarang': 220, 'Kendal': 230, 'Purbalingga': 365, 'Temanggung': 205, 'Wonosobo': 235, 'Banjarnegara': 330, 'Banyumas': 375, 'Magelang': 185, 'Boyolali': 145, 'Salatiga': 170, 'Solo': 115, 'Klaten': 130, 'Sragen': 100, 'Yogyakarta': 220, 'Demak': 190, 'Kudus': 175, 'Jepara': 205, 'Pati': 195, 'Ngawi': 70, 'Madiun': 95, 'Surabaya': 100, 'Kediri': 165, 'Jombang': 125, 'Mojokerto': 110, 'Sidoarjo': 110, 'Gresik': 80, 'Lamongan': 50, 'Tuban': 0, 'Malang': 185, 'Tulungagung': 175, 'Trenggalek': 205, 'Pacitan': 225, 'Blitar': 185, 'Batu': 175, 'Probolinggo': 210, 'Lumajang': 240, 'Jember': 290, 'Situbondo': 340, 'Bondowoso': 320, 'Banyuwangi': 400},
    'Malang': {'Jakarta': 850, 'Tangerang': 865, 'Bogor': 880, 'Bandung': 800, 'Cianjur': 840, 'Serang': 915, 'Cirebon': 615, 'Purwakarta': 770, 'Tasikmalaya': 765, 'Purwokerto': 545, 'Tegal': 520, 'Pekalongan': 470, 'Semarang': 390, 'Kendal': 400, 'Purbalingga': 530, 'Temanggung': 375, 'Wonosobo': 405, 'Banjarnegara': 495, 'Banyumas': 540, 'Magelang': 355, 'Boyolali': 315, 'Salatiga': 340, 'Solo': 290, 'Klaten': 305, 'Sragen': 275, 'Yogyakarta': 330, 'Demak': 360, 'Kudus': 345, 'Jepara': 375, 'Pati': 365, 'Ngawi': 245, 'Madiun': 215, 'Surabaya': 90, 'Kediri': 85, 'Jombang': 120, 'Mojokerto': 95, 'Sidoarjo': 85, 'Gresik': 110, 'Lamongan': 145, 'Tuban': 185, 'Malang': 0, 'Tulungagung': 95, 'Trenggalek': 105, 'Pacitan': 155, 'Blitar': 85, 'Batu': 20, 'Probolinggo': 60, 'Lumajang': 85, 'Jember': 135, 'Situbondo': 185, 'Bondowoso': 155, 'Banyuwangi': 235},
    'Tulungagung': {'Jakarta': 690, 'Tangerang': 705, 'Bogor': 720, 'Bandung': 645, 'Cianjur': 685, 'Serang': 755, 'Cirebon': 460, 'Purwakarta': 615, 'Tasikmalaya': 610, 'Purwokerto': 390, 'Tegal': 365, 'Pekalongan': 315, 'Semarang': 230, 'Kendal': 240, 'Purbalingga': 375, 'Temanggung': 215, 'Wonosobo': 245, 'Banjarnegara': 340, 'Banyumas': 385, 'Magelang': 195, 'Boyolali': 155, 'Salatiga': 180, 'Solo': 125, 'Klaten': 140, 'Sragen': 110, 'Yogyakarta': 170, 'Demak': 250, 'Kudus': 265, 'Jepara': 295, 'Pati': 285, 'Ngawi': 80, 'Madiun': 50, 'Surabaya': 155, 'Kediri': 35, 'Jombang': 75, 'Mojokerto': 100, 'Sidoarjo': 125, 'Gresik': 155, 'Lamongan': 135, 'Tuban': 175, 'Malang': 95, 'Tulungagung': 0, 'Trenggalek': 30, 'Pacitan': 65, 'Blitar': 35, 'Batu': 105, 'Probolinggo': 165, 'Lumajang': 155, 'Jember': 205, 'Situbondo': 255, 'Bondowoso': 235, 'Banyuwangi': 315},
    'Trenggalek': {'Jakarta': 720, 'Tangerang': 735, 'Bogor': 750, 'Bandung': 675, 'Cianjur': 715, 'Serang': 785, 'Cirebon': 490, 'Purwakarta': 645, 'Tasikmalaya': 640, 'Purwokerto': 420, 'Tegal': 395, 'Pekalongan': 345, 'Semarang': 260, 'Kendal': 270, 'Purbalingga': 405, 'Temanggung': 245, 'Wonosobo': 275, 'Banjarnegara': 370, 'Banyumas': 415, 'Magelang': 225, 'Boyolali': 185, 'Salatiga': 210, 'Solo': 155, 'Klaten': 170, 'Sragen': 140, 'Yogyakarta': 200, 'Demak': 280, 'Kudus': 295, 'Jepara': 325, 'Pati': 315, 'Ngawi': 110, 'Madiun': 80, 'Surabaya': 185, 'Kediri': 50, 'Jombang': 95, 'Mojokerto': 120, 'Sidoarjo': 145, 'Gresik': 175, 'Lamongan': 165, 'Tuban': 205, 'Malang': 105, 'Tulungagung': 30, 'Trenggalek': 0, 'Pacitan': 40, 'Blitar': 55, 'Batu': 115, 'Probolinggo': 180, 'Lumajang': 175, 'Jember': 225, 'Situbondo': 275, 'Bondowoso': 255, 'Banyuwangi': 335},
    'Pacitan': {'Jakarta': 740, 'Tangerang': 755, 'Bogor': 770, 'Bandung': 695, 'Cianjur': 735, 'Serang': 805, 'Cirebon': 510, 'Purwakarta': 665, 'Tasikmalaya': 660, 'Purwokerto': 440, 'Tegal': 415, 'Pekalongan': 365, 'Semarang': 280, 'Kendal': 290, 'Purbalingga': 425, 'Temanggung': 265, 'Wonosobo': 295, 'Banjarnegara': 390, 'Banyumas': 435, 'Magelang': 245, 'Boyolali': 205, 'Salatiga': 230, 'Solo': 175, 'Klaten': 190, 'Sragen': 160, 'Yogyakarta': 220, 'Demak': 300, 'Kudus': 315, 'Jepara': 345, 'Pati': 335, 'Ngawi': 130, 'Madiun': 100, 'Surabaya': 240, 'Kediri': 95, 'Jombang': 145, 'Mojokerto': 170, 'Sidoarjo': 195, 'Gresik': 225, 'Lamongan': 200, 'Tuban': 225, 'Malang': 155, 'Tulungagung': 65, 'Trenggalek': 40, 'Pacitan': 0, 'Blitar': 90, 'Batu': 165, 'Probolinggo': 220, 'Lumajang': 215, 'Jember': 265, 'Situbondo': 315, 'Bondowoso': 295, 'Banyuwangi': 375},
    'Blitar': {'Jakarta': 700, 'Tangerang': 715, 'Bogor': 730, 'Bandung': 655, 'Cianjur': 695, 'Serang': 765, 'Cirebon': 470, 'Purwakarta': 625, 'Tasikmalaya': 620, 'Purwokerto': 400, 'Tegal': 375, 'Pekalongan': 325, 'Semarang': 240, 'Kendal': 250, 'Purbalingga': 385, 'Temanggung': 225, 'Wonosobo': 255, 'Banjarnegara': 350, 'Banyumas': 395, 'Magelang': 205, 'Boyolali': 165, 'Salatiga': 190, 'Solo': 135, 'Klaten': 150, 'Sragen': 120, 'Yogyakarta': 180, 'Demak': 260, 'Kudus': 275, 'Jepara': 305, 'Pati': 295, 'Ngawi': 90, 'Madiun': 60, 'Surabaya': 165, 'Kediri': 40, 'Jombang': 85, 'Mojokerto': 110, 'Sidoarjo': 135, 'Gresik': 165, 'Lamongan': 145, 'Tuban': 185, 'Malang': 85, 'Tulungagung': 35, 'Trenggalek': 55, 'Pacitan': 90, 'Blitar': 0, 'Batu': 95, 'Probolinggo': 150, 'Lumajang': 145, 'Jember': 195, 'Situbondo': 245, 'Bondowoso': 225, 'Banyuwangi': 305},
    'Batu': {'Jakarta': 830, 'Tangerang': 845, 'Bogor': 860, 'Bandung': 780, 'Cianjur': 820, 'Serang': 895, 'Cirebon': 595, 'Purwakarta': 750, 'Tasikmalaya': 745, 'Purwokerto': 525, 'Tegal': 500, 'Pekalongan': 450, 'Semarang': 370, 'Kendal': 380, 'Purbalingga': 510, 'Temanggung': 355, 'Wonosobo': 385, 'Banjarnegara': 475, 'Banyumas': 520, 'Magelang': 335, 'Boyolali': 295, 'Salatiga': 320, 'Solo': 270, 'Klaten': 285, 'Sragen': 255, 'Yogyakarta': 310, 'Demak': 340, 'Kudus': 325, 'Jepara': 355, 'Pati': 345, 'Ngawi': 225, 'Madiun': 195, 'Surabaya': 100, 'Kediri': 90, 'Jombang': 105, 'Mojokerto': 80, 'Sidoarjo': 95, 'Gresik': 120, 'Lamongan': 135, 'Tuban': 175, 'Malang': 20, 'Tulungagung': 105, 'Trenggalek': 115, 'Pacitan': 165, 'Blitar': 95, 'Batu': 0, 'Probolinggo': 70, 'Lumajang': 95, 'Jember': 145, 'Situbondo': 195, 'Bondowoso': 165, 'Banyuwangi': 245},
    'Probolinggo': {'Jakarta': 900, 'Tangerang': 915, 'Bogor': 930, 'Bandung': 850, 'Cianjur': 890, 'Serang': 965, 'Cirebon': 665, 'Purwakarta': 820, 'Tasikmalaya': 815, 'Purwokerto': 595, 'Tegal': 570, 'Pekalongan': 520, 'Semarang': 440, 'Kendal': 450, 'Purbalingga': 580, 'Temanggung': 425, 'Wonosobo': 455, 'Banjarnegara': 545, 'Banyumas': 590, 'Magelang': 405, 'Boyolali': 365, 'Salatiga': 390, 'Solo': 340, 'Klaten': 355, 'Sragen': 325, 'Yogyakarta': 380, 'Demak': 410, 'Kudus': 395, 'Jepara': 425, 'Pati': 415, 'Ngawi': 295, 'Madiun': 265, 'Surabaya': 100, 'Kediri': 155, 'Jombang': 160, 'Mojokerto': 135, 'Sidoarjo': 115, 'Gresik': 120, 'Lamongan': 170, 'Tuban': 210, 'Malang': 60, 'Tulungagung': 165, 'Trenggalek': 180, 'Pacitan': 220, 'Blitar': 150, 'Batu': 70, 'Probolinggo': 0, 'Lumajang': 50, 'Jember': 85, 'Situbondo': 100, 'Bondowoso': 95, 'Banyuwangi': 175},
    'Lumajang': {'Jakarta': 920, 'Tangerang': 935, 'Bogor': 950, 'Bandung': 870, 'Cianjur': 910, 'Serang': 985, 'Cirebon': 685, 'Purwakarta': 840, 'Tasikmalaya': 835, 'Purwokerto': 615, 'Tegal': 590, 'Pekalongan': 540, 'Semarang': 460, 'Kendal': 470, 'Purbalingga': 600, 'Temanggung': 445, 'Wonosobo': 475, 'Banjarnegara': 565, 'Banyumas': 610, 'Magelang': 425, 'Boyolali': 385, 'Salatiga': 410, 'Solo': 360, 'Klaten': 375, 'Sragen': 345, 'Yogyakarta': 400, 'Demak': 430, 'Kudus': 415, 'Jepara': 445, 'Pati': 435, 'Ngawi': 315, 'Madiun': 285, 'Surabaya': 170, 'Kediri': 140, 'Jombang': 175, 'Mojokerto': 150, 'Sidoarjo': 140, 'Gresik': 170, 'Lamongan': 200, 'Tuban': 240, 'Malang': 85, 'Tulungagung': 155, 'Trenggalek': 175, 'Pacitan': 215, 'Blitar': 145, 'Batu': 95, 'Probolinggo': 50, 'Lumajang': 0, 'Jember': 50, 'Situbondo': 100, 'Bondowoso': 65, 'Banyuwangi': 150},
    'Jember': {'Jakarta': 970, 'Tangerang': 985, 'Bogor': 1000, 'Bandung': 920, 'Cianjur': 960, 'Serang': 1035, 'Cirebon': 735, 'Purwakarta': 890, 'Tasikmalaya': 885, 'Purwokerto': 665, 'Tegal': 640, 'Pekalongan': 590, 'Semarang': 510, 'Kendal': 520, 'Purbalingga': 650, 'Temanggung': 495, 'Wonosobo': 525, 'Banjarnegara': 615, 'Banyumas': 660, 'Magelang': 475, 'Boyolali': 435, 'Salatiga': 460, 'Solo': 410, 'Klaten': 425, 'Sragen': 395, 'Yogyakarta': 450, 'Demak': 480, 'Kudus': 465, 'Jepara': 495, 'Pati': 485, 'Ngawi': 365, 'Madiun': 335, 'Surabaya': 220, 'Kediri': 190, 'Jombang': 225, 'Mojokerto': 200, 'Sidoarjo': 190, 'Gresik': 220, 'Lamongan': 250, 'Tuban': 290, 'Malang': 135, 'Tulungagung': 205, 'Trenggalek': 225, 'Pacitan': 265, 'Blitar': 195, 'Batu': 145, 'Probolinggo': 85, 'Lumajang': 50, 'Jember': 0, 'Situbondo': 60, 'Bondowoso': 40, 'Banyuwangi': 100},
    'Situbondo': {'Jakarta': 1020, 'Tangerang': 1035, 'Bogor': 1050, 'Bandung': 970, 'Cianjur': 1010, 'Serang': 1085, 'Cirebon': 785, 'Purwakarta': 940, 'Tasikmalaya': 935, 'Purwokerto': 715, 'Tegal': 690, 'Pekalongan': 640, 'Semarang': 560, 'Kendal': 570, 'Purbalingga': 700, 'Temanggung': 545, 'Wonosobo': 575, 'Banjarnegara': 665, 'Banyumas': 710, 'Magelang': 525, 'Boyolali': 485, 'Salatiga': 510, 'Solo': 460, 'Klaten': 475, 'Sragen': 445, 'Yogyakarta': 500, 'Demak': 530, 'Kudus': 515, 'Jepara': 545, 'Pati': 535, 'Ngawi': 415, 'Madiun': 385, 'Surabaya': 235, 'Kediri': 240, 'Jombang': 275, 'Mojokerto': 250, 'Sidoarjo': 240, 'Gresik': 270, 'Lamongan': 300, 'Tuban': 340, 'Malang': 185, 'Tulungagung': 255, 'Trenggalek': 275, 'Pacitan': 315, 'Blitar': 245, 'Batu': 195, 'Probolinggo': 100, 'Lumajang': 100, 'Jember': 60, 'Situbondo': 0, 'Bondowoso': 50, 'Banyuwangi': 90},
    'Bondowoso': {'Jakarta': 1000, 'Tangerang': 1015, 'Bogor': 1030, 'Bandung': 950, 'Cianjur': 990, 'Serang': 1065, 'Cirebon': 765, 'Purwakarta': 920, 'Tasikmalaya': 915, 'Purwokerto': 695, 'Tegal': 670, 'Pekalongan': 620, 'Semarang': 540, 'Kendal': 550, 'Purbalingga': 680, 'Temanggung': 525, 'Wonosobo': 555, 'Banjarnegara': 645, 'Banyumas': 690, 'Magelang': 505, 'Boyolali': 465, 'Salatiga': 490, 'Solo': 440, 'Klaten': 455, 'Sragen': 425, 'Yogyakarta': 480, 'Demak': 510, 'Kudus': 495, 'Jepara': 525, 'Pati': 515, 'Ngawi': 395, 'Madiun': 365, 'Surabaya': 215, 'Kediri': 220, 'Jombang': 255, 'Mojokerto': 230, 'Sidoarjo': 220, 'Gresik': 250, 'Lamongan': 280, 'Tuban': 320, 'Malang': 155, 'Tulungagung': 235, 'Trenggalek': 255, 'Pacitan': 295, 'Blitar': 225, 'Batu': 165, 'Probolinggo': 95, 'Lumajang': 65, 'Jember': 40, 'Situbondo': 50, 'Bondowoso': 0, 'Banyuwangi': 80},
    'Banyuwangi': {'Jakarta': 1080, 'Tangerang': 1095, 'Bogor': 1110, 'Bandung': 1030, 'Cianjur': 1070, 'Serang': 1145, 'Cirebon': 845, 'Purwakarta': 1000, 'Tasikmalaya': 995, 'Purwokerto': 775, 'Tegal': 750, 'Pekalongan': 700, 'Semarang': 620, 'Kendal': 630, 'Purbalingga': 760, 'Temanggung': 605, 'Wonosobo': 635, 'Banjarnegara': 725, 'Banyumas': 770, 'Magelang': 585, 'Boyolali': 545, 'Salatiga': 570, 'Solo': 520, 'Klaten': 535, 'Sragen': 505, 'Yogyakarta': 560, 'Demak': 590, 'Kudus': 575, 'Jepara': 605, 'Pati': 595, 'Ngawi': 475, 'Madiun': 445, 'Surabaya': 295, 'Kediri': 300, 'Jombang': 335, 'Mojokerto': 310, 'Sidoarjo': 300, 'Gresik': 330, 'Lamongan': 360, 'Tuban': 400, 'Malang': 235, 'Tulungagung': 315, 'Trenggalek': 335, 'Pacitan': 375, 'Blitar': 305, 'Batu': 245, 'Probolinggo': 175, 'Lumajang': 150, 'Jember': 100, 'Situbondo': 90, 'Bondowoso': 80, 'Banyuwangi': 0}
}


# Heuristik A* diperluas untuk SEMUA 52 kota
city_coords = {
    # Jawa Barat
    'Jakarta': (0, 0),
    'Tangerang': (-10, 10),
    'Serang': (-80, 5),
    'Bogor': (20, -50),
    'Cianjur': (60, -50),
    'Purwakarta': (70, -20),
    'Bandung': (100, -50),
    'Cirebon': (200, 10),
    'Tasikmalaya': (150, -80),
    
    # Jawa Tengah (Barat/Tengah)
    'Tegal': (280, 20),
    'Pekalongan': (320, 20),
    'Purwokerto': (300, -20),
    'Banyumas': (305, -25),
    'Purbalingga': (310, -30),
    'Banjarnegara': (330, -35),
    'Wonosobo': (360, -30),
    'Temanggung': (370, -20),
    'Kendal': (330, 20),
    'Semarang': (350, 20),
    'Magelang': (380, -25),
    'Yogyakarta': (400, -30),
    'Salatiga': (380, 0),
    'Boyolali': (430, -10),
    'Solo': (450, 10),
    'Klaten': (420, -20),
    'Sragen': (480, 15),

    # Jawa Tengah (Pantura Timur)
    'Demak': (370, 30),
    'Kudus': (390, 35),
    'Jepara': (395, 50),
    'Pati': (410, 35),
    
    # Jawa Timur (Barat/Tengah)
    'Ngawi': (510, 10),
    'Madiun': (530, -10),
    'Pacitan': (540, -90),
    'Trenggalek': (580, -80),
    'Tulungagung': (600, -70),
    'Kediri': (590, -50),
    'Blitar': (610, -75),
    
    # Jawa Timur (Area Surabaya)
    'Tuban': (580, 40),
    'Lamongan': (600, 45),
    'Gresik': (610, 55),
    'Surabaya': (600, 50),
    'Sidoarjo': (605, 40),
    'Mojokerto': (580, 30),
    'Jombang': (570, 25),
    
    # Jawa Timur (Area Malang)
    'Malang': (650, 0),
    'Batu': (645, 5),
    
    # Jawa Timur (Timur/Tapal Kuda)
    'Probolinggo': (710, 20),
    'Lumajang': (720, -10),
    'Jember': (770, -10),
    'Bondowoso': (800, 10),
    'Situbondo': (820, 25),
    'Banyuwangi': (870, 0)
}

# Konversi koordinat ke DataFrame untuk plotting
coords_df = pd.DataFrame.from_dict(city_coords, orient='index', columns=['x', 'y'])
coords_df['Kota'] = coords_df.index


# Fungsi dibuat lebih aman dengan .get()
def euclidean_distance(city1, city2):
    """Heuristik untuk A*"""
    x1, y1 = city_coords.get(city1, (0, 0)) 
    x2, y2 = city_coords.get(city2, (0, 0))
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

# ... (Semua fungsi algoritma: nearest_neighbor, brute_force, genetic_algorithm, astar_tsp, chinese_postman) ...
# ... Biarkan semua fungsi ini apa adanya ...
# Algoritma Nearest Neighbor
def nearest_neighbor(start, destinations):
    route = [start]
    current = start
    remaining = destinations.copy()
    total_distance = 0
    
    while remaining:
        nearest = None
        min_distance = float('inf')
        
        for city in remaining:
            dist = distance_matrix[current][city]
            if dist < min_distance:
                min_distance = dist
                nearest = city
        
        route.append(nearest)
        total_distance += min_distance
        current = nearest
        remaining.remove(nearest)
    
    total_distance += distance_matrix[current][start]
    route.append(start)
    
    return route, total_distance

# Algoritma Brute Force
def brute_force(start, destinations):
    from itertools import permutations
    
    min_distance = float('inf')
    best_route = None
    
    for perm in permutations(destinations):
        route = [start] + list(perm)
        distance = 0
        
        for i in range(len(route) - 1):
            distance += distance_matrix[route[i]][route[i + 1]]
        distance += distance_matrix[route[-1]][start]
        
        if distance < min_distance:
            min_distance = distance
            best_route = route
    
    best_route.append(start)
    return best_route, min_distance

# Algoritma Genetic
def genetic_algorithm(start, destinations):
    population_size = 50
    generations = 100
    mutation_rate = 0.1
    
    def create_chromosome():
        shuffled = destinations.copy()
        random.shuffle(shuffled)
        return [start] + shuffled
    
    def calculate_fitness(chromosome):
        distance = 0
        for i in range(len(chromosome) - 1):
            distance += distance_matrix[chromosome[i]][chromosome[i + 1]]
        distance += distance_matrix[chromosome[-1]][start]
        return 1 / distance
    
    population = [create_chromosome() for _ in range(population_size)]
    
    for gen in range(generations):
        population.sort(key=calculate_fitness, reverse=True)
        new_population = population[:10]
        
        while len(new_population) < population_size:
            parent1 = population[random.randint(0, 19)]
            parent2 = population[random.randint(0, 19)]
            
            cut_point = random.randint(1, len(destinations) - 1)
            child = [start]
            first_part = parent1[1:cut_point + 1]
            child.extend(first_part)
            
            for city in parent2[1:]:
                if city not in child:
                    child.append(city)
            
            if random.random() < mutation_rate and len(child) > 3:
                i = random.randint(1, len(child) - 2)
                j = random.randint(1, len(child) - 2)
                child[i], child[j] = child[j], child[i]
            
            new_population.append(child)
        
        population = new_population
    
    best = population[0]
    total_distance = 0
    for i in range(len(best) - 1):
        total_distance += distance_matrix[best[i]][best[i + 1]]
    total_distance += distance_matrix[best[-1]][start]
    
    return best + [start], total_distance

# Algoritma A* (A-Star)
def astar_tsp(start, destinations):
    all_cities = [start] + destinations
    n = len(all_cities)
    start_state = (0, 0, start, (start,), [start])
    pq = [start_state]
    visited_states = set()
    
    while pq:
        f_score, g_score, current, visited_tuple, path = heapq.heappop(pq)
        
        if len(visited_tuple) == n:
            final_distance = g_score + distance_matrix[current][start]
            final_path = path + [start]
            return final_path, final_distance
        
        state_key = (current, visited_tuple)
        if state_key in visited_states:
            continue
        visited_states.add(state_key)
        
        for next_city in all_cities:
            if next_city not in visited_tuple:
                new_g = g_score + distance_matrix[current][next_city]
                unvisited = [c for c in all_cities if c not in visited_tuple and c != next_city]
                h_score = 0
                if unvisited:
                    min_to_unvisited = min(euclidean_distance(next_city, c) for c in unvisited)
                    min_to_start = min(euclidean_distance(c, start) for c in unvisited + [next_city])
                    h_score = min_to_unvisited + min_to_start + len(unvisited) 
                else:
                    h_score = euclidean_distance(next_city, start)
                
                new_f = new_g + h_score
                new_visited = visited_tuple + (next_city,)
                new_path = path + [next_city]
                
                heapq.heappush(pq, (new_f, new_g, next_city, new_visited, new_path))
    
    return nearest_neighbor(start, destinations)

# Chinese Postman Problem (CPP)
def chinese_postman(start, destinations):
    all_cities = [start] + destinations
    edges = []
    for i, city1 in enumerate(all_cities):
        for city2 in all_cities[i+1:]:
            edges.append((city1, city2, distance_matrix[city1][city2]))
    
    degree = {city: 0 for city in all_cities}
    for city1, city2, dist in edges:
        degree[city1] += 1
        degree[city2] += 1
    
    odd_nodes = [city for city in all_cities if degree[city] % 2 == 1]
    
    if not odd_nodes:
        route = [start]
        current = start
        unvisited = set(destinations)
        total_distance = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            total_distance += distance_matrix[current][nearest]
            current = nearest
            unvisited.remove(nearest)
        
        total_distance += distance_matrix[current][start]
        route.append(start)
        return route, total_distance
    
    matched_pairs = []
    odd_nodes_copy = odd_nodes.copy()
    
    while len(odd_nodes_copy) >= 2:
        node1 = odd_nodes_copy.pop(0)
        min_dist = float('inf')
        closest = None
        for node2 in odd_nodes_copy:
            dist = distance_matrix[node1][node2]
            if dist < min_dist:
                min_dist = dist
                closest = node2
        if closest:
            matched_pairs.append((node1, closest, min_dist))
            odd_nodes_copy.remove(closest)
    
    base_route, base_distance = nearest_neighbor(start, destinations)
    additional_distance = sum(dist for _, _, dist in matched_pairs)
    
    return base_route, base_distance + additional_distance * 0.3  # Faktor koreksi


# Fungsi baru untuk plot Matplotlib
def plot_route_matplotlib(route_list, all_coords_df, algo_name):
    """
    Membuat plot rute menggunakan Matplotlib berdasarkan koordinat heuristik.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 1. Plot semua 52 kota sebagai latar belakang
    ax.scatter(all_coords_df['x'], all_coords_df['y'], color='grey', alpha=0.3, s=30, label='Kota Lain')
    
    # 2. Ambil koordinat untuk rute yang dipilih
    route_coords = all_coords_df.loc[route_list].copy()
    
    # 3. Plot garis rute (merah tebal)
    for i in range(len(route_list) - 1):
        city1_data = route_coords.iloc[i]
        city2_data = route_coords.iloc[i+1]
        
        # Gambar garis
        ax.plot([city1_data['x'], city2_data['x']], 
                [city1_data['y'], city2_data['y']], 
                color='red', 
                linewidth=2, 
                marker='o', 
                markersize=5,
                alpha=0.8)
        
        # Tambahkan panah penunjuk arah
        ax.annotate("",
                    xy=(city2_data['x'], city2_data['y']), 
                    xytext=(city1_data['x'], city1_data['y']),
                    arrowprops=dict(arrowstyle="->", color="red", lw=0.5, shrinkA=5, shrinkB=5))

    # 4. Tandai kota awal/depot (hijau)
    start_coords = route_coords.iloc[0]
    ax.scatter(start_coords['x'], start_coords['y'], color='green', s=200, zorder=5, label=f'Start/Depot ({route_list[0]})', edgecolors='black')
    
    # 5. Tandai kota tujuan (biru)
    dest_coords = route_coords.iloc[1:-1] # Semua kecuali start dan end
    if not dest_coords.empty:
        ax.scatter(dest_coords['x'], dest_coords['y'], color='blue', s=80, zorder=4, label='Tujuan', edgecolors='black')

    # 6. Tambahkan label nama kota pada rute
    for city, row in route_coords.iloc[:-1].iterrows(): # Semua kecuali kembali ke start
        ax.text(row['x'] + 5, row['y'] + 2, city, fontsize=9, ha='left')
    
    # Styling plot
    ax.set_title(f"Visualisasi Rute - {algo_name}", fontsize=16)
    ax.set_xlabel("Posisi X (Estimasi Geografis)")
    ax.set_ylabel("Posisi Y (Estimasi Geografis)")
    ax.legend(loc='best')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Hapus axis Y jika nilainya negatif (tampilan peta lebih baik)
    ax.set_ylim(bottom=min(all_coords_df['y'].min(), 0) - 10) # Beri sedikit padding
    
    plt.tight_layout()
    return fig


# Header
st.title("🚚 Optimasi Rute Pengiriman Kurir")
st.markdown("**Project JTE - KKA**")
st.divider()

# Layout 2 kolom
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Konfigurasi Pengiriman")
    
    start_city = st.selectbox(
        "Kota Awal (Depot)",
        cities,
        index=0
    )
    
    available_cities = [c for c in cities if c != start_city]
    selected_cities = st.multiselect(
        "Kota Tujuan (pilih beberapa)",
        available_cities,
        default=['Bandung', 'Semarang', 'Surabaya'] if start_city == 'Jakarta' else available_cities[:3]
    )
    
    algorithm = st.selectbox(
        "Algoritma",
        ["Nearest Neighbor (Greedy)", 
         "Brute Force (Optimal)", 
         "Genetic Algorithm",
         "A* (A-Star)",
         "Chinese Postman Problem"]
    )
    
    algorithm_info = {
        "Nearest Neighbor (Greedy)": {
            "desc": "Memilih kota terdekat pada setiap langkah. Cepat tapi tidak selalu optimal.",
            "complexity": "O(n²)"
        },
        "Brute Force (Optimal)": {
            "desc": "Mencoba semua kemungkinan rute. Menjamin solusi optimal untuk kota sedikit.",
            "complexity": "O(n!)"
        },
        "Genetic Algorithm": {
            "desc": "Menggunakan evolusi populasi solusi. Baik untuk kota banyak, mendekati optimal.",
            "complexity": "O(g × p × n)"
        },
        "A* (A-Star)": {
            "desc": "Algoritma pencarian informed dengan heuristik. Efisien dan mendekati optimal.",
            "complexity": "O(b^d)"
        },
        "Chinese Postman Problem": {
            "desc": "Mencari rute terpendek yang melewati semua edge minimal sekali. Optimal untuk graf Eulerian.",
            "complexity": "O(n³)"
        }
    }
    
    st.info(f"**{algorithm}**\n\n{algorithm_info[algorithm]['desc']}\n\nKompleksitas: `{algorithm_info[algorithm]['complexity']}`")
    
    calculate_btn = st.button("🚀 Hitung Rute Optimal", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Hasil Optimasi")
    
    if calculate_btn and selected_cities:
        with st.spinner("Menghitung rute optimal..."):
            route = []
            total_distance = 0
            
            if algorithm == "Nearest Neighbor (Greedy)":
                route, total_distance = nearest_neighbor(start_city, selected_cities)
            elif algorithm == "Brute Force (Optimal)":
                if len(selected_cities) > 8: 
                    st.error("Brute Force tidak disarankan untuk > 8 kota. Pilih algoritma lain.")
                else:
                    route, total_distance = brute_force(start_city, selected_cities)
            elif algorithm == "Genetic Algorithm":
                route, total_distance = genetic_algorithm(start_city, selected_cities)
            elif algorithm == "A* (A-Star)":
                route, total_distance = astar_tsp(start_city, selected_cities)
            else:  # Chinese Postman Problem
                route, total_distance = chinese_postman(start_city, selected_cities)
            
            if route: 
                st.success("✅ Rute optimal berhasil dihitung!")
                
                st.markdown("### 📍 Visualisasi Rute (Estimasi)")
                fig = plot_route_matplotlib(route, coords_df, algorithm)
                st.pyplot(fig)
                
                st.metric(
                    label="Total Jarak Tempuh",
                    value=f"{total_distance:.0f} km"
                )
                
                st.markdown("### 🗺️ Urutan Rute Perjalanan:")
                for i, city in enumerate(route):
                    if i < len(route) - 1:
                        distance = distance_matrix[city][route[i + 1]]
                        st.markdown(f"**{i + 1}.** {city} ➡️ ({distance} km)")
                    else:
                        st.markdown(f"**{i + 1}.** {city} (Selesai)")
                
                st.info(f"""
                **Informasi Rute:**
                - Jumlah kota: {len(route) - 1} kota
                - Algoritma: {algorithm}
                - Kompleksitas: {algorithm_info[algorithm]['complexity']}
                """)
    
    elif calculate_btn and not selected_cities:
        st.warning("⚠️ Pilih minimal 1 kota tujuan!")
    else:
        st.info("👆 Pilih kota tujuan dan klik 'Hitung Rute Optimal'")

# Menggunakan Tabs untuk Matriks dan Peta Heuristik
st.divider()
st.subheader("📈 Data Jarak & Peta Heuristik")

tab1, tab2 = st.tabs(["📋 Matriks Jarak (km)", "🗺️ Peta Heuristik (Titik Kota)"])

with tab1:
    st.markdown("Matriks Jarak Antar Kota (km). *Highlight* hijau untuk jarak < 200 km.")
    
    df = pd.DataFrame(distance_matrix).T
    df = df[cities]

    def highlight_short_distance(val):
        if isinstance(val, (int, float)) and val > 0 and val < 200:
            return 'background-color: #d4edda; font-weight: bold'
        return ''

    styled_df = df.style.map(highlight_short_distance)
    st.dataframe(styled_df, height=400) 

with tab2:
    st.markdown("Peta Titik Relatif 52 Kota (Digunakan untuk Heuristik A*)")
    
    chart = alt.Chart(coords_df).mark_circle(size=80).encode(
        x=alt.X('x:Q', title='Posisi X (Estimasi Timur)'),
        y=alt.Y('y:Q', title='Posisi Y (Estimasi Selatan)'),
        tooltip=['Kota', 'x', 'y'],
    ).properties(
        title="Peta Relatif Kota (Titik Heuristik)"
    ).interactive() 

    text = chart.mark_text(
        align='left',
        baseline='middle',
        dx=7, 
        fontSize=10
    ).encode(
        text='Kota'
    )

    final_chart = chart + text
    
    st.altair_chart(final_chart, use_container_width=True)


# Perbandingan Algoritma
st.divider()
st.subheader("🔬 Perbandingan Algoritma")

if st.button("Bandingkan Semua Algoritma", use_container_width=True):
    if selected_cities:
        results = {} 
        if len(selected_cities) > 8:
            st.warning("⚠️ Perbandingan Brute Force dilewati karena > 8 kota (terlalu lama).")
            with st.spinner("Membandingkan algoritma (tanpa Brute Force)..."):
                results["Nearest Neighbor"] = nearest_neighbor(start_city, selected_cities)
                results["Genetic Algorithm"] = genetic_algorithm(start_city, selected_cities)
                results["A*"] = astar_tsp(start_city, selected_cities)
                results["Chinese Postman"] = chinese_postman(start_city, selected_cities)
        else:
            with st.spinner("Membandingkan semua algoritma..."):
                results["Nearest Neighbor"] = nearest_neighbor(start_city, selected_cities)
                results["Brute Force"] = brute_force(start_city, selected_cities)
                results["Genetic Algorithm"] = genetic_algorithm(start_city, selected_cities)
                results["A*"] = astar_tsp(start_city, selected_cities)
                results["Chinese Postman"] = chinese_postman(start_city, selected_cities)
        
        # Buat tabel perbandingan
        comparison_data = []
        for algo_name, (route, distance) in results.items():
            comparison_data.append({
                "Algoritma": algo_name,
                "Total Jarak (km)": f"{distance:.0f}",
                "Jumlah Kota": len(route) - 1,
                "Rute": " → ".join(route[:4]) + "..." if len(route) > 4 else " → ".join(route)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df["Total Jarak (km)"] = comparison_df["Total Jarak (km)"].astype(float)
        comparison_df = comparison_df.sort_values(by="Total Jarak (km)")
        
        # <<< MODIFIKASI: Dikembalikan ke st.dataframe
        st.dataframe(comparison_df, use_container_width=True)
        # MODIFIKASI SELESAI >>>

        # Algoritma terbaik
        best_algo = min(results.items(), key=lambda x: x[1][1])
        st.success(f"🏆 **Algoritma Terbaik:** {best_algo[0]} dengan jarak {best_algo[1][1]:.0f} km")
    else:
        st.warning("⚠️ Pilih kota tujuan terlebih dahulu!")

st.divider()
st.caption("Kurir JTE | Project KKA")