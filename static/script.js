document.addEventListener('DOMContentLoaded', function() {
    const novaSenhaInput = document.getElementById('nova_senha');
    const confirmarSenhaInput = document.getElementById('confirmar_senha');
    const submitBtn = document.getElementById('submitBtn');
    const passwordHelpBlock = document.getElementById('passwordHelpBlock');
    const confirmPasswordHelpBlock = document.getElementById('confirmPasswordHelpBlock');

    novaSenhaInput.addEventListener('input', validatePassword);
    confirmarSenhaInput.addEventListener('input', validateConfirmPassword);

    function validatePassword() {
        const password = novaSenhaInput.value;
        const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

        if (!pattern.test(password)) {
            novaSenhaInput.classList.add('invalid');
            passwordHelpBlock.textContent = 'A senha deve conter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.';
            submitBtn.disabled = true;
        } else {
            novaSenhaInput.classList.remove('invalid');
            passwordHelpBlock.textContent = '';
            submitBtn.disabled = false;
        }
    }

    function validateConfirmPassword() {
        const password = novaSenhaInput.value;
        const confirmPassword = confirmarSenhaInput.value;

        if (password !== confirmPassword) {
            confirmarSenhaInput.classList.add('invalid');
            confirmPasswordHelpBlock.textContent = 'As senhas não coincidem.';
            submitBtn.disabled = true;
        } else {
            confirmarSenhaInput.classList.remove('invalid');
            confirmPasswordHelpBlock.textContent = '';
            submitBtn.disabled = false;
        }
    }
});
