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


def ip_to_bin(ip):
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


def ip_to_list(ip):
    lista = []
    tmp = ''
    for let in ip:
        if let != '.':
            tmp += let
        else:
            lista.append(int(tmp))
            tmp = ''
    lista.append(int(tmp))
    return lista


def adres_sieci(ip, maska):
    ip = ip_to_bin(ip)
    maska = ip_to_bin(maska)
    ip_sieci = []

    for i in range(len(ip)):
        ip_oktet = ip[i]
        maska_oktet = maska[i]
        adres_sieci_oktet = ''

        for i1 in range(len(ip_oktet)):
            ip_num = ip_oktet[i1]
            maska_num = maska_oktet[i1]

            if maska_num == '1' and ip_num == '1':
                adres_sieci_oktet += '1'
            else:
                adres_sieci_oktet += '0'

        ip_sieci.append(bin_to_dec(adres_sieci_oktet))

    return ip_sieci


def adres_broadcast(ip, maska):
    ip = ip_to_bin(ip)
    maska = ip_to_bin(maska)
    ip_rozgl = []

    for i in range(len(ip)):
        ip_oktet = ip[i]
        maska_oktet = maska[i]
        ip_rozgl_oktet = ''

        for i1 in range(len(ip_oktet)):
            ip_num = ip_oktet[i1]
            maska_num = maska_oktet[i1]

            if maska_num == '1':
                ip_rozgl_oktet += ip_num
            elif maska_num == '0':
                ip_rozgl_oktet += '1'

        ip_rozgl.append(bin_to_dec(ip_rozgl_oktet))

    return ip_rozgl


def maska_to_skrot(maska):
    maska = ip_to_bin(maska)
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
    ip_broadcast = adres_broadcast(ip, maska)

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
    # tworzenie pierwszego broadcastu zeby zaczac petle
    ip_sieci = adres_sieci(ip, maski[0])
    ip_broadcast = adres_broadcast(ip, maski[0])

    lista_ip.append(ip_sieci)
    for maska in maski[1:]:
        # jezeli broadcast nie konczy sie na 255 (jezeli sie konczy nie mozna dodac po prostu 1 do adresu sieci)
        if ip_broadcast[3] != 255:
            ip_broadcast[3] += 1
            ip_sieci = ip_broadcast
            ip_broadcast = adres_broadcast(ip_sieci, maska)

        # jezeli konczy sie na 255
        elif ip_broadcast[3] == 255:
            # jezeli nie jest x.x.255.255
            if ip_broadcast[2] != 255:
                ip_broadcast[2] += 1
                ip_broadcast[3] = 0
                ip_sieci = ip_broadcast
                ip_broadcast = adres_broadcast(ip_sieci, maska)

            # jezeli jest x.x.255.255
            elif ip_broadcast[2] == 255:
                # jezeli nie jest x.255.255.255
                if ip_broadcast[1] != 255:
                    ip_broadcast[1] += 1
                    ip_broadcast[2] = 0
                    ip_broadcast[3] = 0
                    ip_sieci = ip_broadcast
                    ip_broadcast = adres_broadcast(ip_sieci, maska)

                # jezeli jest x.255.255.255
                elif ip_broadcast[1] == 255:
                    if ip_broadcast[0] != 255:
                        ip_broadcast[0] += 1
                        ip_broadcast[1] = 0
                        ip_broadcast[2] = 0
                        ip_broadcast[3] = 0
                        ip_sieci = ip_broadcast
                        ip_broadcast = adres_broadcast(ip_sieci, ip_broadcast)
                    elif ip_broadcast[0] == 255:
                        return False

        lista_ip.append(ip_sieci)

    return lista_ip


def przydzielanie_hostow_info(hosty, maski, ip_lista, kolejnosc):
    if kolejnosc == 'default':
        tabela = [['liczba hostów', 'IP podsieci', 'IP broadcast', 'maska', 'hosty maski',
                   'host min', 'host max']]
    else:
        tmp = []
        for obj in kolejnosc:
            tmp.append(obj)
        tabela = [tmp]

    for i in range(len(hosty)):
        host = czytalne(hosty[i])
        # ip lista to ip
        ip = ip_lista[i]
        maska = maski[i]

        broadcast = adres_broadcast(ip, maska)
        skrot = ' /' + str(maska_to_skrot(maska))
        l_hostow = czytalne(liczba_hostow(maska))
        min_host, max_host = min_max_host(ip, maska)

        ip = str(list_to_ip(ip))
        maska = str(list_to_ip(maska))
        broadcast = str(list_to_ip(broadcast))
        min_host, max_host = str(list_to_ip(min_host)), str(list_to_ip(max_host))

        slownik = {'liczba hostow': host, 'ip': ip, 'broadcast': broadcast, 'maska': maska+skrot, 'hosty maski': l_hostow,
                   'min': min_host, 'max': max_host}

        if kolejnosc == 'default':
            tabela.append([host, ip, broadcast, maska + skrot, l_hostow,
                           min_host, max_host])

        else:
            tmp = []
            for obj in kolejnosc:
                tmp.append(slownik[obj])
                print(tmp)
            tabela.append(tmp)
            print(tabela)

    return tabela


def podstawowe_info(ip, maska):
    tabela = []

    siec = adres_sieci(ip, maska)
    broadcast = adres_broadcast(ip, maska)
    hosty = liczba_hostow(maska)
    minh, maxh = min_max_host(ip, maska)
    skrot = maska_to_skrot(maska)
    ip = list_to_ip(ip)
    maska = list_to_ip(maska)

    tabela.append(['IP', str(ip)])
    tabela.append(['maska', str(maska) + ' /' + str(skrot)])
    tabela.append(['=======', '======='])
    tabela.append(['IP sieci', list_to_ip(siec)])
    tabela.append(['IP broadcast', list_to_ip(broadcast)])
    tabela.append(['hosty', czytalne(hosty)])
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
    if len(ip) != 4:
        return False
    for oktet in ip:
        oktet = int(oktet)
        if oktet > 255:
            return False
    return True


def czy_maska_jest_poprawna(maska):
    maski = []
    for i in range(32):
        maski.append(skrot_to_maska(i+1))
    print(maski)
    print(maska)
    if maska in maski: return True
    return False


def czy_poprawna_pisownia(rodzaj, txt):
    if rodzaj == 2:
        tmp = 0
        if len(txt) != 35:
            return False
        for digit in txt:
            if digit == '0' or digit == '1':
                tmp += 1
            elif digit == '.':
                if tmp != 8:
                    return False
                tmp = 0
            else:
                return False

    if rodzaj == 10:
        tmp = 0
        liczby = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        for digit in txt:
            if digit in liczby:
                tmp += 1

            elif digit == '.':
                if tmp < 1 or tmp > 4:
                    return False

                else:
                    tmp = 0
            else:
                return False

        if tmp < 1 or tmp > 4:
            return False

    if rodzaj == 'skrot':
        try:
            txt = int(txt)
            if txt < 0 or txt > 32:
                return False
        except ValueError:
            return False


    return True


def czytalne(liczba):
    liczba = str(liczba)
    if len(liczba) > 3:
        liczba = liczba[::-1]
        tmp = 0
        rev_liczba = ''
        for cyfra in liczba:
            if tmp != 3:
                rev_liczba += cyfra
                tmp += 1
            else:
                rev_liczba += ' ' + cyfra
                tmp = 0

        liczba = rev_liczba[::-1]

    return liczba


def start():
    print('Siema tutaj obliczę dla ciebie co chcesz')
    print('Włącz fullscreena bo tabelki nie beda sie cale wyswietlac i bedzie nieczytelnie ;0\n')
    print('Wpisz\n'
          '1- konwersja IP na binarną wersję\n'
          '2- konwersja binarnej wersji IP na zwykłą\n'
          '3- informacje na temat danego IP i maski (np. adres sieci adres broadcast ile hostow itp)\n'
          '4- przydzielanie podsieci urządzeniom\n'
          '5- wyświetl każdą możliwą maskę wraz z podstawowymi informacjami')
    wybor = input()

    # ip na bin
    if wybor == '1':
        ip_text = input('Podaj adres IP: ')

        # jezeli pisowania poprawna
        if czy_poprawna_pisownia(10, ip_text):
            ip = ip_to_list(ip_text)

            # jezeli IP jest poprawne
            if czy_ip_jest_poprawne(ip):
                ip_bin = ip_to_bin(ip)
                print('{} - {}'.format(ip_text, list_to_ip(ip_bin)))

            else:
                print('Niepoprawny adres IP')
        else:
            print('Niepoprawny adres IP')

    # bin na ip
    elif wybor == '2':
        ip_bin_text = input('Podaj adres IP w wersji binarnej: ')

        # jezeli pisowania poprawna
        if czy_poprawna_pisownia(2, ip_bin_text):
            ip_bin = ip_to_list(ip_bin_text)
            ip = bin_to_ip(ip_bin)
            print('{} - {}'.format(ip_bin_text, list_to_ip(ip)))

        else:
            print('Niepoprawne IP')

    # info o IP
    elif wybor == '3':
        ip_text = input('Podaj IP: ')
        maska_text = input('Podaj maskę (zapis skrocony lub adres): ')

        # czy podana maska jest skrocona
        if maska_text[0] == '/':
            sposob = 'skrot'
            maska_text = maska_text[1:]
        else:
            sposob = 10
        # czy poprawna pisownia
        if czy_poprawna_pisownia(10, ip_text) and czy_poprawna_pisownia(sposob, maska_text):
            ip = ip_to_list(ip_text)
            if sposob == 'skrot':
                maska = skrot_to_maska(maska_text)
            else:
                maska = ip_to_list(maska_text)

            # czy poprawne adresy
            if czy_ip_jest_poprawne(ip) and czy_maska_jest_poprawna(maska):
                info = podstawowe_info(ip, maska)
                tworzenie_tabelki(info)

            else:
                print('Niepoprawny adres IP lub maski')

        else:
            print('Niepoprawny adres IP lub maski')

    # przydzielanie podsieci
    elif wybor == '4':
        ip_text = input('Podaj adres IP: ')

        # jezeli poprawna pisownia
        if czy_poprawna_pisownia(10, ip_text):
            ip = ip_to_list(ip_text)

            # czy poprawne IP
            if czy_ip_jest_poprawne(ip):

                # przypisywanie hostow
                try:
                    n = int(input('Podaj liczbę podsieci: '))
                    if n < 1:
                        raise ValueError
                    urzadzenia = []
                    for i in range(n):
                        urzadzenia.append(int(input('Podaj l. hostow- podsiec {}: '.format(i+1))))
                        if urzadzenia[i] > 2147483646:
                            raise Exception

                    # zmienne
                    maski_urzadzen = przydzielanie_podsieci_hostom(urzadzenia)
                    # sprawdza czy sa dostepne hosty w sieci
                    if przydzielanie_ip_maskom(ip, maski_urzadzen):
                        ip_urzadzen = przydzielanie_ip_maskom(ip, maski_urzadzen)
                        info = przydzielanie_hostow_info(urzadzenia, maski_urzadzen,ip_urzadzen, 'default')
                        tworzenie_tabelki(info)

                        # zmiana kolejnosci
                        if input('Jeżeli chcesz zmienić kolejność wpisz 1\n') == '1':
                            dostepne = ('liczba hostow', 'ip', 'broadcast', 'maska', 'hosty maski', 'min', 'max')
                            kolejnosc = []
                            print('Wpisuj kolumny jedna po drugiej w kolejności jakiej zechcesz lub exit żeby zakonczyc')
                            print('Dostepne nazwy: {} '.format(tuple(nazwa for nazwa in dostepne)))
                            while True:
                                x = input('Podaj kolumnę lub wpisz "exit": ')
                                if x in dostepne:
                                    kolejnosc.append(x)
                                elif x == 'exit':
                                    if kolejnosc:
                                        info = przydzielanie_hostow_info(urzadzenia, maski_urzadzen, ip_urzadzen,
                                                                         kolejnosc)
                                        tworzenie_tabelki(info)
                                        break
                                    else:
                                        print('Prosze podać chociaż jedną pozycję')
                                else:
                                    print('Nieprawidłowa kolumna')

                    else:
                        print('Za mało dostępnych hostów w sieci!')

                except ValueError:
                    print('Podano nieprawidłową liczbę')

                except Exception:
                    print('Nieosiągalna liczba hostów')

            else:
                print('Niepoprawne IP lub maska')

        else:
            print('Niepoprawne IP lub maska')

    # wszystkie maski
    elif wybor == '5':
        tabela = [['maska', 'skrot', 'liczba hostow'], ]

        # dla kazdej istniejacej maski
        for i in range(32):
            skrot = i + 1
            maska = skrot_to_maska(skrot)
            hosty = liczba_hostow(maska)

            tabela.append([list_to_ip(maska), '/'+str(skrot), czytalne(hosty)])
        tworzenie_tabelki(tabela)

    else:
        print('Nieprawidłowy wybór')


if __name__ == '__main__':
    start()
    input('\nNaciśnij enter, żeby wyjść\n')
