# Sintesi visiva

## Dalle definizioni ai risultati

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
Objects e assegnazioni                   ← almeno un placement per oggetto
│
├── Accordo professionale [obj-001]
│   └── P3: Lavoro → Ferrari → Contratti
│
├── Contratto di acquisto di un modellino [obj-002]
│   └── P6: Passioni → Ferrari → Contratti
│
└── Foto a Monza [obj-003]
    ├── P7: Passioni → Ferrari → Fotografie
    ├── Metadata: photo.year = 2026
    └── Risorsa originale: /Foto/monza.jpg ← il file non viene spostato
              │
              ▼
Ricerca deterministica                   ← include i discendenti selezionati
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
Facet                                    ← filtri sui Metadata
└── Ambito P5 + Anno: [x] 2026
    └── Condizione: photo.year = 2026
        └── Risultato: Foto a Monza [obj-003]
              │
              ▼
Smart Collection: Ferrari personale, anno 2026
├── Salva ambito P5 e condizione photo.year = 2026
└── Mostra gli oggetti corrispondenti, senza copiarli o spostarli
```

Il contesto completo distingue i due contratti: il solo padre immediato darebbe Ferrari → Contratti in entrambi i casi. I figli di un placement non vengono condivisi automaticamente con gli altri placement dello stesso Tag.

“Ovunque” considera tutte le collocazioni del Tag e i loro discendenti. “Solo questo ramo” non salta alle altre collocazioni dei Tag incontrati. Ogni oggetto compare una sola volta nei risultati; gli antenati non diventano automaticamente Tag direttamente assegnati.

## Operazioni e vincoli

```text
Assegnazioni degli oggetti
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

Il namespace `work` non è il Tag Lavoro: i metadati vengono assegnati esplicitamente e devono rispettare lo schema. Le Smart Collections usano riferimenti stabili; se un riferimento viene eliminato, la ricerca viene segnalata come non valida anziché ignorare il criterio.

## Questioni ancora aperte

```text
Da definire
├── Calcolo e presentazione dei suggerimenti basati sullo storico
├── Spostamento dei placement e gestione delle destinazioni già occupate
├── Risoluzione di figli e assegnazioni prima di eliminare un placement
├── Composizione delle query tra Tag, ambiti e metadati
└── Effetti delle riorganizzazioni sulle Smart Collections
```
