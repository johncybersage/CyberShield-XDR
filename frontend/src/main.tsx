import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#151a27',
            color: '#e2e8f0',
            border: '1px solid #1e3a5f',
          },
          success: { iconTheme: { primary: '#30d158', secondary: '#151a27' } },
          error:   { iconTheme: { primary: '#ff2d55', secondary: '#151a27' } },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)
