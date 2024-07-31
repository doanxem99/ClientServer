import socket
import threading
import os

HOST 		    = ""
PORT 		    = 54321
BUFFER_SIZE 	= 1024
MAX_USER	    = 1
DIR		        = "./files/"

def send_file(clis, addr):
	filenames = [f for f in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, f)) ]
	for filename in filenames:
		clis.sendall(filename.encode())
		if len(clis.recv(BUFFER_SIZE)) == 0:
			print("ERROR: client not responding")
			break
	clis.sendall(b".")                          # stop list filenames
	filename = clis.recv(BUFFER_SIZE).decode()
	try:
		try:
            print(f"[!] {addr} requested to download \"{filename}\"")
			filename = os.path.join(DIR, filename)
			with open(filename, "rb") as f:
				clis.sendall(b"OK")
				filesize = os.path.getsize(filename)
				clis.sendall(str(filesize).encode())
				
				while True:
					data = f.read(BUFFER_SIZE)
					if not data:
						break
					clis.sendall(data)
					if len(clis.recv(BUFFER_SIZE)) == 0:
						print("ERROR: client not responding")
						break
		except Exception as e:
			clis.sendall(str(e).encode())
	except BrokenPipeError:
		print("ERROR: broken pipe")
	except Exception as e:
		clis.sendall(str(e).encode())
	finally:
		print(f"[-] {addr} disconnected")
		clis.close()


if __name__ == "__main__":
	if not os.path.isdir(DIR):
		os.makedirs(DIR)
	busy = True
	sers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sers.bind((HOST, PORT))
	sers.listen()
	
	threads = [None] * MAX_USER

	try:
		while True:
			clis, addr = sers.accept()
			first_not_busy = -1
			for (i, thread) in enumerate(threads):
				if (thread == None) or (type(thread) is threading.Thread and not thread.is_alive()):
					first_not_busy = i
					break
			if first_not_busy == -1:
				clis.sendall(b"WARNING: the server is currently full")
				clis.close()
				continue

			clis.sendall(b"OK")
			print(f"[+] {addr} connected")
			threads[first_not_busy] = threading.Thread(target=send_file, args=(clis, addr, ))
			threads[first_not_busy].start()
	except KeyboardInterrupt:
		print("Interrupt")
	finally:
		for thread in threads:
			if thread != None:
				thread.join()

		print("close socket")
		sers.close()
