const ACCESS_TOKEN_KEY = 'instagramproyect_access';

export const storage = {
  storeToken(token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  },
  readToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  clearToken() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
  },
};
