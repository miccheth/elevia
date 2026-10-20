
## Un oggetto

```text
Object
│
├── id: obj-001                       ← identità stabile
├── name: Ferrari rossa
│
├── Risorsa originale                 ← resta nella sua posizione
│   ├── filename: ferrari.jpg
│   ├── path: /Foto/ferrari.jpg
│   ├── mime: image/jpeg
│   ├── size: 4 MB
│   ├── created: 2026-03-10
│   ├── modified: 2026-03-12
│   ├── hash: …
│   └── thumbnail: …
│
├── Disponibilità: disponibile
│
├── Tags                              ← almeno uno, riferimenti al Registry
│   ├── Ferrari [tag-003]
│   ├── Automobile [tag-004]
│   └── Rosso [tag-005]
│
└── Metadati                           ← proprietà raggruppate per namespace
    ├── work                          ← namespace
    │   ├── client: Ferrari
    │   └── project: Website 2026
    ├── review                        ← namespace
    │   └── rating: 5
    └── photo                         ← namespace
        └── year: 2026
```

## Tag: identità e gerarchia

```text
Tag Registry                         Tag Tree
│                                    │
├── tag-001: Clienti                  ├── Clienti [tag-001]
├── tag-002: Marchi                   │   └── Ferrari [tag-003]
├── tag-003: Ferrari                  │
├── tag-004: Automobile               ├── Marchi [tag-002]
└── tag-005: Rosso                    │   └── Ferrari [tag-003]
                                     │
                                     ├── Automobile [tag-004]
                                     └── Rosso [tag-005]
```

`Ferrari` compare sotto due genitori, ma è un solo Tag: entrambe le voci rimandano a `tag-003` e agli stessi oggetti. I rami non sono cartelle fisiche. I Tag superiori includono i contenuti dei discendenti; la gerarchia non ammette cicli.

## Dalle proprietà ai risultati

```text
Object
│
├── Tags: Ferrari, Automobile, Rosso
└── Metadati
    ├── work
    │   └── client: Ferrari
    ├── review
    │   └── rating: 5
    └── photo
        └── year: 2026
          │
          ▼
Facet                                ← valori selezionabili per filtrare
├── Cliente (work.client)
│   ├── [ ] Ferrari
│   └── [ ] Altri valori disponibili…
├── Rating (review.rating)
│   ├── [ ] 5
│   └── [ ] Altri valori disponibili…
└── Anno (photo.year)
    ├── [x] 2026
    └── [ ] Altri valori disponibili…
          │
          ▼
Ricerca deterministica               ← combina Tag e condizioni
└── tag:Ferrari AND photo.year = 2026
          │
          ├── Risultati: obj-001, …    ← ogni oggetto compare una sola volta
          │
          └── Smart Collection: Ferrari 2026
              └── salva i criteri e mostra gli oggetti corrispondenti
```

Metadati e facet possono mostrare gli stessi nomi e valori. Nei metadati leggi le proprietà di un singolo oggetto; nelle facet scegli tra i valori disponibili negli oggetti consultati per restringere i risultati. Selezionare `[x] 2026` applica il filtro `photo.year = 2026`, senza modificare i metadati.

La ricerca combina la facet dell'anno selezionata con il Tag `Ferrari`. Selezionare anche il cliente aggiungerebbe `work.client = Ferrari`: stesso nome del Tag, criterio diverso. Assegnare il Tag non implica assegnare anche il metadato, né viceversa.

La notazione delle condizioni è illustrativa. Le Smart Collections salvano ricerche, senza copiare o spostare gli oggetti o i file originali.
