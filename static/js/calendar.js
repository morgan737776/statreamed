// Инициализация календаря
let calendar = null;

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        locale: 'ru',
        firstDay: 1, // Понедельник как первый день недели
        businessHours: true,
        editable: true,
        droppable: true,
        selectable: true,
        selectMirror: true,
        select: handleDateSelect,
        eventClick: handleEventClick,
        eventsSet: handleEvents,
        eventDidMount: function(info) {
            // Добавляем возможность перетаскивания
            info.el.setAttribute('draggable', 'true');
            info.el.addEventListener('dragstart', function(event) {
                event.dataTransfer.setData('text/plain', info.event.id);
            });
        },
        eventTimeFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: false
        },
        eventDidMount: function(info) {
            // Добавляем тултип с информацией о приеме
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.innerHTML = `
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-3">
                    <p class="font-medium">${info.event.title}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">${info.event.extendedProps.patient.first_name} ${info.event.extendedProps.patient.last_name}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">${info.event.extendedProps.doctor_name}</p>
                </div>
            `;
            info.el.appendChild(tooltip);
            
            // Показываем тултип при наведении
            info.el.addEventListener('mouseover', function() {
                tooltip.style.display = 'block';
            });
            
            info.el.addEventListener('mouseout', function() {
                tooltip.style.display = 'none';
            });
        },
        eventDrop: function(info) {
            // Обновляем время приема при перетаскивании
            updateAppointmentTime(info.event.id, info.event.start, info.event.end);
        }
    });
    
    calendar.render();
}

// Обработчик выбора даты
function handleDateSelect(selectInfo) {
    const title = prompt('Введите название приема');
    
    if (title) {
        calendar.addEvent({
            id: Math.random().toString(36).substr(2, 9),
            title,
            start: selectInfo.startStr,
            end: selectInfo.endStr,
            allDay: selectInfo.allDay
        });
    }
    
    calendar.unselect();
}

// Обработчик клика по событию
function handleEventClick(clickInfo) {
    if (confirm(`Удалить прием "${clickInfo.event.title}"?`)) {
        clickInfo.event.remove();
    }
}

// Обработчик загрузки событий
function handleEvents(events) {
    // Загружаем приемы из API
    fetch('/api/appointments/')
        .then(response => response.json())
        .then(data => {
            calendar.removeAllEvents();
            calendar.addEventSource(data);
        });
}

// Обновление времени приема
function updateAppointmentTime(appointmentId, newStart, newEnd) {
    fetch(`/api/appointments/${appointmentId}/update_time/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            start_time: newStart.toISOString(),
            end_time: newEnd.toISOString()
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка обновления времени приема');
        }
        return response.json();
    })
    .catch(error => {
        console.error('Ошибка:', error);
        calendar.refetchEvents();
    });
}

// Получение CSRF токена из куков
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Инициализация календаря при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
});
