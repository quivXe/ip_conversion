def dec_to_bin(num):
    num = int(num)
    _bin = ''
    while num != 0:
        if num % 2 == 0:
            _bin += '0'
            num = int(num/2)
        elif num % 2 == 1:
            _bin += '1'
            num = int(num/2)

    while len(_bin) < 8:
        _bin = _bin + '0'

    return _bin[::-1]


def bin_to_dec(num):
    num = str(num)
    num = num[::-1]
    dec = 0
    for i in range(len(num)):
        if num[i] == '1':
            n = 2**i
            dec += n

    return dec


def ip_to_bin_ip(ip):
    ip_bin = []
    for obj in ip:
        ip_bin.append(dec_to_bin(obj))

    return ip_bin


def bin_to_ip(ip_bin):
    ip = []
    for obj in ip_bin:
        ip.append(bin_to_dec(obj))

    return ip


def list_to_ip(lista):
    ip = ''
    for oktet in lista:
        ip += str(oktet) + '.'

    ip = ip[:-1]
    return ip


def ip_to_lista(ip):
    ip_l = []
    tmp = ''
    for let in ip:
        if let != '.':
            tmp += let
        else:
            ip_l.append(tmp)
            tmp = ''
    ip_l.append(tmp)
    return ip_l


def adres_sieci(ip, maska):
    ip = ip_to_bin_ip(ip)
    maska = ip_to_bin_ip(maska)
    ip_sieci = []

    for i in range(4):
        ip_oktet = ip[i]
        maska_oktet = maska[i]
        adres_sieci_oktet = ''

        for i1 in range(8):
            ip_num = ip_oktet[i1]
            maska_num = maska_oktet[i1]

            if maska_num == '1' and ip_num == '1':
                adres_sieci_oktet += '1'
            else:
                adres_sieci_oktet += '0'

        ip_sieci.append(bin_to_dec(adres_sieci_oktet))

    return ip_sieci


def adres_rozgloszeniowy(ip, maska):
    ip = ip_to_bin_ip(ip)
    maska = ip_to_bin_ip(maska)
    ip_rozgl = []

    for i in range(4):
        ip_oktet = ip[i]
        maska_oktet = maska[i]
        ip_rozgl_oktet = ''

        for i1 in range(8):
            ip_num = ip_oktet[i1]
            maska_num = maska_oktet[i1]

            if maska_num == '1':
                ip_rozgl_oktet += ip_num
            elif maska_num == '0':
                ip_rozgl_oktet += '1'

        ip_rozgl.append(bin_to_dec(ip_rozgl_oktet))

    return ip_rozgl


def maska_to_skrot(maska):
    maska = ip_to_bin_ip(maska)
    n = 0

    for oktet in maska:
        for cyfra in oktet:
            if cyfra == '1':
                n += 1
            elif cyfra == '0':
                break

    return n


def skrot_to_maska(skrot):
    skrot = int(skrot)
    tmp = ''
    for i in range(skrot):
        tmp += '1'
    while len(tmp) < 32:
        tmp += '0'

    ip = [tmp[0:8], tmp[8:16], tmp[16:24], tmp[24:32]]

    return bin_to_ip(ip)


def liczba_hostow(maska):
    n = maska_to_skrot(maska)
    return (2 ** (32-n)) - 2


def min_max_host(ip, maska):
    ip_siec = adres_sieci(ip, maska)
    ip_broadcast = adres_rozgloszeniowy(ip, maska)

    ip_siec[3] += 1
    ip_broadcast[3] -= 1
    return ip_siec, ip_broadcast


def przydzielanie_podsieci_hostom(hosty):
    hosty.sort(reverse=True)
    maski = []
    for host in hosty:
        n = 0
        while (2**n)-2 < host:
            n += 1

        maska = skrot_to_maska(32-n)
        maski.append((maska))

    return maski


def przydzielanie_ip_maskom(ip, maski):
    lista_ip = []
    # tworzenie pierwszego broadcastu zeby zaczac petle (tbh mozna bylo dac to do petli w/e)
    ip_sieci = adres_sieci(ip, maski[0])
    ip_broadcast = adres_rozgloszeniowy(ip, maski[0])

    lista_ip.append((ip_sieci))
    for maska in maski[1:]:
        # jezeli broadcast nie konczy sie na 255 (jezeli sie konczy nie mozna dodac po prostu 1 do adresu sieci)
        if ip_broadcast[3] != 255:
            ip_broadcast[3] += 1
            ip_sieci = ip_broadcast
            ip_broadcast = adres_rozgloszeniowy(ip_sieci, maska)

        # jezeli konczy sie na 255
        elif ip_broadcast[3] == 255:
            # jezeli nie jest x.x.255.255
            if ip_broadcast[2] != 255:
                ip_broadcast[2] += 1
                ip_broadcast[3] = 0
                ip_sieci = ip_broadcast
                ip_broadcast = adres_rozgloszeniowy(ip_sieci, maska)
                print('x')

            # jezeli jest x.x.255.255
            elif ip_broadcast[2] == 255:
                print('xx')
                # jezeli nie jest x.255.255.255
                if ip_broadcast[1] != 255:
                    ip_broadcast[1] += 1
                    ip_broadcast[2] = 0
                    ip_broadcast[3] = 0
                    ip_sieci = ip_broadcast
                    ip_broadcast = adres_rozgloszeniowy(ip_sieci, maska)

                # jezeli jest x.255.255.255
                elif ip_broadcast[1] == 255:
                    ip_broadcast[0] += 1
                    ip_broadcast[1] = 0
                    ip_broadcast[2] = 0
                    ip_broadcast[3] = 0
                    ip_sieci = ip_broadcast
                    ip_broadcast = adres_rozgloszeniowy(ip_sieci, ip_broadcast)

        lista_ip.append(ip_sieci)

    return lista_ip


def przydzielanie_hostow_info(hosty, maski, ip_lista):
    tabela = [['liczba hostów', 'IP podsieci', 'IP broadcast', 'maska', 'hosty maski',
               'host min', 'host max']]
    for i in range(len(hosty)):
        host = hosty[i]
        ip = ip_lista[i]
        maska = maski[i]

        broadcast = adres_rozgloszeniowy(ip, maska)
        skrot = ' /' + str(maska_to_skrot(maska))
        l_hostow = liczba_hostow(maska)
        min_host, max_host = min_max_host(ip, maska)

        ip = list_to_ip(ip)
        maska = list_to_ip(maska)
        broadcast = list_to_ip(broadcast)
        min_host, max_host = list_to_ip(min_host), list_to_ip(max_host)

        tabela.append([str(host), str(ip), str(broadcast), str(maska) + str(skrot), str(l_hostow),
                       str(min_host), str(max_host)])

    return tabela


def podstawowe_info(ip, maska):
    tabela = []

    siec = adres_sieci(ip, maska)
    broadcast = adres_rozgloszeniowy(ip, maska)
    hosty = liczba_hostow(maska)
    minh, maxh = min_max_host(ip, maska)
    ip = list_to_ip(ip)
    maska = list_to_ip(maska)

    tabela.append(['IP', str(ip)])
    tabela.append(['maska', str(maska)])
    tabela.append('======')
    tabela.append(['IP sieci', list_to_ip(siec)])
    tabela.append(['IP broadcast', list_to_ip(broadcast)])
    tabela.append(['hosty', str(hosty)])
    tabela.append(['min host', list_to_ip(minh)])
    tabela.append(['max host', list_to_ip(maxh)])

    return tabela


def tworzenie_tabelki(row_l):
    # dla kazdej instniejacej kolumny
    col_l = []
    for i in range(len(row_l[0])):
        col = []
        # dla kazdego wiersza
        for row in row_l:
            col.append(row[i])

        col_l.append(col)

    # dla kazdej kolumny
    for col in col_l:
        # najdluzszy znak w kolumnie
        width = max((obj for obj in col), key=len)
        width = len(width)

        # dodaje dla kazdejego wyrazu w kolumnie padding
        for i in range(len(col)):
            obj = col[i]
            obj = '  ' + obj.ljust(width) + '  |'
            col[i] = obj

    # dla kazdego mozliwego wiersza
    row_l = []
    for i in range(len(col)):
        row = []
        # dla kazdej kolumny
        for col in col_l:
            row.append(col[i])

        row_l.append(row)

    print('\n\n')
    for row in row_l:
        print(''.join(row))


def czy_ip_jest_poprawne(ip):
    for oktet in ip:
        oktet = int(oktet)
        if oktet > 255:
            return False
    return True


def funkcje():
    while True:
        wybor = input('\nWcisnij 1 żeby przekonwertować IP (maski rowniez) na binarna wersje\n'
                      '2 żeby przekonwertować binarna wersje IP na normalna\n'
                      '3 żeby wyświetlić info o IP np jakie IP sieci, jaki broadcast, ile hostow itp\n'
                      '4 żeby przydzielić urządzeniom podsieci i całe info np IP broadcast host min i max itppp\n'
                      'lub exit zeby wyjsc\n')
    # '5 żeby wyświetlić wszystkie dostepne maski z info o nich (np ile hostow itp)\n')

        # IP to BIN
        if wybor == '1':
            print('Wpisz exit zeby wyjsc z petli')
            while True:
                ip = input('\nPodaj IP ')
                if ip == 'exit': break  # jezeli exit to wyjdz
                ip = ip_to_lista(ip)    # tworzenie listy z ip
                if czy_ip_jest_poprawne(ip):    # jezeli ip jest poprawne
                    ip_bin = list_to_ip(ip_to_bin_ip(ip))  # czytelne ip bin
                    ip = list_to_ip(ip)     # czytelne ip
                    print('{} - {}'.format(ip, ip_bin))     # wypisanie
                # jezeli niepoprawne
                else: print('IP niepoprawne')

        # BIN to IP
        elif wybor == '2':
            print('Wpisz exit zeby wyjsc z petli')
            while True:
                permisison = True   # do sprawdzania czy sa inee znaki niz . 0 1
                ip = input('\nPodaj IP binarnie ')
                if ip == 'exit': break  # wyjscie
                for num in ip:  # sprawdza czy co innego niz . 0 1
                    if num != '1' and num != '0' and num != '.': permisison = False
                ip = ip_to_lista(ip)    # tworzenie listy ip
                if czy_ip_jest_poprawne(bin_to_ip(ip)) and permisison:  # jezeli poprawne wszystko
                    ip_ = list_to_ip(bin_to_ip(ip))     # tworzenie czytelnego ip
                    bin_ip = list_to_ip(ip)     # tworzenie czytelnego bin ip
                    print('{} - {}'.format(bin_ip, ip_))
                # jezeli niepoprawne
                else: print('IP niepoprawne')

        elif wybor == '3':
            print('Wpisz exit zeby wyjsc z petli')
            while True:
                ip = input('\nPodaj IP ')
                if ip == 'exit': break  # wyjscie
                maska = input('Podaj maske ')
                ip, maska = ip_to_lista(ip), ip_to_lista(maska)   # tworzenie listy
                if maska == 'exit': break   # wyjscie
                if czy_ip_jest_poprawne(ip) and czy_ip_jest_poprawne(maska):    # jezeli poprawne wszystko
                    info = podstawowe_info(ip, maska)
                    tworzenie_tabelki(info)  # stworz tabelke
                # jezeli niepoprawne
                else: print('Niepoprawne ip lub maska')
        # CALA TA FUKNCJA DO ZMIANY I WARTOSCI ZWRACANE PRZEZ FUNKCJE UNORMOWAC NP ZEBY ZAWSZE LISTE ZWRACALY ITP
        elif wybor == '4':
            print('Wpisz exit zeby wyjsc')
            while True:
                ip = input('\nPodaj IP ')
                if ip == 'exit': break   # wyjscie
                maska = input('Podaj maske ')
                if maska == 'exit': break   # wyjscie
                ip, maska = ip_to_lista(ip), ip_to_lista(maska)
                if not czy_ip_jest_poprawne(ip) or not czy_ip_jest_poprawne(maska):     # czy ip i maska poprawne
                    print('Niepoprawne IP lub maska')
                    continue
                try:
                    n = int(input('Ile ma być podsieci '))
                    urzadzenia = []
                    for i in range(n):  # petla na wszystkie podsieci
                        urzadzenia.append(int(input('Podaj {} urządzenie'.format(i+1))))
                # blad gdy uzytkownik nie podal int
                except:
                    print('Prosze podac poprawna liczbe')
                    continue
                wszystkie_maski = przydzielanie_podsieci_hostom(urzadzenia)
                info = przydzielanie_hostow_info(urzadzenia, wszystkie_maski, ip)
                tworzenie_tabelki(info)

        elif wybor == 'exit': break
        else: print('Podano nieprawidlowa liczbe')


print('Siema tutaj obliczę dla ciebie co chcesz')
print('Włącz fullscreena bo tabelki nie beda sie cale wyswietlac i bedzie nieczytelnie ;0\n')

funkcje()

#
#
#
#
#
#
#
#
# print(adres_sieci(ip, mask))
# print(adres_rozgloszeniowy(ip, mask))
# print('/{}'.format(maska_to_skrot(mask)))
# print(liczba_hostow(mask))
# print(min_max_host(ip, mask)[0], '-', min_max_host(ip, mask)[1])
# print('aaa')
# print(skrot_to_maska(3))
#
# print('MASKI')
# urzadzenia = [1600, 500, 550, 200, 2]
# ipp = [192, 168, 1, 0]
# ipp = (255, 100, 255, 245)
# print(przydzielanie_podsieci_hostom(urzadzenia))
# maskii = przydzielanie_podsieci_hostom(urzadzenia)
# ippp = przydzielanie_ip_maskom(ipp, maskii)
# print(przydzielanie_ip_maskom((255, 100, 255, 245), przydzielanie_podsieci_hostom(urzadzenia)))
#
# print('\n\n\n\n')
# tabela = przydzielanie_hostow_info(urzadzenia, maskii, ippp)
# tworzenie_tabelki(tabela)
#
# """
# adres IP	192.168.245.10	11000000.10101000.1 1110101.00001010	sieć prywatna RFC1918
# maska	255.255.128.0 = 17	11111111.11111111.1 0000000.00000000
# adres sieci	192.168.128.0/17	11000000.10101000.1 0000000.00000000	stara klasa C
# adres rozgłoszeniowy	192.168.255.255	11000000.10101000.1 1111111.11111111
# hostów w sieci	32766
# host min	192.168.128.1	11000000.10101000.1 0000000.00000001
# host max	192.168.255.254	11000000.10101000.1 1111111.11111110
# """


