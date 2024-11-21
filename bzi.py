import streamlit as st
import pyserial
import serial
import pandas as pd
import time
import os

# Streamlit App
st.title("Arduino Serial Monitor with Visualization and Logging")

# Serial Port Configurations
serial_port = st.text_input("Enter Serial Port (e.g., COM3 or /dev/ttyUSB0):", "COM3")
baud_rate = st.number_input("Enter Baud Rate:", value=9600, step=1)
connect_button = st.button("Connect to Arduino")

# File for Logging
log_data = st.checkbox("Log data to a CSV file")
log_file = "arduino_data_log.csv"

# Initialize Data Storage for Visualization
data_list = []
time_list = []

if connect_button:
    try:
        # Try initializing the serial port
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        st.success(f"Connected to {serial_port} at {baud_rate} baud.")
        
        # Display Serial Data
        st.write("Reading data from Arduino...")
        data_placeholder = st.empty()  # Placeholder to dynamically update serial data
        graph_placeholder = st.empty()  # Placeholder for the graph
        
        # Create/Append to the Log File
        if log_data:
            if not os.path.exists(log_file):
                with open(log_file, "w") as f:
                    f.write("Timestamp,Data\n")  # Write header
        
        # Real-time Reading and Visualization Loop
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode("utf-8").strip()
                timestamp = time.time()
                
                # Display Data
                data_placeholder.text(f"Serial Data: {data}")
                
                # Add Data to Lists
                try:
                    numeric_data = float(data)
                    time_list.append(timestamp)
                    data_list.append(numeric_data)
                    
                    # Update Real-time Graph
                    df = pd.DataFrame({"Time": time_list, "Data": data_list})
                    graph_placeholder.line_chart(df.set_index("Time"))
                    
                    # Log Data to CSV
                    if log_data:
                        with open(log_file, "a") as f:
                            f.write(f"{timestamp},{data}\n")
                except ValueError:
                    st.warning("Non-numeric data received. Skipping graph update.")
                
                # Small delay to prevent overloading
                time.sleep(0.1)
    
    except serial.SerialException as e:
        st.error(f"Could not open port {serial_port}. Error: {e}")
        st.stop()

    except FileNotFoundError:
        st.error(f"The port {serial_port} does not exist. Check your connection and try again.")
        st.stop()
