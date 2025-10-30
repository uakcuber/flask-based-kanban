# Kanban Pano Uygulaması

Flask tabanlı bir görev yönetimi uygulaması. Kullanıcılar kayıt olup giriş yaparak kendi Kanban panolarını oluşturabilir, görevlerini listeler halinde organize edebilir.

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Kişiye özel Kanban panoları
- Görev kartları (başlık, açıklama, öncelik)
- Liste bazlı görev organizasyonu
- REST API desteği
- SQLite veritabanı

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı başlatın:
```bash
python api.py
```

3. Tarayıcıda açın:
   - Ana sayfa: http://127.0.0.1:5000
   - API: http://127.0.0.1:5000/api

## Kullanım

1. Ana sayfadan kayıt ol
2. Giriş yap
3. Pano oluştur
4. Listeler ekle (Yapılacak, Devam Eden, Tamamlandı vb.)
5. Görev kartları ekleyip yönet






