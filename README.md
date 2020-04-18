# syncfiles

The following project aims at syncing files between two systems. This works on a client server model, where the server (here system1) initiates the sync process and the client (here system2) syncs with the server.

The idea behind syncing is both the systems maintain a version of the files in their respective directories. A version for a file is a tuple of the file name, its sha-256 hash value and the time since it was modified. Both the systems exchange their versions. Based on which file needs to be updated, both systems communicate orderly to obtain the file they need as well as to provide the file the other system requires. Consequently, both folders become in sync.

## Getting Started

The repository contains two folders namely folder1 and folder2.

folder1 has the following files: helloworld.py, post_to_irc.sh, tcpserver.py
folder2 has the following files: helloworld.py, tcpclient.py

The file helloworld.py was modified latest in folder1.
Thus when we sync these two folders, each folder should get the following files:
helloworld.py, post_to_irc.sh, tcpclient.py, tcpserver.py
The contents of helloworld.py should be the one of folder1.

Run the following steps to perform this test.

### Installation


Clone the repository to the systems that want to sync

```
$ git clone https://theharshyadav@bitbucket.org/theharshyadav/syncfiles.git
```

Navigate to enter the directory syncfiles

```
$ cd syncfiles
```

On one of the systems, run the following:

```
$ python system1.py
Enter path of directory >> folder1
```

On the other system, run the following

```
$ python system2.py
Enter path of directory >> folder2
Enter the IP Address of System 1 >> 
```

Enter the IP Address of System 1 when prompted.

After the programs have executed. Look in the folders to find the sync performed.

## Algorithm

1. System 1 creates a server.
2. System 2 becomes a client to the server using the IP Address provided by the user.
3. Each system generates a version of the files present in their respective directories.
4. System 1 encodes its version and sends it to System 2
5. Upon receiving Version 1 of System 1, System 2 encodes its version and sends it to System 1.
5. Both system compare their versions with the version they received as under:
		1. Does this system have the file named in the other system?
		2. Does the sha-256 hash of the files match? If not, which file was modified the latest?
6. Based on these comparision, each system finds out which file it needs to receive.
7. System 1 first sends a request of all the files it needs.
8. For every file needed by System 1, System 2 creates a server and sends the content of that file over that channel.
9. System 2 sends a request of all the files it needs.
10. For every file needed by System 2, System 1 creates a server and sends the content of that file over that channel.
