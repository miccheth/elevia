# Elevia

## Installazione

Requisiti: Python 3.13 o successivo e `uv`.

```bash
git clone https://github.com/miccheth/elevia.git
cd elevia
uv sync
```

### macOS e Linux

```bash
source .venv/bin/activate
elevia --help
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
elevia --help
```

Se PowerShell blocca l'attivazione:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
elevia --help
```

### Windows CMD

```bat
.venv\Scripts\activate.bat
elevia --help
```

### Senza attivare l'ambiente

```bash
uv run elevia --help
```

Il database viene creato in `.elevia/elevia.db` nella root del clone. Fuori da un clone Git si usa `~/.elevia/elevia.db`.

Per azzerare i dati:

```bash
elevia reset
```

Elenco comandi: [docs/COMMANDS.md](docs/COMMANDS.md).

## Il problema moderno

Gli esseri umani hanno una conoscenza generale del mondo, costruita attraverso esperienze e apprendimento. Il cervello può apprendere e ragionare su problemi molto diversi, ma affrontare un problema preciso richiede informazioni specifiche che non sempre possediamo o riusciamo a richiamare. Anche quando sono disponibili, non possiamo tenerle tutte presenti nello stesso momento: la memoria di lavoro gestisce pochi elementi alla volta, e seguire i dettagli senza perdere la visione d'insieme diventa più difficile con l'aumentare delle informazioni da confrontare.

Nel 2026, il collo di bottiglia è riuscire a usare le eccessive informazioni disponibili per affrontare un problema concreto. Chi studia una possibile cura per il diabete, per esempio, deve confrontare risultati, riconoscere contraddizioni e passare dalla domanda generale ai dettagli dei singoli studi. La conoscenza prodotta sull'argomento supera ciò che una persona può tenere contemporaneamente a mente, e ricostruire ogni volta il contesto rende il lavoro più difficile.

Il flusso continuo di informazioni rende questo lavoro ancora più difficile. Un'osservazione in un commento sui social e un risultato descritto in un articolo scientifico possono riguardare lo stesso problema, ma arrivano in contesti separati. Vorrei poterli confrontare senza perdere la provenienza, le prove disponibili e il diverso grado di attendibilità. Mettere in relazione le fonti non significa attribuire a tutte lo stesso valore. L'obiettivo è cercare un «centroide» il più possibile aderente alle prove disponibili: una sintesi ragionata che tenga conto dei contributi pertinenti, senza presumere che la verità coincida con la media delle opinioni.

## Principi

1. **Amplificare, non sostituire:** la tecnologia si fa carico del lavoro mnemonico e meccanico per liberare risorse mentali, non per sollevare le persone dal compito di pensare. L'obiettivo è diventare più capaci, non disimparare a ragionare sviluppando dipendenza cognitiva.

2. **Organizzazione indipendente dai file:** le risorse sono rappresentate come oggetti logici. Ogni oggetto deve avere almeno un’assegnazione a un placement di un Tag e può averne più di una, senza essere duplicato.

3. **Più descrizione, più visibilità:** più un oggetto è ricco di descrittori, più è facile da ritrovare. La ricchezza informativa è l'antidoto al dimenticatoio.

4. **Human in the loop:** ogni conclusione dev'essere verificabile e ogni automatismo interrompibile. Il sistema propone, suggerisce, mette in evidenza; la decisione, l'intuizione e il giudizio critico appartengono alla persona.

5. **Aderenza ai processi mentali:** lo strumento è progettato per adattarsi al modo in cui pensa il cervello e a come gli esseri umani collegano le idee.

6. **Comprensione del significato (sviluppo futuro):** interpretare il senso reale delle informazioni, gestendo la complessità del linguaggio naturale senza appiattirla.


# Fase Iniziale

Lo sviluppo attuale riguarda il sistema di organizzazione logica delle risorse: oggetti, Tag e metadati. L’obiettivo è rendere le risorse facilmente ritrovabili attraverso ricerche deterministiche, basate su criteri espliciti, senza spostare o modificare i file originali.

## Organizzazione dei contenuti

| Componente        | Responsabilità                                                                                            |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| Object            | Rappresenta una risorsa con identità indipendente.                                                        |
| Tag Registry      | Conserva identità e nomi univoci dei Tag.                                                                 |
| Tag Placements    | Rappresentano le collocazioni contestuali dei Tag, con identità stabili.                                  |
| Tagging           | Collegano gli oggetti ai placement, conservando il contesto completo.                                     |
| Tag Tree          | Visualizza la struttura delle collocazioni dei Tag.                                                       |
| Attributes        | Descrivono proprietà strutturate degli oggetti, utilizzabili come criteri di ricerca e come filtri sui valori. |

### Object

Ogni file, documento o risorsa è un `Object` astratto, non vincolato a una posizione fisica. Le assegnazioni ai placement permettono di ritrovarlo da contesti diversi senza crearne copie. Un oggetto può essere assegnato a più Placement dello stesso Tag o di Tag diversi.

#### Regole proposte

- Rinominare un oggetto non cambia la sua identità né le associazioni.
- Aggiornare il riferimento a un file spostato conserva l'identità dell'oggetto. Non si presume che lo spostamento venga rilevato automaticamente.
- Una risorsa non disponibile resta rappresentata dall'oggetto, con indisponibilità segnalata. L'oggetto resta ricercabile attraverso i dati registrati.
- Rimuovere un oggetto da Elevia rimuove le sue associazioni, ma non elimina la risorsa originale.
- La registrazione viene completata soltanto dopo almeno un’assegnazione a un placement. Eventuali bozze di inserimento non sono oggetti già registrati.

#### Operazioni sulle assegnazioni

| Operazione | Risultato |
| --- | --- |
| Aggiungi anche a… | Aggiunge la coppia Object–placement se assente; se già presente non cambia nulla. |
| Trasferisci in… | Garantisce l’assegnazione di destinazione e rimuove quella di partenza, conservando le altre. |
| Trasferisci nello stesso placement | Nessuna modifica: non rimuove l’assegnazione. |
| Rimuovi da questo contesto | Rimuove la coppia scelta se presente, purché l’Object mantenga almeno un’assegnazione. |

Il trasferimento richiede un’assegnazione di partenza esistente; una partenza inesistente è un errore, non un’aggiunta implicita. Una destinazione o un Object inesistente è sempre un errore. Le operazioni che non cambiano nulla non producono nuove assegnazioni. Nessuna sincronizzazione viene creata tra contesti: un documento futuro richiede le proprie scelte e conferme.

### Struttura dei Placements

```text
Tag
├── Identità stabile di un concetto
└── Riutilizzabile in più placement

Placement
├── Identità stabile di una collocazione
├── Riferimento a un solo Tag
└── Un solo placement padre, oppure nessuno se è una radice

Tagging
└── Coppia univoca: Object + placement
```

I placement formano una struttura di alberi con più radici. Un placement non può avere due padri: per usare lo stesso Tag in due contesti si creano due placement distinti. Non vengono duplicati il Tag o gli oggetti.

| Vincolo             | Decisione                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| Placement fratelli  | Lo stesso Tag può comparire una sola volta sotto lo stesso placement padre.                            |
| Placement radice    | Per ogni Tag può esistere al massimo un placement radice. Il Tag può avere anche placement non radice. |
| Figli               | Appartengono alla collocazione, non vengono condivisi automaticamente tra placement dello stesso Tag.  |
| Tag senza placement | Ammesso nel Registry: è una definizione non ancora utilizzata nella struttura.                         |
| Tagging             | Sempre riferite a placement esistenti. Nessuna assegnazione globale priva di collocazione.             |
| Object registrato   | Ha almeno un’assegnazione. Le bozze non sono Object già registrati.                                    |
| Identificatori      | Stabili, indipendenti dai nomi e mai riassegnati a nuove entità dopo l’eliminazione.                   |

Il contesto completo si ricostruisce risalendo i riferimenti ai padri, dalla collocazione assegnata alla radice. I nomi servono alla visualizzazione, non identificano il percorso. Un eventuale percorso memorizzato per velocizzare le letture è un dato derivato, non una seconda fonte di verità.

Il contesto è quello della struttura corrente, non una fotografia immutabile del momento dell’assegnazione. Rinominare un Tag aggiorna i nomi visualizzati; spostare un placement aggiorna il contesto del ramo. L’assegnazione conserva il riferimento alla stessa collocazione finché questa esiste.

#### Operazioni sulla struttura

Le modifiche strutturali richiedono un’anteprima che mostri collocazioni coinvolte, assegnazioni, nuovi percorsi e conflitti il cui ambito o risultato può cambiare. L’anteprima non modifica dati e non vale come conferma. Alla conferma il backend ricontrolla riferimenti, vincoli e stato usato per l’anteprima; se i dati sono cambiati, rifiuta la conferma e richiede una nuova anteprima.

| Operazione | Risultato |
| --- | --- |
| Aggiungere una collocazione | Crea un placement vuoto con nuova identità, senza copiare figli o assegnazioni. Se la coppia Tag–padre esiste già, viene rifiutata indicando il placement esistente. |
| Spostare un placement | Conserva identità del placement, discendenti e assegnazioni. Cambia solo il collegamento al padre e ricalcola il contesto del ramo. Se a destinazione esiste già un placement dello stesso Tag, viene rifiutato con un conflitto: nessuna fusione automatica. |
| Eliminare un placement | Ammessa solo senza figli e senza assegnazioni. Per una collocazione utilizzata serve un piano unico che risolva figli e assegnazioni; nessun figlio viene promosso automaticamente. |
| Eliminare un Tag | Ammessa solo dopo aver risolto tutti i suoi placement. Un Tag senza placement può essere eliminato direttamente. |
| Fondere due Tag | Operazione esplicita: l’utente sceglie il Tag da mantenere e quello da ritirare. I conflitti tra placement richiedono scelte esplicite; non si condividono rami implicitamente. La fusione viene rifiutata se crea un ciclo. |

Ogni piano confermato è una sola transazione. In caso di errore non viene applicata nessuna parte del piano. Nessuna operazione modifica, sposta o elimina i file originali.

#### Due divieti sui cicli

Ogni modifica deve superare entrambi i controlli sullo stato finale proposto:

1. **Placement:** nessun placement può essere padre di sé stesso o essere spostato sotto un proprio discendente.
2. **Tag:** per ogni collegamento padre–figlio tra placement si considera il collegamento tra le rispettive identità dei Tag. L’unione dei collegamenti di tutti i contesti deve essere aciclica. Sono vietati `A → A`, `A → B → A` e cicli più lunghi, anche attraverso placement distinti.

Se lo stesso collegamento tra Tag esiste in più collocazioni, eliminarne una non elimina il collegamento dalle altre. Il controllo usa tutti i collegamenti effettivamente presenti dopo l’operazione, non quelli di un solo ramo.

Questa scelta è deliberatamente più restrittiva della sola assenza di cicli tra placement: `A → B` e `B → A` non possono coesistere neppure in contesti separati.

### Attributes

Gli **Attributes** sono le caratteristiche informative associate a una risorsa, come anno, autore, formato o importo. Ogni risorsa può avere Attributes differenti, in base alla tipologia e alle informazioni disponibili.

Gli Attributes consentono di descrivere, organizzare e filtrare le risorse in base alle loro proprietà. Ad esempio, `photo.year = 2025` rappresenta un attributo che identifica l’anno associato a una risorsa fotografica. Selezionando il valore `2025` tra i criteri di ricerca disponibili, è possibile restringere i risultati alle risorse corrispondenti.

- **Attributes:** proprietà informative associate alle risorse, rappresentabili nella forma `namespace.chiave = valore`. In `photo.year = 2025`, `photo` identifica il namespace, `year` la chiave e `2025` il valore. Questa notazione è descrittiva e non costituisce la sintassi definitiva.

Gli **Attributes** sono indipendenti dai **Tag** e dai **Placements** di assegnazione. Possono essere utilizzati sia nelle ricerche globali sia nelle ricerche limitate a un ramo specifico. I filtri sui valori degli Attributes e l'ambito della ricerca sono criteri distinti e combinabili: lo stesso filtro si applica a un insieme di risultati diverso a seconda dell'ambito scelto.

## Lifecycle

### Onboarding

Il modello logico di Elevia è più flessibile delle cartelle, ma costa complessità cognitiva, passaggi in più, dipendenza dalla qualità della struttura e attenzione alle performance.

Il problema non è il numero di concetti, ma il modo in cui vengono presentati. L’utente non deve imparare Tag, placement come se due idee astratte.

Se l’utente deve consultare un documento per completare un’operazione quotidiana, l’interfaccia ha fallito. La documentazione serve per approfondire, non per usare il sistema.

#### Soluzioni

| Soluzione               | Comportamento                                                                                                                                      | Esempio                                                                                               |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Onboarding guidato      | Al primo avvio, il sistema guida l’utente nella creazione del primo Tag, del primo placement e della prima assegnazione, usando i suoi dati reali. | «Crea il tuo primo contesto: Lavoro. Ora aggiungi Ferrari sotto Lavoro. Infine assegna un documento.» |
| Terminologia coerente   | Usare sempre gli stessi termini visivi: Tag = concetto, Placement = collocazione, Tagging = collegamento oggetto-placement.                        | Non alternare «categoria», «ramo», «percorso» per lo stesso elemento.                                 |
| Complessità progressiva | Mostrare prima solo «aggiungi tag» e «scegli dove metterlo». I dettagli tecnici emergono solo quando servono.                                      | L’ID del placement appare solo nell’anteprima di una modifica strutturale.                            |
| Esempi concreti         | Usare sempre lo stesso esempio noto: Ferrari sotto Lavoro e Passioni.                                                                              | Mostrare che un contratto e una foto possono avere lo stesso Tag in contesti diversi.                 |

### Maintenance

La manutenzione è una componente fondamentale di Elevia. L’obiettivo è dare all’utente consapevolezza delle operazioni in corso, lasciando al sistema i controlli automatici e le attività ripetitive.

Le operazioni frequenti restano veloci. Le operazioni rischiose richiedono più passaggi.

| Frequenza | Esempi | Passaggi richiesti |
| --- | --- | --- |
| Quotidiana | Aggiungere o rimuovere un Tag da un oggetto già registrato | Un gesto, nessuna anteprima intermedia |
| Frequente | Spostare un oggetto in un altro contesto | Un gesto, con anteprima solo se il contesto di destinazione è già occupato |
| Occasionale | Spostare un intero ramo, fondere Tag, eliminare un Tag | Anteprima, piano esplicito, conferma |

#### Funzionalità principali

1. **Autocompletamento**: suggerisce durante la digitazione i Tag già utilizzati o presenti nel vocabolario controllato.

2. **Suggerimenti di contesto**: durante l’inserimento, Elevia propone i placement del Tag scelto in base allo storico delle assegnazioni confermate. L’inserimento da un ramo predispone quel placement. L’utente può accettare, modificare o rifiutare i suggerimenti e seleziona uno o più contesti prima della conferma. Vengono registrate soltanto le assegnazioni confermate; lo storico non autorizza assegnazioni automatiche e non sincronizza i documenti futuri tra contesti.

3. **Azioni batch**: seleziona più oggetti e assegnali allo stesso contesto in un’unica operazione. Esempio: 20 contratti, un solo contesto «Lavoro → Ferrari → Contratti», una sola conferma.

4. **Scorciatoie da tastiera**: comandi rapidi con autocompletamento dei contesti. Esempio: `Ctrl+T` apre l’aggiunta Tag; digitando «Fer» propone i placement di Ferrari.

5. **Drag & drop con fallback**: trascina un oggetto su un ramo. Se non ci sono conflitti, applica subito; se ci sono, mostra l’anteprima. Esempio: trascinare una foto su «Passioni → Ferrari» la assegna immediatamente.

6. **Operazioni senza effetto**: se un’operazione non cambia nulla, non mostra anteprima né chiede conferma. Esempio: aggiungere un Tag già presente non apre alcuna finestra.

7. **Validazione alla creazione**: blocca cicli, duplicati e nomi ambigui prima che entrino nel sistema. Esempio: `Ferrari → Auto → Ferrari` viene rifiutato con il percorso del ciclo.

8. **Pulizia dei Tag**: segnala refusi, varianti singolari e plurali, nomi simili, Tag inutilizzati, placement orfani e altre anomalie, suggerendo correzioni. Esempio: «Ferrari» e «ferrari» sono lo stesso Tag; «Auto» ha un solo placement senza assegnazioni da 6 mesi.

   La manutenzione impedisce inoltre di rappresentare la stessa informazione sia come Tag sia come attributo. Per esempio, se il cliente è rappresentato dal Tag `Ferrari`, non viene registrato anche come `work.client = Ferrari`. Le regole per dichiarare e verificare queste equivalenze sono da definire; la sola coincidenza del testo non basta a stabilirle.

9. **Anteprima dell’impatto**: prima di una modifica strutturale, mostra oggetti, percorsi e query il cui ambito o risultato può cambiare. Esempio: «Spostare Contratti sotto Passioni coinvolge 12 oggetti e svuota la query S3.»

10. **Undo a livello di operazione**: ogni operazione completata può essere annullata entro un tempo limitato, con ripristino dello stato precedente. Esempio: dopo una fusione, «Annulla» ripristina Tag, placement e assegnazioni.

11. **Snapshot della struttura**: salva una fotografia della gerarchia prima di modifiche massive, per poter tornare indietro. Esempio: prima di una riorganizzazione annuale, il sistema salva lo stato corrente.

12. **Dashboard di salute**: mostra metriche semplici: Tag senza placement, placement senza assegnazioni, profondità media, rami con nomi simili. Una scheda «Manutenzione» elenca i problemi trovati e le azioni suggerite.

13. **Assegnazioni obbligatorie**: la rimozione dell’ultima assegnazione di un oggetto è impedita, salvo sostituzione nella stessa operazione.

14. **Eliminazione**: eliminare un placement non equivale a eliminare il Tag dal Registry. L’eliminazione di una collocazione con figli o assegnazioni è bloccata finché questi non vengono risolti esplicitamente. Prima di eliminare un Tag devono essere risolti tutti i suoi placement e i relativi collegamenti e assegnazioni. Nessuna delle due operazioni comporta la cancellazione degli oggetti o dei file originali.

15. **Modifiche atomiche**: se un’operazione viola i vincoli definiti, viene rifiutata integralmente, senza lasciare modifiche parziali.

## Controlled Vocabulary

I Tag, i Namespace e le proprietà degli Attributes devono essere definiti prima di essere assegnati agli oggetti.

Il Vocabolario Controllato stabilisce i Tag ammessi. Lo schema dei metadati stabilisce i namespace e, per ogni proprietà, la chiave, il tipo e la cardinalità. Per le proprietà con valori controllati, definisce anche l'elenco dei valori ammessi; per le altre, i valori devono rispettare il tipo dichiarato, senza essere elencati in anticipo.

I namespace dei metadati sono indipendenti dai Tag. Il namespace `work` non coincide con il Tag Lavoro: l’assegnazione a un placement non crea automaticamente metadati.

Gli Attributes descrivono l’Object, non la sua singola assegnazione: lo stesso `work.status` non cambia tra i placement dell’oggetto. Una proprietà assente è distinta da una stringa vuota, zero o false. Una condizione di uguaglianza o confronto su una proprietà assente è falsa; «presente» è vera se esiste almeno un valore e «assente» è il suo complemento. Per proprietà multivalore, uguaglianza e confronto sono veri se almeno un valore soddisfa la condizione. `NOT (proprietà = valore)` include anche gli oggetti privi della proprietà; per escluderli occorre richiedere anche «presente». I valori nulli non sono registrabili come sostituti dell’assenza. Ogni condizione deve rispettare tipi, cardinalità e operatori ammessi dallo schema; un confronto non valido viene rifiutato prima dell’esecuzione.

## Query

La ricerca in questo momento è di tipo esplicito, e distingue due ambiti:

| Modalità         | Ambito                                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------------------------- |
| Ovunque          | Tutte le collocazioni del Tag selezionato e i loro discendenti.                                          |
| Solo questo ramo | Il placement selezionato e i suoi discendenti, senza saltare alle altre collocazioni dei Tag incontrati. |

Per esempio, Ferrari ovunque comprende gli oggetti dei contesti Lavoro e Passioni. La ricerca sul placement Lavoro → Ferrari rimane invece nel ramo lavorativo. La ricerca globale raccoglie le assegnazioni nelle diverse collocazioni, non è un tipo diverso di assegnazione.

Una query definisce prima un ambito: tutti gli oggetti, Ovunque T oppure Ramo P. Le condizioni vengono poi valutate sugli oggetti di quell’ambito. Una condizione globale su un Tag esamina tutte le assegnazioni dell’oggetto; per limitarla a un contesto si usa esplicitamente «Tag T nel ramo P», che richiede una stessa assegnazione a soddisfare il vincolo. «Ramo P AND Ovunque T» non è equivalente: può essere soddisfatta da due assegnazioni diverse dello stesso oggetto.

AND è intersezione, OR è unione e NOT è complemento rispetto all’ambito della query. Se T e P esistono ma T non è presente nel ramo P, la condizione contestuale restituisce zero risultati, non un errore.

Un oggetto compare una sola volta nei risultati, anche se soddisfa più rami della query. Una condizione non valida produce un errore comprensibile, non viene ignorata.

La sintassi è in definizione. Gli esempi seguenti indicano le condizioni previste, non la forma finale.

L’utente combina l’ambito della ricerca con condizioni sui Tag e sui metadati.

| Condizione                | Esempio                    |
| ------------------------- | -------------------------- |
| **Tag, ovunque**          | `tag:Medicina`             |
| **Uguaglianza**           | `document.year = 2025`     |
| **Confronto**             | `finance.amount >= 1000`   |
| **Proprietà presente**    | `document.author presente` |
| **Proprietà assente**     | `document.author assente`  |
| **Tutte le condizioni**   | `A AND B`                  |
| **Almeno una condizione** | `A OR B`                   |
| **Esclusione**            | `NOT A`                    |

## Operazioni non ammesse

Queste operazioni vengono rifiutate. Il sistema non le esegue parzialmente e non le interpreta in modo alternativo.

### Struttura e gerarchia

- Creare un placement con due padri.
- Mettere lo stesso Tag due volte sotto lo stesso padre.
- Creare più di un placement radice per lo stesso Tag.
- Creare un ciclo tra placement o tra identità dei Tag, anche in contesti diversi.
- Spostare un ramo dentro sé stesso o dentro un proprio discendente.
- Spostare un placement in una destinazione dove esiste già lo stesso Tag, senza risolvere esplicitamente il conflitto.
- Eliminare ricorsivamente un placement con figli o assegnazioni.
- Eliminare un Tag mentre ha ancora placement non risolti.
- Fondere automaticamente due rami con lo stesso Tag.
- Fondere due Tag se la sostituzione crea un ciclo.
- Creare un alias automatico per un Tag ritirato.

### Assegnazioni

- Registrare un oggetto senza assegnarlo a un placement.
- Creare un’assegnazione globale senza collocazione.
- Assegnare due volte lo stesso oggetto allo stesso placement.
- Rimuovere l’ultima assegnazione di un oggetto senza sostituirla nella stessa operazione.
- Trasferire un oggetto da un contesto in cui non è assegnato.
- Trasferire un oggetto verso un placement o un oggetto inesistente.
- Sincronizzare automaticamente i documenti futuri tra due contesti.
- Registrare un suggerimento come assegnazione senza conferma dell’utente.
- Creare automaticamente un placement radice solo perché un Tag non ne ha uno.

### Ricerca e metadati

- Cercare un Tag «nel ramo» usando implicitamente due assegnazioni diverse dello stesso oggetto.
- Usare `Ramo P AND Ovunque T` come equivalente di `Tag T nel ramo P`.
- Eseguire una query con un riferimento eliminato o inesistente: la query è non valida, non restituisce un risultato parziale.
- Interpretare una proprietà assente come stringa vuota, zero o false.
- Registrare `null` come sostituto dell’assenza.
- Usare un confronto non previsto dallo schema dei metadati.
- Restituire lo stesso oggetto più volte nei risultati.
- Applicare un filtro su un Attribute a un Tag o a un contesto: i filtri sugli Attributes agiscono sui valori delle proprietà, non sui Tag né sui placement.

### Risorse e file

- Spostare, modificare o eliminare il file originale tramite un’operazione su Elevia.
- Rilevare automaticamente lo spostamento di un file: l’aggiornamento del riferimento è un’operazione esplicita.
- Perdere la possibilità di ritrovare un oggetto rimosso da Elevia: la rimozione elimina le associazioni, non la risorsa.

### Operazioni atomiche

- Applicare metà di un piano dopo un errore.
- Confermare un’anteprima obsoleta dopo che i dati coinvolti sono cambiati.
- Permettere a un’operazione concorrente di aggirare unicità, ultima assegnazione o divieti sui cicli.
- Risolvere automaticamente un conflitto senza scelta esplicita dell’utente.

## Sintesi visiva


```text
Definizioni condivise                     ← definite prima dell’uso
│
├── Controlled Vocabulary
│   └── Tag Registry                      ← un’identità per ogni Tag
│       ├── Lavoro     [T1]
│       ├── Passioni   [T2]
│       ├── Ferrari    [T3]
│       ├── Contratti  [T4]
│       └── Fotografie [T5]
│
└── Metadata Schema
    ├── work
    │   ├── status: testo, un valore      ← draft / approved / archived
    │   └── project: testo, un valore     ← valore libero nel tipo
    └── photo
        └── year: numero, un valore       ← valore libero nel tipo
              │
              ▼
Tag placements                           ← collocazioni con identità stabile
│
├── Lavoro [T1, P1]
│   └── Ferrari [T3, P2]
│       └── Contratti [T4, P3]
│
└── Passioni [T2, P4]
    └── Ferrari [T3, P5]                  ← stesso Tag, altro placement
        ├── Contratti [T4, P6]            ← aggiunto esplicitamente anche qui
        └── Fotografie [T5, P7]           ← presente solo in questo contesto
              │
              ▼
Inserimento guidato
├── Da un ramo: Elevia predispone quel contesto
├── Da inserimento generale: propone contesti in base allo storico
└── L’utente sceglie uno o più contesti e conferma
    └── Nessuna assegnazione automatica basata sullo storico
              │
              ▼
Objects e Tagging                        ← almeno un placement per oggetto
│
├── Accordo professionale [obj-001]
│   └── P3: Lavoro → Ferrari → Contratti
│
├── Contratto di acquisto di un modellino [obj-002]
│   └── P6: Passioni → Ferrari → Contratti
│
└── Foto a Monza [obj-003]
    ├── P7: Passioni → Ferrari → Fotografie
    ├── Attribute: photo.year = 2026
    └── Risorsa originale: /Foto/monza.jpg ← il file non viene spostato
              │
              ▼
Ricerca esplicita                        ← include i discendenti selezionati
│
├── OVUNQUE: Ferrari [T3]
│   └── obj-001, obj-002, obj-003
│
├── SOLO QUESTO RAMO: Lavoro → Ferrari [P2]
│   └── obj-001
│
├── SOLO QUESTO RAMO: Passioni → Ferrari [P5]
│   └── obj-002, obj-003
│
└── OVUNQUE: Contratti [T4]
    └── obj-001, obj-002
              │
              ▼
Filtro su Attribute                      ← indipendente da Tag e placement
└── Condizione: photo.year = 2026
    └── Applicabile a tutti gli oggetti o a un ramo scelto separatamente
              │
              ▼
Risultato della query
└── Foto a Monza [obj-003], una sola volta
```

Il contesto completo distingue i due contratti: il solo padre immediato darebbe Ferrari → Contratti in entrambi i casi. I figli di un placement non vengono condivisi automaticamente con gli altri placement dello stesso Tag.

«Ovunque» considera tutte le collocazioni del Tag e i loro discendenti. «Solo questo ramo» non salta alle altre collocazioni dei Tag incontrati. Ogni oggetto compare una sola volta nei risultati; gli antenati non diventano automaticamente Tag direttamente assegnati.

```text
Tagging degli oggetti
├── Aggiungi anche a…                     ← conserva quelle esistenti
├── Trasferisci in…                       ← sostituisce quella di partenza
└── Rimuovi da questo contesto            ← rimuove soltanto quella scelta

Esempio indipendente dai risultati sopra
└── Aggiungi obj-001 anche a P6
    └── obj-001 ha ora P3 e P6, senza duplicare oggetto o file

Vincoli
├── Nessuna assegnazione duplicata allo stesso placement
├── Nessuna rimozione dell’ultima assegnazione senza sostituzione
├── Nessuna sincronizzazione automatica tra contesti per i documenti futuri
├── Modifiche atomiche: un errore rifiuta l’intera operazione
└── Nessun ciclo
    ├── Tra placement: vietato spostare un ramo dentro un proprio discendente
    └── Tra Tag: vietati anche A → B e B → A in contesti diversi

Struttura e risorse
├── Rinominare un Tag non interrompe le assegnazioni ai placement
├── Un placement radice permette di usare un Tag senza genitore
├── Assegnare un oggetto non sposta il placement né il suo ramo
├── Modificare la struttura richiede un’anteprima dell’impatto
├── Nessuna fusione automatica con un placement già presente a destinazione
├── Eliminazione di placement con figli o assegnazioni bloccata finché risolti
├── Risorsa indisponibile: l’Object resta ricercabile
└── Rimuovere un Object non elimina la risorsa originale
```

Il namespace `work` non è il Tag Lavoro: gli Attributes vengono assegnati esplicitamente e devono rispettare lo schema.


# Fase avanzata

La comprensione del linguaggio naturale e l’esplorazione semantica sono sviluppi futuri e non rientrano nel perimetro attuale.

Elevia permetterà di gestire in modo diverso, stile Plugin ogni tipo di file diverso, per avere massima personalizzazione. Tipo un file JPEG uscirà l'anteprima. Un file Font uscirà l'anteprima del font.


____
***Lingua progetto attuale:** it_IT*

***Nota:** il nome **Elevia** è provvisorio e verrà sostituito, poiché già utilizzato altrove.*

***Nota:** sto valutando se trasformarlo in un paper collaborativo. Servirà una struttura decisionale (ad esempio ad albero) e strumenti gestionali per organizzare i contributi senza disperdere le idee migliori.*
