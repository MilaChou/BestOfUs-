/**
 * Who is signed in, and their couple — shared by every screen.
 *
 * On start the saved token is read; then the user and the couple are loaded.
 * Screens call refresh() after changing something that affects them
 * (e.g. creating or joining a couple).
 */
import { createContext, type ReactNode, useCallback, useContext, useEffect, useState } from 'react';

import { api, ApiError, errorMessage, setAuthToken, setOnUnauthorized } from '@/lib/api';
import { deleteToken, loadToken, saveToken } from '@/lib/storage';
import type { Couple, User } from '@/lib/types';

type AuthState = {
  ready: boolean; // false while the saved token is being checked on start
  startError: string | null; // e.g. the server was unreachable on start
  onboarding: boolean; // true right after registration, until the "about you" step is done
  finishOnboarding: () => void;
  user: User | null;
  couple: Couple | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
  retryStart: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

async function loadCouple(): Promise<Couple | null> {
  try {
    return await api<Couple>('/couple');
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null; // not in a couple yet
    throw error;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [couple, setCouple] = useState<Couple | null>(null);
  const [startError, setStartError] = useState<string | null>(null);
  const [onboarding, setOnboarding] = useState(false);

  const signOut = useCallback(async () => {
    setOnboarding(false);
    setAuthToken(null);
    await deleteToken();
    setUser(null);
    setCouple(null);
  }, []);

  const refresh = useCallback(async () => {
    const [me, myCouple] = await Promise.all([api<User>('/users/me'), loadCouple()]);
    setUser(me);
    setCouple(myCouple);
  }, []);

  const startSession = useCallback(
    async (token: string) => {
      setAuthToken(token);
      await saveToken(token);
      await refresh();
    },
    [refresh],
  );

  const signIn = useCallback(
    async (email: string, password: string) => {
      // OAuth2 login is a form, and the email goes in the "username" field.
      const { access_token } = await api<{ access_token: string }>('/auth/login', {
        method: 'POST',
        form: { username: email.trim(), password },
      });
      await startSession(access_token);
    },
    [startSession],
  );

  const signUp = useCallback(
    async (email: string, password: string, name: string) => {
      await api('/auth/register', {
        method: 'POST',
        json: { email: email.trim(), password, name: name.trim() },
      });
      setOnboarding(true);
      await signIn(email, password);
    },
    [signIn],
  );

  // Load the user for the saved token. Only a rejected token logs you out;
  // if the server is just not reachable, the token is kept and we offer a retry.
  const restore = useCallback(async () => {
    const token = await loadToken();
    if (!token) return;
    setAuthToken(token);
    try {
      await refresh();
      setStartError(null);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) await signOut();
      else setStartError(errorMessage(error));
    }
  }, [refresh, signOut]);

  const retryStart = useCallback(async () => {
    setReady(false);
    await restore();
    setReady(true);
  }, [restore]);

  useEffect(() => {
    setOnUnauthorized(() => void signOut());
    let cancelled = false;
    (async () => {
      await restore();
      if (!cancelled) setReady(true);
    })();
    return () => {
      cancelled = true;
      setOnUnauthorized(null);
    };
  }, [restore, signOut]);

  return (
    <AuthContext.Provider
      value={{
        ready,
        startError,
        onboarding,
        finishOnboarding: () => setOnboarding(false),
        user,
        couple,
        signIn,
        signUp,
        signOut,
        refresh,
        retryStart,
      }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>');
  return value;
}

/** The other member of the couple, if they have joined. */
export function usePartner() {
  const { user, couple } = useAuth();
  return couple?.members.find((m) => m.id !== user?.id) ?? null;
}
