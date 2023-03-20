#Diego Marta Hurtado
#Grupo 2
#Sistemas Web

from fileinput import filename
import os
import sys

from bs4 import BeautifulSoup
from pynput import keyboard
from pathlib import Path
import requests
import getpass as gpass

fin_program = False


def pulsar(key):
    global fin_program
    if key == keyboard.Key.enter:
        print('end pressed')
        fin_program = True
        return False


def main(nombre_usuario, nom):
    metodo = 'GET'
    uri = "https://egela.ehu.eus/login/index.php"
    cabeceras = {'Host': 'egela.ehu.eus'}

    print(metodo)
    print(uri)
    print(cabeceras)

    cuerpo = ''
    response = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)

    resp_headers = response.headers
    cookie = str(response.headers.get("Set-Cookie")).split(";")
    cookie = cookie[0]
    localizacion = response.headers.get("location")
    cuerpo = response.content

    print(response.status_code)
    print(cookie)
    print(localizacion)
    print("-")

    if response.status_code == 200:
        egela = BeautifulSoup(cuerpo, "html.parser")
        logintoken = str(egela.find_all('input', {'name': "logintoken"}))
        logintoken = logintoken.split('"')[5]

        password = gpass.getpass()

        metodo = 'POST'

        cabeceras = {'Host': 'egela.ehu.eus', 'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookie}
        print(metodo)
        print(uri)
        print(cabeceras)
        cuerpo = {'logintoken': logintoken, 'username': nombre_usuario, 'password': password}
        print(cuerpo)

        response = requests.request(metodo, uri, data=cuerpo, headers=cabeceras, allow_redirects=False)
        cuerpo = response.content
        resp_headers = response.headers
        cookie = str(response.headers.get("Set-Cookie")).split(";")
        cookie = cookie[0]
        localizacion = response.headers.get("Location")

        print(response.status_code)
        print(cookie)
        print(localizacion)
        print("-")

        if response.status_code == 303:
            metodo = 'GET'
            cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': cookie}
            print(metodo)
            print(localizacion)
            print(cabeceras)

            response = requests.request(metodo, localizacion, headers=cabeceras, allow_redirects=False)
            cuerpo = response.content
            localizacion = resp_headers.get("Location")

            print(response.status_code)
            print(cookie)
            print(localizacion)
            print("-")

            if response.status_code == 303:
                localizacion = response.headers['Location']

                metodo = 'GET'
                cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': cookie}

                print(metodo)
                print(localizacion)
                print(cabeceras)

                response = requests.request(metodo, localizacion, headers=cabeceras, allow_redirects=False)
                cuerpo = str(response.content)
                localizacion = resp_headers.get("Location")

                print(response.status_code)
                print(cookie)
                print(localizacion)
                print("-")

                if response.status_code == 200:
                    if cuerpo.find(nom) != -1:
                        with keyboard.Listener(on_press=pulsar) as listener:
                            print('Press enter to continue...')
                            while fin_program == False:
                                pass
                            listener.join()
                        descarga(response.content, cookie)
                    elif cuerpo.find(nom) == -1:
                        print("The name you entered isn't correct")
                        exit(1)
        else:
            print("The username/password are not correct")
            exit(1)


def descarga(res, cookie):
    egela = BeautifulSoup(res, "html.parser")

    for localizacion in egela.find_all('a'):
        if "Sistemas Web" in localizacion:
            uri = str(localizacion).split('"')[3]
            metodo = 'GET'
            print(metodo)
            print(uri)
            cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': cookie}
            response = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

            print(response.status_code)
            print(response.reason)
            print(cookie)
            print("-")

            egela = BeautifulSoup(response.content, "html.parser")
            counter = 0

            if not os.path.exists("downloadedPDFs"):
                os.mkdir("downloadedPDFs")

            print("\nDescargando PDFs...\n")
            for localizacion in egela.find_all('img', {'class': 'iconlarge activityicon'}):
                if "/pdf" in str(localizacion):
                    uri = localizacion.parent.get('href')
                    metodo = 'GET'
                    cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': cookie}
                    response = requests.request(metodo, uri, headers=cabeceras, allow_redirects=False)

                    egela = BeautifulSoup(response.content, "html.parser")
                    localizacion_pdf = str(egela.find_all('a')).split('"')[1]
                    nom = str(localizacion_pdf).split('/')[8]
                    filename = Path('./downloadedPDFs/' + nom)
                    if not os.path.exists('./downloadedPDFs/' + nom):
                        metodo = 'GET'
                        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': cookie}
                        response = requests.request(metodo, localizacion_pdf, headers=cabeceras, allow_redirects=False)
                        filename.write_bytes(response.content)
                        counter += 1

            print("Descarga completada de " + str(counter) + " PDFs")


if __name__ == "__main__":
    nombre_usuario = sys.argv[1]
    nom = sys.argv[2]
    main(nombre_usuario, nom)