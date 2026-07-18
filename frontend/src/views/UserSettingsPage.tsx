import React, { useEffect, useMemo, useState } from 'react';
import { apiUrl } from '@/api/client';
import { useAuth } from '@/context/AuthContext';

interface UserSettings {
  id: number;
  username: string;
  email: string;
  max_subtask_depth_user: number | null;
}

interface SettingsForm {
  email: string;
  maxDepth: number | '';
  currentPassword: string;
  newPassword: string;
  confirmNewPassword: string;
}

const UserSettingsPage: React.FC = () => {
  const { token } = useAuth();

  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [form, setForm] = useState<SettingsForm>({
    email: '',
    maxDepth: '',
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const authHeaderObj = useMemo(
    () =>
      token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {},
    [token]
  );

  useEffect(() => {
    const fetchSettings = async () => {
      if (!token) {
        setSettings(null);
        setError('Utente non autenticato.');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      setSuccess(null);

      try {
        const res = await fetch(apiUrl('/users/me/settings'), {
          headers: authHeaderObj,
        });

        const raw = await res.text();
        const data = raw ? JSON.parse(raw) : null;

        if (!res.ok) {
          setSettings(null);
          setError(data?.detail || 'Errore nel caricamento delle impostazioni.');
          return;
        }

        const userSettings = data as UserSettings;
        setSettings(userSettings);
        setForm({
          email: userSettings.email ?? '',
          maxDepth:
            userSettings.max_subtask_depth_user !== null
              ? userSettings.max_subtask_depth_user
              : '',
          currentPassword: '',
          newPassword: '',
          confirmNewPassword: '',
        });
      } catch (err) {
        console.error('Exception in fetchSettings', err);
        setSettings(null);
        setError('Eccezione nel caricamento delle impostazioni.');
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [authHeaderObj, token]);

  const handleChange =
    (field: keyof SettingsForm) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;

      setError(null);
      setSuccess(null);

      setForm((prev) => ({
        ...prev,
        [field]:
          field === 'maxDepth'
            ? value === ''
              ? ''
              : Number(value)
            : value,
      }));
    };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!token) {
      setError('Utente non autenticato.');
      return;
    }

    if (!settings) {
      setError('Impostazioni non disponibili.');
      return;
    }

    const payload: Record<string, unknown> = {};

    const trimmedEmail = form.email.trim();
    if (trimmedEmail && trimmedEmail !== settings.email) {
      payload.email = trimmedEmail;
    }

    if (
      form.maxDepth !== '' &&
      form.maxDepth !== settings.max_subtask_depth_user
    ) {
      payload.max_subtask_depth_user = form.maxDepth;
    }

    const isChangingPassword =
      !!form.currentPassword || !!form.newPassword || !!form.confirmNewPassword;

    if (isChangingPassword) {
      payload.current_password = form.currentPassword;
      payload.new_password = form.newPassword;
      payload.confirm_new_password = form.confirmNewPassword;
    }

    if (Object.keys(payload).length === 0) {
      setSuccess('Nessuna modifica da salvare.');
      return;
    }

    setSaving(true);

    try {
      const res = await fetch(apiUrl('/users/me/settings'), {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaderObj,
        },
        body: JSON.stringify(payload),
      });

      const raw = await res.text();
      const data = raw ? JSON.parse(raw) : null;

      if (!res.ok) {
        setError(data?.detail || 'Errore nel salvataggio delle impostazioni.');
        return;
      }

      const updated = data as UserSettings;
      setSettings(updated);
      setForm({
        email: updated.email ?? '',
        maxDepth:
          updated.max_subtask_depth_user !== null
            ? updated.max_subtask_depth_user
            : '',
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
      });
      setSuccess('Impostazioni salvate con successo.');
    } catch (err) {
      console.error('Exception in handleSubmit', err);
      setError('Eccezione nel salvataggio delle impostazioni.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <h1>Impostazioni utente</h1>
        <p>Caricamento...</p>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    );
  }

  if (!settings) {
    return (
      <div style={{ padding: 24 }}>
        <h1>Impostazioni utente</h1>
        <p>Impossibile caricare le impostazioni.</p>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <h1>Impostazioni utente</h1>
      <p>
        Utente: <strong>{settings.username}</strong>
      </p>

      <form
        onSubmit={handleSubmit}
        style={{ display: 'grid', gap: 16, maxWidth: 500 }}
      >
        <div>
          <label
            htmlFor="email"
            style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            value={form.email}
            onChange={handleChange('email')}
            style={{ width: '100%' }}
            autoComplete="email"
          />
        </div>

        <div>
          <label
            htmlFor="maxDepth"
            style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}
          >
            Profondità massima sottotask (utente)
          </label>
          <input
            id="maxDepth"
            type="number"
            min={1}
            max={15}
            value={form.maxDepth}
            onChange={handleChange('maxDepth')}
            style={{ width: '100%' }}
          />
          <small>
            Il valore effettivo sarà il minimo tra questo e il limite globale
            impostato dall&apos;admin.
          </small>
        </div>

        <fieldset
          style={{
            border: '1px solid #ccc',
            padding: 12,
            borderRadius: 4,
          }}
        >
          <legend>Cambia password</legend>

          <div style={{ marginBottom: 8 }}>
            <label
              htmlFor="currentPassword"
              style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}
            >
              Password corrente
            </label>
            <input
              id="currentPassword"
              type="password"
              value={form.currentPassword}
              onChange={handleChange('currentPassword')}
              style={{ width: '100%' }}
              autoComplete="current-password"
            />
          </div>

          <div style={{ marginBottom: 8 }}>
            <label
              htmlFor="newPassword"
              style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}
            >
              Nuova password
            </label>
            <input
              id="newPassword"
              type="password"
              value={form.newPassword}
              onChange={handleChange('newPassword')}
              style={{ width: '100%' }}
              autoComplete="new-password"
            />
          </div>

          <div>
            <label
              htmlFor="confirmNewPassword"
              style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}
            >
              Conferma nuova password
            </label>
            <input
              id="confirmNewPassword"
              type="password"
              value={form.confirmNewPassword}
              onChange={handleChange('confirmNewPassword')}
              style={{ width: '100%' }}
              autoComplete="new-password"
            />
          </div>
        </fieldset>

        {error && <p style={{ color: 'red', margin: 0 }}>{error}</p>}
        {success && <p style={{ color: 'green', margin: 0 }}>{success}</p>}

        <button type="submit" disabled={saving}>
          {saving ? 'Salvataggio...' : 'Salva impostazioni'}
        </button>
      </form>
    </div>
  );
};

export default UserSettingsPage;