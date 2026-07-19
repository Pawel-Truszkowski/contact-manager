# Contact Manager

Prosta aplikacja webowa do zarządzania kontaktami.
Stack: Django, Django REST Framework, Bootstrap 5, vanilla JavaScript,
SQLite. Aktualna pogoda dla miasta każdego kontaktu pobierana z
OpenStreetMap Nominatim (geokodowanie) oraz Open-Meteo (dane pogodowe).

## Instalacja i uruchomienie

    git clone https://github.com/Pawel-Truszkowski/contact-manager.git
    cd contact-manager
    python -m venv venv
    source venv/bin/activate        # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    echo "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > .env
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Aplikacja wymaga pliku `.env` w katalogu głównym z ustawioną zmienną
`SECRET_KEY` (powyższa komenda `echo` generuje ją automatycznie i
zapisuje do `.env`); bez niej `manage.py` zakończy się błędem
`ImproperlyConfigured`. Plik `.env` jest w `.gitignore` — nie commituj
go.

Statusy kontaktów („nowy", „w trakcie", „zagubiony", „nieaktualny")
tworzone są automatycznie podczas `python manage.py migrate`
(data migration). Aplikacja dostępna pod adresem
http://127.0.0.1:8000/.

## Uruchomienie przez Docker Compose

Wymaga Dockera oraz pliku `.env` z `SECRET_KEY` w katalogu głównym
projektu — patrz komenda `echo` w sekcji "Instalacja i uruchomienie"
powyżej.

    docker compose up --build

Kontener automatycznie wykonuje `migrate` przed startem serwera.
Aplikacja dostępna pod adresem http://localhost:8000/ (nie pod
adresem `0.0.0.0:8000` wypisywanym w logu — to tylko adres nasłuchu
w kontenerze). Kod źródłowy jest zamontowany jako wolumen, więc zmiany
w plikach odświeżają się automatycznie (Django `runserver` + autoreload).

Zatrzymanie:

    docker compose down

## Funkcjonalności

- Lista kontaktów z wyszukiwaniem (imię, nazwisko, e-mail, telefon,
  miasto) oraz sortowaniem (po nazwisku / dacie dodania, w obu
  kierunkach)
- Dodawanie / edycja / usuwanie kontaktów z walidacją po stronie
  klienta (JS) i serwera (Django); e-mail i numer telefonu są unikalne
- Aktualna pogoda (temperatura, wilgotność, prędkość wiatru) dla
  miasta każdego kontaktu
- Import kontaktów z pliku CSV z walidacją każdego wiersza i raportem
  błędów
- REST API (Django REST Framework)

## REST API

| Metoda | Endpoint             | Opis               |
|--------|----------------------|--------------------|
| GET    | /api/contacts/       | Lista kontaktów    |
| POST   | /api/contacts/       | Dodanie kontaktu   |
| PUT    | /api/contacts/{id}/  | Edycja kontaktu    |
| DELETE | /api/contacts/{id}/  | Usunięcie kontaktu |

Pole `status` przekazywane jest jako id statusu; odpowiedzi zawierają
dodatkowo pole `status_name` (tylko do odczytu). Przykład:

    curl -X POST http://127.0.0.1:8000/api/contacts/ \
      -H "Content-Type: application/json" \
      -d '{"first_name":"Jan","last_name":"Kowalski","email":"jan@example.com","phone_number":"601234567","city":"Wroclaw","status":1}'

API nie posiada uwierzytelniania (akceptowalne w zakresie tego
zadania); w środowisku produkcyjnym dodałbym np. uwierzytelnianie
tokenem oraz system uprawnień.

## Import CSV

Oczekiwany plik w kodowaniu UTF-8 z wierszem nagłówkowym:
`first_name,last_name,email,phone_number,city,status` — patrz
`sample_contacts.csv`. Kolumna `status` przyjmuje nazwy statusów
(bez rozróżniania wielkości liter). Nieprawidłowe wiersze (brakujące
pola, zduplikowany e-mail/telefon, nieznany status) są pomijane
i raportowane wraz z numerami linii; poprawne wiersze są importowane.

## Decyzje projektowe

- **Status jako ForeignKey** do osobnego modelu zamiast wartości
  zaszytych w kodzie (choices) - statusy można dodawać i zmieniać
  z poziomu bazy danych (panel admina) bez modyfikacji kodu.
- **Statusy inicjalizowane przez data migration** - świeża instalacja
  (`migrate`) od razu zawiera wymagane statusy, bez ręcznej
  konfiguracji; działa to spójnie także w bazie testowej.
- **Pogoda pobierana po stronie backendu**, a nie przez AJAX na
  froncie - umożliwia współdzielenie cache między wszystkimi
  użytkownikami i trzyma logikę zewnętrznych API w jednym miejscu
  (`contacts/services.py`).
- **Cache** (Django LocMemCache): współrzędne miast cache'owane
  bezterminowo (nie zmieniają się), pogoda przez 30 minut. Minimalizuje
  to liczbę zapytań do obu zewnętrznych API i realizuje jednocześnie
  zadanie dodatkowe nr 2. LocMem działa w ramach procesu i znika przy
  restarcie serwera; w środowisku produkcyjnym / wieloprocesowym
  zastosowałbym Redis.
- **Polityka użytkowania Nominatim**: zapytania wysyłają własny,
  identyfikujący aplikację nagłówek User-Agent, zgodnie z wymaganiami
  usage policy OSM Nominatim.
- **DRF zamiast czystych widoków Django** dla API - mniej
  boilerplate'u, wbudowana walidacja i serializacja, browsable API
  ułatwiające testowanie.
- **Import CSV pomija błędne wiersze** zamiast odrzucać cały plik -
  praktyczniejsze przy rzeczywistych, niedoskonałych danych;
  użytkownik otrzymuje podsumowanie zaimportowanych i pominiętych
  wierszy.

## Znane ograniczenia / możliwe usprawnienia

- Import CSV obsługuje wyłącznie kodowanie UTF-8 (brak wsparcia dla
  cp1250 / starszych plików z Excela)
- Współrzędne miast mogłyby być zapisywane w modelu Contact, aby
  przetrwać reset cache
- Brak uwierzytelniania API (patrz wyżej)
- Pierwsze załadowanie strony po starcie serwera jest wolniejsze,
  dopóki cache pogodowy się nie zapełni