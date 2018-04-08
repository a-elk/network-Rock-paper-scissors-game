#!/usr/bin/python3
import time
from socket import *
from selectors import *

if __name__ == "__main__":

    nb_place_rest = int(input("choisissez nombre de joueurs "))
    nb_place_joint = 0
    envois = socket(AF_INET, SOCK_DGRAM)               # UDP socket
    envois.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    envois.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    ecoute = socket()                                  # TCP socket
    ecoute.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    ecoute.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ecoute.bind(('0.0.0.0', 7853))
    ecoute.listen()
    mysel = DefaultSelector()
    mysel.register(ecoute, EVENT_READ, None)

    tuples_cl = []
    client_recu = []                                   #listes des clients recus

    while(nb_place_rest):
        print("broadcast")
        envois.sendto(b'\x44\x49\x53' + bytes([nb_place_rest]), ('255.255.255.255', 7854))  # broadcast
        events = mysel.select(1)
        for key,mask in events:
            try:
                client, addr = key.fileobj.accept()                  #ajout de client
            except Exception as e:
                print(e)
                print("error ecoute")
            try:
                client.send(b'\x43' + bytes([nb_place_joint]))
            except Exception as e:
                print("error send place joint")
                print(e)
            try:
                port_cl = client.recv(1024)
            except Exception as e:
                print("error recv")
                print(e)
            if client not in client_recu:
                client_recu.append(client)
                nb_place_rest = nb_place_rest -1
                nb_place_joint = nb_place_joint + 1

            for x in tuples_cl:
                if type(x[1]) is not bytes:
                    x[1] = bytes(map(int,x[1].split('.')))
                try:
                    p = x[1] + x[0]
                    client.send(p)
                except Exception as e:
                    print("error send tuple")
                    print(e)
            print("addr : {x}".format(x = client.getsockname()[0]))
            tuples_cl.append([port_cl, client.getpeername()[0]])

        print("place rest : " + str(nb_place_rest))
        if(nb_place_rest == 0):
            for cl in client_recu:
                cl.send(b'\x4f\x4b' + bytes([nb_place_joint]))
                cl.close()
            ecoute.close()
            envois.close()
            break
















