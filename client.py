import socket
import time
import os

HOST 		    = "localhost"
PORT 		    = 54321
BUFFER_SIZE 	= 1024

if __name__ == "__main__":
	clis = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		clis.connect((HOST, PORT))
		msg = clis.recv(BUFFER_SIZE)				# server busy ?
		if msg != b"OK":
			print(msg.decode())
		else:
			while True:
				filename = clis.recv(BUFFER_SIZE)
				# print(filename)
				if not filename or filename == b".":
					break
				clis.sendall(b"OK")
				print(filename.decode())
			filename = input("Choose file: ")
			clis.sendall(filename.encode())
			msg = clis.recv(BUFFER_SIZE)
			if msg != b"OK":				# allow download file ?
				print(msg.decode())
			else:
				filesize = int(clis.recv(BUFFER_SIZE).decode())
				path = input("Save file to: ")
				transfer = 0
				with open(path, "wb") as f:
					start = time.time()
					while True:
						data = clis.recv(BUFFER_SIZE)
						if not data:
							break
						f.write(data)
						clis.sendall(b"OK")
						
						transfer += len(data)
						# print(f"Received: {transfer}/{filesize}", end='\r')
					end = time.time()
					print(f"\nTime taken: {end-start:0.2f}s")
	except ConnectionRefusedError:	
		print("WARNING: server not responding")
	except KeyboardInterrupt:
		print("WARNING: keyboard interrupt")
	finally:
		clis.close()
