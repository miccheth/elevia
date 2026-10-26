# Dai tuoi file a Elevia con un LLM

Parti dalla cartella dove conservi i tuoi documenti, anche se contiene sottocartelle. L’LLM userà nomi e percorsi per proporti un’organizzazione in Elevia e generare i comandi necessari.

I file originali resteranno dove sono. L’importazione registra in Elevia il loro percorso e li associa ai contesti scelti.

## 1. Estrai l’elenco dei file

Su macOS o Linux, apri il terminale ed esegui, sostituendo il percorso della cartella:

```bash
find "/percorso/completo/della/cartella" -type f \
  ! -name '.DS_Store' \
  > "$HOME/Desktop/file-da-importare.txt"
```

Otterrai sul Desktop un file con un percorso completo per riga:

```text
/Users/mario/Documenti/Lavoro/Azienda/Busta paga gennaio.pdf
/Users/mario/Documenti/Salute/Certificato sportivo.pdf
/Users/mario/Documenti/Note/Intelligenza artificiale.md
```

Scegli una cartella dedicata ai documenti da organizzare, non l’intero disco.

## 2. Prepara la conversazione con l’LLM

Allega:

- `file-da-importare.txt`, generato nel passaggio precedente;
- [CLI_COMMANDS.md](CLI_COMMANDS.md), con i comandi di Elevia.

Se hai già una struttura in Elevia, allega anche l’output di:

```bash
elevia tag list
elevia placement list
```

Nomi e percorsi possono contenere informazioni personali. Prima di inviarli a un servizio LLM esterno, controlla cosa stai condividendo.

## 3. Incolla questo prompt

```text
Voglio organizzare i miei file in Elevia. Analizza gli allegati
e prepara un unico script Bash con i comandi per creare la
struttura e importare i file. Non eseguire comandi.

ALLEGATI
- Elenco dei file con percorsi completi.
- CLI_COMMANDS.md: unica fonte per la sintassi dei comandi.
- Eventuali elenchi dei tag e placement già presenti in Elevia.

COME FUNZIONA ELEVIA
- Un Object rappresenta una risorsa. Per i file locali conserva
  il riferimento al percorso originale.
- Un Tag rappresenta un concetto con nome univoco.
- Un Placement colloca un Tag in un contesto: ha un solo padre
  oppure è una radice.
- Lo stesso Tag può comparire in placement diversi.
  Esempio: Salute.Certificati medici e Sport.Certificati medici.
- Un oggetto può essere assegnato a più placement senza
  duplicare il file.
- I figli di un placement non vengono condivisi automaticamente
  con altri placement dello stesso Tag.
- Non sono ammessi cicli, neppure tra Tag attraverso placement
  diversi.
- Importare non significa copiare o spostare il file originale.

COME PROGETTARE LA STRUTTURA
1. Usa nomi e cartelle attuali come indizi, senza ricopiare
   automaticamente la struttura del filesystem.
2. Organizza per argomento e contesto, con pochi rami principali.
3. Crea sottorami soltanto quando aiutano concretamente
   a ritrovare i documenti.
4. Non creare automaticamente tag per ogni file, anno,
   estensione o cartella di origine.
5. Riutilizza tag e placement esistenti quando adatti.
6. Usa assegnazioni multiple quando il documento è utile
   in contesti diversi.
7. Non dedurre con certezza il contenuto dai nomi.
   Lascia fuori dallo script i file ambigui e chiedi chiarimenti.
8. Non considerare duplicati due file soltanto perché hanno
   nomi simili o uguali.
9. Non aprire i file: lavora soltanto sull’elenco fornito.

OUTPUT RICHIESTO
A. Albero dei placement proposti.
B. Tabella completa: percorso originale → placement assegnati.
C. File da chiarire ed esclusioni motivate.
D. Conteggi: file ricevuti, inclusi nello script, da chiarire
   ed esclusi. I conteggi devono tornare.
E. Un unico script Bash pronto da salvare ed eseguire,
   contenente prima la creazione della struttura e poi
   l’importazione dei file.
F. Alcune query di esempio basate sui contesti creati.

REGOLE DELLO SCRIPT
- Usa soltanto comandi documentati in CLI_COMMANDS.md.
- Crea i placement genitori prima dei figli: --create-tags
  crea i tag mancanti, non i placement intermedi.
- Non ricreare placement già presenti negli elenchi allegati.
- Importa ogni percorso incluso una sola volta, con tutte
  le assegnazioni necessarie tramite più opzioni --in.
- Ogni file importato deve avere almeno un placement.
- Conserva esattamente i percorsi originali e applica quoting
  sicuro per Bash, anche con spazi, apostrofi e caratteri speciali.
- Usa `set -euo pipefail` per fermarti in caso di errore.
- Non usare reset, cancellazioni, spostamenti o rinomine.
- Termina con `elevia tree` per mostrare la struttura risultante.
- Avvisa che lo script non è necessariamente rieseguibile:
  dopo un errore bisogna controllare cosa è già stato creato
  o importato prima di riprendere.

Se mancano informazioni indispensabili, chiedile prima
di generare lo script. Non dichiarare completa la copertura
se l’elenco allegato è troncato o non interamente leggibile.
```

## 4. Controlla ed esegui

Prima di eseguire lo script, controlla soprattutto la tabella **file → placement**: l’albero può apparire ordinato anche con assegnazioni sbagliate o documenti esclusi.

Salva lo script approvato come `importa-elevia.sh`, quindi eseguilo dalla cartella del progetto Elevia, con la CLI disponibile:

```bash
bash importa-elevia.sh
```

Lo script crea la struttura e registra i file. Se si interrompe, **non rilanciarlo subito dall’inizio**: alcune operazioni potrebbero essere già riuscite.
