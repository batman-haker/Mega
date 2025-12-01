# FRED Data Management Scripts

Skrypty do zarządzania danymi historycznymi FRED w bazie danych.

## Struktura

```
scripts/
├── README.md                  (ten plik)
└── update_fred_daily.py      (aktualizacja codzienna - 7 dni)
```

## Quick Start

### 1. Pierwsze uruchomienie - pobierz 730 dni

```bash
cd stockanalyzer
py collectors/fred_data_manager.py init --days 730 --force
```

To zajmie ~2 minuty i pobierze **6,850+ punktów danych** (20 serii x ~500 punktów każda).

### 2. Codzienna aktualizacja - tylko ostatnie 7 dni

```bash
cd stockanalyzer
py scripts/update_fred_daily.py
```

To zajmie ~10 sekund i zaktualizuje tylko nowe dane.

## Windows Task Scheduler - Automatyzacja

### Setup (jednorazowo):

1. Otwórz **Task Scheduler** (Windows + R -> `taskschd.msc`)
2. Kliknij **"Create Basic Task"**
3. Nazwa: `FRED Data Daily Update`
4. Trigger: **Daily**, godzina **9:00 AM** (po otwarciu rynków USA)
5. Action: **Start a program**
   - Program: `py`
   - Arguments: `C:\\MEGABOT\\stockanalyzer\\scripts\\update_fred_daily.py`
   - Start in: `C:\\MEGABOT\\stockanalyzer`
6. Finish!

### Testowanie Task Schedulera:

- Kliknij prawym na task -> **Run**
- Sprawdź logi w `C:\\Windows\\Tasks`

## Sprawdzanie stanu bazy

```bash
cd stockanalyzer
py collectors/fred_data_manager.py stats
```

Output:
```
=== FRED Database Statistics ===
  reserves            :    24 data points
  bank_assets         :   103 data points  ← Kostecki #1!
  sofr                :   498 data points
  vix                 :   516 data points
  ...
```

## MCP Integration (OPCJONALNE)

Możesz też zarządzać danymi FRED przez MCP Server:

```bash
# TODO: Implement MCP server
npx @modelcontextprotocol/inspector python mcp_server_fred.py
```

## Troubleshooting

### Problem: "Błąd pobierania: 'date'"
- Niektóre serie FRED zwracają inną strukturę danych dla ostatnich 7 dni
- To jest bug w `liquidity_monitor.py` - do naprawy
- Większość serii działa poprawnie

### Problem: "No module named 'collectors'"
- Upewnij się że uruchamiasz skrypt z `stockanalyzer/` directory
- Albo dodaj `PYTHONPATH=C:\\MEGABOT\\stockanalyzer`

## Korzyści z tego systemu

1. **100x szybsze ładowanie strony Makro** - czytamy z DB zamiast API
2. **Oszczędność API limits** - zamiast 120 req/min tylko 20 req/day
3. **Pełna historia** - 730 dni danych do analiz Kosteckiego
4. **Automatyzacja** - Task Scheduler robi update codziennie
