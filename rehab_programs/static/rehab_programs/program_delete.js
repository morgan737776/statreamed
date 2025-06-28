document.addEventListener('DOMContentLoaded', function() {
    var deleteButtons = document.querySelectorAll('.btn-delete-program');
    var modalEl = document.getElementById('deleteProgramModal');
    var form = document.getElementById('deleteProgramForm');
    var programIdInput = document.getElementById('deleteProgramId');
    var programNameSpan = document.getElementById('deleteProgramName');

    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var programId = btn.getAttribute('data-program-id');
            var programName = btn.getAttribute('data-program-name');
            programIdInput.value = programId;
            programNameSpan.textContent = programName;
            // Установить action для формы
            form.action = '/programs/' + programId + '/delete/';
            var modal = new bootstrap.Modal(modalEl);
            modal.show();
        });
    });
});
