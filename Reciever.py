import socket
import json
import time
import ast

with open("r_config.json","r") as f_config:
    # Opens config json file and loads into python dictionary
    config = json.load(f_config)
    # Configuring from json
    HOST = config["ip"]
    PORT = config["port"]

with socket.socket() as s:
    # Bind socket and start listening
    s.bind((HOST, PORT))
    s.listen()
    # Accept connection, set connection object
    while True:
        conn, addr = s.accept()
        with conn:
            # Print when client connects
            print(f"{addr} Connected")
            while True:
                # Recieve data sent from client
                data = conn.recv(32768)
                # Ensure client is still sending data
                if not data:
                    print(f"{addr} Disconnected")
                    break
                # Build data from client into dictionary
                data_dict = ast.literal_eval(data.decode())
                # Write dictionary to file in human readable
                with open(f"logs/{int(time.time())}.txt", "w") as log_file:
                    for pid in data_dict:
                        log_file.write(f"{pid}: {data_dict[pid][0]}: {data_dict[pid][1]}%, {data_dict[pid][2]}B, disk_io = {data_dict[pid][3]}\n")


