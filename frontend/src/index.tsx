/*
* This file initializes and renders the main React application and it is the entry point of the frontend application.
* It is responsible for rendering the root component of the application.
* This code is useful for setting up and running an entire React application, including state management, routing, and icon initialization.
*/

import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter, Route, Routes } from 'react-router-dom'
import { initializeIcons } from '@fluentui/react'

import Chat from './pages/chat/Chat'
import Layout from './pages/layout/Layout'
import NoPage from './pages/NoPage'
import { AppStateProvider } from './state/AppProvider'

//Import global styles from index.css.
import './index.css'

//Initialize Fluent UI icons.
initializeIcons()

//Render the main React application. 
//Defines the main application component that wraps the application in AppStateProvider and HashRouter and sets routes using Routes and Route.
export default function App() {
  return (
    <AppStateProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Chat />} />
            <Route path="*" element={<NoPage />} />
          </Route>
        </Routes>
      </HashRouter>
    </AppStateProvider>
  )
}

//Render the main React application.
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
