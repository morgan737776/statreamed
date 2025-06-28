document.addEventListener('DOMContentLoaded', function() {
    // Открытие модалки
    var addBtn = document.getElementById('openAddProgramModal');
    if (addBtn) {
        addBtn.addEventListener('click', function(e) {
            e.preventDefault();
            var modal = new bootstrap.Modal(document.getElementById('addProgramModal'));
            modal.show();
        });
    }
    // Автопоиск для пациента и специалиста через Select2 (если подключён)
    if (window.jQuery && $.fn.select2) {
        $('#id_patient').select2({width:'100%', dropdownParent:$('#addProgramModal')});
        $('#id_specialist').select2({width:'100%', dropdownParent:$('#addProgramModal')});
    }
});
