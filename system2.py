import socket
import os
import hashlib
import time
import datetime
ip = socket.gethostbyname(socket.gethostname())
port = 8082
sock = socket.socket()
filepath = []
version1 = []
version2 = []
hiddenfiles = ['.DS_Store']
# Efficiently Hash blocks and update the hash value
def hash_file(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()

# Returns the time since the file was last modified
def get_mod_time (filename) :
    file_mod_time = round(os.stat(filename).st_mtime)
    t = datetime.datetime.today() - datetime.timedelta(minutes=30)
    should_time = round(time.mktime(t.timetuple()))
    last_time = round((int(time.time()) - file_mod_time) / 60, 2)

    return last_time

# Returns a list of filepath of all the files in the directory
def filenames(path) :
    for item in os.listdir(path) :
        if (item not in hiddenfiles) :
            if (os.path.isfile(os.path.join(path,item))):
                filepath.append(item)
    return filepath

# Convertes a list to a string delimited by '\n'
def generate_message(file_list) :
    message = ''
    for i in range(len(file_list)) :
        temp = ''
        file = file_list[i]
        if (type(file) is tuple):
            for token in file :
                temp = temp + str(token)
                temp = temp + '\n'
        else:
            temp = temp + str(file)
            temp = temp + '\n'

        message = message + str(temp)

    return message



# Sends a version of the files present on this system
def send_version(dest):
    version_encoded = ''
    if (version2 == []) :
        version_encoded = generate_message([('EMPTY', 'EMPTY', 'EMPTY')])
    else:
        version_encoded = generate_message(version2)
    print("Sending Version 2...")
    dest.send(version_encoded.encode())

# Receives a version of the files present on the connected system
def receive_version(dest) :
    i = 0
    while (1):
        data = dest.recv(1024)
        if not data:
            break
        print('Receiving a version of files from system 1...')
        break
    clean_data = data.decode().split('\n')[:-1]
    if (clean_data[-1] == 'EMPTY'):
        clean_data = []

    while(i < len(clean_data)) :
        version1.append((clean_data[i],clean_data[i+1], clean_data[i+2]))
        i = i + 3

    print("Received Version 1 successfully!")

# Generates a list of the files this system needs to acquire from system 1
def requestfiles():
    request = []
    if (version1 == []):
        return generate_message(['EMPTY', 'EMPTY', 'EMPTY'])

    for i in range(len(version1)) :
        present = 0
        for j in range(len(version2)) :
            if (version1[i][0] == version2[j][0]) :
                present = 1
                if (version1[i][1] != version2[j][1]) :
                    if (float(version1[i][2]) <= float(version2[j][2])):
                        request.append(version1[i][0])
        if (not present) :
            request.append(version1[i][0])

    # If still no files needed, request empty
    if (request == []):
    	return generate_message(['EMPTY', 'EMPTY', 'EMPTY'])

    return generate_message(request)

# Receive the files missing in the system
def receive_files(request,system1, host):
    # No need to receive files if no request
    if (request == []):
        return 1

    # Estabilish a connection for every file it requires
    temp_port = 50000
    for i in range(len(request)):
        # Receive an acknowledgement from system1 after it makes a server
        while(1):
            data = system1.recv(1024)
            if(data != b''):
                break
        ack = data.decode()
        if (ack != "ACK") :
            print('Error')
            break
        # Send a confirmation acknowledgement
        s = socket.socket()
        s.connect((host, temp_port))
        s.send(("ACK").encode())
        # Receive files
        with open(request[i], 'wb') as f:
            while True:
                print('receiving file : ', request[i])
                data = s.recv(1024)
                if not data:
                    break
                # write data to a file
                f.write(data)

        f.close()
        s.close()
        print('file received: ',request[i])
        temp_port = temp_port + 1

# Receive the request of files from system 1
def get_request(system1):
    data = (system1.recv(1024))
    requested = data.decode().split('\n')[:-1]
    if (requested == ['EMPTY', 'EMPTY', 'EMPTY']):
        requested = []
    print("Received request: ", requested)

    return requested

# Send the files requested by system 1
def send_files(requested, system1, ip, temp_port):

    for i in range(len(requested)) :

        # Create a server for sending each file requested
        s = socket.socket()
        s.bind(('', temp_port))
        s.listen(5)

        system1.send(("ACK").encode())

        conn, addr = s.accept()
        data = conn.recv(1024)
        filename = requested[i]
        print('Sending file : ', requested[i])
        f = open(filename,'rb')
        l = f.read(1024)
        while (l):
            conn.send(l)
            l = f.read(1024)
        f.close()

        print('Done sending')
        conn.close()
        temp_port = temp_port + 1

def main():

    path = str(input("Enter path of directory >> "))
    if not os.path.exists(path) :
        print("Invalid path entered")
        exit(0)
    filenames(path)
    for file in filepath :
        version2.append((file, hash_file(os.path.join(path,file)), get_mod_time(os.path.join(path,file))))

    dest_ip = str(input("Enter the IP Address of System 1 >> "))

    # Connect to system1
    system1 = socket.socket()
    system1.connect((dest_ip, port))
    print("Connected to : ",dest_ip)

    # Receive a version of the files on system 1
    receive_version(system1)

    # Send a version of your files to system 1
    send_version(system1)

    # Receive the requirement of system 1
    requested = get_request(system1)
    for i in range(len(requested)):
    	requested[i] = os.path.join(path,requested[i])

    # Send files
    send_files(requested, system1, ip, 5000)

    # Generate the path of the required files
    request_encoded = requestfiles()
    request = request_encoded.split('\n')[:-1]
    if (request == ['EMPTY', 'EMPTY', 'EMPTY']):
        request = []
    for i in range(len(request)) :
    	request[i] = os.path.join(path,request[i])

    # Send the requested files
    system1.send(request_encoded.encode())

    # Receive the files requested
    receive_files(request, system1, dest_ip)

    print("Files synced")
    system1.close()
    
if __name__ == '__main__':
    main()