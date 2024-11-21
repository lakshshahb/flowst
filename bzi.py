import time
import streamlit as st
import pandas as pd
import numpy as np
import random
import serial
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# Simulate serial port data for testing purposes (dummy mode)
def generate_dummy_data():
    t = time.time()  # Use current time for frequency
    flow_rate = 50 + 30 * np.sin(2 * np.pi * t * 0.1) + random.uniform(-5, 5)  # Sinusoidal wave with noise
    return round(flow_rate, 2)

# Read from Arduino (when connected)
def read_from_arduino(arduino):
    try:
        arduino_data = arduino.readline().decode('utf-8').strip()
        if arduino_data:
            return float(arduino_data)  # Convert to float for graphing
        return None
    except:
        return None

# Function to calculate stats (mean, min, max, peak)
def calculate_stats(data):
    if len(data) == 0:
        return {"Mean": 0, "Min": 0, "Max": 0, "Peak": 0}
    return {
        "Mean": round(np.mean(data), 2),
        "Min": round(np.min(data), 2),
        "Max": round(np.max(data), 2),
        "Peak": round(np.max(np.abs(data)), 2)
    }

# Function to generate and save the chart as an image (in memory)
def save_chart_as_image(data):
    fig, ax = plt.subplots()
    ax.plot(data, label="Flow Rate")
    ax.set_title("Flow Rate Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Flow Rate")
    ax.legend()

    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    # Convert the buffer to an image object for further use
    image = Image.open(buf)
    return image

# Function to generate PDF report with chart and stats
def generate_pdf(data, stats, chart_img):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Flow Sensor Data Report", ln=True, align='C')

    # Add statistics
    pdf.ln(10)
    pdf.cell(200, 10, txt="Statistics:", ln=True)
    for key, value in stats.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    # Save the image to a temporary file and include it in the PDF
    chart_img.save('temp_chart_image.png')
    pdf.ln(10)
    pdf.cell(200, 10, txt="Flow Rate Chart:", ln=True)
    pdf.image('temp_chart_image.png', x=10, y=None, w=190)

    # Add data table
    pdf.ln(10)
    pdf.cell(200, 10, txt="Flow Rate Data (All Readings):", ln=True)
    for i, flow in enumerate(data):
        pdf.cell(200, 10, txt=f"{i+1}: {flow}", ln=True)

    # Save to a file
    pdf_output = "flow_sensor_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Streamlit app
def main():
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state['data'] = []
    if 'running' not in st.session_state:
        st.session_state['running'] = False
    if 'dummy_mode' not in st.session_state:
        st.session_state['dummy_mode'] = True  # Start in dummy mode by default
    if 'arduino_connected' not in st.session_state:
        st.session_state['arduino_connected'] = False  # Toggle when Arduino is connected

    # Serial port configuration
    arduino_port = 'COM3'  # Change this based on your setup
    baud_rate = 9600

    # Connect to Arduino
    try:
        if not st.session_state['arduino_connected']:
            st.session_state['arduino'] = serial.Serial(arduino_port, baud_rate, timeout=1)
            st.session_state['arduino_connected'] = True
            st.session_state['dummy_mode'] = False
    except serial.SerialException:
        st.session_state['dummy_mode'] = True

    st.title("📊 Real-Time Flow Sensor Data Simulation")

    # Layout design
    col1, col2 = st.columns([1, 1])

    # Dummy Mode or Real Mode Toggle
    with col1:
        mode = "Dummy" if st.session_state['dummy_mode'] else "Real"
        if st.button(f"Switch to {'Real' if st.session_state['dummy_mode'] else 'Dummy'} Mode"):
            st.session_state['dummy_mode'] = not st.session_state['dummy_mode']
            if st.session_state['dummy_mode']:
                st.write("Switched to Dummy Data Mode.")
            else:
                st.write("Switched to Real Sensor Data Mode.")

    # Pause/Resume Toggle Button
    with col2:
        button_label = '⏸ Pause' if st.session_state['running'] else '▶ Resume'
        if st.button(button_label):
            st.session_state['running'] = not st.session_state['running']  # Toggle running state
            st.write(f"{'Paused' if not st.session_state['running'] else 'Resuming...'}")

    # Export PDF Button
    if st.session_state['data']:
        if st.button('📄 Export PDF'):
            # Save chart as image
            chart_image = save_chart_as_image(st.session_state['data'])
            
            # Calculate stats and generate the PDF
            stats = calculate_stats(st.session_state['data'])
            pdf_file = generate_pdf(st.session_state['data'], stats, chart_image)
            
            # Provide download button for the PDF
            with open(pdf_file, "rb") as f:
                st.download_button('Download Report', f, file_name='flow_sensor_report.pdf')

    # Create placeholders for chart and stats
    chart_placeholder = st.empty()
    table_placeholder = st.empty()

    # Generate data if running
    if st.session_state['running']:
        if st.session_state['dummy_mode']:
            new_data = generate_dummy_data()
        else:
            new_data = read_from_arduino(st.session_state['arduino'])

        if new_data is not None:
            st.session_state['data'].append(new_data)

        # Update the line chart
        chart_placeholder.line_chart(st.session_state['data'])

        # Update stats
        stats = calculate_stats(st.session_state['data'])
        table_placeholder.table(pd.DataFrame([stats]))

        # Delay for 1 second
        time.sleep(1)

    # Show chart and stats when paused
    if not st.session_state['running']:
        if st.session_state['data']:
            # Update the line chart with saved data
            chart_placeholder.line_chart(st.session_state['data'])

            # Update stats
            stats = calculate_stats(st.session_state['data'])
            table_placeholder.table(pd.DataFrame([stats]))

if __name__ == "__main__":
    main()
