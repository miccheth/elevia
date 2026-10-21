# Elevia

## Il problema moderno

Gli esseri umani hanno una conoscenza generale del mondo, costruita attraverso esperienze e apprendimento. Il cervello può apprendere e ragionare su problemi molto diversi, ma affrontare un problema preciso richiede informazioni specifiche che non sempre possediamo o riusciamo a richiamare. Anche quando sono disponibili, non possiamo tenerle tutte presenti nello stesso momento: la memoria di lavoro gestisce pochi elementi alla volta, e seguire i dettagli senza perdere la visione d'insieme diventa più difficile con l'aumentare delle informazioni da confrontare.

Nel 2026, il collo di bottiglia è riuscire a usare le informazioni disponibili per affrontare un problema concreto. Chi studia una possibile cura per il diabete, per esempio, deve confrontare risultati, riconoscere contraddizioni e passare dalla domanda generale ai dettagli dei singoli studi. La conoscenza prodotta sull'argomento supera ciò che una persona può tenere contemporaneamente a mente, e ricostruire ogni volta il contesto rende il lavoro più difficile.

Il flusso continuo di informazioni rende questo lavoro ancora più difficile. Un'osservazione in un commento sui social e un risultato descritto in un articolo scientifico possono riguardare lo stesso problema, ma arrivano in contesti separati. Vorrei poterli confrontare senza perdere la provenienza, le prove disponibili e il diverso grado di attendibilità. Mettere in relazione le fonti non significa attribuire a tutte lo stesso valore. L'obiettivo è cercare un «centroide» il più possibile aderente alle prove disponibili: una sintesi ragionata che tenga conto dei contributi pertinenti, senza presumere che la verità coincida con la media delle opinioni.

## Principi

1. **Amplificare, non sostituire:** la tecnologia si fa carico del lavoro mnemonico e meccanico per liberare risorse mentali, non per sollevare le persone dal compito di pensare. L'obiettivo è diventare più capaci, non disimparare a ragionare sviluppando dipendenza cognitiva.

2. **Organizzazione indipendente dai file:** le risorse sono rappresentate come oggetti logici. Ogni oggetto deve avere almeno un’assegnazione a un placement di un Tag e può averne più di una, senza essere duplicato.

3. **Più descrizione, più visibilità:** più un oggetto è ricco di descrittori, più è facile da ritrovare. La ricchezza informativa è l'antidoto al dimenticatoio.

4. **Human in the loop:** ogni conclusione dev'essere verificabile e ogni automatismo interrompibile. Il sistema propone, suggerisce, mette in evidenza; la decisione, l'intuizione e il giudizio critico appartengono alla persona.

5. **Aderenza ai processi mentali:** lo strumento è progettato per adattarsi al modo in cui pensa il cervello e a come gli esseri umani collegano le idee.

6. **Comprensione del significato (sviluppo futuro):** interpretare il senso reale delle informazioni, gestendo la complessità del linguaggio naturale senza appiattirla.


## Fase Iniziale

Lo sviluppo attuale riguarda il sistema di organizzazione logica delle risorse: oggetti, Tag e metadati. L’obiettivo è rendere le risorse facilmente ritrovabili attraverso ricerche deterministiche, basate su criteri verificabili, senza spostare o modificare i file originali.

Un Tag identifica un concetto e mantiene un’unica identità. Un **placement** rappresenta una sua collocazione nella struttura. Un’**assegnazione** collega un oggetto a un placement, conservandone il contesto completo. Lo stesso oggetto può avere più assegnazioni senza essere duplicato.

La [panoramica visiva della fase iniziale](docs/visual-summary.md) riassume questa fase.

La comprensione del linguaggio naturale e l’esplorazione semantica sono sviluppi futuri e non rientrano nel perimetro attuale.

### Organizzazione dei contenuti

| Componente        | Responsabilità                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| Object            | Rappresenta una risorsa con identità indipendente.                                                     |
| Tag Registry      | Conserva identità e nomi univoci dei Tag.                                                              |
| Tag placements    | Rappresentano le collocazioni contestuali dei Tag, con identità stabili.                                |
| Assegnazioni      | Collegano gli oggetti ai placement, conservando il contesto completo.                                  |
| Tag Tree          | Visualizza la struttura delle collocazioni dei Tag.                                                   |
| Metadati          | Descrivono proprietà strutturate degli oggetti, utilizzabili come criteri di ricerca.                  |
| Facet             | Espongono filtri sui metadati, indipendenti dai Tag e dai contesti di assegnazione.                      |
| Smart Collections | Salvano ambito e condizioni di ricerca e mostrano gli oggetti corrispondenti, senza copiarli o spostarli. |

#### Object

Ogni file, documento o risorsa è un `Object` astratto, non vincolato a una posizione fisica. Le assegnazioni ai placement permettono di ritrovarlo da contesti diversi senza crearne copie. Un oggetto può essere assegnato a più placement dello stesso Tag o di Tag diversi.

##### Regole proposte

- Rinominare un oggetto non cambia la sua identità né le associazioni.
- Aggiornare il riferimento a un file spostato conserva l'identità dell'oggetto. Non si presume che lo spostamento venga rilevato automaticamente.
- Una risorsa non disponibile resta rappresentata dall'oggetto, con indisponibilità segnalata. L'oggetto resta ricercabile attraverso i dati registrati.
- Rimuovere un oggetto da Elevia rimuove le sue associazioni, ma non elimina la risorsa originale.
- La registrazione viene completata soltanto dopo almeno un’assegnazione a un placement. Eventuali bozze di inserimento non sono oggetti già registrati.

#### Tag Registry, placement e Tag Tree

Ferrari può essere un solo Tag con due placement: `Lavoro → Ferrari` e `Passioni → Ferrari`. I collegamenti ai figli e le assegnazioni restano propri di ciascuna collocazione: aggiungere Fotografie sotto Passioni → Ferrari non lo aggiunge anche sotto Lavoro → Ferrari.

Il contesto completo distingue anche collocazioni con lo stesso padre immediato: `Lavoro → Ferrari → Contratti` e `Passioni → Ferrari → Contratti` usano lo stesso Tag Contratti, ma rappresentano contesti diversi. Le assegnazioni fanno riferimento all’identità stabile del placement, non soltanto a una stringa di nomi. I percorsi mostrati sono descrittivi, non la sintassi definitiva delle query.

##### Regole proposte

- Un Tag può comparire in più placement, mantenendo un’unica identità. Riutilizzare un Tag non condivide automaticamente figli o assegnazioni tra contesti.
- Tutti i nomi della struttura sono Tag. Padre e figlio sono ruoli nei collegamenti, non tipi diversi di Tag.
- Ogni assegnazione fa riferimento a un placement. Un placement radice permette di usare un Tag senza genitore; non serve un’assegnazione globale priva di collocazione.
- Rinominare un Tag conserva la sua identità e non interrompe le assegnazioni. Modificare la struttura può invece cambiare i contesti e i risultati delle ricerche: prima della conferma deve essere mostrato l’impatto. Le regole dettagliate degli spostamenti restano da definire.
- La gerarchia non ammette cicli. Il vincolo richiede due controlli distinti:
  - **Tra placement:** un placement è una collocazione contestuale di un Tag. Non può diventare discendente di sé stesso; per esempio, non si può spostare un ramo dentro un proprio discendente.
  - **Tra identità dei Tag:** considerando insieme i collegamenti di tutti i contesti, un Tag non può diventare discendente di sé stesso, nemmeno attraverso placement diversi. Per esempio, `A → B` in un contesto e `B → A` in un altro sono vietati, anche se i placement non formano un ciclo. Lo stesso vale per percorsi più lunghi e per il collegamento diretto `A → A`.
  - Ogni modifica della struttura deve rispettare entrambi i vincoli. Controllare soltanto i placement non basta; se uno dei controlli fallisce, l’operazione viene rifiutata integralmente.
- La ricerca su un ramo include gli oggetti assegnati al placement selezionato e ai suoi discendenti, senza saltare ad altre collocazioni dei Tag incontrati. Gli antenati non diventano automaticamente Tag direttamente assegnati agli oggetti.
- Il nome di un Tag è unico in tutto il sistema. Nomi che differiscono solo per maiuscole e minuscole sono considerati uguali.

#### Assegnazioni e inserimento guidato

Le operazioni sulle assegnazioni sono distinte dalle modifiche della struttura:

| Operazione                   | Effetto                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| Aggiungi anche a…             | Aggiunge un’assegnazione al placement scelto, conservando quelle esistenti.                |
| Trasferisci in…               | Sostituisce l’assegnazione di partenza con quella di destinazione, conservando le altre.   |
| Rimuovi da questo contesto    | Rimuove soltanto l’assegnazione selezionata.                                              |

Non sono ammesse assegnazioni duplicate dello stesso oggetto allo stesso placement. Aggiungere un’assegnazione già presente non ne crea un’altra. Le operazioni non duplicano l’oggetto né il file originale e non spostano il placement.

Elevia propone i contesti basandosi sullo storico delle assegnazioni. Inserendo da un ramo, può predisporre quel contesto e mostrarlo prima della conferma. L’utente può accettare, modificare o rifiutare i suggerimenti e scegliere altre collocazioni disponibili. Vengono registrate soltanto le assegnazioni confermate.

Lo storico non autorizza assegnazioni automatiche. Condividere un oggetto tra due contesti non li sincronizza: i documenti futuri ricevono soltanto le assegnazioni confermate per ciascuno di essi. Il metodo dei suggerimenti resta da definire e non richiede necessariamente AI; in assenza di storico, le collocazioni disponibili restano consultabili.

#### Vocabolario controllato e schema dei metadati

I Tag, i namespace e le proprietà dei metadati devono essere definiti prima di essere assegnati agli oggetti.

Il vocabolario controllato stabilisce i Tag ammessi. Lo schema dei metadati stabilisce i namespace e, per ogni proprietà, la chiave, il tipo e la cardinalità. Per le proprietà con valori controllati, definisce anche l'elenco dei valori ammessi; per le altre, i valori devono rispettare il tipo dichiarato, senza essere elencati in anticipo.

Per esempio, prima di registrare `work.status = approved`, devono esistere il namespace `work` e la proprietà `status`, con le relative regole. Se `status` prevede un elenco di valori ammessi, anche `approved` deve essere presente nell'elenco.

Le definizioni possono essere aggiunte o modificate esplicitamente. Assegnare un dato a un oggetto non crea automaticamente nuovi Tag, namespace, proprietà o valori controllati. Un'assegnazione che non rispetta le definizioni viene rifiutata.

I namespace dei metadati sono indipendenti dai Tag. Il namespace `work` non coincide con il Tag Lavoro: l’assegnazione a un placement non crea automaticamente metadati.

#### Descrittori

I **descrittori** sono le caratteristiche informative ricavate da una risorsa, come anno, autore, formato o importo. Quelli strutturati sono registrati come **metadati**. Non tutte le risorse hanno gli stessi descrittori.

Le **facet** consentono di consultare queste proprietà attraverso filtri selezionabili. Ad esempio, `photo.year = 2025` rappresenta un metadato registrato, mentre selezionare `2025` nella facet dell’anno applica il filtro corrispondente. Metadati e facet non sono sinonimi: i primi descrivono le proprietà degli oggetti, le seconde permettono di filtrare i risultati in base a tali proprietà.

- **Metadati:** proprietà strutturate associate agli oggetti, scritte come `namespace.chiave = valore`. Il namespace indica la categoria della proprietà: in `photo.year = 2025`, `photo` è la categoria, `year` la chiave e `2025` il valore. La notazione è uno pseudo-linguaggio descrittivo, non la sintassi definitiva.

- **Facet:** filtri che consentono di selezionare valori specifici dei metadati per restringere i risultati (ad esempio, selezionare `2025` nella facet dell’anno per visualizzare le risorse corrispondenti).

Le Facet sono indipendenti dai Tag e dai contesti di assegnazione. La stessa Facet può essere applicata a una ricerca globale o a un ramo specifico: il filtro sui metadati e l’ambito della ricerca sono criteri distinti e combinabili.

##### Regole proposte

Ogni proprietà deve rispettare la definizione nello schema dei metadati. I tipi iniziali da valutare sono testo, numero, data e booleano. Una proprietà può ammettere uno o più valori secondo la cardinalità dichiarata.

Una proprietà assente non equivale a una stringa vuota, a zero o a `false`. La ricerca deve poter verificare esplicitamente presenza e assenza.

Proprietà e valore descrivono l'oggetto; l'operatore appartiene alla condizione di ricerca. Per esempio, l'oggetto registra `photo.year = 2025`, mentre la ricerca può chiedere `photo.year >= 2024`.

### Manutenzione

La manutenzione è una componente fondamentale di Elevia, supportata dal software. L’obiettivo è garantire che l’utente abbia consapevolezza delle operazioni in corso, lasciando al sistema la gestione automatica delle attività ripetitive e dei controlli di coerenza.

#### Funzionalità principali

1. **Autocompletamento**: suggerisce durante la digitazione i Tag già utilizzati o presenti nel vocabolario controllato.

2. **Vocabolario controllato e schema dei metadati**: consentono di definire i Tag, i namespace e le proprietà ammesse, con tipi, cardinalità ed eventuali elenchi di valori controllati, prima del loro uso negli oggetti.

3. **Pulizia dei Tag**: segnala possibili refusi, varianti singolari e plurali, Tag inutilizzati e altre anomalie, suggerendo eventuali correzioni.

   La manutenzione impedisce inoltre di rappresentare la stessa informazione sia come Tag sia come metadato. Per esempio, se il cliente è rappresentato dal Tag `Ferrari`, non viene registrato anche come `work.client = Ferrari`. Le regole per dichiarare e verificare queste equivalenze sono da definire; la sola coincidenza del testo non basta a stabilirle.

4. **Assegnazioni obbligatorie**: la rimozione dell’ultima assegnazione di un oggetto è impedita, salvo sostituzione nella stessa operazione.

5. **Eliminazione**: eliminare un placement non equivale a eliminare il Tag dal Registry. L’eliminazione di una collocazione con figli o assegnazioni è bloccata finché questi non vengono risolti esplicitamente. Prima di eliminare un Tag devono essere risolti tutti i suoi placement e i relativi collegamenti e assegnazioni. Nessuna delle due operazioni comporta la cancellazione degli oggetti o dei file originali.

6. **Modifiche atomiche**: se un’operazione viola i vincoli definiti, viene rifiutata integralmente, senza lasciare modifiche parziali.

### Ricerca deterministica

La ricerca distingue due ambiti:

| Modalità           | Ambito                                                                                                               |
| ------------------ | -------------------------------------------------------------------------------------------------------------------- |
| Ovunque            | Tutte le collocazioni del Tag selezionato e i loro discendenti.                                                         |
| Solo questo ramo   | Il placement selezionato e i suoi discendenti, senza saltare alle altre collocazioni dei Tag incontrati.                |

Per esempio, Ferrari ovunque comprende gli oggetti dei contesti Lavoro e Passioni. La ricerca sul placement Lavoro → Ferrari rimane invece nel ramo lavorativo. La ricerca globale raccoglie le assegnazioni nelle diverse collocazioni, non è un tipo diverso di assegnazione.

Un oggetto compare una sola volta nei risultati, anche se soddisfa più rami della query. Una condizione non valida produce un errore comprensibile, non viene ignorata.

La sintassi è in definizione. Gli esempi seguenti indicano le condizioni previste, non la forma finale.

L’utente combina l’ambito della ricerca con condizioni sui Tag e sui metadati.

| Condizione                | Esempio                    |
| ------------------------- | -------------------------- |
| **Tag, ovunque**           | `tag:Medicina`             |
| **Uguaglianza**           | `document.year = 2025`     |
| **Confronto**             | `finance.amount >= 1000`   |
| **Proprietà presente**    | `document.author presente` |
| **Proprietà assente**     | `document.author assente`  |
| **Tutte le condizioni**   | `A AND B`                  |
| **Almeno una condizione** | `A OR B`                   |
| **Esclusione**            | `NOT A`                    |

#### Smart Collections

Le Smart Collections salvano ambito e condizioni della ricerca, non copie degli oggetti. Una raccolta Ferrari ovunque e una raccolta limitata a Passioni → Ferrari non hanno criteri equivalenti.

I riferimenti usano identità stabili, non soltanto nomi visualizzati. Rinominare un Tag non interrompe il riferimento. Se un riferimento viene eliminato, la ricerca viene segnalata come non valida: il criterio non viene ignorato né sostituito silenziosamente.


____
***Lingua progetto attuale:** it_IT*

***Nota:** il nome **Elevia** è provvisorio e verrà sostituito, poiché già utilizzato altrove.*

***Nota:** sto valutando se trasformarlo in un paper collaborativo. Servirà una struttura decisionale (ad esempio ad albero) e strumenti gestionali per organizzare i contributi senza disperdere le idee migliori.*
