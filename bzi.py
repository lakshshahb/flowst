import serial
import serial.tools.list_ports
import time
import streamlit as st
import pandas as pd

# Function to list available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to set up serial communication with Arduino
def setup_serial(port, baudrate=9600, timeout=1):
    try:
        arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        if arduino.is_open:
            st.success(f"Successfully connected to {port}")
            return arduino
        else:
            st.error("Failed to open the selected port.")
            return None
    except serial.SerialException as e:
        st.error(f"Error opening serial port: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# Function to read data from Arduino
def read_from_arduino(arduino):
    try:
        if arduino.is_open:
            arduino_data = arduino.readline().decode('utf-8').strip()
            if arduino_data:
                return arduino_data
        else:
            st.error("Serial port is not open.")
            return None
    except serial.SerialException as e:
        st.error(f"Serial port error: {e}")
        return None
    except Exception as e:
        st.error(f"Error reading from Arduino: {e}")
        return None

# Main app function for Streamlit
def main():
    st.title("Arduino Serial Data Interceptor with Real-Time Graph")

    # Get list of available serial ports
    available_ports = get_serial_ports()

    # Check if any ports are found
    if len(available_ports) == 0:
        st.error("No available serial ports found. Please check your connections.")
        return

    # Display the available ports for selection
    st.write("Available Serial Ports:", available_ports)

    # Select port from dropdown and set baudrate
    port = st.sidebar.selectbox("Select COM Port", available_ports)
    baudrate = st.sidebar.number_input("Baudrate", value=9600, step=1)

    # Button to connect to Arduino
    if st.sidebar.button("Connect"):
        arduino = setup_serial(port=port, baudrate=baudrate)

        # Proceed if connection is successful
        if arduino:
            data_placeholder = st.empty()
            chart_placeholder = st.empty()

            # Lists to store data
            data_list = []
            time_list = []
            start_time = time.time()

            # Pause/Resume handling
            if 'paused' not in st.session_state:
                st.session_state['paused'] = False

            if st.sidebar.button("Pause" if not st.session_state['paused'] else "Resume"):
                st.session_state['paused'] = not st.session_state['paused']

            # Main loop to read data
            while True:
                # If not paused, read data from the serial port
                if not st.session_state['paused']:
                    data = read_from_arduino(arduino)
                    if data:
                        try:
                            flow_rate = float(data)
                        except ValueError:
                            st.error(f"Non-numeric data received: {data}")
                            flow_rate = None

                        if flow_rate is not None:
                            current_time = time.time() - start_time
                            data_list.append(flow_rate)
                            time_list.append(current_time)

                            # Update the display and chart
                            data_placeholder.write(f"Flow Data Received: {flow_rate} L/min")
                            chart_data = pd.DataFrame({"Time": time_list, "Flow Rate": data_list})
                            chart_placeholder.line_chart(chart_data.set_index("Time"))

                # Stop button to close connection
                if st.sidebar.button("Stop"):
                    break

                time.sleep(1)

            # Ensure the serial port is closed
            arduino.close()
            st.success("Disconnected from Arduino.")

if __name__ == "__main__":
    main()
