document.addEventListener('DOMContentLoaded', function() {
    // Элементы для предпросмотра изображений
    const fileInput = document.getElementById('id_document');
    const imagePreview = document.getElementById('imagePreview');
    const fileInfo = document.getElementById('fileInfo');
    const loadingOverlay = document.querySelector('.loading-overlay');
    const documentForm = document.getElementById('documentForm');
    
    // Обработчик изменения файла
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            // Показываем информацию о файле
            fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
            
            // Проверяем, является ли файл изображением
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (imagePreview) {
                        imagePreview.src = e.target.result;
                        imagePreview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            } else if (imagePreview) {
                imagePreview.style.display = 'none';
            }
            
            // Валидация размера файла (максимум 25 МБ)
            const maxSize = 25 * 1024 * 1024; // 25 МБ в байтах
            if (file.size > maxSize) {
                showError('Размер файла не должен превышать 25 МБ');
                fileInput.value = '';
                if (fileInfo) fileInfo.textContent = '';
                if (imagePreview) imagePreview.style.display = 'none';
            }
        });
    }
    
    // Обработка отправки формы документа
    if (documentForm) {
        documentForm.addEventListener('submit', function(e) {
            // Показываем индикатор загрузки
            if (loadingOverlay) loadingOverlay.style.display = 'flex';
            
            // Проверяем, что файл выбран
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                showError('Пожалуйста, выберите файл для загрузки');
                if (loadingOverlay) loadingOverlay.style.display = 'none';
                return false;
            }
            
            return true;
        });
    }
    
    // Форматирование размера файла
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Байт';
        const k = 1024;
        const sizes = ['Байт', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Показать сообщение об ошибке
    function showError(message) {
        // Создаем элемент для отображения ошибки
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.role = 'alert';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
        `;
        
        // Вставляем сообщение об ошибке перед формой
        if (documentForm) {
            documentForm.parentNode.insertBefore(errorDiv, documentForm);
        } else {
            document.body.insertBefore(errorDiv, document.body.firstChild);
        }
        
        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => errorDiv.remove(), 150);
        }, 5000);
    }
    
    // Инициализация tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Скрываем индикатор загрузки после загрузки страницы
    if (loadingOverlay) loadingOverlay.style.display = 'none';
});

// Функция для обновления предпросмотра изображения
function updateImagePreview(input) {
    const preview = document.getElementById('imagePreview');
    const fileInfo = document.getElementById('fileInfo');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
            fileInfo.textContent = input.files[0].name;
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Функция для удаления документа
function confirmDeleteDocument(documentId, documentName) {
    if (confirm(`Вы уверены, что хотите удалить документ "${documentName}"?`)) {
        const form = document.createElement('form');
        form.method = 'post';
        form.action = `/documents/${documentId}/delete/`;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}
