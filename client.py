#!/usr/bin/python3

import os
import math
import random
import time
import  array
from selectors import *
from socket import *
import struct
from hash import *

def extract_addr(tuples):
    if(tuples):
        addr = []
        for t in tuples:
            tmp = []
            ip = []
            x = t[:4]
            i = 0
            while (i < 4):
                tmp.append((x[i:i + 1]))
                i = i + 1
            for i in tmp:
                ip.append(str((struct.unpack("B", i))[0]))
        ip = ".".join(ip)
        for t in tuples:
            x = t[-2:]
            port = struct.unpack("<H",x)
            addr.append((ip,port[0]))
        return addr
    else:
        return []

def udp_msg():
    try:
        recois = socket(AF_INET,SOCK_DGRAM,0,None)
    except Exception as e:
        print(e)
        print("error recois")

    recois.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    recois.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    recois.bind(('', 7854))

    data, addr = recois.recvfrom(4)
    print("UDP msg du serveur : {x}".format(x = data))
    recois.close()
    return (data,addr)

def interact_s(myport,addr):
    tuples = []
    envois = socket()
    envois.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    envois.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    try:
        envois.connect((addr[0], 7853))
        envois.send(myport)
    except Exception as e:
        print("error connect")
        print(e)

    try:
        data2 = envois.recv(2)
    except Exception as e:
        print("error data ")
        print(e)

    for i in range(data2[1]):
        try:
            tuple = envois.recv(6)
            time.sleep(0.1)
        except Exception as e:
            print(e)
        if (tuple[-2:] != myport):
            tuples.append(tuple)

    last_msg = envois.recv(3)
    envois.close()
    return (last_msg,tuples)

def genere_joueurs(tuples,places_rest,game_sock):
    places_rest = places_rest - len(tuples) - 1
    autre_joueurs = []
    for i in tuples:
        try:
            port_game_e = socket()
            port_game_e.connect((i[0], i[1]))
            autre_joueurs.append(port_game_e)
        except Exception as e:
            print("error connect : ", end=' ')
            print((i[0], i[1]))
            print(e)
    sel = DefaultSelector()
    sel.register(game_sock, EVENT_READ, None)
    while (places_rest > 0):
        event = sel.select(1)
        for key, mask in event:
            client, adr = game_sock.accept()
            if (client not in autre_joueurs):
                autre_joueurs.append(client)
                places_rest = places_rest - 1

    return autre_joueurs

def genere_hash(autres_joueurs,nb_joueurs):
    hash_all = []
    sel2 = DefaultSelector()
    for i in autres_joueurs:
        sel2.register(i, EVENT_READ, None)
    s = (input("entrer votre choix "))
    choix = -1
    while(choix == -1):
        if(s == "pierre"):
            choix = 0
        elif(s == "feuille"):
            choix = 1
        elif(s == "ciseaux"):
            choix = 2
        else:
            print("choix possibles : [pierre , feuille , ciseaux]")
            s = (input("entrer votre choix "))
    sequ = random.sample(range(256), 31)
    tmp = [choix] + sequ
    tmp = hash_data(tmp, 32)
    to_send = struct.pack('=BQQQQ', 0x4B, tmp[0].value, tmp[1].value, tmp[2].value, tmp[3].value)
    for i in autre_joueurs:
        try:
            i.send(to_send)
        except Exception as e:
            print("ERROR")
            print(e)
            autre_joueurs.remove(i)
            nb_joueurs = nb_joueurs - 1
            for x in hash_all:
                if x[0] == i:
                    hash_all.remove(x)
            return 0
            pass
    elapsed = 0
    start = time.time()
    while (elapsed < 5):
        event2 = sel2.select(1)
        for key, mask in event2:
            hj = key.fileobj.recv(33)
            if hj:
                if hj[0]== 75:
                    hash_all.append([key.fileobj, hj])
                elif hj[0] == 86:
                    for i in hash_all:
                        if i[0] == key.fileobj:
                            i.append(hj)
        elapsed = time.time() - start
        if (len(hash_all) == len(autre_joueurs)):
            break
    if hash_all == []:
        for i in autre_joueurs:
            i.close()
            autre_joueurs.remove(i)
        return autre_joueurs, hash_all, 0, 0, 0
    if hash_all:
        k = -1
        for i in autre_joueurs:
            for x in hash_all:
                if i == x[0]:
                    k = 1
            if k == 0:
                x[0].close()
                autre_joueurs.remove(i)
                nb_joueurs = nb_joueurs - 1
                for i in hash_all:
                    if i[0] == x:
                        hash_all.remove(i)
    verif = b'\x56' + bytes([choix] + sequ)
    return autre_joueurs,hash_all,verif,choix,nb_joueurs


def verification(verif,autre_joueurs,choix,nb_joueurs,hash_all):
    ltmp = []
    result = []
    sel3 = DefaultSelector()
    for i in autre_joueurs:
        try:
            i.send(verif)
            sel3.register(i,EVENT_READ,None)
        except Exception as e:
            print("ERROR")
            print(e)
            autre_joueurs.remove(i)
            nb_joueurs = nb_joueurs - 1
            for x in hash_all:
                if x[0] == i:
                    return 0
                    hash_all.remove(x)
            pass
    while (len(result) != len(hash_all)):
        event3 = sel3.select(1)
        for key, mask in event3:
            try:
                to_verify = key.fileobj.recv(33)

            except Exception as e:
                print("error recv")
                print(e)
            if to_verify:
                if to_verify[0] == 86:
                    for i in hash_all:
                        if i[0] == key.fileobj:
                            i.append(to_verify)
        for i in hash_all:
            if(len(i)==2):
                continue
            tmp = (struct.unpack("=BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", i[2][1:]))
            tmp = [int(x) for x in tmp]
            tmp2 = hash_data(tmp, 32)
            ver = struct.pack('=QQQQ', tmp2[0].value, tmp2[1].value, tmp2[2].value, tmp2[3].value)
            if ver == i[1][1:] and tmp not in ltmp:
                result.append([tmp[0], i[0], 0])
                ltmp.append(tmp)

            elif ver != i[1][1:]:
                for k in autre_joueurs:
                    if k == i[0]:
                        autre_joueurs.remove(k)
                        i[0].close()
                        nb_joueurs = nb_joueurs - 1
                        for y in hash_all:
                            if k == y[0]:
                                hash_all.remove(y)
    result.append([choix,0, 0])
    return result,nb_joueurs


def check_result(result):
    for i in result:
        choice = i[0]
        v = 0
        for j in result:
            if (choice == 0 and j[0] == 1)or(choice == 1 and j[0] == 2)or(choice == 2 and j[0] == 0):
                v = v - 1
            elif(choice == j[0]):
                continue
            else:
                v = v + 1
        i[2] = v
    return result[-1][2],result

if __name__ == "__main__":
    data, addr = udp_msg()

    port_game = socket()
    port_game.bind(('', 0))
    port_game.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    port_game.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    port_game.listen()


    myport = struct.pack('<H', port_game.getsockname()[1])
    last_msg , tuples = interact_s(myport,addr)
    places_rest = int.from_bytes(last_msg[-1:], 'big')

    if tuples:
        tuples = extract_addr(tuples)
    autre_joueurs = genere_joueurs(tuples,places_rest,port_game)
    nb_joueurs = int.from_bytes(last_msg[-1:],'big')
    while(nb_joueurs > 1):
        autre_joueurs, hash_all,verif,choix,nb_joueurs = genere_hash(autre_joueurs,nb_joueurs)
        resultat,nb_joueurs = verification(verif,autre_joueurs,choix,nb_joueurs,hash_all)
        v,resultat = check_result(resultat)
        if v < 0:
            print("j'ai perdu, je sors")
            for cl in autre_joueurs:
                cl.close()
                port_game.close()
                nb_joueurs = 0
            break

        else:
            print("jai gagné je reste")
            for k in resultat:
                if k[2] < 0:
                    if(isinstance(k[1],int)):
                        continue
                    k[1].close()
                    nb_joueurs = nb_joueurs - 1
                    for i in autre_joueurs:
                        if i == k[1]:
                            autre_joueurs.remove(i)
                    for i in hash_all:
                        if i[0] == k[1]:
                            hash_all.remove(i)
