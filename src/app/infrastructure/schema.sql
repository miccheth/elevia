-- Schema database Elevia
-- Tabelle: OBJECT, LOCAL_FILE_OBJECT, TAG, PLACEMENT, TAGGING
-- Richiede PRAGMA foreign_keys = ON a ogni connessione.

CREATE TABLE IF NOT EXISTS object (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    object_type TEXT    NOT NULL CHECK (object_type IN ('LOCAL_FILE', 'GENERIC_OBJECT')),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS local_file_object (
    object_id       INTEGER PRIMARY KEY,
    is_available    INTEGER NOT NULL CHECK (is_available IN (0, 1)),
    file_path       TEXT    NOT NULL,
    normalized_path TEXT    NOT NULL,
    file_size       INTEGER NOT NULL,
    modified_at     TEXT    NOT NULL,
    file_extension  TEXT    NOT NULL,
    FOREIGN KEY (object_id) REFERENCES object (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tag (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL COLLATE NOCASE UNIQUE,
    description TEXT,
    is_system   INTEGER NOT NULL DEFAULT 0 CHECK (is_system IN (0, 1)),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS placement (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id     INTEGER NOT NULL,
    parent_id  INTEGER,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_id) REFERENCES tag (id) ON DELETE RESTRICT,
    FOREIGN KEY (parent_id) REFERENCES placement (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS tagging (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id    INTEGER NOT NULL,
    placement_id INTEGER NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (object_id) REFERENCES object (id) ON DELETE CASCADE,
    FOREIGN KEY (placement_id) REFERENCES placement (id) ON DELETE RESTRICT,
    UNIQUE (object_id, placement_id)
);

-- Stesso Tag max 1 Placement per padre
CREATE UNIQUE INDEX IF NOT EXISTS ux_placement_tag_parent
    ON placement (tag_id, parent_id)
    WHERE parent_id IS NOT NULL;

-- Max 1 Placement radice per Tag
CREATE UNIQUE INDEX IF NOT EXISTS ux_placement_tag_root
    ON placement (tag_id)
    WHERE parent_id IS NULL;

-- Ricostruzione dei percorsi (QueryService)
CREATE INDEX IF NOT EXISTS ix_placement_parent
    ON placement (parent_id);

-- Filtro sulle assegnazioni (QueryService)
CREATE INDEX IF NOT EXISTS ix_tagging_placement
    ON tagging (placement_id);

-- Trigger: un Tag di sistema non si rinomina e non si elimina
CREATE TRIGGER IF NOT EXISTS trg_tag_system_no_rename
BEFORE UPDATE OF name ON tag
FOR EACH ROW
WHEN OLD.is_system = 1 AND NEW.name <> OLD.name
BEGIN
    SELECT RAISE(ABORT, 'Un Tag di sistema non può essere rinominato');
END;

CREATE TRIGGER IF NOT EXISTS trg_tag_system_no_delete
BEFORE DELETE ON tag
FOR EACH ROW
WHEN OLD.is_system = 1
BEGIN
    SELECT RAISE(ABORT, 'Un Tag di sistema non può essere eliminato');
END;

-- Trigger: updated_at aggiornato a ogni modifica
CREATE TRIGGER IF NOT EXISTS trg_object_updated_at
AFTER UPDATE ON object
FOR EACH ROW
BEGIN
    UPDATE object SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_tag_updated_at
AFTER UPDATE ON tag
FOR EACH ROW
BEGIN
    UPDATE tag SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
