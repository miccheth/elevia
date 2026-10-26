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

    ATTRIBUTE_NAMESPACE {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        string name UK "NOT NULL, CASE INSENSITIVE"
        text description "NULLABLE"
        timestamp created_at "NOT NULL"
    }

    ATTRIBUTE_DEFINITION {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        bigint namespace_id FK "NOT NULL"
        string key "NOT NULL"
        string value_type "NOT NULL (ENUM: TEXT, NUMBER, DATE, BOOLEAN, ENUM)"
        text allowed_values "NULLABLE (JSON array per ENUM)"
        text description "NULLABLE"
        timestamp created_at "NOT NULL"
    }

    OBJECT_ATTRIBUTE {
        bigint id PK "AUTO INCREMENT, NOT NULL"
        bigint object_id FK "NOT NULL"
        bigint definition_id FK "NULLABLE (NULL = attributo libero)"
        string namespace "NULLABLE (copia denormalizzata, NULL = libero)"
        string key "NOT NULL"
        text value "NOT NULL"
        string value_type "NOT NULL (ENUM: TEXT, NUMBER, DATE, BOOLEAN, ENUM)"
        timestamp created_at "NOT NULL"
    }

    OBJECT ||--o| LOCAL_FILE_OBJECT : "estende dettagli file locale"
    TAG ||--o{ PLACEMENT : "definisce"
    PLACEMENT o|--o{ PLACEMENT : "gerarchia padre-figlio"
    OBJECT ||--o{ TAGGING : "assegnato tramite"
    PLACEMENT ||--o{ TAGGING : "collega a"
    ATTRIBUTE_NAMESPACE ||--o{ ATTRIBUTE_DEFINITION : "contiene"
    ATTRIBUTE_DEFINITION ||--o{ OBJECT_ATTRIBUTE : "definisce tipo per"
    OBJECT ||--o{ OBJECT_ATTRIBUTE : "ha attributi"
```

### Vincoli del Database (a livello schema)

- **PK:** `OBJECT.id`, `TAG.id`, `PLACEMENT.id`, `TAGGING.id`, `ATTRIBUTE_NAMESPACE.id`, `ATTRIBUTE_DEFINITION.id`, `OBJECT_ATTRIBUTE.id` — auto-increment, NOT NULL; riutilizzabili dopo `delete()` (interni al Core)
- **FK con integrità referenziale:** tutti i riferimenti a righe inesistenti sono rifiutati
  - `LOCAL_FILE_OBJECT.object_id` → `OBJECT.id` (PK e FK 1:1)
  - `PLACEMENT.tag_id` → `TAG.id` (NOT NULL)
  - `PLACEMENT.parent_id` → `PLACEMENT.id` (NULLABLE, NULL = radice, max 1 padre)
  - `TAGGING.object_id` → `OBJECT.id` (NOT NULL)
  - `TAGGING.placement_id` → `PLACEMENT.id` (NOT NULL)
  - `ATTRIBUTE_DEFINITION.namespace_id` → `ATTRIBUTE_NAMESPACE.id` (NOT NULL)
  - `OBJECT_ATTRIBUTE.object_id` → `OBJECT.id` (NOT NULL)
  - `OBJECT_ATTRIBUTE.definition_id` → `ATTRIBUTE_DEFINITION.id` (NULLABLE, NULL = attributo libero)
- **UNIQUE:**
  - `TAG.name` — NOT NULL, case insensitive
  - `PLACEMENT (tag_id, parent_id)` — stesso Tag max 1 Placement per padre
  - `PLACEMENT (tag_id) WHERE parent_id IS NULL` — max 1 Placement radice per Tag
  - `TAGGING (object_id, placement_id)` — stesso Object max 1 volta per Placement
  - `ATTRIBUTE_NAMESPACE.name` — NOT NULL, case insensitive
  - `ATTRIBUTE_DEFINITION (namespace_id, key)` — stessa chiave max 1 volta per namespace
  - `OBJECT_ATTRIBUTE (object_id, namespace, key)` — stesso valore max 1 volta per oggetto/chiave (namespace NULL = attributo libero)
- **NOT NULL:** tutti i campi dello schema tranne `TAG.description`, `PLACEMENT.parent_id`, `ATTRIBUTE_NAMESPACE.description`, `ATTRIBUTE_DEFINITION.allowed_values`, `ATTRIBUTE_DEFINITION.description`, `OBJECT_ATTRIBUTE.definition_id`, `OBJECT_ATTRIBUTE.namespace`
- **ENUM:**
  - `OBJECT.object_type` (LOCAL_FILE, GENERIC_OBJECT)
  - `ATTRIBUTE_DEFINITION.value_type` (TEXT, NUMBER, DATE, BOOLEAN, ENUM)
  - `OBJECT_ATTRIBUTE.value_type` (TEXT, NUMBER, DATE, BOOLEAN, ENUM)
- **INDICI:**
  - `PLACEMENT(parent_id)` per la ricostruzione dei percorsi
  - `TAGGING(placement_id)` per il filtro sulle assegnazioni
  - `OBJECT_ATTRIBUTE(object_id)` per la lista attributi di un oggetto
  - `OBJECT_ATTRIBUTE(namespace, key, value)` per il filtro nelle query
  - `OBJECT_ATTRIBUTE(key)` per la ricerca per chiave (anche attributi liberi)
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

### Regole su ATTRIBUTE NAMESPACE (R49-R52)

- **R49:** Il nome del namespace è univoco e case insensitive.
- **R50:** Un namespace può esistere senza definizioni (template vuoto).
- **R51:** Eliminare un namespace elimina tutte le sue definizioni e i valori sugli oggetti (CASCADE).
- **R52:** Rinominare un namespace non interrompe i valori sugli oggetti (il nome è denormalizzato in `OBJECT_ATTRIBUTE.namespace`).

### Regole su ATTRIBUTE DEFINITION (R53-R57)

- **R53:** La coppia `(namespace_id, key)` è univoca: stessa chiave max 1 volta per namespace.
- **R54:** Il tipo `ENUM` richiede `allowed_values` (array JSON non vuoto).
- **R55:** I tipi `TEXT`, `NUMBER`, `DATE`, `BOOLEAN` non usano `allowed_values` (NULL).
- **R56:** Eliminare una definizione elimina i valori sugli oggetti che la usano (CASCADE).
- **R57:** Modificare il tipo di una definizione non converte i valori esistenti: è responsabilità dell'utente.

### Regole su OBJECT_ATTRIBUTE (R58-R65)

- **R58:** Gli attributi possono essere **con namespace** (definiti in un template) o **liberi** (senza namespace, `definition_id = NULL`, `namespace = NULL`).
- **R59:** Per gli attributi con namespace, la definizione deve esistere prima dell'assegnazione.
- **R60:** Per gli attributi liberi, il tipo viene **dedotto automaticamente** dal valore alla prima assegnazione.
- **R61:** Un oggetto può avere un solo valore per chiave (con o senza namespace): `UNIQUE (object_id, namespace, key)`.
- **R62:** I valori sono validati in base al tipo quando vengono assegnati.
- **R63:** Per gli attributi `ENUM`, il valore deve essere uno dei `allowed_values` definiti.
- **R64:** Eliminare un oggetto elimina tutti i suoi attributi (CASCADE).
- **R65:** Gli attributi sono indipendenti dai Tag e dai Placement: possono essere usati in query globali o limitate a un ramo.

### Deduzione del tipo (attributi liberi)

Quando l'utente assegna un attributo libero (senza namespace), il sistema deduce il tipo dal valore:

| Valore | Tipo dedotto | Esempio |
|--------|-------------|---------|
| Intero o decimale | `NUMBER` | `2025`, `1500.50` |
| Data ISO 8601 (`YYYY-MM-DD`) | `DATE` | `2025-01-15` |
| `true` / `false` | `BOOLEAN` | `true` |
| Qualsiasi altra stringa | `TEXT` | `"Ferrari"` |

### Regole su TRANSAZIONI e VALIDAZIONE (R34-R40)

Il **TransactionManager** è il garante di tutte le regole di business (R1-R65). Ogni operazione passa attraverso di esso: valida lo stato proposto contro tutte le regole, e solo se tutte sono rispettate esegue la transazione (tutto-o-niente).

- **R30:** Nessun ciclo tra Placement (no padre di sé stesso o di propri discendenti)
- **R31:** Nessun ciclo tra identità dei Tag (grafo globale aciclico)
- **R32:** A→B e B→A non coesistono neppure in contesti separati
- **R33:** Eliminare un collegamento non elimina gli altri equivalenti; vietato fondere automaticamente due rami con lo stesso TAG o due TAG se la sostituzione crea un ciclo (fusione sempre con scelta esplicita)
- **R34:** Ogni piano confermato è una sola transazione (tutto-o-niente)
- **R35:** In caso di violazione di una qualsiasi regola (R1-R65) o in caso di errore, nessuna parte del piano viene applicata
- **R36:** Modifiche strutturali richiedono anteprima (impatto, conflitti)
- **R37:** Anteprima non modifica dati e non vale come conferma
- **R38:** Alla conferma, il TransactionManager ricontrolla riferimenti, vincoli (R1-R65) e stato anteprima
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

Creare un namespace di attributi
└── User → AttributeNamespaceService.create() →
    TransactionManager (valida R49) →
    AttributeNamespaceRepository → Database

Definire un attributo in un namespace
└── User → AttributeDefinitionService.create() →
    TransactionManager (valida R53-R55) →
    AttributeDefinitionRepository → Database

Assegnare un attributo con namespace a un Object
└── User → ObjectAttributeService.set() →
    (cerca definizione, valida tipo e valore, R59, R62-R63) →
    TransactionManager (valida R58-R63) →
    ObjectAttributeRepository → Database

Assegnare un attributo libero (senza namespace) a un Object
└── User → ObjectAttributeService.set() →
    (deduce tipo dal valore, R60) →
    TransactionManager (valida R58, R60-R62) →
    ObjectAttributeRepository → Database

Rimuovere un attributo da un Object
└── User → ObjectAttributeService.unset() →
    TransactionManager (valida R64) →
    ObjectAttributeRepository → Database

Eliminare un namespace (elimina definizioni e valori sugli oggetti)
└── User → AttributeNamespaceService.delete() →
    TransactionManager (valida R51, CASCADE) →
    AttributeNamespaceRepository → Database

Eliminare una definizione (elimina valori sugli oggetti)
└── User → AttributeDefinitionService.delete() →
    TransactionManager (valida R56, CASCADE) →
    AttributeDefinitionRepository → Database
```

## Query

Ricerca esplicita, sola lettura. Nessun TransactionManager, nessuna anteprima, nessun lock. La query non modifica dati e non produce effetti collaterali.

Lo scopo è una sintassi minima: due tipi di condizioni, `tag:percorso` e `namespace.chiave = valore` (o `chiave = valore` per attributi liberi), combinabili con gli operatori logici `AND`, `OR`, `NOT`. Non esistono modalità "ovunque" e "solo questo ramo" come concetti separati: il percorso scritto decide l'ambito.

### Sintassi

```ebnf
query          = or_expr ;
or_expr        = and_expr , { "OR" , and_expr } ;
and_expr       = term , { "AND" , term } ;
term           = [ "NOT" ] , atom ;
atom           = "(" , query , ")" | condition ;
condition      = tag_condition | attr_condition ;
tag_condition  = "tag:" , tag_value ;
tag_value      = "*" | name , { "." , name } ;
attr_condition = attr_path , operator , value ;
attr_path      = [ name , "." ] , name ;
operator       = "=" | "!=" | ">" | "<" | ">=" | "<=" ;
value          = string | number | date | boolean ;
name           = parola | '"' , testo , '"' ;
string         = '"' , testo , '"' ;
number         = [ "-" ] , cifra , { cifra } , [ "." , cifra , { cifra } ] ;
date           = '"' , YYYY-MM-DD , '"' ;
boolean        = "true" | "false" ;
```

### Stile

Una sola condizione si scrive senza parentesi. Più condizioni si scrivono con ogni condizione tra parentesi e l'operatore in mezzo.

```text
tag:Ferrari
tag:*
tag:Passioni.Ferrari.Fotografie
photo.year = 2025
work.status = "approved"
colore = "rosso"

(tag:Ferrari) AND (tag:Fotografie)
(tag:Ferrari) OR (tag:Passioni)
NOT (tag:Fotografie)
(tag:Ferrari) AND NOT (tag:Fotografie)
((tag:Ferrari) OR (tag:Passioni)) AND (tag:Contratti)
(tag:Ferrari) AND (photo.year = 2025)
(photo.year >= 2020) AND (photo.year <= 2025)
(tag:Contratti) AND (work.status = "approved")
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

Le condizioni sugli attributi `namespace.chiave = valore` (o `chiave = valore` per attributi liberi) corrispondono agli oggetti che hanno quell'attributo con quel valore. Gli operatori `>`, `<`, `>=`, `<=` sono ammessi solo per attributi di tipo `NUMBER` o `DATE`.

| Condizione | Restituisce |
| --- | --- |
| `photo.year = 2025` | oggetti con `photo.year` uguale a 2025 |
| `work.status = "approved"` | oggetti con `work.status` uguale a "approved" |
| `finance.amount >= 1000` | oggetti con `finance.amount` maggiore o uguale a 1000 |
| `work.deadline < "2025-12-31"` | oggetti con `work.deadline` precedente al 31 dicembre 2025 |
| `colore = "rosso"` | oggetti con attributo libero `colore` uguale a "rosso" |
| `anno = 2025` | oggetti con attributo libero `anno` uguale a 2025 |

Con i dati del README:

```text
tag:Ferrari                                   → obj-001, obj-002, obj-003
tag:Ferrari.Contratti                         → obj-001, obj-002
tag:Lavoro.Ferrari.Contratti                  → obj-001
(tag:Ferrari) AND (tag:Contratti)             → obj-001, obj-002
(tag:Ferrari) AND NOT (tag:Fotografie)        → obj-001, obj-002
(tag:Passioni.Ferrari) AND NOT (tag:Contratti) → obj-003
photo.year = 2025                             → obj-003 (se obj-003 ha photo.year = 2025)
(tag:Ferrari) AND (photo.year = 2025)         → obj-003
```

Un `AND` tra due condizioni può essere soddisfatto da due Tagging diverse dello stesso oggetto, o da due attributi diversi. Per vincolare allo stesso ramo si scrive una sola condizione con il percorso completo: `tag:Lavoro.Ferrari.Contratti`, non `(tag:Lavoro) AND (tag:Contratti)`.

`NOT` è il complemento rispetto a `tag:*`. `AND` è intersezione, `OR` è unione. Ogni oggetto compare una sola volta nei risultati.

### Regole (R41-R48)

- **R41:** la query è sola lettura: non scrive, non apre transazioni, non passa dal TransactionManager.
- **R42:** una query non valida è un errore esplicito, mai un risultato parziale.
- **R43:** ogni oggetto compare una sola volta nei risultati, anche se soddisfa più condizioni.
- **R44:** il confronto dei nomi dei Tag è case insensitive (R8).
- **R45:** `tag:*` corrisponde a tutti gli oggetti registrati, compresi quelli in `Untagged`.
- **R46:** il confronto delle chiavi degli attributi è case insensitive.
- **R47:** gli operatori `>`, `<`, `>=`, `<=` sono ammessi solo per attributi di tipo `NUMBER` o `DATE`; su altri tipi producono errore.
- **R48:** una condizione su attributo con namespace inesistente è un errore; una condizione su attributo libero inesistente restituisce zero risultati.

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
| namespace attributo inesistente | `photo.year = 2025` senza namespace `photo` | errore, con il nome del namespace |
| chiave attributo inesistente nel namespace | `photo.colore = "rosso"` senza `colore` in `photo` | errore, con namespace e chiave |
| confronto non ammesso per il tipo | `work.status > "approved"` (status è TEXT) | errore, tipo non confrontabile |
| valore non valido per il tipo | `photo.year = "abc"` (year è NUMBER) | errore, valore non valido |
| valore ENUM non nella lista | `work.status = "pending"` (non in allowed_values) | errore, valore non ammesso |

### Limiti della v1

- Nessun wildcard di segmento (`tag:*.Contratti`), nessun alias tipo `ovunque` o `ramo`.
- Nessun ordinamento personalizzato: risultati per nome.
- Nessuna sintassi per `exists` / `missing` (presente/assente).
- Nessun multi-valore per attributi (un oggetto = un valore per chiave).

### Implementazione

`QueryService.search(espressione)` valida la sintassi con il parser, traduce le condizioni in una singola query SQL con `EXISTS` per condizione e una CTE ricorsiva che ricostruisce i percorsi risalendo i `parent_id`. Le condizioni sugli attributi usano `EXISTS` su `OBJECT_ATTRIBUTE` con filtro su `namespace`, `key` e `value`. L'SQL vive nel servizio: non esiste un repository dedicato alla query. Il percorso è calcolato al momento della query e non è memorizzato: resta un dato derivato, non una seconda fonte di verità.

Indici necessari: `PLACEMENT(parent_id)` per la ricostruzione dei percorsi, `TAGGING(placement_id)` per il filtro sulle assegnazioni, `OBJECT_ATTRIBUTE(namespace, key, value)` per il filtro sugli attributi, `OBJECT_ATTRIBUTE(object_id)` per la lista attributi di un oggetto.

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
│   ├── Tagging (collega Object ↔ Placement)
│   ├── AttributeNamespace (template di attributi)
│   ├── AttributeDefinition (definisce tipo e valori di un attributo)
│   └── ObjectAttribute (valore di un attributo su un Object)
│
├── Application Layer (servizi applicativi)
│   ├── extends LocalFileObjectService (override register - rename - remove, update_path, mark_unavailable, mark_available)
│   ├── abstract ObjectService (register, rename, remove)
│   ├── TaggingService (assign, transfer, remove)
│   ├── PlacementService (create_placement, move, delete)
│   ├── TagService (create, rename, delete)
│   ├── PreviewService (anteprima impatto, R36)
│   ├── TagPlacementTreeService (get_tree)
│   ├── AttributeNamespaceService (create, list, delete namespace)
│   ├── AttributeDefinitionService (create, list, delete definizioni)
│   ├── ObjectAttributeService (set, unset, show, deduzione tipo)
│   ├── QueryService (search, ricerca esplicita R41-R48)
│   └── QueryParser (grammatica tag:, attributi, AND, OR, NOT)
│
├── Infrastructure Layer (servizi tecnici)
│   ├── TransactionManager (garante R1-R65, valida cicli R30-R33)
│   ├── LocalFileAvailableCheck (controlla disponibilità file all'avvio)
│   ├── ObjectRepository
│   ├── LocalFileObjectRepository
│   ├── TagRepository
│   ├── PlacementRepository
│   ├── TaggingRepository
│   ├── AttributeNamespaceRepository
│   ├── AttributeDefinitionRepository
│   ├── ObjectAttributeRepository
│   ├── schema.sql (DDL, indici, trigger)
│   ├── migrator (applica lo schema)
│   ├── seed (crea il Tag nativo Untagged e il suo Placement radice)
│   └── Database (esterno)
```