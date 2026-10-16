import { createClient } from "@supabase/supabase-js";

const envUrl = import.meta.env.VITE_SUPABASE_URL;
const envKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

// Consider configured only if valid non-expired custom endpoint is provided
export const isSupabaseConfigured = Boolean(
  envUrl &&
  envKey &&
  !envUrl.includes("ahfzfeecrivvvmpnhzui")
);

const LOCAL_STORAGE_KEY = "careeros_local_user";

export const getStoredUser = () => {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const setStoredUser = (user) => {
  try {
    if (user) {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(LOCAL_STORAGE_KEY);
    }
  } catch {}
};

// Safe local auth provider when Supabase is not configured, expired, or offline
const localAuthClient = {
  auth: {
    getSession: async () => {
      const user = getStoredUser();
      return {
        data: {
          session: user ? { user, access_token: "local-token" } : null,
        },
        error: null,
      };
    },
    onAuthStateChange: () => ({
      data: {
        subscription: {
          unsubscribe: () => {},
        },
      },
    }),
    signUp: async ({ email }) => {
      const user = {
        id: "usr_" + Math.random().toString(36).substring(2, 10),
        email: email || "user@careeros.local",
        user_metadata: { role: "candidate" },
      };
      setStoredUser(user);
      return { data: { user }, error: null };
    },
    signInWithPassword: async ({ email }) => {
      const user = {
        id: "usr_" + Math.random().toString(36).substring(2, 10),
        email: email || "user@careeros.local",
        user_metadata: { role: "candidate" },
      };
      setStoredUser(user);
      return { data: { user }, error: null };
    },
    signOut: async () => {
      setStoredUser(null);
      return { error: null };
    },
  },
};

export const supabase = isSupabaseConfigured
  ? createClient(envUrl, envKey)
  : localAuthClient;