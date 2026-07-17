const formData = document.getElementById('contact-form');

formData.addEventListener('submit', function(event) {

    clearErrors();

    let hasErrors = false;

    const emailInput = document.getElementById('id_email');
    const phoneInput = document.getElementById('id_phone_number');

    if (!validateEmail(emailInput.value.trim())) {
        showError(emailInput, 'Nieprawidłowy adres e-mail.');
        hasErrors = true;
    }

    if (!validatePhone(phoneInput.value.trim())) {
        showError(phoneInput, 'Nieprawidłowy numer telefonu (9-15 znaków, cyfry, opcjonalny "+").');
        hasErrors = true;
    }

    if (hasErrors) {
        event.preventDefault();
    }
});

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^\+?[\d\s-]{9,15}$/;
    return phoneRegex.test(phone);
}

function showError(input, message) {
    input.classList.add('is-invalid');
    const feedback = input.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.textContent = message;
    }
}

function clearErrors() {
    formData.querySelectorAll('.is-invalid').forEach(function (input) {
        input.classList.remove('is-invalid');
    });
}

