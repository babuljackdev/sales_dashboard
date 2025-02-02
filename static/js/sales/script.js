
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

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const inputs = form.querySelectorAll('input, select');
    
    // Add focus and interaction styles
    inputs.forEach(input => {
        const formGroup = input.closest('.form-group');
        
        // Focus effects
        input.addEventListener('focus', function() {
            formGroup.classList.add('is-focused');
            this.classList.add('ring-2', 'ring-primary-500', 'border-primary-500');
        });
        
        input.addEventListener('blur', function() {
            formGroup.classList.remove('is-focused');
            if (!this.value) {
                this.classList.remove('ring-2', 'ring-primary-500', 'border-primary-500');
            }
        });
        
        // Handle changes
        input.addEventListener('change', function() {
            if (this.value) {
                formGroup.classList.add('is-filled');
            } else {
                formGroup.classList.remove('is-filled');
            }
        });
        
        // Initialize filled state
        if (input.value) {
            formGroup.classList.add('is-filled');
        }
    });
    
    // Enhanced form validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        inputs.forEach(input => {
            const formGroup = input.closest('.form-group');
            
            if (input.required && !input.value.trim()) {
                isValid = false;
                formGroup.classList.add('has-error');
                input.classList.add('border-red-300', 'text-red-900', 'placeholder-red-300');
                input.classList.remove('border-gray-300');
                
                // Add or update error message
                let errorMsg = formGroup.querySelector('.text-red-600');
                if (!errorMsg) {
                    errorMsg = document.createElement('p');
                    errorMsg.className = 'mt-2 text-sm text-red-600';
                    formGroup.appendChild(errorMsg);
                }
                errorMsg.textContent = `${input.closest('.form-group').querySelector('label').textContent.replace('*', '').trim()} is required.`;
            } else {
                formGroup.classList.remove('has-error');
                input.classList.remove('border-red-300', 'text-red-900', 'placeholder-red-300');
                input.classList.add('border-gray-300');
                
                // Remove error message if exists
                const errorMsg = formGroup.querySelector('.text-red-600');
                if (errorMsg) {
                    errorMsg.remove();
                }
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            // Scroll to first error
            const firstError = form.querySelector('.has-error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
}, 5000);


//forms

function updateUnitPrice(productSelect) {
    const selectedOption = productSelect.options[productSelect.selectedIndex];
    const price = selectedOption.dataset.price || '0.00';
    document.getElementById('id_price_per_unit').value = price;
    calculateTotal();
}

function calculateTotal() {
    const quantity = parseFloat(document.getElementById('id_quantity').value) || 0;
    const unitPrice = parseFloat(document.getElementById('id_price_per_unit').value) || 0;
    const total = quantity * unitPrice;
    document.getElementById('total_price').value = total.toFixed(2);
}

// Calculate total on page load
document.addEventListener('DOMContentLoaded', calculateTotal);

// multi form
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('productsContainer');
    const addButton = document.getElementById('addProduct');
    const template = container.querySelector('.product-row');
    const grandTotalElement = document.getElementById('grandTotal');

    function calculateRowTotal(row) {
        const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
        const price = parseFloat(row.querySelector('.price-input').value) || 0;
        const total = quantity * price;
        row.querySelector('.row-total').value = total.toFixed(2);
        return total;
    }

    function updateGrandTotal() {
        const rows = container.querySelectorAll('.product-row');
        let grandTotal = 0;
        rows.forEach(row => {
            grandTotal += calculateRowTotal(row);
        });
        grandTotalElement.textContent = grandTotal.toFixed(2);
    }

    function setupRow(row) {
        const removeButton = row.querySelector('.remove-product');
        const productSelect = row.querySelector('select[name="products[]"]');
        const priceInput = row.querySelector('.price-input');
        const quantityInput = row.querySelector('.quantity-input');

        removeButton.addEventListener('click', function() {
            if (container.children.length > 1) {
                row.remove();
                updateGrandTotal();
            }
        });

        productSelect.addEventListener('change', function() {
            const selected = productSelect.options[productSelect.selectedIndex];
            if (selected.dataset.price) {
                priceInput.value = selected.dataset.price;
                updateGrandTotal();
            }
        });

        quantityInput.addEventListener('input', updateGrandTotal);
    }

    addButton.addEventListener('click', function() {
        const newRow = template.cloneNode(true);
        setupRow(newRow);
        container.appendChild(newRow);
    });

    setupRow(template);
});
