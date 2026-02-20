document.addEventListener('DOMContentLoaded', function() {
    // Quick Jump form
    var form = document.getElementById('quick-jump-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var num = document.getElementById('quick-jump-input').value;
            if (num >= 1 && num <= 107) {
                window.location.href = '/questions/' + num + '/';
            }
        });
    }

    // Add Bootstrap classes to Django form inputs that don't have them
    var formInputs = document.querySelectorAll('form input[type="text"], form input[type="email"], form input[type="password"]');
    formInputs.forEach(function(input) {
        if (!input.classList.contains('form-control')) {
            input.classList.add('form-control');
        }
    });
});
