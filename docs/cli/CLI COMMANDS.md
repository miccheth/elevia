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

## Query

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

## Reset

```bash
elevia reset
elevia reset --yes
```

