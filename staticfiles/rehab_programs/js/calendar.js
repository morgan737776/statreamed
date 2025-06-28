document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const specialistFilter = document.getElementById('specialist-filter');
    const patientFilter = document.getElementById('patient-filter');
    const printButton = document.getElementById('print-button');

    // The API URL is passed from the template via a json_script
    const calendarApiUrl = JSON.parse(document.getElementById('calendar-api-url').textContent);

    function getApiUrl() {
        const specialistId = specialistFilter.value;
        const patientId = patientFilter.value;
        const params = new URLSearchParams();
        if (specialistId) {
            params.append('specialist_id', specialistId);
        }
        if (patientId) {
            params.append('patient_id', patientId);
        }
        return `${calendarApiUrl}?${params.toString()}`;
    }

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        locale: 'ru',
        buttonText: {
            today: 'Сегодня',
            month: 'Месяц',
            week: 'Неделя',
            day: 'День',
            list: 'Список'
        },
        events: getApiUrl(),
        eventTimeFormat: { 
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false
        },
        eventClick: function(info) {
            if (info.event.url) {
                window.open(info.event.url, '_blank');
                info.jsEvent.preventDefault();
            }
        },
        height: 'auto',
        contentHeight: 700,
    });

    calendar.render();

    // Add event listeners for filters to refetch events
    specialistFilter.addEventListener('change', () => {
        calendar.setOption('events', getApiUrl());
    });

    patientFilter.addEventListener('change', () => {
        calendar.setOption('events', getApiUrl());
    });

    // Add event listener for print button
    printButton.addEventListener('click', () => {
        window.print();
    });
});
