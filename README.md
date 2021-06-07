# Subiect preselecție internship

## Cloud Security Analytics Team - Bitdefender

Să se implementeze în limbajul Python un script care îndeplinește următoarele cerințe:

1. Atunci când primește în linia de comandă parametrul **scan** :
    a. Culege următoarele informații despre fișierele prezente în directorul de lucru curent (în _current_
       _directory_ ), construind pentru acestea un dicționar al cărui chei îl reprezintă denumirile fișierelor
       analizate:
          i. **_FileSize_** : dimensiunea fișierului, exprimată în octeți
ii. **_Changed_** : data și ora ultimei modificări a fișierului, în formatul textual (string)
_YYYY/MM/DD-hh:mm_ , unde:
1. _YYYY_ reprezintă, pe 4 cifre zecimale, anul (de exemplu 2019)
2. _MM_ este luna din an, 01 însemnând Ianuarie iar 1 2 reprezentând Decembrie
3. _DD_ , cu valori intre 1 și 28/29/30/31, reprezintă ziua din lună
4. _hh_ și _mm_ sunt ora (00-23) și minutul (00-59)
iii. **_Hidden_** : marchează fișierele care au atributul de fișier ( _file attribute_ ) _hidden_ setat;
valoarea va fi 1 dacă fișierul este ascuns sau 0 în caz contrar
iv. **_ReadOnly_** : valoare 0 sau 1 care specifică dacă fișierul este protejat contra operațiilor de
scriere (valoare 1) sau dacă scrierea este permisă (valoare 0), conform atributelor de fișier
aferente.
    b. Informațiile vor fi stocate într-un fișier din directorul curent, în format **JSON** , fișier numit
       _cache.json_
2. Când se primește în linia de comandă parametrul **query** :
    a. Generează conținutul fișierului _cache.json,_ în cazul în care acesta nu există deja, întocmai după
       cum se procedează la punctul 1.
    b. Încarcă informațiile prezente în _cache.json_ într-o structură de date echivalentă celei construite la
       punctul 1.a.
    c. Afișează pe consolă următoarele informații despre fișierele descrise în _cache.json_ :
       i. Numărul total de fișiere pentru care există informații în cache.json, sub forma _Number of_
          _files: 422_
ii. Numele celor mai mari 5 fișiere (după dimensiune) în ordine crescătoare a dimensiunii
lor, mesajul afișat fiind formatat precum _Top 5 largest files: a.txt, b.bin, c.c, arc.zip, 12.exe_
iii. Procentul fișierelor ascunse (raportat la numărul total de fișiere) după modelul _3% are
hidden_
iv. Procentul fișierelor protejate contra scrierii, de exemplu _16% are read-only_
v. Numărul fișierelor care au suferit modificări în fiecare lună în care cel puțin un fișier a fost
modificat, datele afișate pentru o astfel de lună fiind formatate după modelul _2019/03: 4
modified files_ , datele pentru mai multe luni fiind afișate pe linii separate (câte o lună per
linie afișată).


