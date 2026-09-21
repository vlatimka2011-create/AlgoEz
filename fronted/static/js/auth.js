/*
    АВТОРИЗАЦИЯ
    ===========
    Что здесь:
    - Автоматический вход через MAX
    - Регистрация новых пользователей

    Что делать:
    - Получить user_id из MAX Bridge
    - Проверить, зарегистрирован ли пользователь
    - Если да — сохранить токен и показать профиль
    - Если нет — показать форму регистрации
*/

// TODO: получить данные из MAX
function getMaxUserData() {
    // window.WebApp.initDataUnsafe.user
    // Возвращает { id, first_name, last_name }
}

// TODO: автоматический вход
async function autoLogin() {
    // Получить user_id из MAX
    // POST /auth/login
    // Сохранить токен
}