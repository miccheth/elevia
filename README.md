# Elevia

## Il problema moderno

Gli esseri umani hanno una conoscenza generale del mondo, costruita attraverso esperienze e apprendimento. Il cervello può apprendere e ragionare su problemi molto diversi, ma affrontare un problema preciso richiede informazioni specifiche che non sempre possediamo o riusciamo a richiamare. Anche quando sono disponibili, non possiamo tenerle tutte presenti nello stesso momento: la memoria di lavoro gestisce pochi elementi alla volta, e seguire i dettagli senza perdere la visione d'insieme diventa più difficile con l'aumentare delle informazioni da confrontare.

Nel 2026, il collo di bottiglia è riuscire a usare le informazioni disponibili per affrontare un problema concreto. Chi studia una possibile cura per il diabete, per esempio, deve confrontare risultati, riconoscere contraddizioni e passare dalla domanda generale ai dettagli dei singoli studi. La conoscenza prodotta sull'argomento supera ciò che una persona può tenere contemporaneamente a mente, e ricostruire ogni volta il contesto rende il lavoro più difficile.

Il flusso continuo di informazioni rende questo lavoro ancora più difficile. Un'osservazione in un commento sui social e un risultato descritto in un articolo scientifico possono riguardare lo stesso problema, ma arrivano in contesti separati. Vorrei poterli confrontare senza perdere la provenienza, le prove disponibili e il diverso grado di attendibilità. Mettere in relazione le fonti non significa attribuire a tutte lo stesso valore. L'obiettivo è cercare un «centroide» il più possibile aderente alle prove disponibili: una sintesi ragionata che tenga conto dei contributi pertinenti, senza presumere che la verità coincida con la media delle opinioni.

## Principi

1. **Amplificare, non sostituire:** la tecnologia si fa carico del lavoro mnemonico e meccanico per liberare risorse mentali, non per sollevare le persone dal compito di pensare. L'obiettivo è diventare più capaci, non disimparare a ragionare sviluppando dipendenza cognitiva.

2. **Organizzazione indipendente dai file:** le risorse sono rappresentate come oggetti logici. Ogni oggetto deve avere almeno un Tag e può averne più di uno.

3. **Più descrizione, più visibilità:** più un oggetto è ricco di descrittori, più è facile da ritrovare. La ricchezza informativa è l'antidoto al dimenticatoio.

4. **Human in the loop:** ogni conclusione dev'essere verificabile e ogni automatismo interrompibile. Il sistema propone, suggerisce, mette in evidenza; la decisione, l'intuizione e il giudizio critico appartengono alla persona.

5. **Aderenza ai processi mentali:** lo strumento è progettato per adattarsi al modo in cui pensa il cervello e a come gli esseri umani collegano le idee.

6. **Comprensione del significato (sviluppo futuro):** interpretare il senso reale delle informazioni, gestendo la complessità del linguaggio naturale senza appiattirla.


## Fase Iniziale

Lo sviluppo attuale riguarda il sistema di organizzazione logica delle risorse: oggetti, Tag e metadati. L’obiettivo è rendere le risorse facilmente ritrovabili attraverso ricerche deterministiche, basate su criteri verificabili, senza spostare o modificare i file originali.

La comprensione del linguaggio naturale e l’esplorazione semantica sono sviluppi futuri e non rientrano nel perimetro attuale.

### Organizzazione dei contenuti

| Componente        | Responsabilità                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| Object            | Rappresenta una risorsa con identità indipendente.                                               |
| Tag Registry      | Conserva identità e nomi dei Tag.                                                                |
| Tag Tree          | Mostra la gerarchia dei Tag: lo stesso Tag può comparire sotto più genitori.                     |
| Metadati          | Descrivono proprietà strutturate degli oggetti, utilizzabili come criteri di ricerca.            |
| Facet             | Espongono proprietà e valori come filtri per restringere i risultati.                            |
| Smart Collections | Salvano criteri di ricerca e mostrano gli oggetti che li soddisfano, senza copiarli o spostarli. |

#### Object

Ogni file, documento o risorsa è un `Object` astratto, non vincolato a una posizione fisica. A ogni oggetto si applicano uno o più `Tag`, permettendo di ritrovarlo da contesti diversi: una fattura può essere `Amministrazione`, `ClienteX` e `2025.Q1` contemporaneamente.

##### Regole proposte

- Rinominare un oggetto non cambia la sua identità né le associazioni.
- Aggiornare il riferimento a un file spostato conserva l'identità dell'oggetto. Non si presume che lo spostamento venga rilevato automaticamente.
- Una risorsa non disponibile resta rappresentata dall'oggetto, con indisponibilità segnalata. L'oggetto resta ricercabile attraverso i dati registrati.
- Rimuovere un oggetto da Elevia rimuove le sue associazioni, ma non elimina la risorsa originale.
- La registrazione viene completata soltanto dopo l'assegnazione di almeno un Tag. Eventuali bozze di inserimento non sono oggetti già registrati.

#### Tag Registry e Tag Tree

##### Regole proposte

- Un Tag può avere più genitori, mantenendo un'unica identità e le stesse associazioni agli oggetti. La gerarchia è un grafo diretto aciclico, visualizzabile con rami simili a cartelle.
- Rinominare un Tag o modificarne i genitori non cambia le associazioni già registrate agli oggetti. Rimuovere una relazione con un genitore non elimina il Tag né le altre relazioni.
- La gerarchia non ammette cicli: un Tag non può diventare discendente di sé stesso.
- Il Tag a livello superiore eredita i contenuti presenti nei Sub Tag inferiori.
- Il nome di un Tag è unico in tutto il sistema. Nomi che differiscono solo per maiuscole e minuscole sono considerati uguali.

#### Descrittori

I **descrittori** sono le caratteristiche informative ricavate da una risorsa, come anno, autore, formato o importo. Quelli strutturati sono registrati come **metadati**. Non tutte le risorse hanno gli stessi descrittori.

Le **facet** consentono di consultare queste proprietà attraverso filtri selezionabili. Ad esempio, `photo.year = 2025` rappresenta un metadato registrato, mentre selezionare `2025` nella facet dell’anno applica il filtro corrispondente. Metadati e facet non sono sinonimi: i primi descrivono le proprietà degli oggetti, le seconde permettono di filtrare i risultati in base a tali proprietà.

- **Metadati:** proprietà strutturate associate agli oggetti, scritte come `namespace.chiave = valore`. Il namespace indica la categoria della proprietà: in `photo.year = 2025`, `photo` è la categoria, `year` la chiave e `2025` il valore. La notazione è uno pseudo-linguaggio descrittivo, non la sintassi definitiva.

- **Facet:** filtri che consentono di selezionare valori specifici dei metadati per restringere i risultati (ad esempio, selezionare `2025` nella facet dell’anno per visualizzare le risorse corrispondenti).

##### Regole proposte

Ogni proprietà ha una chiave, un tipo e una cardinalità dichiarati. I tipi iniziali da valutare sono testo, numero, data e booleano. Una proprietà può ammettere uno o più valori secondo la sua definizione; valori incompatibili con il tipo vengono rifiutati.

Una proprietà assente non equivale a una stringa vuota, a zero o a `false`. La ricerca deve poter verificare esplicitamente presenza e assenza.

Proprietà e valore descrivono l'oggetto; l'operatore appartiene alla condizione di ricerca. Per esempio, l'oggetto registra `photo.year = 2025`, mentre la ricerca può chiedere `photo.year >= 2024`.

Lo schema descriverà namespace, proprietà, tipi e cardinalità ammessi.

### Manutenzione

La manutenzione è una componente fondamentale di Elevia, supportata dal software. L’obiettivo è garantire che l’utente abbia consapevolezza delle operazioni in corso, lasciando al sistema la gestione automatica delle attività ripetitive e dei controlli di coerenza.

#### Funzionalità principali

1. **Autocompletamento**: suggerisce durante la digitazione i Tag già utilizzati o presenti nel vocabolario controllato.

2. **Vocabolario controllato**: consente di definire i Tag ammessi.

3. **Pulizia dei Tag**: segnala possibili refusi, varianti singolari e plurali, Tag inutilizzati e altre anomalie, suggerendo eventuali correzioni.

4. **Tag obbligatori**: la rimozione dell’ultimo Tag è impedita, salvo che venga assegnato un sostituto nella stessa operazione.

5. **Fusione**: per fondere due Tag è necessario scegliere quale mantenere. Le associazioni vengono trasferite al Tag mantenuto, evitando duplicati. L'eventuale collocazione dei Tag figli deve essere risolta esplicitamente.

6. **Eliminazione**: prima di eliminare un Tag è necessario risolverne le associazioni e la struttura gerarchica, compresi gli eventuali Tag figli. L'eliminazione di un Tag non comporta la cancellazione degli oggetti o dei file originali.

7. **Modifiche atomiche**: se un’operazione viola i vincoli definiti, viene rifiutata integralmente, senza lasciare modifiche parziali.

### Ricerca deterministica

Un oggetto compare una sola volta nei risultati, anche se soddisfa più rami della query. Una condizione non valida produce un errore comprensibile, non viene ignorata.

La sintassi è in definizione. Gli esempi seguenti indicano le condizioni previste, non la forma finale.

| Condizione                | Esempio                    |
| ------------------------- | -------------------------- |
| **Tag**                   | `tag:Medicina`             |
| **Uguaglianza**           | `document.year = 2025`     |
| **Confronto**             | `finance.amount >= 1000`   |
| **Proprietà presente**    | `document.author presente` |
| **Proprietà assente**     | `document.author assente`  |
| **Tutte le condizioni**   | `A AND B`                  |
| **Almeno una condizione** | `A OR B`                   |
| **Esclusione**            | `NOT A`                    |


____
***Lingua progetto attuale:** it_IT*

***Nota:** il nome **Elevia** è provvisorio e verrà sostituito, poiché già utilizzato altrove.*

***Nota:** sto valutando se trasformarlo in un paper collaborativo. Servirà una struttura decisionale (ad esempio ad albero) e strumenti gestionali per organizzare i contributi senza disperdere le idee migliori.*
