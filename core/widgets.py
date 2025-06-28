from django.forms import widgets

class BootstrapDatePickerInput(widgets.DateInput):
    template_name = 'core/widgets/bootstrap_datepicker.html'

    def __init__(self, attrs=None, format='%Y-%m-%d'):
        default_attrs = {
            'class': 'form-control',
            'type': 'date',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)


class BootstrapDateTimePickerInput(widgets.DateTimeInput):
    template_name = 'core/widgets/bootstrap_datetimepicker.html'

    def __init__(self, attrs=None, format='%Y-%m-%dT%H:%M'):
        default_attrs = {
            'class': 'form-control',
            'type': 'datetime-local',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)
