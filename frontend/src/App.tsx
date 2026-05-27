import { useState, useEffect } from 'react'

import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { getHealth } from './api/client'

function App() {
  const [count, setCount] = useState(0)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')

  useEffect(() => {
    getHealth()
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('disconnected'))
  }, [])

  const statusText = {
    checking: '⏳ Checking backend...',
    connected: '✅ Backend connected',
    disconnected: '❌ Backend disconnected',
  }[backendStatus]

  const statusColor = {
    checking: '#888',
    connected: '#4caf50',
    disconnected: '#f44336',
  }[backendStatus]

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <p style={{ color: statusColor, fontWeight: 'bold', marginTop: '1rem' }}>
        {statusText}
      </p>
    </>
  )
}

export default App
