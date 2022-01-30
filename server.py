import socket

import tqdm

import os



SERVER_HOST = "0.0.0.0"     # device's IP address

SERVER_PORT = 5001



BUFFER_SIZE = 4096          # receive 4096 bytes each time

SEPARATOR = "<SEPARATOR>"



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # create the server socket TCP socket



s.bind((SERVER_HOST, SERVER_PORT))      # bind the socket to our local address



s.listen(5)     # enabling our server to accept connections

print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")



while True:

    client_socket, address = s.accept()     # accept connection if there is any 

    print(f"[+] {address} is connected.")   # if below code is executed, that means the sender is connected



    received = client_socket.recv(BUFFER_SIZE).decode()     # receive the file infos

    filename, filesize = received.split(SEPARATOR)

    filename = os.path.basename(filename)       # remove absolute path if there is

    filesize = int(filesize)        # convert to integer



	# start receiving the file from the socket and writing to the file stream

    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "wb") as f:

        while True:

            bytes_read = client_socket.recv(BUFFER_SIZE)    # read 1024 bytes from the socket (receive)

            if not bytes_read:    

                break       # nothing is received and file transmitting is done

            f.write(bytes_read)

            progress.update(len(bytes_read))        # update the progress bar



    client_socket.close()   # close the client socket

s.close()                   # close the server socket

