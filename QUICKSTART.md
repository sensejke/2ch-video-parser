# ⚡ Быстрый старт - 2ch Video Parser

## 🪟 Windows (1 минута)

```batch
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser
install.bat
run.bat
```

**Готово!** → http://localhost:5000

---

## 🐧 Ubuntu (2 минуты)

```bash
wget https://raw.githubusercontent.com/sensejke/2ch-video-parser/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

**Готово!** → http://localhost:5000

---

## 🐳 Docker (везде)

```bash
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser
docker-compose up -d
```

**Готово!** → http://localhost:5000

---

## 🎯 Что дальше?

1. **Откройте** http://localhost:5000
2. **Выберите** доску (/b/, /mus/, etc.)
3. **Наслаждайтесь** видео! 🎬

---

## 📊 Мониторинг

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)

---

## 🆘 Проблемы?

**Windows:**
```batch
run.bat -Logs
run.bat -Status
```

**Ubuntu:**
```bash
docker-compose logs -f app
docker-compose ps
```

**Docker:**
```bash
docker-compose restart
docker-compose logs app
```

---

*🚀 Приятного использования!* 
