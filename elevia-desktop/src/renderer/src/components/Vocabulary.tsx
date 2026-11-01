import { useEffect, useState } from 'react'
import type { VocabularyItem, VocabularyRequest } from '../../../preload/vocabulary'

type Node = VocabularyItem & { children: Node[] }
type Editor =
  | { action: 'create'; parentId: number | null; label: string }
  | { action: 'rename'; item: VocabularyItem }

function treeFrom(items: VocabularyItem[]): Node[] {
  const nodes = new Map(items.map((item) => [item.id, { ...item, children: [] as Node[] }]))
  const roots: Node[] = []
  for (const node of nodes.values()) {
    if (node.parentId === null) roots.push(node)
    else nodes.get(node.parentId)?.children.push(node)
  }
  return roots
}

function filterTree(nodes: Node[], filter: string): Node[] {
  return nodes.flatMap((node) => {
    if (node.name.toLocaleLowerCase().startsWith(filter)) return [node]
    const children = filterTree(node.children, filter)
    return children.length ? [{ ...node, children }] : []
  })
}

function highlighted(name: string, filter: string): React.ReactNode {
  if (!filter || !name.toLocaleLowerCase().startsWith(filter)) return name
  return (
    <>
      <mark>{name.slice(0, filter.length)}</mark>
      {name.slice(filter.length)}
    </>
  )
}

export function Vocabulary({
  selected,
  onSelect
}: {
  selected: string
  onSelect: (value: string) => void
}): React.JSX.Element {
  const [items, setItems] = useState<VocabularyItem[]>([])
  const [filter, setFilter] = useState('')
  const [menu, setMenu] = useState<number | null>(null)
  const [editor, setEditor] = useState<Editor | null>(null)
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [loaded, setLoaded] = useState(false)

  async function run(request: VocabularyRequest): Promise<boolean> {
    setBusy(true)
    setError('')
    try {
      const result = await window.api.vocabulary(request)
      if (result.error || !result.items) {
        setError(result.error || 'Impossibile caricare i tag.')
        return false
      }
      setItems(result.items)
      return true
    } catch {
      setError('Impossibile comunicare con il core.')
      return false
    } finally {
      setBusy(false)
      setLoaded(true)
    }
  }

  useEffect(() => {
    let cancelled = false
    window.api
      .vocabulary({ action: 'list' })
      .then((result) => {
        if (cancelled) return
        if (result.error || !result.items) setError(result.error || 'Impossibile caricare i tag.')
        else setItems(result.items)
        setLoaded(true)
      })
      .catch(() => {
        if (!cancelled) {
          setError('Impossibile comunicare con il core.')
          setLoaded(true)
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  function edit(next: Editor): void {
    setMenu(null)
    setName(next.action === 'rename' ? next.item.name : '')
    setEditor(next)
  }

  async function submit(event: React.FormEvent): Promise<void> {
    event.preventDefault()
    if (!editor || !name.trim()) return
    const request: VocabularyRequest =
      editor.action === 'create'
        ? { action: 'create', name: name.trim(), parentId: editor.parentId }
        : { action: 'rename', tagId: editor.item.tagId, name: name.trim() }
    if (await run(request)) {
      setEditor(null)
      setFilter('')
    }
  }

  function renderNode(node: Node): React.ReactNode {
    return (
      <li key={node.id}>
        <details className="tag-tree__group" open key={`${node.id}-${filter}`}>
          <summary
            className={`tag-tree__parent${selected === `tag:${node.id}` ? ' tag-tree__child--selected' : ''}`}
            onClick={() => onSelect(`tag:${node.id}`)}
            onContextMenu={(event) => {
              event.preventDefault()
              setMenu(node.id)
            }}
          >
            <svg className="tag-tree__chevron" viewBox="0 0 24 24" aria-hidden="true">
              <path d="m9 6 6 6-6 6" />
            </svg>
            <svg className="tag-tree__parent-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 4h7l9 9-7 7-9-9V4Z" />
              <circle cx="8" cy="8" r="1" />
            </svg>
            <span className="tag-tree__name">{highlighted(node.name, filter)}</span>
            <button
              className="tag-tree__menu-button"
              type="button"
              aria-label={`Azioni per ${node.name}`}
              onClick={(event) => {
                event.preventDefault()
                event.stopPropagation()
                setMenu(menu === node.id ? null : node.id)
              }}
            >
              ⋯
            </button>
          </summary>
          {menu === node.id && (
            <div className="tag-tree__menu">
              <button
                type="button"
                onClick={() => edit({ action: 'create', parentId: node.id, label: node.name })}
              >
                Aggiungi tag figlio
              </button>
              <button type="button" onClick={() => edit({ action: 'rename', item: node })}>
                Rinomina tag
              </button>
              <button
                type="button"
                onClick={() => {
                  setMenu(null)
                  if (
                    window.confirm(
                      `Rimuovere “${node.name}” da questa posizione? Il tag resterà nel vocabolario.`
                    )
                  ) {
                    void run({ action: 'delete', placementId: node.id })
                  }
                }}
              >
                Rimuovi posizione
              </button>
            </div>
          )}
          {node.children.length > 0 && (
            <ul className="tag-tree__children">{node.children.map(renderNode)}</ul>
          )}
        </details>
      </li>
    )
  }

  const normalizedFilter = filter.trim().toLocaleLowerCase()
  const visible = filterTree(treeFrom(items), normalizedFilter)
  return (
    <>
      <section className="sidebar__tags" aria-label="Vocabolario">
        <div className="sidebar__separator" />
        <div className="vocabulary__header">
          <span>Tag</span>
          <button
            type="button"
            className="icon-button"
            aria-label="Crea tag principale"
            title="Crea tag principale"
            onClick={() => edit({ action: 'create', parentId: null, label: '' })}
          >
            +
          </button>
        </div>
        {editor && (
          <form
            className="vocabulary__editor"
            onSubmit={(event) => {
              void submit(event)
            }}
          >
            <label htmlFor="vocabulary-name">
              {editor.action === 'rename'
                ? 'Rinomina tag'
                : editor.parentId === null
                  ? 'Nuovo tag'
                  : `Nuovo tag in ${editor.label}`}
            </label>
            {editor.action === 'rename' && <small>Il nome cambia in tutte le posizioni.</small>}
            <input
              id="vocabulary-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              autoFocus
            />
            <div>
              <button type="submit" disabled={busy || !name.trim()}>
                Salva
              </button>
              <button type="button" onClick={() => setEditor(null)}>
                Annulla
              </button>
            </div>
          </form>
        )}
        {error && (
          <p className="vocabulary__error" role="alert">
            {error}
          </p>
        )}
        <ul className="tag-tree">{visible.map(renderNode)}</ul>
        {loaded && !error && visible.length === 0 && (
          <p className="tag-tree__empty">
            {normalizedFilter ? 'Nessun tag trovato' : 'Nessun tag. Crea il primo con +.'}
          </p>
        )}
      </section>
      <label className="sidebar__filter">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M3 5h18l-7 8v6l-4 2v-8z" />
        </svg>
        <input
          type="search"
          placeholder="Filter"
          aria-label="Filtra tag"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
        />
      </label>
    </>
  )
}
