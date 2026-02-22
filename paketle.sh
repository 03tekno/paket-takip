#!/bin/bash

# Değişkenler
APP_NAME="paket-takip"
VERSION="1.0.0"
DEB_DIR="${APP_NAME}_${VERSION}"

echo "📦 Paketleme süreci başlıyor: $APP_NAME"

# 1. Klasör Yapısını Oluştur
mkdir -p $DEB_DIR/DEBIAN
mkdir -p $DEB_DIR/usr/bin
mkdir -p $DEB_DIR/usr/share/applications
mkdir -p $DEB_DIR/usr/share/pixmaps
mkdir -p $DEB_DIR/usr/share/$APP_NAME

# 2. Python Kodunu ve İkonu Kopyala
cp paket-takip.py $DEB_DIR/usr/share/$APP_NAME/main.py
cp icon.png $DEB_DIR/usr/share/pixmaps/$APP_NAME.png

# 3. Çalıştırılabilir Script Oluştur (/usr/bin/paket-takip)
cat <<EOF > $DEB_DIR/usr/bin/$APP_NAME
#!/bin/bash
python3 /usr/share/$APP_NAME/main.py "\$@"
EOF
chmod +x $DEB_DIR/usr/bin/$APP_NAME

# 4. Control Dosyasını Oluştur (Paket Bilgileri)
cat <<EOF > $DEB_DIR/DEBIAN/control
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Maintainer: mobilturka
Depends: python3, python3-pip, python3-pyqt6, python3-requests
Description: Repology Akilli Paket Takip Sistemi
 Repology API kullanarak dagitimlardaki paket surumlerini sorgulayan GUI araci.
EOF

# 5. Masaüstü Başlatıcıyı Oluştur (.desktop)
cat <<EOF > $DEB_DIR/usr/share/applications/$APP_NAME.desktop
[Desktop Entry]
Name=Paket Takip
Comment=Paket Sürüm Sorgulama
Exec=$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=System;
EOF

# 6. Paketi İnşa Et
dpkg-deb --build $DEB_DIR

echo "✅ İşlem tamam! ${DEB_DIR}.deb dosyası oluşturuldu."