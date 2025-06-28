// Services Module JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize datepickers
    $('.datepicker').datepicker({
        format: 'dd.mm.yyyy',
        autoclose: true,
        todayHighlight: true,
        language: 'ru',
        orientation: 'bottom auto'
    });

    // Initialize timepickers
    $('.timepicker').timepicker({
        showMeridian: false,
        minuteStep: 15,
        showInputs: false,
        disableFocus: true
    });

    // Handle service category selection
    $('select[name="category"]').on('change', function() {
        var categoryId = $(this).val();
        var $serviceSelect = $('select[name="service"]');
        
        // Clear and disable service select
        $serviceSelect.empty().prop('disabled', true);
        
        if (categoryId) {
            // Fetch services for selected category
            $.ajax({
                url: '/services/api/services-by-category/',
                data: { category_id: categoryId },
                dataType: 'json',
                success: function(data) {
                    $serviceSelect.empty().append('<option value="">Выберите услугу</option>');
                    
                    $.each(data.services, function(key, value) {
                        $serviceSelect.append(`<option value="${value.id}" data-price="${value.price}">${value.name} (${value.price} руб.)</option>`);
                    });
                    
                    $serviceSelect.prop('disabled', false);
                }
            });
        }
    });

    // Handle service selection
    $(document).on('change', 'select[name="service"]', function() {
        var selectedOption = $(this).find('option:selected');
        var price = selectedOption.data('price');
        
        if (price) {
            $('input[name="price"]').val(price);
            updateTotalPrice();
        }
    });

    // Handle quantity changes
    $(document).on('input', 'input[name="quantity"]', function() {
        updateTotalPrice();
    });

    // Calculate and update total price
    function updateTotalPrice() {
        var price = parseFloat($('input[name="price"]').val()) || 0;
        var quantity = parseInt($('input[name="quantity"]').val()) || 1;
        var total = price * quantity;
        
        $('input[name="total_price"]').val(total.toFixed(2));
    }

    // Initialize calendar if it exists on the page
    if (document.getElementById('calendar')) {
        initializeCalendar();
    }
});

// Initialize FullCalendar
function initializeCalendar() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ru',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: 'Сегодня',
            month: 'Месяц',
            week: 'Неделя',
            day: 'День',
            list: 'Список'
        },
        events: JSON.parse(document.getElementById('calendar-events').textContent),
        eventClick: function(info) {
            // Handle event click
            window.location.href = `/services/appointments/${info.event.id}/`;
        },
        dateClick: function(info) {
            // Handle date click - redirect to create appointment with pre-filled date
            window.location.href = `/services/appointments/add/?date=${info.dateStr}`;
        },
        eventClassNames: function(arg) {
            // Add custom classes based on event properties
            const classNames = [];
            
            // Add status class
            if (arg.event.extendedProps.status_class) {
                classNames.push(`fc-event-${arg.event.extendedProps.status_class}`);
            }
            
            return classNames;
        },
        eventContent: function(arg) {
            // Custom event content
            const eventHtml = `
                <div class="fc-event-main-frame">
                    <div class="fc-event-time">${arg.timeText}</div>
                    <div class="fc-event-title-container">
                        <div class="fc-event-title">${arg.event.title}</div>
                    </div>
                </div>
            `;
            
            return { html: eventHtml };
        }
    });
    
    calendar.render();
}

// Initialize data tables if they exist on the page
$(document).ready(function() {
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Russian.json'
            },
            dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                 "<'row'<'col-sm-12'tr>>" +
                 "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            pageLength: 25,
            order: [[0, 'desc']]
        });
    }
});
