# Elevia

Elevia è un progetto per organizzare e collegare documenti, note e altre risorse attraverso Tag e relazioni semantiche. Aggiunge uno strato logico ai contenuti esistenti senza spostare o modificare i file originali. Ogni risorsa può appartenere a più contesti ed essere ritrovata indipendentemente da dove si trova.

## Il problema moderno

Gli esseri umani hanno una conoscenza generale del mondo, costruita attraverso esperienze e apprendimento. Il cervello può apprendere e ragionare su problemi molto diversi, ma affrontare un problema preciso richiede informazioni specifiche che non sempre possediamo o riusciamo a richiamare. Anche quando sono disponibili, non possiamo tenerle tutte presenti nello stesso momento: la memoria di lavoro gestisce pochi elementi alla volta, e seguire i dettagli senza perdere la visione d'insieme diventa più difficile con l'aumentare delle informazioni da confrontare.

Nel 2026, il collo di bottiglia è riuscire ad utilizzare questa immensità di informazioni, che possono servire per un problema che vogliamo affrontare.

Il flusso continuo di informazioni rende questo lavoro ancora più difficile. Un'osservazione in un commento sui social e un risultato descritto in un articolo scientifico possono riguardare lo stesso problema, ma arrivano in contesti separati. Vorrei poterli confrontare senza perdere la provenienza, le prove disponibili e il diverso grado di attendibilità. Mettere in relazione le fonti non significa attribuire a tutte lo stesso valore.

## Perché serve un nuovo Framework

Vorrei costruire Elevia come un framework per lavorare sulle informazioni, non soltanto per conservarle o cercarle. L’idea è una lavagna concettuale similmente allo spazio di pensiero astratto umano: uno spazio in cui leggere, confrontare fonti, collegare concetti e sviluppare ipotesi. Il sistema dovrebbe seguire il ragionamento della persona e rendere accessibili le informazioni pertinenti a ciò su cui sta ponendo attenzione.

Immaginiamo di raccogliere in questo spazio la letteratura disponibile sul diabete. Chi studia una possibile cura dovrebbe poter confrontare risultati, riconoscere contraddizioni e passare da una domanda generale ai dettagli di uno studio, senza dover ricostruire ogni volta il contesto. Elevia dovrebbe aiutare in questo lavoro, mantenendo ogni affermazione collegata alle sue fonti. Valutare le prove e formulare ipotesi resterebbe compito della persona.

L’obiettivo è rendere più facile usare la conoscenza disponibile come base per il proprio ragionamento. Raccogliere testi è solo il punto di partenza: il lavoro che Elevia dovrebbe sostenere è capire come si collegano e che cosa possiamo ricavarne.

## Principi

1. **Amplificare, non sostituire:** la tecnologia si fa carico del lavoro mnemonico e meccanico per liberare risorse mentali, non per sollevare le persone dal compito di pensare. L'obiettivo è diventare più capaci, non disimparare a ragionare sviluppando dipendenza cognitiva. Uno strumento che pensa al posto tuo ha fallito, anche se il risultato è corretto.

2. **Organizzazione indipendente dai file:** Le risorse sono rappresentate come oggetti logici. Ogni oggetto deve avere almeno un Tag e può averne più di uno, senza richiedere copie o spostamenti del file originale.

3. **Più descrizione, più visibilità:** Più un oggetto è ricco di descrittori, più è facile da ritrovare. La ricchezza informativa è l'antidoto al dimenticatoio.

4. **Manutenzione assistita:** Il sistema deve aiutare a prevenire duplicati, unire Tag equivalenti e aggiornare o rimuovere quelli obsoleti, rendendo le operazioni comprensibili all'utente.

5. **Human in the loop:** ogni conclusione dev'essere verificabile e ogni automatismo interrompibile. Il sistema propone, suggerisce, mette in evidenza; la decisione, l'intuizione e il giudizio critico appartengono alla persona.

6. **Architettura esplorabile:** i dati non vengono solo conservati, ma organizzati per essere navigati; le relazioni emergono anche dove l'utente non le stava cercando. Un archivio restituisce ciò che chiedi. Questo strumento deve mostrarti anche ciò che non sapevi di dover chiedere.

7. **Aderenza ai processi mentali:** lo strumento è progettato per adattarsi al modo in cui pensa il cervello e collegano le idee gli essere umani.

8. **Comprensione del significato:** Interpreta il senso reale delle informazioni, gestendo la complessità del linguaggio naturale senza appiattirla.


# Organizzazione dei contenuti

## Oggetti e Tag

Ogni file, documento o risorsa è un `Object` astratto, non vincolato a una posizione fisica. A ogni oggetto si applicano uno o più `Tag`, permettendo di ritrovarlo da contesti diversi: una fattura può essere `Amministrazione`, `ClienteX` e `2025.Q1` contemporaneamente.

## Gerarchia dei Tag

**Livello 1 — Tag Registry.** Tutti i Tag esistenti nel sistema, con ID immutabile. Nessun Tag viene duplicato solo perché serve in un altro contesto.

**Livello 2 — Tag Tree.** L'utente organizza i Tag in una gerarchia ad albero, crea rami, sposta e rinomina nodi. I nodi possono esistere anche prima di contenere documenti.

## Descrittori

- **Metadati:** proprietà strutturate nel formato `namespace:key:operator:value` (es. `photo:/year/eq/2025/`)

## Manutenzione

La manutenzione è la parte più fondamentale di Elevia, assistita dal software. L'obiettivo è che l'utente abbia consapevolezza di ciò che sta avvenendo, senza dover gestire le operazioni deterministiche che la macchina può fare autonomamente.

1. **Prevenzione dei duplicati:** Il sistema evita di aggiungere Tag già presenti e ignora la rimozione di Tag inesistenti.

2. **Autocompletamento:** Suggerisce Tag già utilizzati o definiti nel vocabolario durante la digitazione.

3. **Visualizzazione dei Tag comuni:** Quando selezioni più file, mostra automaticamente i Tag condivisi da tutti i file selezionati.

4. **Vocabolario controllato:** Consente di definire un vocabolario di Tag ammessi o suggeriti e di organizzare gruppi di Tag mutuamente esclusivi.

5. **Pulizia dei Tag:** Evidenzia possibili refusi, varianti singolari/plurali e Tag inutilizzati o sospetti, suggerendo correzioni.


---
***Lingua progetto attuale:** it_IT*

***Nota:** il nome **Elevia** è provvisorio e verrà sostituito, poiché già utilizzato altrove.*

***Nota:** sto valutando se trasformarlo in un paper collaborativo. Servirà una struttura decisionale (ad esempio ad albero) e strumenti gestionali per organizzare i contributi senza disperdere le idee migliori.*
