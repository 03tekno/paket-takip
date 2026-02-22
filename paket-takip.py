import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QHeaderView, QLabel, 
                             QLineEdit, QProgressBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

class RepologyTurkce(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Repology - Akıllı Paket Takip Sistemi")
        self.setMinimumSize(QSize(1000, 750))
        
        # Ekranın ortasına yerleştirme fonksiyonunu çağırıyoruz
        self.merkeze_yerlestir()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Üst Arama Alanı
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Paket adını buraya yazın (örn: qmplay2, vlc, ffmpeg)...")
        self.search_input.setFixedHeight(45)
        self.search_input.returnPressed.connect(self.fetch_data)
        
        self.search_btn = QPushButton("Sürümleri Sorgula")
        self.search_btn.setFixedHeight(45)
        self.search_btn.setFixedWidth(150)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.fetch_data)
        
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.layout.addLayout(self.search_layout)

        # Durum Bilgisi
        self.status_label = QLabel("Arama yapmak için bir paket ismi giriniz.")
        self.layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Dağıtım / Sistem", "Depo Bölümü", "Sürüm", "Güncellik Durumu"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QLineEdit { border: 2px solid #dee2e6; border-radius: 10px; padding: 5px 15px; font-size: 14px; }
            QPushButton { background-color: #2ecc71; color: white; border-radius: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #27ae60; }
            QTableWidget { background-color: white; border-radius: 10px; font-family: 'Segoe UI', Arial; }
        """)

    def merkeze_yerlestir(self):
        """Uygulama penceresini ekranın tam ortasına konumlandırır."""
        ekran = self.screen().availableGeometry() # Ekran boyutlarını al
        pencere = self.frameGeometry() # Mevcut pencere boyutlarını al
        merkez_noktasi = ekran.center() # Ekranın merkez noktasını hesapla
        pencere.moveCenter(merkez_noktasi) # Pencereyi merkeze taşı
        self.move(pencere.topLeft()) # Sol üst köşeyi yeni koordinata göre güncelle

    def terim_cevir(self, metin):
        """Teknik terimleri Türkçeye çevirir."""
        if not metin: return "-"
        sozluk = {
            'newest': 'En Güncel',
            'outdated': 'Eski Sürüm',
            'nosuchpkg': 'Paket Yok',
            'untrusted': 'Güvenilmez',
            'obsolete': 'Kullanımdan Kalkmış',
            'unique': 'Tekil Sürüm',
            'incorrect': 'Hatalı Veri',
            'legacy': 'Eski Altyapı (Legacy)',
            'testing': 'Test Sürümü',
            'unstable': 'Kararsız',
            'stable': 'Kararlı',
            'rolling': 'Sürekli Güncel',
            'main': 'Ana Depo',
            'community': 'Topluluk',
            'multilib': 'Çoklu Mimari'
        }
        ham_metin = metin.lower()
        for ing, tr in sozluk.items():
            if ing in ham_metin:
                ham_metin = ham_metin.replace(ing, tr)
        return ham_metin.capitalize()

    def fetch_data(self):
        paket = self.search_input.text().strip().lower()
        if not paket: return

        self.status_label.setText(f"'{paket}' için güncel veriler alınıyor...")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.search_btn.setEnabled(False)
        
        api_url = f"https://repology.org/api/v1/project/{paket}"
        headers = {'User-Agent': 'Mozilla/5.0 (Debian 13; Linux x86_64)'}
        
        try:
            QApplication.processEvents()
            res = requests.get(api_url, headers=headers, timeout=10)
            if res.status_code == 200:
                self.verileri_doldur(res.json())
                self.status_label.setText(f"✅ '{paket}' için en güncel sürümler yukarıda listelendi.")
            elif res.status_code == 404:
                self.table.setRowCount(0)
                self.status_label.setText("❌ Paket bulunamadı.")
            else:
                self.status_label.setText(f"Hata: {res.status_code}")
        except Exception as e:
            self.status_label.setText(f"Bağlantı Hatası: {str(e)}")
        
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)

    def verileri_doldur(self, veri):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        def siralama_anahtari(x):
            durum = x.get('status', '').lower()
            if durum == 'newest': return 0
            if durum == 'outdated': return 1
            return 2

        sirali_veri = sorted(veri, key=siralama_anahtari)

        for item in sirali_veri:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            dagitim = QTableWidgetItem(item.get('visiblename', '-'))
            depo = QTableWidgetItem(self.terim_cevir(item.get('repo', '-')))
            surum = QTableWidgetItem(item.get('version', '-'))
            
            durum_ham = item.get('status', 'unknown')
            durum_tr = self.terim_cevir(durum_ham)
            durum = QTableWidgetItem(durum_tr)

            if durum_ham == 'newest':
                durum.setForeground(QColor("#27ae60"))
                font = QFont()
                font.setBold(True)
                durum.setFont(font)
            elif durum_ham == 'outdated':
                durum.setForeground(QColor("#e74c3c"))

            self.table.setItem(row, 0, dagitim)
            self.table.setItem(row, 1, depo)
            self.table.setItem(row, 2, surum)
            self.table.setItem(row, 3, durum)

        self.table.setSortingEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = RepologyTurkce()
    ex.show()
    sys.exit(app.exec())