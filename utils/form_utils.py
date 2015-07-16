import itertools

from django import forms
from django.forms import widgets
from django.utils import safestring
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class MultiFileInput(forms.ClearableFileInput):

    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super().render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            value_list = files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                value_list = value
            elif value is None:
                value_list = None
            else:
                value_list = [value]

        if value_list:
            return_list = []
            for upload in value_list:
                return_list.append(self._check_clear(upload, data, files,
                                                     name))
        else:
            return_list = self._check_clear(None, data, files, name)

        return return_list

    def _check_clear(self, upload, data, files, name):
        if (not self.is_required
                and widgets.CheckboxInput().value_from_datadict(
                    data, files, self.clear_checkbox_name(name)
                )):

            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return widgets.FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just
            # None
            return False
        return upload


class MultiFileField(forms.FileField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': _(u'Ensure at least %(min_num)s files are uploaded (received %(num_files)s).'),
        'max_num': _(u'Ensure at most %(max_num)s files are uploaded (received %(num_files)s).'),
        'file_size': _(u'File %(uploaded_file_name)s exceeded maximum upload size.'),
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            i = super().to_python(item)
            if i:
                ret.append(i)

        return ret

    def validate(self, data):
        super().validate(data)

        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})
        for uploaded_file in data:
            if self.maximum_file_size and uploaded_file.size > self.maximum_file_size:
                raise ValidationError(self.error_messages['file_size'] % {'uploaded_file_name': uploaded_file.name})

    def _check_clear(self, data, initial):
        # If the widget got contradictory inputs, we raise a validation error
        if data is widgets.FILE_INPUT_CONTRADICTION:
            raise ValidationError(self.error_messages['contradiction'],
                                  code='contradiction')
        # False means the field value should be cleared; further validation is
        # not needed.
        if data is False:
            if not self.required:
                return False
            # If the field is required, clearing is not possible (the widget
            # shouldn't return False data in that case anyway). False is not
            # in self.empty_value; if a False value makes it this far
            # it should be validated from here on out as None (so it will be
            # caught by the required check).
            data = None
        if not data and initial:
            return initial

        cleaned_data = super(forms.FileField, self).clean(data)

        return cleaned_data

    def clean(self, data, initial=None):
        cleaned_data = []
        LAST_DATUM = object()
        both = itertools.zip_longest(data, initial, fillvalue=LAST_DATUM)
        for datum, initial_datum in both:
            if initial_datum is not LAST_DATUM:
                cleaned_datum = self._check_clear(datum, initial_datum)
                cleaned_data.append(cleaned_datum)
            else:
                cleaned_data.append(datum)

        return cleaned_data


class ClearableFile(widgets.ClearableFileInput):

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }

        # don't display browse for files button
        template = 'EMPTY<br />'

        if self.is_initial(value):
            # don't display change and browse for files button
            template = (
                '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> '
                '%(clear_template)s<br />'
            )
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = \
                    conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = \
                    conditional_escape(checkbox_id)
                substitutions['clear'] = widgets.CheckboxInput().render(
                    checkbox_name, False, attrs={'id': checkbox_id}
                )
                substitutions['clear_template'] = \
                    self.template_with_clear % substitutions

        output = mark_safe(template % substitutions)

        return output


class ConfirmFileWidgetBase():
    script = '''
        <script>
            document.getElementById("%(form_id)s").addEventListener(
                "submit", function(event) {
                    var clear = document.getElementById("%(clear_id)s");
                    if (clear.checked) {
                        var c = confirm("Are you sure you want to clear"
                                        + " %(file_name)s?");
                        if (!c) { event.preventDefault(); }
                    }
                }
            );
        </script>
    '''

    def __init__(self, *args, **kwargs):
        if 'form_id' not in kwargs:
            raise Exception('ConfirmFileWidget requires the form id.')
        if 'form' not in kwargs:
            raise Exception('ConfirmFileWidget requires the form instance.')
        if 'field_name' in kwargs:
            self.field_name = kwargs.pop('field_name')

        self.form_id = kwargs.pop('form_id')
        self.form = kwargs.pop('form')

        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        html = super().render(name, value, attrs)

        if hasattr(self, 'field_name'):
            field_name = self.field_name
            widget_index = int(name[-1:])
            file_name = self.form.initial[field_name][widget_index]
        else:
            field_name = name
            file_name = self.form.initial[field_name]

        widget_name = name

        if field_name in self.form.initial and self.form.initial[field_name]:
            html += self.script % {
                'clear_id': '{0}-clear_id'.format(widget_name),
                'form_id': self.form_id,
                'file_name': file_name
            }
        # else:  # empty file field

        return safestring.mark_safe(html)


class ConfirmFileWidget(ConfirmFileWidgetBase, widgets.ClearableFileInput):
    pass


class ConfirmMultiFileWidget(ConfirmFileWidgetBase, ClearableFile,
                             MultiFileInput):
    pass


class ConfirmMultiFileMultiWidget(widgets.MultiWidget):

    def __init__(self, form_id, form, field_name, file_count, attrs=None):
        widgets = []
        for i in range(file_count):
            widgets.append(ConfirmMultiFileWidget(form_id=form_id, form=form,
                                                  field_name=field_name))

        widgets.append(MultiFileInput())

        super().__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        output = "Current Number of Files: {0}<br />".format(
            len(rendered_widgets) - 1  # Last widget is the multiupload
        )
        for i, rendered_widget in enumerate(rendered_widgets[:-1]):  # no last
            output += "{0}. {1}".format(i + 1,  # humans like 1 based arrays
                                        rendered_widget)
        else:
            output += rendered_widgets[-1]  # last

        return output
