import threading
import socket
import sys
import cv2
import pickle
import struct ##



connections = {}
frame_number = 0
frams = []
def createAcceptingSocket():
    try:
        global host
        global port
        global s
        host = ""
        port = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket creation done")
        s.bind((host, port))
        print("Socket bind done")
        s.listen(10)
        print("Socket listen done")
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

# Establish connection with a client (socket must be listening)

def startServer():
    global frame_number
    while True:
        conn, address = s.accept()
        frame_number += 1
        print("Connection has been established! |" + " IP " + address[0] + " | Port" + str(address[1]))
        thread = threading.Thread(target = handleClient, args = (conn,))
        thread.start()
    s.close()
    sys.exit()


def handleClient(conn):
    global connections
    data = conn.recv(512)
    data = str(data)
    # data = data[5:46]
    print(data)
    info_dict = {}
    for info in data.split(","):
        splited_data = info.split(":")
        info_dict[splited_data[0]] = splited_data[1]
    connections[conn] = info_dict
    # print(connections[conn])

    #set up wanted cam info
    cam = cv2.VideoCapture(int(connections[conn]["camera"]))
    cam.set(3, int(connections[conn]["width"]))
    cam.set(4, int(connections[conn]["hight"]))
    accuricy_level = int(connections[conn]["quality"])
    ###
    img_counter = 0
    ## start streaming
    while True:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), accuricy_level]
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)
        result, frame = cv2.imencode('.jpeg', frame, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)

        print("{}: {}".format(img_counter, size))
        conn.sendall(struct.pack(">L", size) + data)
        img_counter += 1

    cam.release()
    conn.close()


if __name__=="__main__":
    createAcceptingSocket()
    startServer()