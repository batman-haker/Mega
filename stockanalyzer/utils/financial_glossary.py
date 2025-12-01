"""
STOCKANALYZER - Financial Glossary (Humorystyczny Przewodnik Finansowy)

Wyjaśnienia wszystkich terminów finansowych w przystępny i zabawny sposób.
Walory edukacyjne + lekki humor = łatwiej zapamiętać!

Użycie:
    from utils.financial_glossary import get_explanation, format_term_with_tooltip
"""

from typing import Dict, Tuple


# ============================================
# GLOSSARY - Wyjaśnienia terminów
# ============================================

FINANCIAL_GLOSSARY: Dict[str, Dict[str, str]] = {
    # === WSKAŹNIKI FRED ===
    'VIX': {
        'full_name': 'Volatility Index',
        'short': 'Miernik strachu na rynku',
        'long': '''
**VIX (Volatility Index)** - znany jako "wskaźnik strachu" 😱

**Co to jest?**
VIX to liczba pokazująca jak bardzo inwestorzy się boją. Im wyższy VIX, tym większa panika.

**Jak to działa?**
- VIX < 15: Spokój, wszyscy się uśmiechają ☀️
- VIX 15-30: Normalne wahania, nic się nie dzieje 😐
- VIX > 30: PANIKA! Ludzie sprzedają wszystko! 🔥

**Fun fact:**
W marcu 2020 (COVID) VIX osiągnął 82! To był poziom "wszyscy krzyczą i uciekają".

**Po co to śledzić?**
Gdy VIX rośnie = akcje spadają (zwykle). Gdy VIX spada = akcje rosną (zwykle).
        ''',
        'emoji': '😱'
    },

    'SOFR': {
        'full_name': 'Secured Overnight Financing Rate',
        'short': 'Stopa overnight dla banków (zabezpieczona)',
        'long': '''
**SOFR (Secured Overnight Financing Rate)** 🏦

**Co to jest?**
To stopa procentowa, po której banki pożyczają sobie nawzajem pieniądze na 1 noc (overnight).

**Dlaczego to ważne?**
To "temperatura" rynku pieniężnego. Jak SOFR rośnie = bankom brakuje kasy, płynność spada.

**SOFR vs IORB:**
Różnica między SOFR a IORB to kluczowy wskaźnik napięć:
- Spread < 10 bps: Wszystko cool 😎
- Spread 15-20 bps: Zaczyna się robić nerwowo 😬
- Spread > 20 bps: REPO STRESS! Płynność wysycha! 🚨

**Kontekst historyczny:**
SOFR zastąpił LIBOR (który był manipulowany przez banki - skandal!).
        ''',
        'emoji': '🏦'
    },

    'IORB': {
        'full_name': 'Interest on Reserve Balances',
        'short': 'Odsetki które FED płaci bankom za trzymanie rezerw',
        'long': '''
**IORB (Interest on Reserve Balances)** 💰

**Co to jest?**
To odsetki, które Federal Reserve PŁACI bankom za trzymanie pieniędzy w Fed.

**Czemu FED płaci bankom?**
To narzędzie kontroli stóp procentowych. IORB to "podłoga" dla stóp - banki nie pożyczą taniej niż IORB.

**Przykład:**
IORB = 5.40% → Bank może dostać 5.40% od Feda za nic
Więc nie pożyczy innym bankom poniżej tej stopy (po co ryzyko?).

**Dan Kostecki Alert:**
Różnica SOFR - IORB to najważniejszy wskaźnik płynności!
        ''',
        'emoji': '💰'
    },

    'YIELD_CURVE': {
        'full_name': '10Y-2Y Treasury Spread',
        'short': 'Różnica między 10-letnimi a 2-letnimi obligacjami USA',
        'long': '''
**Yield Curve (Krzywa dochodowości)** 📈📉

**Co to jest?**
Różnica między oprocentowaniem 10-letnich i 2-letnich obligacji USA.

**Normalnie:**
10Y > 2Y (dodatni spread) = zdrowa ekonomia 🌟
Ludzie chcą więcej za długoterminowe ryzyko.

**Inwersja (Yield Curve < 0):**
10Y < 2Y = ALARM! Recesja blisko! 🚨

**Statystyki:**
Inwersja krzywej poprzedzała KAŻDĄ recesję w USA od 1970!
- 2000: Inwersja → Bańka dot-com pękła
- 2006: Inwersja → Kryzys 2008
- 2022: Inwersja → ... czekamy 🤔

**Czemu tak działa?**
Inwersja = rynek myśli że FED będzie musiał ciąć stopy (recesja = niższe stopy).
        ''',
        'emoji': '📉'
    },

    'M2': {
        'full_name': 'M2 Money Supply',
        'short': 'Ilość pieniędzy w obiegu (gotówka + depozyty + fundusze)',
        'long': '''
**M2 Money Supply** 💵

**Co to jest?**
To cała kasa która krąży w ekonomii:
- M1: Gotówka + konta czekowe (ready to spend)
- M2: M1 + oszczędności + fundusze rynku pieniężnego

**Dlaczego to ważne?**
Więcej pieniędzy = inflacja (zwykle). Mniej pieniędzy = deflacja/recesja.

**COVID Story:**
W 2020-2021 M2 EKSPLODOWAŁO o ~40%!
FED drukował pieniądze jak szalony → Inflacja w 2022: 9%!

**Teraz (2024-2025):**
M2 spada pierwszy raz od Great Depression. QT (Quantitative Tightening) w akcji.

**TL;DR:**
M2 rośnie = party time 🎉 (ale inflacja)
M2 spada = hangover time 🤕 (ale stabilność)
        ''',
        'emoji': '💵'
    },

    'NFCI': {
        'full_name': 'National Financial Conditions Index',
        'short': 'Wskaźnik warunków finansowych (Chicago Fed)',
        'long': '''
**NFCI (National Financial Conditions Index)** 📊

**Co to jest?**
Jeden wskaźnik który łączy 105 innych wskaźników finansowych.
Think of it as: "Czy warunki finansowe są łatwe czy trudne?"

**Jak czytać:**
- NFCI < -0.5: Luźne warunki, łatwo pożyczyć 😊
- NFCI ≈ 0: Normalne warunki 😐
- NFCI > 0: Napięte warunki, trudno pożyczyć 😬
- NFCI > 0.5: Bardzo napięte, kredyt się zaciska 🔒

**Co składa się na NFCI:**
- Stopy procentowe
- Spready kredytowe
- Warunki bankowe
- Ceny akcji
- Volatility

**Real-life:**
NFCI > 0 = firmy mają trudniej z kredytem = wolniejszy wzrost = akcje w dół (zwykle).
        ''',
        'emoji': '📊'
    },

    'DXY': {
        'full_name': 'US Dollar Index',
        'short': 'Siła dolara vs koszyk innych walut',
        'long': '''
**DXY (Dollar Index)** 💲

**Co to jest?**
Mierzy siłę dolara amerykańskiego vs koszyk 6 walut:
- EUR (57.6% wagi - największy)
- JPY, GBP, CAD, SEK, CHF

**Jak czytać:**
- DXY > 110: Bardzo silny dolar 💪
- DXY 90-110: Normalny zakres
- DXY < 90: Słaby dolar 📉

**Czemu to ważne?**
- Silny dolar = złe dla firm USA (eksport droższy)
- Silny dolar = dobre dla importu (taniej kupić z zagranicy)
- Silny dolar = złe dla emerging markets (dług w USD droższy)

**Akcje vs DXY:**
Zwykle: DXY up = akcje down (ale nie zawsze!)

**Crypto fun fact:**
Bitcoin często zachowuje się odwrotnie do DXY (dolar w dół = BTC w górę).
        ''',
        'emoji': '💲'
    },

    'HY_SPREAD': {
        'full_name': 'High Yield Spread',
        'short': 'Premia za ryzyko dla śmieciowych obligacji',
        'long': '''
**High Yield Spread** 🗑️💰

**Co to jest?**
Różnica między oprocentowaniem "śmieciowych" (high yield) obligacji a bezpiecznych (Treasury).

**Czemu "śmieciowe"?**
To obligacje firm z niskim ratingiem (wysoka szansa bankructwa).

**Jak czytać:**
- Spread < 4%: Inwestorzy spokojni, gotowi ryzykować 😊
- Spread 4-6%: Normalny poziom ostrożności 😐
- Spread > 6%: STRACH! Nikt nie chce śmieci! 😱

**Co to oznacza:**
Wysoki spread = rynek boi się recesji/bankructw.
Niski spread = rynek myśli że wszystko będzie OK.

**2008 flashback:**
Lehman Brothers bankrutuje → HY spread do 20%!
Panika totalna, nikt nie kupuje obligacji firm.
        ''',
        'emoji': '🗑️'
    },

    'RESERVES': {
        'full_name': 'Bank Reserves',
        'short': 'Rezerwy banków trzymane w Fedzie',
        'long': '''
**Bank Reserves (Rezerwy bankowe)** 🏦💰

**Co to jest?**
Kasa którą banki MUSZĄ trzymać w Federal Reserve.

**Ample vs Scarce:**
- Ample reserves (> $3T): Dużo kasy, banki spokojne 😊
- Scarce reserves (< $2.5T): Mało kasy, banki nerwowe 😬

**Czemu to ważne?**
Im mniej rezerw, tym większe napięcia w repo market.
= SOFR-IORB spread rośnie!

**QT Effect:**
FED robi QT (Quantitative Tightening) = rezerwy spadają
→ Płynność spada → Napięcia rosną

**Dan Kostecki rule:**
Rezerwy < $2.8T = zaczynają się problemy.
        ''',
        'emoji': '🏦'
    },

    'TGA': {
        'full_name': 'Treasury General Account',
        'short': 'Konto rządu USA w Fedzie',
        'long': '''
**TGA (Treasury General Account)** 🏛️💰

**Co to jest?**
To konto czekowe rządu USA w Federal Reserve. Tak, rząd też ma konto bankowe!

**Czemu to ważne?**
Gdy rząd płaci rachunki:
- TGA spada → Pieniądze wpływają do banków → Płynność rośnie! 🎉

Gdy rząd zbiera podatki:
- TGA rośnie → Pieniądze znikają z banków → Płynność spada! 😬

**Debt Ceiling Drama:**
Gdy Kongres blokuje podniesienie limitu długu:
→ TGA spada do zera (rząd wydaje ostatnie grosze)
→ Mega boost płynności!

**Seasonal Pattern:**
TGA zwykle rośnie pod koniec roku fiskalnego (rząd zbiera kasę).
        ''',
        'emoji': '🏛️'
    },

    'RRP': {
        'full_name': 'Reverse Repo',
        'short': 'Parking dla nadmiaru gotówki (overnight)',
        'long': '''
**Reverse Repo (ON RRP)** 🅿️💰

**Co to jest?**
Program Fedu gdzie banki/fundusze mogą "zaparkować" nadmiar kasy overnight.

**Jak działa:**
1. Fundusz ma $1B gotówki (nic nie robi)
2. Daje Fedowi $1B → dostaje ~5% rocznie (overnight rate)
3. Następnego dnia dostaje kasę z powrotem + odsetki

**Peak COVID:**
RRP osiągnął $2.5 TRILLION! 🤯
Tyle kasy było "zaparkowane" zamiast inwestowane.

**Co to oznacza:**
- Wysoki RRP = za dużo kasy, mało możliwości inwestycyjnych
- Niski RRP = kasa idzie do roboty (akcje, obligacje)

**Teraz:**
RRP spada → kasa wraca na rynek → bullish! 🚀
        ''',
        'emoji': '🅿️'
    },

    'FED_BALANCE': {
        'full_name': 'Federal Reserve Balance Sheet',
        'short': 'Wielkość bilansu Fedu (ile aktywów ma FED)',
        'long': '''
**FED Balance Sheet** 🏦📊

**Co to jest?**
To wszystkie aktywa które Federal Reserve posiada (głównie obligacje).

**Historia:**
- 2008: ~$900B (normalny poziom)
- 2020: ~$4.2T (po QE)
- 2021 peak: ~$9T! (COVID money printer go BRRR 🖨️💵)
- 2024: ~$7.5T (QT w akcji)

**QE (Quantitative Easing):**
FED kupuje obligacje → bilans rośnie → więcej pieniędzy w systemie → akcje/crypto up!

**QT (Quantitative Tightening):**
FED sprzedaje/nie rolluje obligacji → bilans spada → mniej kasy → akcje/crypto down!

**JPow meme:**
"Money printer go BRRR" = QE
"Money shredder go RRRR" = QT

**Real impact:**
Bilans Fedu a S&P500 są skorelowane ~0.8 (2010-2022).
        ''',
        'emoji': '🖨️'
    },

    'UNEMPLOYMENT': {
        'full_name': 'Unemployment Rate',
        'short': 'Procent ludzi bez pracy (którzy jej szukają)',
        'long': '''
**Unemployment Rate (Bezrobocie)** 👷‍♂️📉

**Co to jest?**
Procent ludzi którzy:
- Nie mają pracy
- Aktywnie jej szukają

**Ważne:**
Nie liczy osób które się poddały (discouraged workers).

**Sahm Rule:**
Jeśli bezrobocie rośnie o 0.5% w ciągu 3 miesięcy = RECESJA BLISKO! 🚨

**Jak czytać:**
- < 4%: Bardzo dobre, tight labor market 💪
- 4-5%: Normalne
- 5-7%: Słabe, recesja prawdopodobna
- > 7%: Kryzys!

**COVID peak:** 14.7% (kwiecień 2020) - historyczny rekord!

**FED mandate:**
FED ma 2 cele: niska inflacja + niskie bezrobocie.
Czasem są w konflikcie (wysoka inflacja = FED podnosi stopy = bezrobocie rośnie).
        ''',
        'emoji': '👷'
    },
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_explanation(term: str) -> Tuple[str, str, str, str]:
    """
    Zwraca wyjaśnienie terminu.

    Args:
        term: Nazwa terminu (np. 'VIX', 'SOFR')

    Returns:
        Tuple: (full_name, short, long, emoji)

    Example:
        >>> full, short, long, emoji = get_explanation('VIX')
        >>> print(f"{emoji} {full}: {short}")
    """
    info = FINANCIAL_GLOSSARY.get(term.upper(), {
        'full_name': term,
        'short': 'Brak opisu',
        'long': 'Wyjaśnienie niedostępne.',
        'emoji': '❓'
    })

    return (
        info['full_name'],
        info['short'],
        info['long'],
        info['emoji']
    )


def format_term_with_tooltip(term: str, value: any = None) -> str:
    """
    Formatuje termin z emoji i tooltipem (dla Streamlit).

    Args:
        term: Nazwa terminu
        value: Opcjonalna wartość do wyświetlenia

    Returns:
        str: Sformatowany HTML

    Example:
        >>> html = format_term_with_tooltip('VIX', 18.5)
        >>> st.markdown(html, unsafe_allow_html=True)
    """
    full_name, short, _, emoji = get_explanation(term)

    if value is not None:
        return f"{emoji} **{term}** ({full_name}): {value}"
    else:
        return f"{emoji} **{term}** ({full_name})"


def get_all_terms() -> list:
    """Zwraca listę wszystkich dostępnych terminów"""
    return list(FINANCIAL_GLOSSARY.keys())


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("Financial Glossary - Dostępne terminy:")
    print("=" * 60)

    for term in get_all_terms():
        full_name, short, _, emoji = get_explanation(term)
        print(f"\n{emoji} {term} ({full_name})")
        print(f"   {short}")

    print("\n" + "=" * 60)
    print(f"Total: {len(get_all_terms())} terminów")
