export function useAuth() {
  /**
   * Placeholder: se encargará de manejar tokens, refresh silencioso y roles.
   */
  const login = async (credentials) => {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(credentials)
    });
    return await res.json();
  };

  const logout = async () => {
    await fetch('/auth/logout', { method: 'POST' });
  };

  return { login, logout };
}
