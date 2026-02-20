document.addEventListener('DOMContentLoaded', function() {
    // Quick Jump form
    var form = document.getElementById('quick-jump-form');
    if (form) {
        var catSelect = document.getElementById('quick-jump-catechism');
        var numInput = document.getElementById('quick-jump-input');

        // Update max when catechism selection changes
        if (catSelect) {
            catSelect.addEventListener('change', function() {
                var selected = catSelect.options[catSelect.selectedIndex];
                numInput.max = selected.getAttribute('data-max') || 107;
            });
        }

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var num = parseInt(numInput.value);
            var slug = catSelect ? catSelect.value : 'wsc';
            var selected = catSelect ? catSelect.options[catSelect.selectedIndex] : null;
            var max = selected ? parseInt(selected.getAttribute('data-max')) : 107;
            if (num >= 1 && num <= max) {
                window.location.href = '/' + slug + '/questions/' + num + '/';
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
