# ECP
Ewidencja czasu pracy

## Start

### Instalacja
Niezbędny do działania programu jest zainstalowany Python w wersji 3.x. 

## Zbudowane przy użyciu
* Tkinter - GUI programu
* [PyPDF](https://pyfpdf.readthedocs.io/en/latest/index.html) - Generowanie plików PDF

## Wygląd programu

### Główne okno

Jest to okno w którym w prawym górnym rogu interfejsu można nawigować stronie między pracownikami oraz miesiącami. Dostępne jest także __MENU__, dzięki któremu m.in. dodamy, zedytujemy, usuniemy pracownika, zmienimy harmonogram.
Po prawej stronie mieści się także panel podsumowujący aktualny miesiąc wraz ze wszystkimi czasami pracy.

![alt text](https://raw.githubusercontent.com/ciszko/ECP/master/Other/main_screen.png)

Możliwe formaty wpisywania w polu: __Czas pracy__:
* HH:MM - HH:MM - wszystkie kombinacje
* Szkolenie
* Inne
* Urlop
* Chorobowe
* 0 - aby wyzerować wszystkie pola w wierszu

_Wystarczy jedna litera do przeczytania formatu_

Godziny nocne zostaną policzone automatycznie (od 22 do 6)

### Roczne podsumowanie

Panel podsumowujący cały rok. Poniżej są dostępne dwa suwaki przy pomocy, których definiujemy zakres do obliczeń kolumny __Razem__. Dostępna jest opcja nawigacji między czasem pracy, a wykorzystanym urlopem.

![alt text](https://raw.githubusercontent.com/ciszko/ECP/master/Other/annualy_screen.PNG)

### Przykładowy raport PDF

Po naciśnięciu przycisku __Drukuj__ otworzy się plik .pdf z wygenerowanym przez nas raportem.
Wszystkie raporty znajdują się w folderze _Raporty_.

![alt text](https://raw.githubusercontent.com/ciszko/ECP/master/Other/pdf_example.PNG)
