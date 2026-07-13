// src/router/AppRouter.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

// Pagine
import HomePage from '@/views/HomePage';
import DayPage from '@/views/DayPage';
import WeekPage from '@/views/WeekPage';
import TasksPage from '@/views/TasksPage';
import EventsPage from '@/views/EventsPage';
import CategoriesPage from '@/views/CategoriesPage';
import CategoryEditPage from '@/views/CategoryEditPage';
import UserSettingsPage from '@/views/UserSettingsPage';
import LoginScreen from '@/views/LoginScreen';
import ShoppingPage from '@/pages/ShoppingPage';

// Layout
import AppShellLayout from '@/components/AppShellLayout';

const AppRouter: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <BrowserRouter>
      {isAuthenticated ? (
        <Routes>
          <Route element={<AppShellLayout onLogout={logout} />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/giorno" element={<DayPage />} />
            <Route path="/settimana" element={<WeekPage />} />
            <Route
              path="/mese"
              element={
                <div className="p-6 text-xl font-bold">
                  Pagina Mese in costruzione...
                </div>
              }
            />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/categories/:id/edit" element={<CategoryEditPage />} />
            <Route path="/shopping" element={<ShoppingPage />} />
            <Route path="/settings" element={<UserSettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      ) : (
        <Routes>
          <Route path="/login" element={<LoginScreen />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </BrowserRouter>
  );
};

export default AppRouter;