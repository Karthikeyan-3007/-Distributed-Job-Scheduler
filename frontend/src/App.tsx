import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import AppLayout from "./layouts/AppLayout";
import LoginPage from "./pages/Login";
import OverviewPage from "./pages/Overview";
import ProjectsPage from "./pages/Projects";
import QueuesPage from "./pages/Queues";
import JobsPage from "./pages/Jobs";
import WorkersPage from "./pages/Workers";
import DeadLetterQueuePage from "./pages/DeadLetterQueue";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex min-h-screen items-center justify-center text-slate-500">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<OverviewPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/queues" element={<QueuesPage />} />
        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/workers" element={<WorkersPage />} />
        <Route path="/dlq" element={<DeadLetterQueuePage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
