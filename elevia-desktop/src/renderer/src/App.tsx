import { useState } from 'react'

const exampleTags = [
  { name: 'Fotografia', children: ['Paesaggi', 'Ritratti', 'Architettura'] },
  { name: 'Progetti', children: ['Identità visiva', 'Interfacce', 'Illustrazioni'] },
  { name: 'Automobili', children: ['Ferrari', 'Modellini'] }
]

function highlightMatch(name: string, filter: string): React.ReactNode {
  if (!filter) return name

  const parts: React.ReactNode[] = []
  const lowerName = name.toLocaleLowerCase()
  let start = 0
  let match = lowerName.indexOf(filter)

  while (match !== -1) {
    parts.push(name.slice(start, match))
    parts.push(<mark key={match}>{name.slice(match, match + filter.length)}</mark>)
    start = match + filter.length
    match = lowerName.indexOf(filter, start)
  }

  parts.push(name.slice(start))
  return parts
}

function App(): React.JSX.Element {
  const [selected, setSelected] = useState<string>('all')
  const [tagFilter, setTagFilter] = useState('')
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const isMac = window.electron.process.platform === 'darwin'
  const filter = tagFilter.trim().toLocaleLowerCase()
  const visibleTags = exampleTags
    .map((group) => ({
      ...group,
      children: group.name.toLocaleLowerCase().includes(filter)
        ? group.children
        : group.children.filter((name) => name.toLocaleLowerCase().includes(filter))
    }))
    .filter((group) => group.name.toLocaleLowerCase().includes(filter) || group.children.length > 0)

  return (
    <div className="app">
      <aside className="sidebar" aria-label="Sidebar">
        <div className={`sidebar__toolbar${isMac ? ' sidebar__toolbar--mac' : ''}`}>
          <button
            className="icon-button"
            type="button"
            aria-label="Importa"
            title="Importa (non ancora disponibile)"
            disabled
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3v18M3 12h18" />
            </svg>
          </button>
        </div>

        <div className="sidebar__brand">Elevia</div>
        <nav className="sidebar__nav" aria-label="Risorse">
          <button
            className={`nav-item${selected === 'all' ? ' nav-item--selected' : ''}`}
            type="button"
            aria-pressed={selected === 'all'}
            onClick={() => setSelected('all')}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <rect x="3" y="3" width="18" height="18" rx="3" />
              <path d="M3 14h5l2 3h4l2-3h5" />
            </svg>
            <span>All</span>
          </button>
          <button
            className={`nav-item${selected === 'untagged' ? ' nav-item--selected' : ''}`}
            type="button"
            aria-pressed={selected === 'untagged'}
            onClick={() => setSelected('untagged')}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v6M5 21l7-4 3 1.7M18 15a2 2 0 1 1 2 2c-1 0-1 1-1 1M19 21h.01" />
            </svg>
            <span>Untagged</span>
          </button>
        </nav>
        <section className="sidebar__tags" aria-label="Tags Tree">
          <div className="sidebar__separator" />
          <div className="tag-tree">
            {visibleTags.map((group) => (
              <details className="tag-tree__group" key={`${group.name}/${filter}`} open>
                <summary className="tag-tree__parent">
                  <svg className="tag-tree__chevron" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="m9 6 6 6-6 6" />
                  </svg>
                  <svg className="tag-tree__parent-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M12 3 20 7.5v9L12 21l-8-4.5v-9L12 3Z" />
                    <path d="m4 7.5 8 4.5 8-4.5M12 12v9" />
                  </svg>
                  <span>{highlightMatch(group.name, filter)}</span>
                </summary>
                <ul className="tag-tree__children">
                  {group.children.map((name) => (
                    <li key={name}>
                      <button
                        className={`tag-tree__child${selected === `${group.name}/${name}` ? ' tag-tree__child--selected' : ''}`}
                        type="button"
                        aria-pressed={selected === `${group.name}/${name}`}
                        onClick={() => setSelected(`${group.name}/${name}`)}
                      >
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                          <path d="M4 4h7l9 9-7 7-9-9V4Z" />
                          <circle cx="8" cy="8" r="1" />
                        </svg>
                        <span>{highlightMatch(name, filter)}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </details>
            ))}
            {visibleTags.length === 0 && (
              <p className="tag-tree__empty" role="status">
                Nessun tag trovato
              </p>
            )}
          </div>
        </section>
        <label className="sidebar__filter">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M3 5h18l-7 8v6l-4 2v-8z" />
          </svg>
          <input
            type="search"
            placeholder="Filter"
            aria-label="Filtra tag"
            value={tagFilter}
            onChange={(event) => setTagFilter(event.target.value)}
          />
        </label>
      </aside>
      <main className="workspace">
        <form
          className="workspace__toolbar"
          role="search"
          onSubmit={(event) => event.preventDefault()}
        >
          <div className="workspace__search">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="10.5" cy="10.5" r="6.5" />
              <path d="m16 16 4 4" />
            </svg>
            <input type="search" placeholder="Search" aria-label="Cerca nella libreria" />
          </div>
          <button className="workspace__reset" type="reset">
            Reset
          </button>
        </form>
        <div className="workspace__view-bar" role="group" aria-label="Visualizzazione elementi">
          <button
            className="workspace__view-button"
            type="button"
            aria-label="Visualizzazione a griglia"
            aria-pressed={view === 'grid'}
            title="Griglia"
            onClick={() => setView('grid')}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <rect x="4" y="4" width="6" height="6" rx="1" />
              <rect x="14" y="4" width="6" height="6" rx="1" />
              <rect x="4" y="14" width="6" height="6" rx="1" />
              <rect x="14" y="14" width="6" height="6" rx="1" />
            </svg>
          </button>
          <button
            className="workspace__view-button"
            type="button"
            aria-label="Visualizzazione a lista"
            aria-pressed={view === 'list'}
            title="Lista"
            onClick={() => setView('list')}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01" />
            </svg>
          </button>
        </div>
        <div className="gallery-empty">
          <svg className="gallery-empty__illustration" viewBox="0 0 180 132" aria-hidden="true">
            <rect className="gallery-empty__back" x="22" y="35" width="76" height="70" rx="10" />
            <rect className="gallery-empty__back" x="82" y="29" width="76" height="70" rx="10" />
            <rect className="gallery-empty__front" x="52" y="18" width="76" height="86" rx="10" />
            <path className="gallery-empty__lines" d="M70 45h40M70 57h40M70 69h27" />
            <circle className="gallery-empty__accent" cx="131" cy="97" r="17" />
            <path className="gallery-empty__plus" d="M131 89v16m-8-8h16" />
          </svg>
          <h1>Nessun elemento</h1>
          <p>Gli elementi aggiunti appariranno qui.</p>
        </div>
      </main>
      <aside className="inspector" aria-label="Inspector">
        <header className="inspector__header" />
        <div className="inspector__content">
          <p>Nessun elemento selezionato</p>
        </div>
      </aside>
    </div>
  )
}

export default App
