import serial
import serial.tools.list_ports
import time
import streamlit as st
import pandas as pd

# 1. Function to list available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# 2. Function to set up serial communication with Arduino (with increased timeout, debugging, and manual port option)
def setup_serial(port, baudrate=9600, timeout=5):  # Option 4: Increased timeout
    st.write(f"Attempting to connect to {port} with baudrate {baudrate} and timeout {timeout}")
    try:
        arduino = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        st.write(f"Port is open: {arduino.is_open}")
        if arduino.is_open:
            st.success(f"Successfully connected to {port}")
            return arduino
    except serial.SerialException as e:
        st.error(f"Error opening serial port: {e}. Check if the port is being used by another application.")  # Option 6: More detailed error handling
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None

# 3. Function to read data from Arduino with more detailed error messages
def read_from_arduino(arduino):
    if not arduino.is_open:
        st.error("Attempting to use a port that is not open.")  # Option 5: Check if the port is open
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

    # 4. Get list of available serial ports
    available_ports = get_serial_ports()
    
    # Check if any ports are found
    if len(available_ports) == 0:
        st.error("No available serial ports found. Please check your connections.")
    else:
        # 5. Display available ports with manual port entry option
        st.write("Available Serial Ports:", available_ports)
        
        # Allow user to manually select port from dropdown
        port = st.sidebar.selectbox("Select COM Port", available_ports)
        
        # Manual port entry option in case the dropdown doesn't show correct ports
        manual_port = st.sidebar.text_input("Or manually enter COM Port (e.g., COM3 or /dev/ttyUSB0)", "")
        if manual_port:
            port = manual_port

        baudrate = st.sidebar.number_input("Baudrate", 9600)
        
        # Button to connect to Arduino
        if st.sidebar.button("Connect"):
            arduino = setup_serial(port=port, baudrate=baudrate)

            # If connection is successful, proceed
            if arduino:
                data_placeholder = st.empty()
                chart_placeholder = st.empty()

                data_list = []
                time_list = []
                start_time = time.time()

                # 6. Ensure pause functionality
                if 'paused' not in st.session_state:
                    st.session_state['paused'] = False

                if st.sidebar.button("Pause" if not st.session_state['paused'] else "Resume"):
                    st.session_state['paused'] = not st.session_state['paused']

                # Main loop to read data
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

                arduino.close()  # Ensure the serial port is properly closed
                st.success("Disconnected from Arduino.")

if __name__ == "__main__":
    main()
