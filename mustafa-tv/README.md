# Mustafa TV — Windows

Electron tabanlı Windows masaüstü canlı yayın oynatıcısı.

## Özellikler
- Sol tarafta kanal listesi, arama, kategori ve favoriler
- M3U dosyası veya URL yükleme
- Aynı kanal adına ait birden fazla M3U girdisini Yayın 1, Yayın 2… olarak gösterme
- Video alanında tam ekran düğmesi ve çift tıklama
- HLS master playlist seviyelerinde Otomatik / 480p / 720p / 1080p seçimi

## EXE oluşturma
GitHub deposunda **Actions → Build Mustafa TV for Windows → Run workflow** seçin. İşlem bitince **Mustafa-TV-Windows** artifact'ini indirin. İçinde kurulum EXE'si ve portable EXE bulunur.

## Yerel geliştirme
```bash
cd mustafa-tv
npm install
npm start
npm run dist
```

Varsayılan M3U: `https://raw.githubusercontent.com/gonenmustafa1-lab/mstfgnn1/main/tv-kanallari.m3u`

Kalite seçimi sadece yayın kaynağının sunduğu HLS seviyeleri arasından yapılır; tek çözünürlüklü bir yayına yazılımla gerçek 1080p eklenemez. Yayınların erişilebilirliği ve üçüncü taraf kaynakların sürekliliği garanti edilmez. Yalnızca erişim izniniz olan yayınları kullanın.
