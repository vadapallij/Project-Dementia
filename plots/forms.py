# forms.py
from django import forms
import os


class DateRangeForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    excel_file = forms.ChoiceField(
        label='Select Excel File:',
        widget=forms.Select(attrs={'id': 'id_excel_file', 'required': True}),
        choices=[
            ('1331647-Motion sensors.xlsx', '1331647-Motion sensors.xlsx'),
            ('1328632-Motion sensors.xlsx', '1328632-Motion sensors.xlsx'),
            ('1306666-Motion sensors.xlsx', '1306666-Motion sensors.xlsx'),
            ('1306781-Motion sensors.xlsx', '1306781-Motion sensors.xlsx'),
            ('1306617-Motion sensors.xlsx', '1306617-Motion sensors.xlsx'),
            ('Motionsensors-1306512.xlsx', 'Motionsensors-1306512.xlsx'),
            ('Motion sensors- 1306638-Bathroom,Bedroom,Familyroom,Kitchen,Computer-room.xlsx',
             'Motion sensors- 1306638-Bathroom,Bedroom,Familyroom,Kitchen,Computer-room.xlsx')

        ],
        required=True,
    )

    select_room = forms.MultipleChoiceField(label='Select Rooms',
                                            choices=[('Bathroom', 'Bathroom'), ('Bedroom', 'Bedroom'),
                                                     ('Kitchen', 'Kitchen'),
                                                     ('Computer-room', 'Computer-room'),
                                                     ('Living-Room', 'Living-Room'),
                                                     ('Hall', 'Hall'),
                                                     ('Familyroom', 'Familyroom')],
                                            widget=forms.CheckboxSelectMultiple(attrs={'class': 'room-checkbox'}))
