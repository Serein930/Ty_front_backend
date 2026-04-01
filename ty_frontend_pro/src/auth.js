const AUTH_STORAGE_KEY = 'ty-auth-session';
const AUTH_USER_KEY = 'ty-auth-user';

const mockAccounts = [
  {
    username: 'Administrator',
    password: 'admin123',
    displayName: 'Administrator'
  },
  {
    username: 'analyst',
    password: '123456',
    displayName: '分析员'
  }
];

export const getMockAccounts = () => mockAccounts.map(({ username, password, displayName }) => ({ username, password, displayName }));

export const isAuthenticated = () => localStorage.getItem(AUTH_STORAGE_KEY) === '1';

export const getAuthUser = () => {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
};

export const login = (username, password) => {
  const matched = mockAccounts.find(account => account.username === username && account.password === password);
  if (!matched) return { success: false, message: '账号或密码错误' };

  localStorage.setItem(AUTH_STORAGE_KEY, '1');
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify({
    username: matched.username,
    displayName: matched.displayName
  }));

  return { success: true, user: matched };
};

export const logout = () => {
  localStorage.removeItem(AUTH_STORAGE_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
};
