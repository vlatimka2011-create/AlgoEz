/*
    ОСНОВНАЯ ЛОГИКА
    ===============
    Что здесь:
    - Общие функции (запросы к API, работа с токеном)
    - Навигация между страницами

    Что делать:
    - Функция apiRequest() — обёртка над fetch с JWT
    - Функция checkAuth() — проверка токена
    - Функция logout() — выход
*/

// TODO: базовый URL API
const API_URL = 'http://localhost:8000';

// TODO: функция запроса к API
async function apiRequest(endpoint, options = {}) {
    // Добавить заголовок Authorization
    // Вернуть response.json()
}

// TODO: проверка авторизации
function checkAuth() {
    // Проверить токен в localStorage
    // Если нет — перенаправить на register.html (для новых)
    // Если есть — показать профиль
}

// TODO: выход
function logout() {
    // Очистить localStorage
    // Перенаправить на register.html (так как login.html убрали)
}