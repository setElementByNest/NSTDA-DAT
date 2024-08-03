import esptool
import sys
from io import StringIO
import contextlib
import readchar
import serial.tools.list_ports
import requests

def save_data(mac_address):
    response = input("Do you want to save? (Y/n): ").strip().lower()
    if response == 'y' or response == '':
        print("Data saving...")
        data = {
            mac_address: {
                "id": mac_address,
                "detail": ""
            }
        }
        url = "https://vercel-api-three-pied.vercel.app/data"
        try:
            result = requests.post(url, json=data)
            if result.status_code == 200:
                print("Data saved successfully.")
            else:
                print(f"Status code: {result.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    else:
        print("Data not saved.")

def list_com_ports():
    datacom = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        datacom.append(port.device)
    return datacom


def print_options(options, selected_index):
    for i, option in enumerate(options):
        if i == selected_index:
            print(f"> {option}")
        else:
            print(f"  {option}")

def get_mac_address(port, baud):
    sys.argv = ['esptool', '--port', port, '--baud', str(baud), 'read_mac']

    # Capture the output of esptool
    with contextlib.redirect_stdout(StringIO()) as f:
        try:
            esptool.main()
        except SystemExit:
            pass  # esptool.main() calls sys.exit(), which we want to ignore

    output = f.getvalue()

    # Parse the MAC address from the output
    for line in output.splitlines():
        if "MAC" in line:
            return line.split(': ')[1]

    raise Exception("Failed to find MAC address in esptool output")

if __name__ == "__main__":
    bool_main_loop = True
    while bool_main_loop:
        bool_main_skip = False
        datacom = list_com_ports()

        options = datacom + ["Refresh", "Cancel"]
        selected_index = 0

        print("\033c", end="")  # Clear the screen

        while True:
            print("Please select your com port.")
            print_options(options, selected_index)
            key = readchar.readkey()
            
            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == '\r':  # Enter key
                if options[selected_index] == "Refresh":
                    print("Operation restarted.")
                    bool_main_skip = True
                elif options[selected_index] == "Cancel":
                    print("Operation cancelled.")
                    sys.exit(0)  # End the script
                break
            
            print("\033c", end="")  # Clear the screen
        if not bool_main_skip:
            print(f"You selected: {options[selected_index]}")
            port = options[selected_index]
            baud = 115200

            try:
                mac_address = get_mac_address(port, baud)
                print(f"ESP32 MAC Address: {mac_address}")
                save_data(mac_address)
                response = input("Do you want to restart? (Y/n): ").strip().lower()
                if response == 'n':
                    sys.exit(0)
            except Exception as e:
                print(f"Failed to get MAC address: {e}", file=sys.stderr)
                response = input("Do you want to restart? (Y/n): ").strip().lower()
                if response == 'n':
                    sys.exit(0)
