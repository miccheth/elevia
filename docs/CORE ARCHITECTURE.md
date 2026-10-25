# CORE ARCHITECTURE

## Schema Relazione Database

```text
erDiagram
    OBJECT {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        string name "NOT NULL"
        string object_type "NOT NULL (ENUM: LOCAL_FILE, GENERIC_OBJECT)"
        timestamp created_at "NOT NULL"
        timestamp updated_at "NOT NULL"
    }

    LOCAL_FILE_OBJECT {
        bigint object_id PK, FK "NOT NULL"
        boolean is_available "NOT NULL"
        text file_path "NOT NULL"
        text normalized_path "NOT NULL"
        bigint file_size "NOT NULL"
        timestamp modified_at "NOT NULL"
        string file_extension "NOT NULL"
    }

    TAG {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        string name UK "NOT NULL, CASE INSENSITIVE"
        text description "NULLABLE"
        boolean is_system "NOT NULL, DEFAULT 0"
        timestamp created_at "NOT NULL"
        timestamp updated_at "NOT NULL"
    }

    PLACEMENT {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        bigint tag_id FK "NOT NULL"
        bigint parent_id FK "NULLABLE"
        timestamp created_at "NOT NULL"
    }

    TAGGING {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        bigint object_id FK "NOT NULL"
        bigint placement_id FK "NOT NULL"
        timestamp created_at "NOT NULL"
    }

    OBJECT ||--o| LOCAL_FILE_OBJECT : "estende dettagli file locale"
    TAG ||--o{ PLACEMENT : "definisce"
    PLACEMENT o|--o{ PLACEMENT : "gerarchia padre-figlio"
    OBJECT ||--o{ TAGGING : "assegnato tramite"
    PLACEMENT ||--o{ TAGGING : "collega a"
```

### Vincoli del Database (a livello schema)

- **PK:** `OBJECT.id`, `TAG.id`, `PLACEMENT.id`, `TAGGING.id` — auto-increment, NOT NULL; riutilizzabili dopo `delete()` (interni al Core)
- **FK con integrità referenziale:** tutti i riferimenti a righe inesistenti sono rifiutati
  - `LOCAL_FILE_OBJECT.object_id` → `OBJECT.id` (PK e FK 1:1)
  - `PLACEMENT.tag_id` → `TAG.id` (NOT NULL)
  - `PLACEMENT.parent_id` → `PLACEMENT.id` (NULLABLE, NULL = radice, max 1 padre)
  - `TAGGING.object_id` → `OBJECT.id` (NOT NULL)
  - `TAGGING.placement_id` → `PLACEMENT.id` (NOT NULL)
- **UNIQUE:**
  - `TAG.name` — NOT NULL, case insensitive
  - `PLACEMENT (tag_id, parent_id)` — stesso Tag max 1 Placement per padre
  - `PLACEMENT (tag_id) WHERE parent_id IS NULL` — max 1 Placement radice per Tag
  - `TAGGING (object_id, placement_id)` — stesso Object max 1 volta per Placement
- **NOT NULL:** tutti i campi dello schema tranne `TAG.description` e `PLACEMENT.parent_id`
- **ENUM:** `OBJECT.object_type` (LOCAL_FILE, GENERIC_OBJECT)
- **INDICI:**
  - `PLACEMENT(parent_id)` per la ricostruzione dei percorsi
  - `TAGGING(placement_id)` per il filtro sulle assegnazioni
- **TRIGGER:**
  - `TAG.is_system = 1` → rinomina e cancellazione rifiutate a livello DB
  - aggiornamento automatico di `updated_at` su `OBJECT` e `TAG`

## Regole di Business (a livello application)

### Regole su OBJECT (R1-R7)

- **R1:** Object registrato ha almeno 1 TAGGING (se non assegnato, finiscono nei Tag di default 'Untagged')
- **R2:** Rinominare non cambia identità né associazioni
- **R3:** Aggiornare `file_path` conserva identità (operazione automatico, con conferma utente)
- **R4:** `is_available=0` → risorsa indisponibile, resta ricercabile nel DB
- **R5:** Rimuovere Object elimina le associazioni, NON il file originale
- **R6:** Mai modificare, spostare o eliminare file originali tramite Elevia (solo `file_path` salvato, mai modifiche filesystem)
- **R7:** Un Object rimosso resta ritrovabile: vengono rimosse solo dallo strato logico di Elevia, non la risorsa originale.

### Regole su TAG (R8-R12)

- **R8:** Nome univoco e case insensitive.
- **R9:** Tag può esistere senza Placement (definizione non usata); non si crea automaticamente un Placement radice solo perché un TAG non ne ha uno
- **R10:** Rinominare Tag non interrompe assegnazioni ai Placement
- **R11:** Eliminare Tag solo dopo aver risolto tutti i suoi Placement
- **R12:** Nessun alias automatico per un TAG ritirato
- **R46:** Il Tag `Untagged` è nativo: esiste dal seed iniziale con `is_system = 1`, insieme al suo Placement radice
- **R47:** Un Tag con `is_system = 1` non può essere rinominato, eliminato né usato come sorgente di una fusione
- **R48:** `Untagged` non è una scorciatoia per gli oggetti senza Tag: è la collocazione assegnata quando l'ultima Tagging viene rimossa (R1, R25)

### Regole su PLACEMENT (R13-R21)

- **R13:** Max 1 padre per Placement
- **R14:** `parent_id = NULL` indica radice
- **R15:** Max 1 Placement radice per Tag
- **R16:** Stesso Tag max 1 volta sotto lo stesso padre
- **R17:** Stesso Tag può avere più Placement in contesti diversi
- **R18:** Figli non condivisi automaticamente tra Placement dello stesso Tag
- **R19:** Spostare Placement conserva identità, discendenti, assegnazioni; vietato spostare un ramo dentro sé stesso o dentro un proprio discendente
- **R20:** Eliminare Placement solo se senza figli e senza assegnazioni (no eliminazione ricorsiva automatica)
- **R21:** Aggiungere collocazione crea Placement vuoto, senza copiare; vietato spostare un Placement dove esiste già lo stesso TAG senza conflitto esplicito

### Regole su TAGGING (R22-R29)

- **R22:** Coppia univoca (`object_id`, `placement_id`)
- **R23:** Nessuna assegnazione globale senza collocazione
- **R24:** Object può avere più Tagging (a Placement diversi)
- **R25:** Rimuovere l'ultimo Tagging di un Object viene messo in UnTagged
- **R26:** Trasferimento richiede partenza esistente (vietato trasferire da un contesto in cui non è assegnato)
- **R27:** Destinazione o Object inesistente = errore
- **R28:** Operazioni senza effetto non producono nuove assegnazioni
- **R29:** Nessuna sincronizzazione automatica tra contesti; un suggerimento non diventa assegnazione senza conferma esplicita

### Regole su TRANSAZIONI e VALIDAZIONE (R34-R40)

Il **TransactionManager** è il garante di tutte le regole di business (R1-R40). Ogni operazione passa attraverso di esso: valida lo stato proposto contro tutte le regole, e solo se tutte sono rispettate esegue la transazione (tutto-o-niente).

- **R30:** Nessun ciclo tra Placement (no padre di sé stesso o di propri discendenti)
- **R31:** Nessun ciclo tra identità dei Tag (grafo globale aciclico)
- **R32:** A→B e B→A non coesistono neppure in contesti separati
- **R33:** Eliminare un collegamento non elimina gli altri equivalenti; vietato fondere automaticamente due rami con lo stesso TAG o due TAG se la sostituzione crea un ciclo (fusione sempre con scelta esplicita)
- **R34:** Ogni piano confermato è una sola transazione (tutto-o-niente)
- **R35:** In caso di violazione di una qualsiasi regola (R1-R33) o in caso di errore, nessuna parte del piano viene applicata
- **R36:** Modifiche strutturali richiedono anteprima (impatto, conflitti)
- **R37:** Anteprima non modifica dati e non vale come conferma
- **R38:** Alla conferma, il TransactionManager ricontrolla riferimenti, vincoli (R1-R33) e stato anteprima
- **R39:** Dati cambiati dopo anteprima → conferma rifiutata
- **R40:** Operazioni concorrenti non aggirano vincoli (lock DB); vietato risolvere automaticamente un conflitto senza scelta esplicita dell'utente


## Flusso Operativo

```text
Importare un file
└── User → import_cmd →
    LocalFileObjectService.register() (crea Object + LocalFileObject + Tagging, atomico) →
    TransactionManager (valida R1-R7, R22-R29) →
    ObjectRepository + LocalFileObjectRepository + TaggingRepository → Database

Aggiungere un Tag a un Object
└── User → TaggingService.assign() →
    TransactionManager (valida R22, R23, R28) →
    TaggingRepository → Database

Trasferire un Object in un altro contesto
└── User → TaggingService.transfer() →
    TransactionManager (valida R26, R27) →
    TaggingRepository → Database

Rimuovere un Object da un contesto
└── User → TaggingService.remove() →
    (se ultimo Tagging → assegna a Untagged, R25) →
    TransactionManager (valida R25) →
    TaggingRepository → Database

Creare un Placement
└── User → PlacementService.create() →
    TransactionManager (valida R13-R17, R21) →
    PlacementRepository → Database

Spostare un Placement
└── User → PreviewService (anteprima impatto, R36) →
    conferma utente → PlacementService.move() →
    TransactionManager (valida R19, R30-R33 cicli, R38-R39) →
    PlacementRepository → Database

Eliminare un Placement
└── User → PlacementService.delete() →
    TransactionManager (valida R20: bloccato se figli o assegnazioni) →
    PlacementRepository → Database

Eliminare un Tag
└── User → TagService.delete() →
    TransactionManager (valida R11: bloccato se Placement non risolti) →
    TagRepository → Database

Rinominare un Object / un Tag
└── User → ObjectService.rename() / TagService.rename() →
    TransactionManager (valida R2, R8, R10) →
    ObjectRepository / TagRepository → Database

Rimuovere un Object da Elevia
└── User → ObjectService.remove() →
    (rimuove solo TAGGING, non il file originale, R5-R7) →
    TransactionManager (valida R5-R7) →
    TaggingRepository + ObjectRepository → Database

Vedere albero — sola lettura, nessun TransactionManager
└── User → TagPlacementTreeService.get_tree() →
    PlacementRepository.find_all() →
    struttura ad albero (radici → figli ricorsivo)

Ricercare oggetti — sola lettura, nessun TransactionManager
└── User → QueryService.search(espressione) →
    parser → SQL generato → Database (percorsi calcolati, nessuna scrittura)

Controllo disponibilità file (all'avvio della CLI)
└── LocalFileAvailableCheck → confronta i percorsi registrati con il filesystem →
    LocalFileObjectService.mark_available()/mark_unavailable() (R3, R4) →
    TransactionManager (valida R3, R4, R6) →
    LocalFileObjectRepository.save() → Database
```

## Query

Ricerca esplicita, sola lettura. Nessun TransactionManager, nessuna anteprima, nessun lock. La query non modifica dati e non produce effetti collaterali.

Lo scopo è una sintassi minima: un solo tipo di condizione, `tag:percorso`, e gli operatori logici `AND`, `OR`, `NOT`. Non esistono modalità "ovunque" e "solo questo ramo" come concetti separati: il percorso scritto decide l'ambito.

### Sintassi

```ebnf
query     = or_expr ;
or_expr   = and_expr , { "OR" , and_expr } ;
and_expr  = term , { "AND" , term } ;
term      = [ "NOT" ] , atom ;
atom      = "(" , query , ")" | condition ;
condition = "tag:" , value ;
value     = "*" | name , { "." , name } ;
name      = parola | '"' , testo , '"' ;
```

### Stile

Una sola condizione si scrive senza parentesi. Più condizioni si scrivono con ogni condizione tra parentesi e l'operatore in mezzo.

```text
tag:Ferrari
tag:*
tag:Passioni.Ferrari.Fotografie

(tag:Ferrari) AND (tag:Fotografie)
(tag:Ferrari) OR (tag:Passioni)
NOT (tag:Fotografie)
(tag:Ferrari) AND NOT (tag:Fotografie)
((tag:Ferrari) OR (tag:Passioni)) AND (tag:Contratti)
```

### Semantica

`tag:X.Y.Z` corrisponde agli oggetti con una Tagging su un Placement il cui percorso contiene, uno dietro l'altro, i Tag `X`, `Y` e `Z`. Da questa sola regola derivano tutti i casi:

| Condizione | Restituisce |
| --- | --- |
| `tag:*` | tutti gli oggetti registrati, `Untagged` incluso |
| `tag:Ferrari` | tutto ciò che ha Ferrari, in qualunque ramo, discendenti compresi |
| `tag:Ferrari.Fotografie` | il ramo Ferrari → Fotografie, in qualunque radice |
| `tag:Passioni.Ferrari.Fotografie` | lo stesso ramo, ma solo sotto Passioni |
| `tag:Lavoro.Ferrari.Contratti` | il ramo contratti di lavoro |

Con i dati del README:

```text
tag:Ferrari                                   → obj-001, obj-002, obj-003
tag:Ferrari.Contratti                         → obj-001, obj-002
tag:Lavoro.Ferrari.Contratti                  → obj-001
(tag:Ferrari) AND (tag:Contratti)             → obj-001, obj-002
(tag:Ferrari) AND NOT (tag:Fotografie)        → obj-001, obj-002
(tag:Passioni.Ferrari) AND NOT (tag:Contratti) → obj-003
```

Un `AND` tra due condizioni può essere soddisfatto da due Tagging diverse dello stesso oggetto. Per vincolare allo stesso ramo si scrive una sola condizione con il percorso completo: `tag:Lavoro.Ferrari.Contratti`, non `(tag:Lavoro) AND (tag:Contratti)`.

`NOT` è il complemento rispetto a `tag:*`. `AND` è intersezione, `OR` è unione. Ogni oggetto compare una sola volta nei risultati.

### Regole (R41-R45)

- **R41:** la query è sola lettura: non scrive, non apre transazioni, non passa dal TransactionManager.
- **R42:** una query non valida è un errore esplicito, mai un risultato parziale.
- **R43:** ogni oggetto compare una sola volta nei risultati, anche se soddisfa più condizioni.
- **R44:** il confronto dei nomi dei Tag è case insensitive (R8).
- **R45:** `tag:*` corrisponde a tutti gli oggetti registrati, compresi quelli in `Untagged`.

### Errori

| Caso | Esempio | Esito |
| --- | --- | --- |
| operatore senza parentesi | `tag:A AND tag:B` | errore di sintassi |
| parentesi non chiusa o vuota | `(tag:A` , `()` | errore di sintassi |
| operatore mancante | `(tag:A) (tag:B)` | errore di sintassi |
| condizione vuota | `tag:` | errore di sintassi |
| `NOT` senza condizione | `NOT` | errore di sintassi |
| operatore sconosciuto | `(tag:A) XOR (tag:B)` | errore di sintassi |
| wildcard insieme ad altro | `tag:*.Ferrari` | errore di sintassi |
| Tag inesistente | `tag:Inesistente` | errore, con il nome del Tag |
| percorso inesistente con Tag validi | `tag:Ferrari.Contratti` senza quel ramo | zero risultati, non errore |

### Limiti della v1

- Nessuna condizione sugli Attributes: arriverà con lo schema dei metadati.
- Nessun wildcard di segmento (`tag:*.Contratti`), nessun alias tipo `ovunque` o `ramo`.
- Nessun ordinamento personalizzato: risultati per nome.
- Nessuna sintassi per intervalli o confronti numerici.

### Implementazione

`QueryService.search(espressione)` valida la sintassi con il parser, traduce le condizioni in una singola query SQL con `EXISTS` per condizione e una CTE ricorsiva che ricostruisce i percorsi risalendo i `parent_id`. L'SQL vive nel servizio: non esiste un repository dedicato alla query. Il percorso è calcolato al momento della query e non è memorizzato: resta un dato derivato, non una seconda fonte di verità.

Indici necessari: `PLACEMENT(parent_id)` per la ricostruzione dei percorsi, `TAGGING(placement_id)` per il filtro sulle assegnazioni.

## Architettura a Layer

```text
Elevia Core
├── Actor
│   ├── User (GUI/CLI)
│   └── FileSystem (sorgente esterna, monitorata)
│
├── Domain Layer (entità di dominio)
│   ├── Object (abstract)
│   │   └── LocalFileObject (extends Object)
│   ├── Tag
│   ├── Placement (auto-referenza: parent_id)
│   └── Tagging (collega Object ↔ Placement)
│
├── Application Layer (servizi applicativi)
│   ├── extends LocalFileObjectService (override register - rename - remove, update_path, mark_unavailable, mark_available)
│   ├── abstract ObjectService (register, rename, remove)
│   ├── TaggingService (assign, transfer, remove)
│   ├── PlacementService (create_placement, move, delete)
│   ├── TagService (create, rename, delete)
│   ├── PreviewService (anteprima impatto, R36)
│   ├── TagPlacementTreeService (get_tree)
│   ├── QueryService (search, ricerca esplicita R41-R45)
│   └── QueryParser (grammatica tag:, AND, OR, NOT)
│
├── Infrastructure Layer (servizi tecnici)
│   ├── TransactionManager (garante R1-R40, valida cicli R30-R33)
│   ├── LocalFileAvailableCheck (controlla disponibilità file all'avvio)
│   ├── ObjectRepository
│   ├── LocalFileObjectRepository
│   ├── TagRepository
│   ├── PlacementRepository
│   ├── TaggingRepository
│   ├── schema.sql (DDL, indici, trigger)
│   ├── migrator (applica lo schema)
│   ├── seed (crea il Tag nativo Untagged e il suo Placement radice)
│   └── Database (esterno)
```