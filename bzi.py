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
            st.error("Port is not open")
    except serial.SerialException as e:
        st.error(f"Error opening serial port: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None

# Function to read data from Arduino
def read_from_arduino(arduino):
    if not arduino.is_open:
        st.error("Attempting to use a port that is not open.")
        return None

    try:
        arduino_data = arduino.readline().decode('utf-8').strip()
        if arduino_data:
            return arduino_data
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
        # Allow manual input if no ports are detected
        port = st.sidebar.text_input("Enter COM Port manually", "")
    else:
        # Display the available ports in a selectbox
        port = st.sidebar.selectbox("Select COM Port", available_ports)

    # Get baudrate input
    baudrate = st.sidebar.number_input("Baudrate", 9600)

    # Button to connect to Arduino
    if st.sidebar.button("Connect"):
        if port:
            arduino = setup_serial(port=port, baudrate=baudrate)
            if arduino:
                data_placeholder = st.empty()
                chart_placeholder = st.empty()

                data_list = []
                time_list = []
                start_time = time.time()

                if 'paused' not in st.session_state:
                    st.session_state['paused'] = False

                if st.sidebar.button("Pause" if not st.session_state['paused'] else "Resume"):
                    st.session_state['paused'] = not st.session_state['paused']

                while True:
                    if not st.session_state['paused']:
                        data = read_from_arduino(arduino)
                        if data:
                            try:
                                flow_rate = float(data)
                            except ValueError:
                                flow_rate = None

                            if flow_rate is not None:
                                current_time = time.time() - start_time
                                data_list.append(flow_rate)
                                time_list.append(current_time)

                                data_placeholder.write(f"Flow Data Received: {flow_rate} L/min")
                                chart_data = pd.DataFrame({"Time": time_list, "Flow Rate": data_list})
                                chart_placeholder.line_chart(chart_data.set_index("Time"))

                    stop = st.sidebar.button("Stop")
                    if stop:
                        break

                    time.sleep(1)

                arduino.close()
                st.success("Disconnected from Arduino.")
        else:
            st.error("Please select or enter a valid COM port.")

if __name__ == "__main__":
    main()
