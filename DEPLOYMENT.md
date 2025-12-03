# 🚀 MEGABOT - Instrukcja Wdrożenia

## Wdrożenie na Streamlit Cloud (Zalecane)

### Krok 1: Przygotowanie Repozytorium

1. **Upewnij się, że wszystkie zmiany są commitnięte:**
```bash
cd C:\MEGABOT
git status
git add .
git commit -m "Prepare for deployment"
git push
```

2. **Sprawdź czy profile ekspertów są w repozytorium:**
```bash
ls stockanalyzer/data/profiles/*.json
# Powinno pokazać 15 plików JSON
```

### Krok 2: Konfiguracja Streamlit Cloud

1. **Wejdź na:** https://share.streamlit.io/

2. **Zaloguj się przez GitHub**

3. **Kliknij "New app"**

4. **Wybierz:**
   - **Repository:** batman-haker/Mega (lub twoje repo)
   - **Branch:** main
   - **Main file path:** `stockanalyzer/Home.py`

### Krok 3: Dodanie Secrets (API Keys)

1. W Streamlit Cloud kliknij **"Advanced settings"** → **"Secrets"**

2. **Wklej konfigurację secrets:**

```toml
[gemini]
api_key = "TWÓJ_GEMINI_API_KEY"

[fred]
api_key = "TWÓJ_FRED_API_KEY"
```

3. **Gdzie znaleźć API keys:**
   - **Gemini API:** https://ai.google.dev/ (Google AI Studio)
   - **FRED API:** https://fred.stlouisfed.org/docs/api/api_key.html

### Krok 4: Deploy

1. Kliknij **"Deploy!"**

2. Streamlit Cloud automatycznie:
   - Zainstaluje zależności z `requirements.txt`
   - Uruchomi aplikację na `stockanalyzer/Home.py`
   - Przypisze URL: `https://twoja-app.streamlit.app`

3. **Czas wdrożenia:** ~2-5 minut

---

## Alternatywne Opcje Wdrożenia

### Railway.app

1. Wejdź na https://railway.app/
2. Połącz z GitHub repo
3. Ustaw:
   - **Start Command:** `streamlit run stockanalyzer/Home.py --server.port=$PORT`
   - **Secrets:** Dodaj GEMINI_API_KEY i FRED_API_KEY
4. Deploy!

### Heroku

1. Utwórz `Procfile` w głównym katalogu:
```
web: sh -c 'cd stockanalyzer && streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0'
```

2. Deploy:
```bash
heroku create twoja-app
git push heroku main
heroku config:set GEMINI_API_KEY=your_key
```

---

## 📊 Po Wdrożeniu

### Weryfikacja

1. **Sprawdź czy aplikacja działa:**
   - Otwórz URL aplikacji
   - Przetestuj wszystkie strony (Home, 📊 Makro, 🧠 AI Investment Council)

2. **Sprawdź profile ekspertów:**
   - W AI Investment Council wybierz kilku ekspertów
   - Wprowadź ticker (np. AAPL)
   - Zweryfikuj czy opinie się generują

3. **Sprawdź zapisywanie analiz:**
   - Po wygenerowaniu analizy sprawdź czy jest dostępna w historii
   - (Funkcja w przygotowaniu - wymaga dodania UI)

### Monitoring

1. **Logi aplikacji:**
   - Streamlit Cloud: Zakładka "Logs"
   - Railway: Zakładka "Logs"

2. **Użycie API:**
   - Gemini: https://console.cloud.google.com/apis/
   - FRED: Sprawdź limit na https://fred.stlouisfed.org/

---

## 🔧 Troubleshooting

### Problem: "Module not found"
**Rozwiązanie:** Sprawdź czy `requirements.txt` zawiera wszystkie zależności:
```bash
pip freeze > requirements-check.txt
```

### Problem: "API Key not found"
**Rozwiązanie:**
1. Sprawdź czy secrets są dodane w Streamlit Cloud
2. Upewnij się że klucze to: `gemini.api_key` i `fred.api_key`

### Problem: "Profiles not loading"
**Rozwiązanie:** Upewnij się że pliki są w repozytorium:
```bash
git ls-files stockanalyzer/data/profiles/
```

### Problem: "Database error"
**Rozwiązanie:** Streamlit Cloud może mieć problem z zapisem. Użyj st.session_state zamiast SQLite lub skonfiguruj external storage.

---

## 📝 Aktualizacja Aplikacji

```bash
# Lokalne zmiany
cd C:\MEGABOT
git add .
git commit -m "Update: opis zmian"
git push

# Streamlit Cloud automatycznie wykryje zmiany i redeployuje
```

---

## 🌟 Gotowe!

Twoja aplikacja powinna być dostępna pod adresem:
**https://twoja-app.streamlit.app**

**15 ekspertów AI** jest gotowych do analizy! 🎉

---

## Kontakt & Support

- GitHub Issues: https://github.com/batman-haker/Mega/issues
- Dokumentacja Streamlit: https://docs.streamlit.io/
