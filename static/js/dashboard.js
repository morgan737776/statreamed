// Кэшируем часто используемые элементы DOM
const cache = {};

// Функция для отложенной загрузки
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Основная функция инициализации
function initDashboard() {
    // Инициализация только видимых элементов
    const initVisibleElements = () => {
        // Код инициализации видимых элементов
    };

    // Используем Intersection Observer для ленивой загрузки
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Ленивая загрузка контента
                if (entry.target.dataset.src) {
                    entry.target.src = entry.target.dataset.src;
                    observer.unobserve(entry.target);
                }
            }
        });
    }, {
        rootMargin: '100px',
        threshold: 0.01
    });

    // Наблюдаем за элементами с атрибутом data-src
    document.querySelectorAll('[data-src]').forEach(el => observer.observe(el));

    // Оптимизация ресайза окна
    const handleResize = debounce(() => {
        initVisibleElements();
    }, 250);

    // Вешаем обработчики событий
    window.addEventListener('resize', handleResize, { passive: true });
    document.addEventListener('scroll', () => {
        requestAnimationFrame(initVisibleElements);
    }, { passive: true });

    // Первоначальная инициализация
    initVisibleElements();
}

// Запускаем инициализацию после полной загрузки страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
    // Инициализация календаря
    initCalendar();
    
    // Инициализация графика статистики
    initStatsChart();
    
    // Инициализация карточек статистики
    initStatCards();
    
    // Инициализация кликабельных карточек
    initClickableCards();
    
    // Инициализация анимаций при скролле
    initScrollAnimations();
});

// Инициализация календаря
function initCalendar() {
    const calendarWidget = document.querySelector('.calendar-widget');
    if (!calendarWidget) return;
    
    const monthYearElement = calendarWidget.querySelector('.cal-month-year');
    const prevMonthButton = calendarWidget.querySelector('.cal-nav:first-child');
    const nextMonthButton = calendarWidget.querySelector('.cal-nav:last-child');
    const calendarGrid = calendarWidget.querySelector('.calendar-grid');
    const appointmentDates = JSON.parse(calendarWidget.dataset.appointmentDates || '[]');

    let currentDate = new Date();

    function renderCalendar(date) {
        const year = date.getFullYear();
        const month = date.getMonth();
        
        monthYearElement.textContent = `${date.toLocaleString('default', { month: 'long' })} ${year}`;

        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const lastDateOfMonth = new Date(year, month + 1, 0).getDate();
        const lastDateOfLastMonth = new Date(year, month, 0).getDate();

        let daysHtml = '';

        // Добавляем названия дней недели
        ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'].forEach(day => {
            daysHtml += `<div class="cal-day-name text-xs font-medium text-gray-500 dark:text-gray-400">${day}</div>`;
        });

        // Пустые дни в начале месяца
        for (let i = firstDayOfMonth; i > 0; i--) {
            daysHtml += '<div class="cal-day empty"></div>';
        }

        // Дни месяца
        for (let i = 1; i <= lastDateOfMonth; i++) {
            const isToday = i === new Date().getDate() && 
                          month === new Date().getMonth() && 
                          year === new Date().getFullYear();
            const hasEvent = appointmentDates.includes(i) && 
                           month === new Date().getMonth() && 
                           year === new Date().getFullYear();

            let dayClasses = 'cal-day flex items-center justify-center w-8 h-8 rounded-full';
            if (isToday) dayClasses += ' bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-200';
            if (hasEvent) dayClasses += ' has-event relative';

            const eventDot = hasEvent ? '<span class="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>' : '';
            
            daysHtml += `
                <div class="${dayClasses}">
                    ${i}
                    ${eventDot}
                </div>`;
        }

        calendarGrid.innerHTML = daysHtml;
    }

    prevMonthButton.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextMonthButton.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    renderCalendar(currentDate);
}

// Инициализация графика статистики
function initStatsChart() {
    const monthlyStatsCtx = document.getElementById('monthlyStatsChart');
    if (!monthlyStatsCtx) return;

    // Функция для получения цветов в зависимости от темы
    function getChartColors() {
        const isDark = document.documentElement.classList.contains('dark');
        return {
            textColor: isDark ? '#9ca3af' : '#6b7280',
            gridColor: isDark ? 'rgba(156, 163, 175, 0.1)' : 'rgba(156, 163, 175, 0.1)',
            bgColor: isDark ? 'rgba(31, 41, 55, 0.8)' : 'rgba(255, 255, 255, 0.8)',
            borderColor: isDark ? 'rgba(75, 85, 99, 0.5)' : 'rgba(229, 231, 235, 0.8)'
        };
    }

    
    // Создаем градиент для заливки графика
    function createGradient(ctx, color) {
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, `${color}33`);
        gradient.addColorStop(1, `${color}03`);
        return gradient;
    }
    
    // Настройки графика
    function getChartOptions(colors) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: colors.textColor,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 13
                        },
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: colors.bgColor,
                    titleColor: document.documentElement.classList.contains('dark') ? '#f3f4f6' : '#111827',
                    bodyColor: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#4b5563',
                    titleFont: {
                        family: 'Inter, sans-serif',
                        size: 13,
                        weight: 500
                    },
                    bodyFont: {
                        family: 'Inter, sans-serif',
                        size: 13,
                        weight: 400
                    },
                    padding: 12,
                    cornerRadius: 8,
                    borderColor: colors.borderColor,
                    borderWidth: 1,
                    displayColors: true,
                    usePointStyle: true,
                    boxPadding: 6,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += context.parsed.y;
                            }
                            return label;
                        },
                        labelColor: function(context) {
                            return {
                                borderColor: context.dataset.borderColor,
                                backgroundColor: context.dataset.borderColor,
                                borderWidth: 2,
                                borderRadius: 2,
                                borderDash: [0, 0],
                                borderDashOffset: 0
                            };
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false,
                        drawTicks: false
                    },
                    ticks: {
                        color: colors.textColor,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12
                        },
                        padding: 8
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: colors.gridColor,
                        drawBorder: false,
                        borderDash: [4, 4],
                        drawTicks: false,
                        tickLength: 0
                    },
                    ticks: {
                        color: colors.textColor,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12
                        },
                        padding: 10,
                        callback: function(value) {
                            return value % 1 === 0 ? value : '';
                        }
                    },
                    border: {
                        display: false
                    }
                }
            },
            elements: {
                line: {
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                },
                point: {
                    radius: 0,
                    hoverRadius: 6,
                    hoverBorderWidth: 2,
                    hoverBorderColor: function(context) {
                        return context.dataset.borderColor;
                    },
                    hoverBackgroundColor: '#fff'
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            transitions: {
                show: {
                    animations: {
                        x: { from: 0 },
                        y: { from: 0.5 }
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    right: 10,
                    bottom: 10,
                    left: 10
                }
            },
            onHover: function(event, chartElement) {
                const target = event.native && event.native.target;
                if (target) {
                    target.style.cursor = chartElement && chartElement[0] ? 'pointer' : 'default';
                }
            }
        };
    }
    
    // Функция для обновления данных графика в зависимости от периода
    function updateChartData(period) {
        // В реальном приложении здесь был бы AJAX-запрос за новыми данными
        console.log('Загрузка данных за период:', period);
        
        // Пример данных для разных периодов
        const periodData = {
            week: {
                labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                data1: [12, 19, 3, 5, 2, 3, 15],
                data2: [8, 5, 10, 7, 12, 8, 5]
            },
            month: {
                labels: ['Неделя 1', 'Неделя 2', 'Неделя 3', 'Неделя 4'],
                data1: [45, 52, 48, 60],
                data2: [32, 40, 35, 50]
            },
            year: {
                labels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
                data1: [180, 195, 210, 230, 245, 260, 250, 265, 280, 270, 290, 300],
                data2: [150, 165, 180, 200, 215, 230, 220, 235, 250, 240, 260, 270]
            }
        };
        
        const data = periodData[period] || periodData.week;
        
        // Анимация обновления графика
        if (monthlyStatsChart) {
            monthlyStatsChart.data.labels = data.labels;
            monthlyStatsChart.data.datasets[0].data = data.data1;
            monthlyStatsChart.data.datasets[1].data = data.data2;
            monthlyStatsChart.update();
        }
    }
    
    const colors = getChartColors();
    let monthlyStatsChart;
    
    // Конфигурация графика
    const config = {
        type: 'line',
        data: {
            labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
            datasets: [
                {
                    label: 'Пациенты',
                    data: [12, 19, 3, 5, 2, 3, 15],
                    borderColor: '#3b82f6',
                    backgroundColor: createGradient(monthlyStatsCtx, '#3b82f6'),
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#3b82f6',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#3b82f6',
                    pointHoverBorderWidth: 2,
                    pointHitRadius: 10,
                    pointStyle: 'circle',
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'Приемы',
                    data: [8, 5, 10, 7, 12, 8, 5],
                    borderColor: '#10b981',
                    backgroundColor: createGradient(monthlyStatsCtx, '#10b981'),
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#10b981',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#10b981',
                    pointHoverBorderWidth: 2,
                    pointHitRadius: 10,
                    pointStyle: 'circle',
                    pointRadius: 0,
                    pointHoverRadius: 5
                }
            ]
        },
        options: getChartOptions(colors)
    };
    
    // Обработка переключения периодов
    const periodButtons = document.querySelectorAll('[data-period]');
    periodButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Обновляем активную кнопку
            periodButtons.forEach(btn => {
                btn.classList.remove('bg-blue-100', 'dark:bg-blue-900/30', 'text-blue-600', 'dark:text-blue-400');
                btn.classList.add('bg-gray-100', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
            });
            
            this.classList.remove('bg-gray-100', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
            this.classList.add('bg-blue-100', 'dark:bg-blue-900/30', 'text-blue-600', 'dark:text-blue-400');
            
            // Обновляем данные графика
            const period = this.getAttribute('data-period');
            updateChartData(period);
        });
    });
    
    // Обработчик изменения темы
    function handleThemeChange() {
        const colors = getChartColors();
        
        if (monthlyStatsChart) {
            // Обновляем цвета графика
            monthlyStatsChart.options.scales.x.ticks.color = colors.textColor;
            monthlyStatsChart.options.scales.y.ticks.color = colors.textColor;
            monthlyStatsChart.options.scales.y.grid.color = colors.gridColor;
            monthlyStatsChart.options.plugins.tooltip.backgroundColor = colors.bgColor;
            monthlyStatsChart.options.plugins.tooltip.titleColor = document.documentElement.classList.contains('dark') ? '#f3f4f6' : '#111827';
            monthlyStatsChart.options.plugins.tooltip.bodyColor = document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#4b5563';
            monthlyStatsChart.options.plugins.legend.labels.color = colors.textColor;
            
            monthlyStatsChart.update();
        }
    }
    
    // Следим за изменением темы
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                handleThemeChange();
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
    });
    
    // Инициализация графика
    monthlyStatsChart = new Chart(monthlyStatsCtx, config);
    
    // Инициализация с данными за неделю
    updateChartData('week');
}

// Инициализация карточек статистики
function initStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });
}

// Инициализация кликабельных карточек
function initClickableCards() {
    const clickableCards = document.querySelectorAll('.card-clickable');
    clickableCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function(e) {
            // Пропускаем клики по кнопкам и ссылкам внутри карточки
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON' && !e.target.closest('a') && !e.target.closest('button')) {
                const link = this.querySelector('a[href]');
                if (link) {
                    window.location.href = link.href;
                }
            }
        });
    });
}

// Инициализация анимаций при скролле
function initScrollAnimations() {
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('[data-aos]');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - 100) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Запускаем анимацию при загрузке и скролле
    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);
}
