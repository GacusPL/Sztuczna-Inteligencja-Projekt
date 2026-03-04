# Sztuczna-Inteligencja-Projekt

Kacper Szponar 21306

🎮 Steam Sale Optimizer: Optymalizacja Koszyka Zakupowego

📌 O projekcie

W czasie wielkich wyprzedaży na platformie Steam gracze często stają przed klasycznym dylematem: jak kupić jak najlepsze gry, dysponując ograniczonym budżetem? Ten projekt modeluje ten codzienny scenariusz, przekładając go na język matematyki i optymalizacji.

Głównym celem projektu jest znalezienie idealnej kombinacji gier wideo, która zmaksymalizuje ogólną "satysfakcję" gracza (wynikającą z wysokich ocen kupowanych tytułów), przy jednoczesnym rygorystycznym zachowaniu limitu wydatków. Problem ten jest idealnym, rzeczywistym przykładem zastosowania klasycznego Problemu Plecakowego.

🧮 Modelowanie Problemu Optymalizacyjnego

Aby algorytmy mogły rozwiązać dylemat kupującego, rzeczywiste zmienne zostały zmapowane na parametry problemu plecakowego:

    -Pojemność plecaka: Maksymalny budżet użytkownika przeznaczony na wyprzedaż (np. 200 PLN).

    -Przedmioty: Baza dostępnych gier wideo na platformie Steam.

    -Waga przedmiotu: Aktualna cena danej gry.

    -Wartość przedmiotu: Wyliczony wskaźnik jakości gry. Zamiast subiektywnych opinii, metryka ta opiera się na odsetku pozytywnych recenzji oraz ich całkowitej liczbie, promując tytuły o ugruntowanej, świetnej reputacji.

📊 Charakterystyka Danych

Projekt opiera się na analizie rzeczywistego, obszernego zbioru danych ze sklepu Steam, obejmującego tysiące rekordów. Wyzwanie optymalizacyjne polega na przeszukaniu ogromnej przestrzeni możliwych kombinacji zakupowych. Ponieważ wyboru dokonujemy w systemie zero-jedynkowym (nie można kupić ułamka gry), problem szybko zyskuje na złożoności, uniemożliwiając ręczne lub siłowe (brute-force) znalezienie najlepszego rozwiązania dla dużych budżetów.
