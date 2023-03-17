import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction, QMessageBox, QVBoxLayout
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqttclient
import paho.mqtt.client as paho
import pymain
import json
from sys import argv, exit
import sys
import glob
import base64
import csv
import time
from datetime import datetime
import requests
esta_no_lora=None
directory=""
DIRECTORY=""
COM = ""
sucesso = True
ser = serial.Serial()
read_serial = False
Parar = True
r_serial = None
pulsos_n = 0
run_thread2 = None
run_thread3 = None
Messagerecieved = False
connected = False
broker_address = "192.168.0.127"
port = 1883
user = ""
password = ""
topic = None
payload = None
payload_1 = None
payload_2 = None
payload_3 = None
payload_4 = None
payload_5 = None
payload_22 = None
payload_33 = None
serial_number = None
ok = False
jwt = None
mqtt_t_publish = "application/1/device/ffff8caab58465fc/command/down"
const_cmd_status = "{\"fPort\":50,\"data\":\"AA==\",\"confirmed\":false}"
const_cmd_ligar10 = "{\"fPort\":50,\"data\":\"BgEBCg==\",\"confirmed\":false}"
const_cmd_ligar100 = "{\"fPort\":50,\"data\":\"BgEBZA==\",\"confirmed\":false}"
const_cmd_desligar = "{\"fPort\":50,\"data\":\"BgAAAA==\",\"confirmed\":false}"
lumi_tensao = 0
lumi_corrente = 0
lumi_status_rele = 0
lumi_percentual = 0
lumi_lat = -34.545554
lumi_lon = -8.54545
lumi_rssi_gw = -120
lumi_rssi_lumi = -120
lumi_rcv_payload = False
lumi_payload = ""
rcv_serial_payload = ""
flg_serial_rcv = False
currentindex_placa = 0
import os, random, string
length = 13
chars = string.ascii_letters + string.digits + '!@#$%^&*()'
random.seed = (os.urandom(1024))
mqtt_user = ''.join(random.choice(chars) for i in range(length))
pulsos = [".", "."]
pulsos2 = [".", "."]
pulsos3 = [".", "."]
pulsos4 = [".", "."]
mqtt_t = "application/4/#"
mqtt_t_2 = "inTopic"
mqtt_msg = "teste 1"
tempo=""
co_serial = False
import win32gui, win32con
hide = win32gui.GetForegroundWindow()
try:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    txt = dt_string
    tempo= now.strftime("%d/%m/%Y %H:%M:%S")
    x = txt.replace("/", "_").replace(" ", "_").replace(":", "_")
    z = x
except Exception as e:
    print(e)
def teste_temp():
    try:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y")
        txt = dt_string
        tempo = now.strftime("%d/%m/%Y %H:%M:%S")
        print(tempo)
    except Exception as e:
        print(e)

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    try:
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    except Exception as e:
        print(e)
        return []

ipadr=""
DEVPFID=""
APPID=""
DEVID_classA=""
deviceProfileID_classA=""
VERSION_lORA=""
version_erro=False

def config_read():
        global DEVPFID
        global APPID
        global ipadr
        global DEVID_classA
        global VERSION_lORA
        global deviceProfileID_classA
        with open("IP.json", 'r', encoding='utf-8') as meu_json:
            dados = json.load(meu_json)
            #dados = json.load(meu_json)DEVPFID
            #dados = APPID

        print(dados)
        ipadr = str(dados["IP"])
        DEVPFID = str(dados["deviceProfileID"])
        APPID = str(dados["applicationID"])
        DEVID_classA = str(dados["applicationID_classA"])
        deviceProfileID_classA = str(dados["deviceProfileID_classA"])
        VERSION_lORA = str(dados["Version"])
        # print(ipadr)
        # print(DEVPFID)
        # print(APPID)
config_read()
def worker():
    global mqtt_t
    global client
    client.loop_start()
    client.subscribe(mqtt_t)
    print(f"subscribe - {mqtt_t}")
    global connected
    while connected != True:
        time.sleep(0.2)
        #print("Testando5")
    # client.publish(mqtt_t_2, mqtt_msg)
    while Messagerecieved != True:
        time.sleep(0.2)
        #print("Testando3")
    # client.loop_stop()
    time.sleep(0.2)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global connected
        print("MQTT OK")
        connected = True

def on_message(client, userdata, message):
    Messagerecieved = True
    global topic
    global pulsos
    global pulsos2
    global pulsos3
    global pulsos4
    global pulsos_n
    global payload
    global payload_1
    global payload_2
    global payload_3
    global payload_22
    global payload_33
    global currentindex_placa
    global lumi_payload
    global lumi_rcv_payload
    global lumi_rcv_payload_rssi
    global lumi_rssi_gw
    global esta_no_lora
    global VERSION_lORA
    global version_erro
    try:
        if message:
            #print(payload)
            print("está no lora")

        topic = message.topic
        payload = bytes(json.loads(message.payload.decode("utf-8"))["data"], 'utf-8')
        print(payload)
        result = json.loads(message.payload.decode("utf-8"))
        print(result)
        temp_lumi_rssi_gw = int(result["rxInfo"][0]["rssi"])
        #esta_no_lora = False
        if (temp_lumi_rssi_gw > lumi_rssi_gw):
            lumi_rssi_gw = temp_lumi_rssi_gw

        if currentindex_placa == 3:
            print(payload)

            decoded = base64.b64decode(payload).hex()
            if decoded[:2] == "00":
                decoded = base64.b64decode(payload).hex()[64:]

                print(decoded)
                decoded_2 = decoded[:2]
                # pulsos[pulsos_n] = str(int(decoded_2, 16))
                print(decoded_2)
                if decoded_2 == VERSION_lORA:
                    esta_no_lora = True
                else:
                    version_erro=True
                    esta_no_lora = False

        elif currentindex_placa == 2:
            print(payload[:3])
            decodedbateria= base64.b64decode(payload).hex()
            bateria = int(payload[:3],16)
            print(bateria)
            decoded1 = base64.b64decode(payload).hex()[4:]
            decoded1_2 = decoded1[:8]
            pulsos[pulsos_n] = str(int(decoded1_2, 16))
            print(pulsos)

            decoded2 = base64.b64decode(payload).hex()[12:]
            decoded2_2 = decoded2[:8]
            pulsos2[pulsos_n] = str(int(decoded2_2, 16))
            print(pulsos2)

            decoded3 = base64.b64decode(payload).hex()[20:]
            decoded3_2 = decoded3[:8]
            pulsos3[pulsos_n] = str(int(decoded3_2, 16))
            print(pulsos3)

            decoded4 = base64.b64decode(payload).hex()[28:]
            decoded4_2 = decoded4[:8]
            pulsos4[pulsos_n] = str(int(decoded4_2, 16))
            print(pulsos4)
            esta_no_lora = True

        else:
            esta_no_lora = True

    except Exception as e:
        print(e)

try:
    client = mqttclient.Client(mqtt_user, clean_session=True, userdata=None, protocol=paho.MQTTv31)
    client.on_message = on_message
    client.username_pw_set(user, password=password)
    client.on_connect = on_connect
    client.connect(ipadr, port=port)
    print("CONECTADO EM ")
    print(ipadr)

except Exception as e:
    print(e)

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """

    try:

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(20)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    except Exception as e:
        return []


class Teste(QMainWindow, pymain.Ui_MainWindow):

    def worker_1(self):
        try:

            while 1:
                #print("testando2")
                if self.comboBox.currentText() != "":
                    self.pushButton_3.setEnabled(True)
                else:
                    self.pushButton_3.setEnabled(False)

                if self.comboBox_2.currentIndex() != 0:
                    # if self.comboBox_2.currentIndex() == 3:
                    #    self.pushButton.setEnabled(True)
                    # else:
                    self.groupBox_4.setEnabled(True)
                else:
                    self.groupBox_4.setEnabled(False)
        except Exception as e:
            print(e)
            #print("hggghghghghg")
        finally:
            global Messagerecieved
            global connected
            if Messagerecieved == False:
                Messagerecieved = True
            if connected == False:
                connected = True

    def worker_2(self):
        global payload
        global client

        time.sleep(1)
        global Messagerecieved
        try:
            while Messagerecieved != True:

                if payload != None:
                    Messagerecieved = True
                    break

                time.sleep(0.1)
                #print("testando")
        except Exception as e:
            print(e)

    def __init__(self):

        super(Teste, self).__init__()
        super(Teste, self).setupUi(self)
        self.pushButton_2.clicked.connect(self.atualizar_portas_com)
        self.pushButton_3.clicked.connect(self.co_serial)
        self.pushButton.clicked.connect(self.get_serial_number_barcode)
        self.pushButton_66.clicked.connect(self.btn_close_error)
        self.pushButton_6.clicked.connect(self.btn_close_scs)
        self.scrollArea_6.setGeometry(QtCore.QRect(9, 10, 771, 571))
        self.scrollArea_6.setVisible(False)
        self.scrollArea_3.setVisible(False)
        self.scrollArea.setVisible(False)
        self.groupBox.setVisible(True)
        self.groupBox_2.setVisible(False)
        self.run_thread2 = None
        self.run_thread3 = None
        self.run_thread4 = None
        self.comboBox_2.currentIndexChanged.connect(self.mudar_placa)
        self.pushButton_5.clicked.connect(self.btn_cancel_gsnbc)
        self.pushButton_4.clicked.connect(self.btn_next_gsnbc)
        #self.pushButton_7.clicked.connect(self.escolher_diretorio)
        self.pushButton_8.clicked.connect(self.Desligar_Lumi)
        self.pushButton_7.clicked.connect(self.Ligar_lumi)
        self.pushButton_9.clicked.connect(self.lumi_10_porcento)
        self.pushButton_10.clicked.connect(self.lumi_100_porcento)
        self.atualizar_portas_com()
        self.pushButton_3.setEnabled(False)
        self.pushButton.setEnabled(True)
        threading.Thread(target=self.worker_1).start()
        self.label_4.setText("")
        threads = []
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        t_1 = threading.Thread(target=self.worker_2)
        threads.append(t_1)
        t_1.start()
        self.textEdit.verticalScrollBar().rangeChanged.connect(self.ResizeScroll)

    def ResizeScroll(self, min, maxi):
        try:
            self.textEdit.verticalScrollBar().setValue(maxi)
        except Exception as e:
            print(e)

    def mudar_placa(self):
        global currentindex_placa
        try:

            if self.comboBox_2.currentIndex() == 0:
                self.label_6.setText(f"... ")
                currentindex_placa = 0

            elif self.comboBox_2.currentIndex() != 0:
                currentindex_placa = int(self.comboBox_2.currentIndex())
                self.label_6.setText(f"{self.comboBox_2.currentText()}")
        except Exception as e:
            print(e)

    def get_serial_number_barcode(self):
        try:
            self.lineEdit.setFocus()

            print(f"{self.scrollArea.isVisible()} ------ --- --- -------")

            if self.scrollArea.isVisible() == True:
                self.scrollArea.setVisible(False)
            if self.scrollArea_3.isVisible() == True:
                self.btn_close_error()

            self.scrollArea_6.setVisible(True)
            self.pushButton.setEnabled(False)
            self.groupBox_2.setEnabled(False)
            self.groupBox_3.setEnabled(False)
            self.lineEdit.setText("")
        except Exception as e:
            print(e)

    def btn_cancel_gsnbc(self):
        try:
            self.scrollArea_6.setVisible(False)
            self.label_4.setText("")
            self.pushButton.setEnabled(True)
            self.groupBox_2.setEnabled(True)
            self.groupBox_3.setEnabled(True)
        except Exception as e:
            print(e)

    def btn_close_error(self):
        try:
            self.scrollArea_3.setVisible(False)
            self.textEdit_2.setText("")
        except Exception as e:
            print(e)

    def btn_open_error(self, msg):
        try:
            self.textEdit_2.append(msg)
            time.sleep(1)
            self.scrollArea_3.setVisible(True)
            time.sleep(1)
        except Exception as e:
            print(e)

    def btn_Sucesso_ok(self):
        try:
            time.sleep(1)
            self.scrollArea.setVisible(True)
            time.sleep(1)
        except Exception as e:
            print(e)

    def btn_teste_error(self,msg):
        try:
            # msg="ID NÃO ENCONTRADO"
            self.textEdit_2.append(msg)
            time.sleep(1)
            self.scrollArea_3.setVisible(True)
            time.sleep(1)
        except Exception as e:
            print(e)

    def btn_close_scs(self):
        try:
            self.scrollArea.setVisible(False)
        except Exception as e:
            print(e)

    def btn_open_scs(self):
        try:
            time.sleep(0.1)
            self.scrollArea.setVisible(True)
            time.sleep(0.8)
        except Exception as e:
            print(e)

    def keyPressEvent(self, qKeyEvent):
        try:
            if qKeyEvent.key() == QtCore.Qt.Key_Return:
                # print('Enter pressed')
                if self.scrollArea_6.isVisible() is True:
                    config_read()
                    print("oioioi")
                    self.btn_next_gsnbc()

                else:
                    global currentindex_placa

                    if self.comboBox_2.currentIndex() == 0:
                        self.label_6.setText(f"... ")
                        currentindex_placa = 0

                    else:
                        self.get_serial_number_barcode()
                        print("saiu")

            if qKeyEvent.key() == QtCore.Qt.Key_Space:
                # print('Enter pressed')
                if self.scrollArea_6.isVisible() is False:
                    # self.scrollArea_6.setEnabled(True)
                    print("oioioi")
                    self.get_serial_number_barcode()

                else:
                    print("saiu")
            else:
                super().keyPressEvent(qKeyEvent)
                # print("0909")
        except Exception as e:
            print(e)

    def Desligar_Lumi(self):
        global mqtt_t_publish
        global serial_number
        global const_cmd_desligar
        global tempo
        global teste_temp
        try:

            mqtt_t_publish = f"application/1/device/{serial_number}/command/down"
            print(mqtt_t_publish)
            print(const_cmd_desligar)
            #print(tempo)
            #teste_temp()
            print("Desligando Lumi")
            client.publish(mqtt_t_publish, const_cmd_desligar);
        except Exception as e:
            print(e)

    def lumi_10_porcento(self):
        global mqtt_t_publish
        global serial_number
        global const_cmd_desligar
        global tempo
        global teste_temp
        const_cmd_10 = "{\"fPort\":50,\"data\":\"BgEBCg==\",\"confirmed\":false}"

        try:

            mqtt_t_publish = f"application/1/device/{serial_number}/command/down"
            print(mqtt_t_publish)
            #print(tempo)
            print(const_cmd_10)
            #teste_temp()
            print("Ligando em 10%")
            client.publish(mqtt_t_publish, const_cmd_10);
        except Exception as e:
            print(e)

    def lumi_100_porcento(self):
        global mqtt_t_publish
        global serial_number
        global const_cmd_desligar
        global tempo
        const_cmd_100 = "{\"fPort\":50,\"data\":\"BgEBZA==\",\"confirmed\":false}"
        global teste_temp

        try:

            mqtt_t_publish = f"application/1/device/{serial_number}/command/down"
            print(mqtt_t_publish)
            print(const_cmd_100)
            #teste_temp()
            print("Ligando em 100%")
            client.publish(mqtt_t_publish, const_cmd_100);
        except Exception as e:
            print(e)

    def Ligar_lumi(self):
        global mqtt_t_publish
        global serial_number
        global const_cmd_ligar100
        global tempo
        global teste_temp
        try:

            mqtt_t_publish = f"application/1/device/{serial_number}/command/down"
            print(const_cmd_ligar100)
            print("Ligando Lumi")
            client.publish(mqtt_t_publish, const_cmd_ligar100);
        except Exception as e:
            print(e)

    def btn_next_gsnbc(self):
        try:
            global serial_number
            global ser
            global client
            print(str(self.lineEdit.text()))

            if self.lineEdit.text()[:2] == "ID":
                serial_number = self.lineEdit.text()[3:].lower()
                serial_number = serial_number.replace("ç", "")
                if len(serial_number)==16:
                    APPID=""
                    global mqtt_t
                    global mqtt_t_publish
                    client.unsubscribe(mqtt_t)
                    if self.comboBox_2.currentIndex() != 3:
                        if self.comboBox_2.currentIndex() == 5:
                            APPID = str(7)
                        else:
                            APPID = str(4)
                        print(APPID)
                    else:
                        APPID = str(1)
                        print(APPID)
                    if serial_number != None:
                        mqtt_t = f"application/{APPID}/device/{serial_number}/event/up"
                        client.subscribe(mqtt_t)
                        self.textEdit.clear()
                        self.textEdit.append(f"subscribe - {mqtt_t}")
                    self.btn_cancel_gsnbc()
                    self.inicio_da_thread3()
                    if self.comboBox_2.currentIndex() == 1:
                        self.inicio_da_thread2()
                else:
                    self.label_4.setText("* Campo Obrigatório")
                    self.get_serial_number_barcode()
            else:
                self.label_4.setText("* Campo Obrigatório")
                self.get_serial_number_barcode()
        except Exception as e:
            print(e)
            try:
                self.get_serial_number_barcode()
            except:
                print("")

    def open_serial(self):
        global co_serial
        co_serial = True
        global ser
        global COM

        if COM == "":
            time.sleep(0.1)
            COM = self.comboBox.currentText()

        try:
            if ser.is_open is False:
                if self.comboBox_2.currentIndex() == 3:
                    ser.baudrate = 9600
                else:
                    ser.baudrate = 115200
                ser.port = str(self.comboBox.currentText())
                ser.open()

                self.textEdit.append(f" Você abriu a porta {self.comboBox.currentText()} serial")
                self.pushButton.setEnabled(True)

                read_serial = True
                print(ser)
        except:
            self.textEdit.append(f" Erro ao abrir a porta {self.comboBox_2.currentText()} serial")

    def inicio_da_thread3(self):
        try:
            print(str(self.lineEdit.text()))

            if self.lineEdit.text()[:2] == "ID":

                self.pushButton.setEnabled(False)
                self.groupBox_2.setEnabled(False)
                # print("oioioio")

                if self.run_thread3 is not None:
                    self.run_thread3.requestInterruption()
                    print("matou a thread3")
                time.sleep(0.1)

                self.run_thread3 = RunThread3(parent=None)
                self.run_thread3.Teste = self
                self.run_thread3.start()

            else:

                self.label_4.setText("* Campo Obrigatório")
                self.get_serial_number_barcode()
                print(str(self.lineEdit.text()))

        except Exception as e:
            print(e)

    def atualizar_portas_com(self):
        try:
            def _fn(params):
                self = params[0]

                global serial_ports
                portas = serial_ports()
                print(portas)

                self.comboBox.clear()
                for porta in portas:
                    self.comboBox.addItem(porta)

            _fn([self])
        except Exception as e:
            print(e)

    def co_serial(self):
        global co_serial
        try:
            print(co_serial)
            if co_serial == False:
                self.pushButton_2.setEnabled(False)
                self.open_serial()
            else:
                self.pushButton_2.setEnabled(True)
                self.close_serial()
        except Exception as e:
            print(e)
    def close_serial(self):
        global co_serial
        co_serial = False
        global read_serial
        global ser
        global Parar
        Parar = True
        try:
            ser.close()
            self.textEdit.append(f" Você fechou a porta {self.comboBox.currentText()} serial")
            self.pushButton.setEnabled(False)
        except:
            self.textEdit.append(f" Erro ao fechar a porta {self.comboBox.currentText()} serial")

class RunThread3(QtCore.QThread):
    def __init__(self, parent=None):
        super(RunThread3, self).__init__(parent)

        self.Teste = None
        #self.chirpstackCadastro()

    status_rele = 0
    dimmer_rele = 0
    tensao_rele = 0
    corrente_rele = 0
    real_potencia = 0
    real_potencia = 0
    aparente_potencia = 0
    fp_potencia = 0
    rssi_gw = -120
    rssi_lumi = -120

    config_vref = 0
    config_vref_mais = 0
    config_vref_menos = 0

    config_iref = 0
    config_iref_mais = 0
    config_iref_menos = 0

    config_iref10 = 0
    config_iref10_mais = 0
    config_iref10_menos = 0

    config_pot = 0
    config_pot_mais = 0
    config_pot_menos = 0

    config_pot10 = 0
    config_pot10_mais = 0
    config_pot10_menos = 0

    config_pot_calibracao = 0
    config_volt_calibracao = 0

    config_rssi_gw = 0
    config_rssi_gw_mais = 0
    config_rssi_gw_menos = 0

    config_rssi_diferenca = 0
    config_rssi_diferenca_mais = 0
    config_rssi_diferenca_menos = 0

    config_rssi_lumi = 0
    config_rssi_lumi_mais = 0
    config_rssi_lumi_menos = 0

    payload_cmd_calibracao_lumi = "{\"fPort\":50,\"data\":\"BgAAAA==\",\"confirmed\":false}"



    def get_jwt(self):
        global jwt
        global ipadr
        import json

        try:
            # url_base = "https://ns.atc.everynet.io/api/v1.0"
            url_base = "http://{ipadr}:8080/api/internal/login"
            url_base = url_base.replace("{ipadr}", ipadr)

            # }"""
            jsonObj = """{
      "email": "admin",
      "password": "bottomup"
    }"""

            print(jsonObj)
            # print(jsonObj[0])

            # url_ = (url_base + app_path + "?access_token=f8cbe5233bb2470fbbdaeb923c6493d5")
            url_ = (url_base)

            hds = {"content-type": "application/json", "Accept": "application/json"}
            response = requests.post(url=url_, data=jsonObj, headers=hds)

            if response is not None:
                import json
                print("respondeu")
                print(response.status_code)
                # print(response.text)

                teste = response.text
                objeto = json.loads(teste)

                jwt=objeto['jwt']

                #print(objeto['jwt'])

                # print(response.text)

            else:
                print("Servidr nao respondeu ou requisicao invalida")
                return (False, -1, "Servidr nao respondeu ou requisicao invalida")
        except ValueError as error:
            print(str(error))
            return (False, -1, str(error))


    def chirpstackCadastro(self):
        global ipadr
        #self.show_confirm()
        self.get_jwt()
        #if respostaDaRequisicao[0] == False:
        # self.Jiga.lineEdit_CADASTROLORA.setText("REPROVADO")
        # self.cadastro_lora_status = False
         #print("Reprovado")
        global jwt
        global DEVPFID
        global APPID
        global DEVID_classA
        global deviceProfileID_classA

        global serial_number
        dvadr=serial_number[8:]
        if self.Teste.comboBox_2.currentIndex() == 3:
            aplication_ID = APPID
            deviceprof_ID = DEVPFID

        else:
            aplication_ID = DEVID_classA
            deviceprof_ID = deviceProfileID_classA
        if self.Teste.comboBox_2.currentIndex() != 3:
            print("")
            if self.Teste.comboBox_2.currentIndex() == 5:
                APPID = str(7)
                aplication_ID = APPID
                print(APPID)
            else:
                APPID =str(4)
                aplication_ID = APPID

            print(APPID)
            #APPID=4
        else:
            APPID = str(1)
            aplication_ID = APPID
            print(APPID)


        try:
            # url_base = "https://ns.atc.everynet.io/api/v1.0"
            #url_base = "http://192.168.0.127:8080/api/devices"
            url_base = "http://#{ipadr}:8080/api/devices"
            url_base = url_base.replace("#{ipadr}", ipadr)



            # }"""
            jsonObj = """{  
          "device": {  
            "applicationID": "#{APPID}",  
            "description": "#{nomedv}",  
            "devEUI": "#{deviceui}",  
            "deviceProfileID": "#{DEVPFID}",  
            "isDisabled": false,  
            "name": "#{nomedv}",  
            "referenceAltitude": 0,  
            "skipFCntCheck": true,     
            "tags": {},  
            "variables": {}  
          }  
        }"""
            jsonObj = jsonObj.replace("#{deviceui}",serial_number)
            jsonObj = jsonObj.replace("#{nomedv}",serial_number)
            jsonObj = jsonObj.replace("#{descrtion}",serial_number)
            jsonObj = jsonObj.replace("#{DEVPFID}",deviceprof_ID)
            jsonObj = jsonObj.replace("#{APPID}",aplication_ID)

            print(jsonObj)

            # url_ = (url_base + app_path + "?access_token=f8cbe5233bb2470fbbdaeb923c6493d5")
            url_ = (
                        url_base + f"?access_token={jwt}")

            hds = {"content-type": "application/json", "Accept": "application/json",
                   "Grpc-Metadata-Authorization": f"Bearer {jwt}"}

            response = requests.post(url=url_, data=jsonObj, headers=hds)

            if response is not None:
                print("respondeu")
                print(response.status_code)
                print(response.text)
                if response.status_code==200:
                    #self.textEdit.append(f"ID:{serial_number} cadastrado")
                    time.sleep(0.1)
                    try:
                        #self.add_dev_lora()
                        self.chirpstackKeys()
                        #self.add_dev_lora()
                    except Exception as e:
                        print(e)
                if response.status_code==409:
                    import ctypes
                    try:
                        self.chirpstackKeys()
                    except Exception as e:
                        print(e)
                    resposta="Esse ID já existe"
                    resposta=resposta.replace("#{ID}",serial_number)
                    print(resposta)

            else:
                print("Servidr nao respondeu ou requisicao invalida")
                return (False, -1, "Servidr nao respondeu ou requisicao invalida")
        except ValueError as error:
            print(str(error))
            return (False, -1, str(error))


    def chirpstackKeys(self):

        global serial_number
        global jwt
        global DEVPFID
        global APPID
        dvadr = serial_number[8:]

        if self.Teste.comboBox_2.currentIndex() == 3:
            #placa = self.Jiga.zplAtual["nome"]
            # tipo = "C"
            Network = "7eace255b8a5e2699151960647569d23"
            APP_SK = "fbacb647f35845c7507dbf168ba8c17c"
        else:
           # placa = self.Jiga.zplAtual["nome"]
            # tipo = "A"
            Network = "72bcb53ca86b4ad2cb44a5c8c89147ae"
            APP_SK = "f1502971d2fd8b74dde6067e345a6dac"

        try:
            # url_base = "https://ns.atc.everynet.io/api/v1.0"
            #url_base = "http://192.168.0.127:8080/api/devices/#{serial}/activate"
            url_base = "http://#{ipadr}:8080/api/devices/#{serial}/activate"
            url_base = url_base.replace("#{ipadr}", ipadr)
            url_base = url_base.replace("#{serial}", serial_number)
            jsonObj = """{
               "deviceActivation": {  
                 "aFCntDown": 0,  
                 "appSKey": "#{appsk}",  
                 "devAddr": "#{dvadrs}",  
                 "devEUI": "#{deviceui}",  
                 "fCntUp": 0,  
                 "fNwkSIntKey": "#{nwsk}",  
                 "nFCntDown": 0,  
                 "nwkSEncKey": "#{nwsk}",  
                 "sNwkSIntKey": "#{nwsk}"  
               }  
             }"""

            jsonObj = jsonObj.replace("#{deviceui}", serial_number)
            jsonObj = jsonObj.replace("#{dvadrs}", dvadr)
            jsonObj = jsonObj.replace("#{appsk}", APP_SK)
            jsonObj = jsonObj.replace("#{nwsk}", Network)
            # jsonObj = jsonObj.replace("#{descrtion}", serial_number)

            print(jsonObj)
            # bearer=f"Bearer {jwt}"

            # url_ = (url_base + app_path + "?access_token=f8cbe5233bb2470fbbdaeb923c6493d5")
            url_ = (
                    url_base + f"?access_token={jwt}'")

            hds = {"content-type": "application/json", "Accept": "application/json",
                   "Grpc-Metadata-Authorization": f"Bearer {jwt}"}

            response = requests.post(url=url_, data=jsonObj, headers=hds)

            if response is not None:
                print("respondeu")
                print(response.status_code)
                print(response.text)
                # if response.status_code == 200:
                # self.chirpstackKeys()



            else:
                print("Servidr nao respondeu ou requisicao invalida")
                return (False, -1, "Servidr nao respondeu ou requisicao invalida")

        except ValueError as error:
            print(str(error))
        # return (False, -1, str(error))

    def run(self):
        global payload_1
        global payload_5
        global payload_2
        global payload_3
        global payload_4

        global pulsos
        global pulsos2
        global pulsos3
        global pulsos4
        global sucesso
        global esta_no_lora
        flg_erro_test=True
        esta_no_lora = False
        self.primeiro_pulso=True
        v=None
        to=0


        sucesso = True
        pulsos = [".", "."]
        pulsos2 = [".", "."]
        pulsos3 = [".", "."]
        pulsos4 = [".", "."]

        try:
            global ser
            global pulsos_n
            global client
            global lumi_rcv_payload
            global mqtt_t_publish
            global const_cmd_ligar100
            global lumi_rssi_gw
            global flg_serial_rcv
            global rcv_serial_payload
            global serial_number
            global version_erro
            flg_erro_test = True
            version_erro=False
            descricao_erro = ""
            esta_no_lora = False
            self.chirpstackCadastro()
            #self.Teste.textEdit.append("----------------------------------PASSE O IMÃ--------------------------------")
            print("----------------------------------Faça o device transmitir--------------------------------")
            while to < 45:
                to = to + 1
                v = "WAIT "
                v = v + str(to) + "s"
                self.Teste.textEdit.append(v)
                time.sleep(1)
                if esta_no_lora == True:
                    flg_erro_test = False
                    break
                if version_erro== True:
                    self.Teste.textEdit.append("-----Verssão errada-----")
                    time.sleep(1)
                    self.Teste.btn_teste_error("Versão Errada!!!")
                    break
            if flg_erro_test == True and version_erro== False:
                self.Teste.textEdit.append("-----ID Não LOCALIZADO-----")
                time.sleep(1)
                self.Teste.btn_teste_error("ID NÃO ENCONTRADO")

            elif flg_erro_test == False:
                self.Teste.textEdit.append(f"---ID:{serial_number} ENCONTRADO ----")
                flg_erro_test = False
                esta_no_lora = False
                self.Teste.btn_Sucesso_ok()

        except Exception as e:
            print(e)
        finally:
            try:

                self.Teste.btn_cancel_gsnbc()
            except Exception as e:
                print(e)

    def sucesso(self):
        self.Teste.scrollArea.setVisible()
        print("fhiwrfberkbk")
        #self.scrollArea.setVisible(False)
    def erro_teste(self):
        #self.scrollArea_3.setVisible(False)
        self.Teste.scrollArea.setVisible()

def close_cmd():
    qt = QApplication(argv)
    teste_teste = Teste()

    teste_teste.show()
    exit(qt.exec_())

if __name__ == '__main__':
    close_cmd()

