/*
    АВТОРИЗАЦИЯ
    ===========
    Что здесь:
    - Регистрация
    - Вход
    - Сохранение токена

    Что делать:
    - Функция register() — POST /auth/register
    - Функция login() — POST /auth/login
    - Сохранять токен в localStorage
*/

// TODO: загрузить статистику сотрудника
async function loadEmployeeStats() {
    // GET /stats/me
    // Нарисовать график
}

// TODO: загрузить статистику руководителя
async function loadManagerStats() {
    // GET /stats/organization
    // Нарисовать график по сотрудникам
}