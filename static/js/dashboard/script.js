
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#0284c7',
                    700: '#0369a1',
                    800: '#075985',
                    900: '#0c4a6e',
                }
            }
        }
    }
}
//forms
document.addEventListener('DOMContentLoaded', function() {
    const formGroups = document.querySelectorAll('.form-group');
    
    formGroups.forEach(group => {
        const input = group.querySelector('input, textarea');
        const label = group.querySelector('label');
        
        if (input && label) {
            // Add floating effect
            input.addEventListener('focus', () => {
                label.classList.add('text-primary-600');
                input.classList.add('border-primary-500');
            });
            
            input.addEventListener('blur', () => {
                label.classList.remove('text-primary-600');
                if (!input.value) {
                    input.classList.remove('border-primary-500');
                }
            });
            
            // Initialize if field has value
            if (input.value) {
                input.classList.add('border-gray-400');
            }
        }
    });
});

setTimeout(function() {
    var message = document.getElementById('message');
    message.style.transition = 'opacity 1s';
    message.style.opacity = '0';
    setTimeout(function() {
        message.remove();
    }, 1000);
}, 2000);