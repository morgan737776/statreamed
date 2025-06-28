document.addEventListener('DOMContentLoaded', () => {
    const createProgramForm = document.getElementById('createProgramForm');
    const createProgramModal = document.getElementById('createProgramModal');
    const programsTableBody = document.getElementById('programsTableBody');

    if (createProgramForm) {
        createProgramForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(createProgramForm);
            
            try {
                const response = await fetch(createProgramForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });

                const data = await response.json();

                // Clear previous errors
                document.querySelectorAll('.form-error-message').forEach(el => el.remove());
                document.querySelectorAll('[name]').forEach(el => el.classList.remove('border-red-500'));

                if (data.success) {
                    // Hide the modal using Flowbite's instance
                    const modal = new window.Flowbite.Modal(createProgramModal);
                    modal.hide();
                    createProgramForm.reset();
                    
                    // Add new row to the table
                    if (programsTableBody.querySelector('.no-programs-row')) {
                        programsTableBody.innerHTML = data.program_html;
                    } else {
                        programsTableBody.insertAdjacentHTML('afterbegin', data.program_html);
                    }

                } else {
                    // Display form errors
                    for (const [field, errors] of Object.entries(data.errors)) {
                        const input = createProgramForm.querySelector(`[name="${field}"]`);
                        if (input) {
                            input.classList.add('border-red-500');
                            const errorElement = document.createElement('p');
                            errorElement.className = 'mt-2 text-sm text-red-600 dark:text-red-500 form-error-message';
                            errorElement.textContent = errors.join(', ');
                            const parent = input.closest('div');
                            if (parent) {
                                parent.appendChild(errorElement);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('An error occurred:', error);
                alert('Произошла ошибка. Пожалуйста, проверьте консоль для получения дополнительной информации.');
            }
        });
    }
});
