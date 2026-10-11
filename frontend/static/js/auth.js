const API_URL = 'http://localhost:8000';

/**
 * Регистрация пользователя через MAX
 */
async function register() {
    // Проверяем, что мы внутри MAX
    if (!window.WebApp || !window.WebApp.initDataUnsafe) {
        console.warn('Приложение должно быть открыто внутри MAX');
        return;
    }

    const maxUser = window.WebApp.initDataUnsafe.user;
    const fullName = `${maxUser.first_name} ${maxUser.last_name || ''}`.trim();

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                max_id: maxUser.id,
                full_name: fullName,
                position: 'employee',
                specialty: null
            })
        });

        if (!response.ok) {
            throw new Error(`Ошибка регистрации: ${response.status}`);
        }

        /** @type {TokenResponse} */
        const data = await response.json();
        localStorage.setItem('token', data.access_token);

        console.log('Регистрация успешна');
        window.location.href = '/profile.html';

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Не удалось зарегистрироваться. Попробуйте позже.');
    }
}

/**
 * Вход через MAX
 */
async function login() {
    if (!window.WebApp || !window.WebApp.initDataUnsafe) {
        console.warn('Приложение должно быть открыто внутри MAX');
        return;
    }

    const maxUser = window.WebApp.initDataUnsafe.user;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ max_id: maxUser.id })
        });

        if (response.status === 404) {
            console.log('Пользователь не найден — нужна регистрация');
            window.location.href = '/register.html';
            return;
        }

        if (!response.ok) {
            throw new Error(`Ошибка входа: ${response.status}`);
        }

        /** @type {TokenResponse} */
        const data = await response.json();
        localStorage.setItem('token', data.access_token);

        console.log('✅ Вход выполнен');
        window.location.href = '/profile.html';

    } catch (error) {
        console.error('Ошибка:', error);
    }
}
