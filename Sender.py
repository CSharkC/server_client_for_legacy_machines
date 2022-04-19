import socket
import json
import psutil
import time
import os

def ps_collect():
    """function to collect process information"""
    process_dict = {}
    # Itterate over all system PIDs
    for pid in psutil.pids():
        # Sanity check, make sure process hasn't closed
        if psutil.pid_exists(pid):
            # Create process object with PID
            process = psutil.Process(pid)
            try:
                # Collect process data and add to dictionary
                process_dict[pid] = process.name(), process.cpu_percent(interval=0.1), process.memory_info().rss, process.io_counters()
            except (psutil.NoSuchProcess, ProcessLookupError, psutil.AccessDenied):
                pass
    # Return all processes
    return process_dict

def sender():
    """main sender function"""
    with open("s_config.json","r") as f_config:
        # Opens config json file and loads into python dictionary
        config = json.load(f_config)
        HOST = config["ip"]
        PORT = config["port"]

    with socket.socket() as s:

        # Connect to the server
        s.connect((HOST, PORT))
        while True:
            # Menu Mode Selection
            print("Menu:\n 1: Run Single Process Grab\n 2: Main Continuous Mode\n 3:Testing Mode\n exit: Close Connection")
            menu_opt = input("Menu Option: ")

            if menu_opt == "1": # Run Single Process Grab

                data = ps_collect()
                data_json = json.dumps(data)
                print("collected")
                s.sendall(bytes(data_json, encoding="utf-8"))
                print("done")

            elif menu_opt == "2": # Main Continuous Mode

                while True: # Get delay from user and check it can be a float
                    delay = input("Delay (seconds): ")
                    try:
                        float(delay)
                        break
                    except ValueError:
                        pass

                while True:
                    # Collect Process Data
                    data = ps_collect()
                    # Format data into JSON format and send to server
                    data_json = json.dumps(data)
                    s.sendall(bytes(data_json, encoding="utf-8"))
                    print("Completed and Sent")
                    # Delay until next execution
                    time.sleep(float(delay))
            
            elif menu_opt == "3": # Testing Mode

                while True: # Get delay from user and check it can be a float
                    delay = input("Delay (seconds): ")
                    try:
                        float(delay)
                        break
                    except ValueError:
                        pass

                # Collect Process information about running script
                py_process = psutil.Process(os.getpid())
                        
                # Setup option to run for a given amount of time (5 minutes)
                start_time = time.time()
                counter = 0
                while time.time() < start_time + 30:
                    py_process.cpu_percent() # Record average use between this and next call
                    # Collect Process Data
                    data = ps_collect()
                    # Format data into JSON format and send to server
                    data_json = json.dumps(data)
                    s.sendall(bytes(data_json, encoding="utf-8"))
                    # Delay until next execution
                    time.sleep(float(delay))
                    counter += 1
                    print(f"Completed {counter} requests, {py_process.cpu_percent()}% CPU Usage")
            
            elif menu_opt == "exit": #Close Connection
                s.close()
                break

if __name__ == "__main__":
    sender()