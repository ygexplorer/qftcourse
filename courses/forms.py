"""
作业提交表单

支持：
- PDF 文件上传（前后端校验）
- 留言/备注（选填）
- 逾期原因（逾期提交时必填）
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import Submission
from .utils import validate_pdf


class SubmissionForm(forms.ModelForm):
    """
    学生提交作业表单

    动态行为（通过 __init__ 参数控制）：
    - is_late=True 时，late_reason 变为必填
    """

    class Meta:
        model = Submission
        fields = ['file', 'message', 'late_reason']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': '可选：给老师/助教留言',
                'class': 'w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            }),
            'late_reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': '请说明逾期原因',
                'class': 'w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500',
            }),
            'file': forms.FileInput(attrs={
                'accept': '.pdf,application/pdf',
            }),
        }

    def __init__(self, *args, is_late=False, **kwargs):
        """
        is_late: 是否逾期提交。
        逾期时 late_reason 字段变为必填，并加红色边框样式。
        """
        super().__init__(*args, **kwargs)
        self.is_late = is_late

        if is_late:
            self.fields['late_reason'].required = True
            self.fields['late_reason'].label = '逾期原因（必填）'
            self.fields['late_reason'].widget.attrs.update({
                'class': 'w-full rounded-lg border-2 border-red-300 px-4 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500',
            })
        else:
            self.fields['late_reason'].required = False
            self.fields['late_reason'].widget = forms.HiddenInput()

        # 文件字段的 label
        self.fields['file'].label = '上传作业 PDF'
        self.fields['file'].required = True
        self.fields['file'].validators.append(validate_pdf)

    def clean_file(self):
        """双重校验：validators 已经校验过，这里做兜底"""
        f = self.cleaned_data.get('file')
        if f and hasattr(f, 'name'):
            ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
            if ext != 'pdf':
                raise ValidationError('只支持 PDF 文件。')
        return f
