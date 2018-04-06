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
    to_hach = str(tmp[0].value) + str(tmp[1].value) + str(tmp[2].value) + str(tmp[3].value)
    to_hach = int(to_hach)
    to_hach = list(to_hach.to_bytes(math.ceil(to_hach.bit_length()/8),'big'))
    to_hach2 = to_hach[:32]
    to_send = b'\x4B' + array.array('B', to_hach2).tostring()
    for i in autre_joueurs:
        try:
            i.send(to_send)
        except Exception as e:
            autre_joueurs.remove(i)
            nb_joueurs = nb_joueurs - 1
            for x in hash_all:
                if x[0] == i:
                    hash_all.remove(x)
            pass
    elapsed = 0
    start = time.time()
    while (elapsed < 7):
        event2 = sel2.select(1)
        for key, mask in event2:
            hj = key.fileobj.recv(1024)
            if hj:
                hash_all.append((key.fileobj, hj))
        elapsed = time.time() - start
        if (len(hash_all) == len(autre_joueurs)):
            break

    if hash_all:
        k = -1
        for i in autre_joueurs:
            for x, y in hash_all:
                if i == x:
                    k = 1
            if k == 0:
                x.close()
                autre_joueurs.remove(i)
                nb_joueurs = nb_joueurs - 1
                for i, z in hash_all:
                    if i == x:
                        hash_all.remove((i, z))
    verif = b'\x56' + bytes([choix] + sequ)
    return autre_joueurs,hash_all,verif,choix,nb_joueurs


def verification(verif,autre_joueurs,choix,nb_joueurs):
    result = []
    sel3 = DefaultSelector()
    for i in autre_joueurs:
        try:
            i.send(verif)
            sel3.register(i,EVENT_READ,None)
        except Exception as e:
            print(e)
            autre_joueurs.remove(i)
            nb_joueurs = nb_joueurs - 1
            for x in hash_all:
                if x[0] == i:
                    hash_all.remove(x)
            pass

    event3 = sel3.select(1)
    while (len(result) != len(hash_all)):
        for key, mask in event3:
            try:
                to_verify = key.fileobj.recv(1024)
            except Exception as e:
                print("error recv")
                print(e)
            if to_verify:
                tmp2 = hash_data(to_verify[1:], 32)
                r = str(tmp2[0].value) + str(tmp2[1].value) + str(tmp2[2].value) + str(tmp2[3].value)
                r = int(r)
                r = list(r.to_bytes(math.ceil(r.bit_length() / 8), 'big'))
                r = r[:32]
                for x in hash_all:
                    if x[0] == key.fileobj:
                        if r != list(x[1][1:]):
                            for i in autre_joueurs:
                                if i == key.fileobj:
                                    autre_joueurs.remove(i)
                                    key.fileobj.close()
                                    nb_joueurs = nb_joueurs - 1
                                    for y, z in hash_all:
                                        if i == y:
                                            hash_all.remove((y, z))

                        else:
                            result.append([to_verify[1:2], key.fileobj, 0])

    result.append([bytes([choix]), 0, 0])
    return result,nb_joueurs

def check_result(result):
    choix = result[-1][0]
    v = 0
    if result:
        for x, j, y in result:
            if j == 0:
                continue
            if (isinstance(x, int) == 0):
                x = int.from_bytes(x, 'big')
            if (isinstance(choix, int) == 0):
                choix = int.from_bytes(choix, 'big')

            if(choix == x):
                continue
            if (choix == 0 and x == 1)or(choix == 1 and x == 2)or(choix == 2 and x == 0):
                v = v - 1
            else:
                v = v + 1

        for i, (x, j, y) in enumerate(result):
            for x2, j2, y2 in result:
                if x > x2:
                    result[i][2] = result[i][2] + 1
                elif x < x2:
                    result[i][2] = result[i][2] - 1
        return v




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

        resultat,nb_joueurs = verification(verif,autre_joueurs,choix,nb_joueurs)

        v = check_result(resultat)
        if v < 0:
            print("j'ai perdu, je sors")
            for cl in autre_joueurs:
                cl.close()
                port_game.close()
                nb_joueurs = 0
            break

        else:
            print("jai gagné je reste")
            for x, j, y in resultat:
                if y < 0:
                    if(isinstance(j,int)):
                        continue
                    j.close()
                    nb_joueurs = nb_joueurs - 1
                    for i in autre_joueurs:
                        if i == j:
                            autre_joueurs.remove(i)
                    for i, z in hash_all:
                        if i == j:
                            hash_all.remove((i, z))
