import { useState } from 'react'
import { Vocabulary } from './components/Vocabulary'

function App(): React.JSX.Element {
  const [selected, setSelected] = useState<string>('all')
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const isMac = window.electron.process.platform === 'darwin'

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
        <Vocabulary selected={selected} onSelect={setSelected} />
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
