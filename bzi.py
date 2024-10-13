import serial
import time
import streamlit as st
import pandas as pd
import serial.tools.list_ports
import matplotlib.pyplot as plt

# Function to get available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to set up serial communication with Arduino
def setup_serial(port='COM8', baudrate=9600, timeout=1):
    try:
        return serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
    except Exception as e:
        st.error(f"Error opening serial port: {e}")
        return None

# Function to read data from Arduino
def read_from_arduino(arduino):
    try:
        arduino_data = arduino.readline().decode('utf-8').strip()
        if arduino_data:
            return arduino_data
    except Exception as e:
        st.error(f"Error reading from Arduino: {e}")
        return None

# Function to plot the data
def plot_data(time_list, liter_per_hour_list, rps_list):
    plt.figure(figsize=(10, 5))
    plt.plot(time_list, liter_per_hour_list, label='Flow Rate (L/h)', color='blue')
    plt.plot(time_list, rps_list, label='Rotations (RPS)', color='orange')
    plt.xlabel("Time (s)")
    plt.ylabel("Values")
    plt.title("Flow Rate and Rotations Over Time")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    st.pyplot(plt)

# Initialize Streamlit app
def main():
    # Streamlit layout
    st.title("Flow Sensor Data Reader")
    st.write("This app reads flow rate data from an Arduino connected to a flow sensor.")

    # Get available serial ports
    available_ports = get_serial_ports()
    selected_port = st.selectbox("Select Serial Port", available_ports)

    # Set up serial connection
    arduino = setup_serial(port=selected_port, baudrate=9600)  # Use selected port
    if not arduino:
        st.stop()  # Stop the app if no serial connection is available

    # Initialize empty lists for storing data
    liter_per_hour_list = []
    rps_list = []
    time_list = []
    start_time = time.time()

    # Create a button to start data collection
    if st.button("Start Reading Data"):
        # Start reading data
        while True:
            # Read data from Arduino
            data = read_from_arduino(arduino)
            
            if data:
                # Expecting data format: "Flow rate: <value> L/h"
                try:
                    flow_rate_str = data.split("Flow rate: ")[1].split(" L/h")[0]
                    liter_per_hour = float(flow_rate_str)
                except (IndexError, ValueError):
                    liter_per_hour = None
                
                # Update the time and data lists
                current_time = time.time() - start_time
                if liter_per_hour is not None:
                    liter_per_hour_list.append(liter_per_hour)
                    rps = liter_per_hour / 60.0  # Example calculation for RPS
                    rps_list.append(rps)
                    time_list.append(current_time)

                    # Display the latest readings
                    st.write(f"Flow Rate: {liter_per_hour:.2f} L/h | Rotations: {rps:.2f} RPS")

                    # Plot the data
                    plot_data(time_list, liter_per_hour_list, rps_list)

            # Delay between reads
            time.sleep(1)

if __name__ == "__main__":
    main()
