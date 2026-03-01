export const apiClient = (token) => {
  const headers = {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : undefined,
  };
  return (endpoint, options = {}) =>
    fetch(endpoint, {
      ...options,
      headers: { ...headers, ...options.headers },
      credentials: 'include',
    });
};
