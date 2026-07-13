import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

// Layout components
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'

// Pages
import Dashboard from './pages/Dashboard'
import RepositoryView from './pages/RepositoryView'
import Timeline3D from './pages/Timeline3D'
import NotFound from './pages/NotFound'

// Page transition variants
const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
}

function App() {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Sidebar />
      <div className="lg:pl-64">
        <Header />
        <main className="p-6">
          <AnimatePresence mode="wait">
            <Routes>
              <Route 
                path="/" 
                element={
                  <motion.div
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    variants={pageVariants}
                    transition={{ duration: 0.2 }}
                  >
                    <Dashboard />
                  </motion.div>
                } 
              />
              <Route 
                path="/repo/:repoId" 
                element={
                  <motion.div
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    variants={pageVariants}
                    transition={{ duration: 0.2 }}
                  >
                    <RepositoryView />
                  </motion.div>
                } 
              />
              <Route 
                path="/repo/:repoId/timeline" 
                element={
                  <motion.div
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    variants={pageVariants}
                    transition={{ duration: 0.2 }}
                  >
                    <Timeline3D />
                  </motion.div>
                } 
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}

export default App
