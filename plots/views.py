from django.shortcuts import render
from django.contrib import messages
from .forms import DateRangeForm
from .models import SpiralPlotImage
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse


def homepage(request):
    return render(request, 'graph_plot.html')


def graph_plot(request):
    plt.switch_backend('agg')

    if request.method == 'POST':
        form = DateRangeForm(request.POST)

        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            excel_file = form.cleaned_data['excel_file']
            selected_rooms = form.cleaned_data['select_room']

            # Store values in session after formatting
            request.session['from_date'] = from_date.strftime('%Y-%m-%d')
            request.session['to_date'] = to_date.strftime('%Y-%m-%d')
            request.session['excel_file'] = excel_file
            request.session['select_room'] = selected_rooms

            start_date = from_date
            end_date = to_date

            data = pd.read_excel(f"excel_files/{excel_file}")

            timestamp_columns = [col for col in data.columns if 'timestamp_excel_' in col]
            room_colors = {room.replace('motionStatus_', ''): np.random.rand(3, ) for room in data.columns if
                           'motionStatus_' in room}

            fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'))
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)

            time_interval = 20
            num_points = 24 * 60
            num_ticks = int(num_points / (time_interval))

            ax.set_xticks((2 * np.pi * np.arange(num_ticks)) / num_ticks)
            ax.set_xticklabels(["{:02d}:{:02d}".format(j // 60, j % 60) for j in range(0, num_points, time_interval)])

            # Track rooms that have been added to the legend
            added_rooms = set()

            # Plot data for each selected room
            for selected_room in selected_rooms:
                for i in range((end_date - start_date).days + 1):
                    # Filter the data for the specific date and motion status == 1
                    date = start_date + pd.Timedelta(days=i)

                    room_data = data[(data[f'timestamp_excel_{selected_room}'].dt.date == date) &
                                     (data[f'motionStatus_{selected_room}'] == 1)]

                    # Drop duplicates to ensure one point per minute
                    room_data = room_data.drop_duplicates(subset=[f'timestamp_excel_{selected_room}']).copy()

                    # Calculate the minute of the day for each timestamp (minutes since midnight)
                    room_data['minute_of_day'] = room_data[f'timestamp_excel_{selected_room}'].dt.hour * 60 + room_data[
                        f'timestamp_excel_{selected_room}'].dt.minute

                    # Create theta (angle) data for the plot
                    theta = (2 * np.pi * room_data['minute_of_day']) / num_points

                    # The radius is just 1 because we're plotting one full circle for the day
                    radius = np.ones(len(room_data)) * (i + 1)  # Increase the radius for each date

                    # Plot each point with reduced dot size and color according to the room
                    ax.scatter(theta, radius, s=7, label=selected_room, color=room_colors[selected_room])

                    # Add the room to the legend if it hasn't been added before
                    if selected_room not in added_rooms:
                        added_rooms.add(selected_room)

            # Add concentric circles and date labels for specified dates
            label_dates = [start_date, '2020-03-13', '2020-06-11', '2020-09-09', to_date]
            label_dates = [pd.to_datetime(date).date() for date in label_dates]
            for i in range((end_date - start_date).days + 1):
                date = start_date + pd.Timedelta(days=i)
                if date in label_dates:
                    date_label = date.strftime('%Y-%m-%d')
                    ax.text(0, i + 1, date_label, ha='center', va='center', color='black', fontsize=8)
                    ax.plot(np.linspace(0, 2 * np.pi, num_points), np.ones(num_points) * (i + 1), color='black',
                            linestyle='dashed', alpha=0.5)

            # Set the title and other parameters to clean up the plot
            selected_rooms_label = ', '.join(selected_rooms)
            ax.set_title(f'Spiral plot for motion sensor data ({selected_rooms_label}) from {start_date} to {end_date}',
                         va='bottom')
            ax.set_yticklabels([])  # Hide radial ticks
            ax.grid(True)

            # Create a custom legend with one entry per room
            legend_labels = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=room_colors[selected_room], markersize=10,
                           label=selected_room) for selected_room in added_rooms]
            ax.legend(handles=legend_labels, title='Room', bbox_to_anchor=(1.05, 1), loc='upper left')

            # Save the figure in a BytesIO buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            plt.close()

            # Save the buffer content to the model's image field
            spiral_plot_image = SpiralPlotImage.objects.create()
            spiral_plot_image.image.save('spiral_plot_motion_sensor_data.png', ContentFile(buffer.getvalue()),
                                         save=False)
            spiral_plot_image.save()

            # Render the merged template with the model instance
            return render(request, 'graph_plot.html', {'form': form, 'spiral_plot_image': spiral_plot_image})

        else:
            form = DateRangeForm()

        return render(request, 'graph_plot.html', {'form': form, 'spiral_plot_image': None})

    else:
        form_data = {
            'from_date': request.session.get('from_date', ''),
            'to_date': request.session.get('to_date', ''),
            'excel_file': request.session.get('excel_file', ''),
            'select_room': request.session.get('select_room', 'all'),
        }
        form = DateRangeForm(initial=form_data)
    spiral_plot_image = None

    return render(request, 'graph_plot.html', {'form': form, 'spiral_plot_image': spiral_plot_image})
