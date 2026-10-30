# Comandi Elevia

## Tag

```bash
elevia tag list
elevia tag create "Ferrari"
elevia tag create "Ferrari" --description "Auto e modellini"
elevia tag rename TAG "Ferrari Auto"
elevia tag delete TAG
elevia tag delete TAG --yes
```

## Placement

```bash
elevia placement list
elevia placement add "Lavoro"
elevia placement add "Lavoro.Ferrari"
elevia placement add "Lavoro.Ferrari.Contratti" --create-tags
elevia placement add Ferrari --parent "Lavoro"
elevia placement move "Lavoro.Ferrari" --parent "Passioni"
elevia placement move "Lavoro.Ferrari" --parent "Passioni" --yes
elevia placement delete "Lavoro.Ferrari"
elevia placement delete "Lavoro.Ferrari" --yes
```

## Object

```bash
elevia object list
elevia object show OBJECT_ID
elevia object add "Nome oggetto"
elevia object add "Nome oggetto" --in "Lavoro.Ferrari"
elevia object import ./documento.pdf
elevia object import ./documento.pdf --name "Documento"
elevia object import ./documento.pdf --name "Documento" --in "Lavoro.Ferrari"
elevia object import ./documento.pdf --name "Documento" --in "Lavoro" --in "Passioni"
elevia object rename OBJECT_ID "Nuovo nome"
elevia object delete OBJECT_ID
elevia object delete OBJECT_ID --yes
elevia object assign OBJECT_ID "Lavoro.Ferrari"
elevia object transfer OBJECT_ID "Lavoro.Ferrari" "Passioni.Ferrari"
elevia object unassign OBJECT_ID "Lavoro.Ferrari"
```

## File locali

```bash
elevia object file list
elevia object file unavailable OBJECT_ID
elevia object file relink OBJECT_ID ./nuovo/percorso.pdf
elevia object file relink OBJECT_ID ./nuovo/percorso.pdf --yes
```

## Albero

```bash
elevia tree
```

`Untagged` è un Tag di sistema: ammette solo il proprio Placement radice e non
può essere usato per creare un nuovo Placement, per esempio `Elevia.Untagged`.

## Attributi

### Namespace (template di attributi)

```bash
elevia attr namespace list
elevia attr namespace add "photo" --description "Attributi per foto"
elevia attr namespace add "work"
elevia attr namespace delete "photo"
elevia attr namespace delete "photo" --yes
```

### Definizioni di attributi

```bash
elevia attr def list "photo"
elevia attr def add "photo" "year" --type NUMBER
elevia attr def add "photo" "camera" --type TEXT
elevia attr def add "photo" "date" --type DATE
elevia attr def add "work" "remote" --type BOOLEAN
elevia attr def add "work" "status" --type ENUM --values "draft,in_review,approved,archived"
elevia attr def add "photo" "year" --type ENUM --values "2020,2021,2022,2023,2024,2025"
elevia attr def delete "photo" "year"
elevia attr def delete "photo" "year" --yes
```

### Valori sugli oggetti

```bash
# Con namespace (la definizione deve esistere)
elevia attr set set OBJECT_ID "photo.year" 2025
elevia attr set set OBJECT_ID "work.status" "approved"
elevia attr set set OBJECT_ID "work.deadline" "2025-12-31"
elevia attr set set OBJECT_ID "work.remote" true

# Senza namespace (attributo libero, tipo dedotto automaticamente)
elevia attr set set OBJECT_ID "colore" "rosso"
elevia attr set set OBJECT_ID "prezzo" 1500.50
elevia attr set set OBJECT_ID "data_evento" "2025-06-15"
elevia attr set set OBJECT_ID "is_premium" true

# Rimozione
elevia attr set unset OBJECT_ID "photo.year"
elevia attr set unset OBJECT_ID "colore"

# Visualizzazione
elevia attr set show OBJECT_ID
```

## Query

Metti sempre l'espressione tra apici. La shell interpreta `>` e `<` come
redirezioni: `elevia query prezzo > 100` crea un file `100` e non esegue il
confronto. Usa `elevia query 'prezzo > 100'`.

### Condizioni sui Tag

```bash
elevia query 'tag:Ferrari'
elevia query 'tag:*'
elevia query 'tag:Lavoro.Ferrari.Contratti'
elevia query 'tag:"Scontrini Coop"'
elevia query '(tag:Ferrari) AND (tag:Fotografie)'
elevia query '(tag:Ferrari) OR (tag:Passioni)'
elevia query 'NOT (tag:Fotografie)'
elevia query '(tag:Ferrari) AND NOT (tag:Fotografie)'
elevia query '((tag:Ferrari) OR (tag:Passioni)) AND (tag:Contratti)'
```

### Condizioni sugli attributi

```bash
# Uguaglianza
elevia query 'photo.year = 2025'
elevia query 'work.status = "approved"'
elevia query 'colore = "rosso"'
elevia query 'is_premium = true'

# Confronto numerico
elevia query 'finance.amount >= 1000'
elevia query 'prezzo > 500'

# Confronto date
elevia query 'work.deadline < "2025-12-31"'
elevia query 'data_evento >= "2025-01-01"'

# Combinato con tag
elevia query '(tag:Ferrari) AND (photo.year = 2025)'
elevia query '(tag:Contratti) AND (work.status = "approved")'
elevia query '(photo.year >= 2020) AND (photo.year <= 2025)'
elevia query '(tag:Ferrari) AND NOT (work.status = "archived")'
```

## Reset

```bash
elevia reset
elevia reset --yes
```

