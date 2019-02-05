import serial
import xlsxwriter
from statistics import mean, stdev
from os import startfile
from time import sleep
# import seaborn as sns


def initial_menu():
    print('-' * 90)
    print('#' * 37, 'VISCOTESTER 6L', '#' * 37)
    print('#' * 35, 'INSTRUÇÕES DE USO', '#' * 36)
    print('-' * 90)
    print('1 - Ligue o aparelho, realize o AUTO TEST pressionando a tecla START;')
    print('2 - Observe se não há nenhum fuso acoplado ao aparelho, se sim, pressione START;')
    print('3 - Aguarde o AUTO TEST ser finalizado;')
    print('4 - Adicione o fuso correto, selecione o fuso correto no aparelho pressionando ENTER;')
    print('5 - Selecione a RPM desejada e pressione ENTER;')
    print('6 - Observe se o fuso correto está acoplado ao aparelho e pressione START.')
    print('-' * 90)
    print('#' * 90)
    print('#' * 90)
    print('-' * 90)


def sample_name():
    sample_name = str(input('Digite o nome da amostra: '))
    print('Aguarde que em instantes o programa se inicializará.')
    return sample_name


def serial_object_creator(time_set):
    ser = serial.Serial('COM1', 9600, timeout=time_set)
    serial_object = ser.readline().split()
    return serial_object


def timer_for_closing_port(object):
    time_for_closing = (60/float(object[3])) + 15
    return time_for_closing


def torque_validator(serial_object):
    if serial_object[7] == b'off':
        return False
    else:
        return True


def readings_printer(object):
    print(f'RPM: {float(object[3])} / cP: {int(object[7])} / Torque: {float(object[5])}%')


def values_storager(object):
    if str(float(object[3])) not in registers.keys():
        registers[str(float(object[3]))] = [[int(object[7])], [float(object[5])]]
    elif str(float(object[3])) in registers.keys():
        registers[str(float(object[3]))][0].append(int(object[7]))
        registers[str(float(object[3]))][1].append(float(object[5]))
    return registers


def sheet_maker(sample_name, **registers):
    if len(registers) > 0:


        def data_processor(**registers):
            for value in registers.values():
                if len(value[0]) > 1:    
                    mean_value = mean(value[0])
                    std_value = stdev(value[0])
                    cp_list = [x for x in value[0] if (x > mean_value - std_value)]
                    cp_list = [x for x in cp_list if (x < mean_value + std_value)]
                    value[0] = cp_list
                else:
                    pass
            return registers


        workbook = xlsxwriter.Workbook(f'{sample_name}.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', f'{sample_name}', bold)
        worksheet.write('B1', 'RPM', bold)
        worksheet.write('C1', 'cP', bold)
        worksheet.write('D1', 'Torque(%)', bold)
        worksheet.write('E1', 'Processamento dos dados >>', bold)
        worksheet.write('H1', 'RPM', bold)
        worksheet.write('I1', 'cP', bold)
        row = 1
        col = 1
        for key, value in registers.items():
            worksheet.write(row, col, float(key))
            for cp in value[0]:
                worksheet.write(row, col + 1, cp)
                row += 1
            row -= len(value[0])
            for torque in value[1]:
                worksheet.write(row, col + 2, torque)
                row += 1
        processed_registers = data_processor(**registers)
        row = col = 1
        for key, value in processed_registers.items():
            worksheet.write(row, col + 6, float(key))
            worksheet.write(row, col + 7, mean(value[0]))
            row += 1
        workbook.close()
        print('Aguarde que uma planilha será aberta com seus resultados.')
        startfile(f'{sample_name}.xlsx')
        return workbook


    else:
        print('Nenhuma planilha será gerada por falta de dados.')


registers = dict()  # Registros das leituras serão armazenados neste dicionário.
time = 200  # Tempo para timeout da porta inicial alto para evitar bugs na inicialização do programa.


initial_menu()
sample_name = sample_name()

sleep(10)  # Tempo de espera para evitar que bugs que o aparelho gera na inicialização possam dar crash no programa.
while True:
    try:
        object = serial_object_creator(time)
        time = timer_for_closing_port(object)
        if torque_validator(object):
            if object == False:
                print('Torque máximo atingido ou erro no aparelho')
            else:
                readings_printer(object)
                registers = values_storager(object)
        else:
            print('Torque máximo atingido')
            print('Leituras não são possíveis de serem feitas')
            print('Pressione STOP no aparelho')

    except KeyboardInterrupt:
        print(f'Resultados registrados: {registers}')
        print('Programa interrompido por atalho de teclado')
        break

    except IndexError:
        print(f'Resultados registrados: {registers}')
        print('Foi pressionado STOP no aparelho')
        break


sheet_maker(sample_name, **registers)


print('FIM DO PROGRAMA')
print('OBRIGADO POR USAR O VISCOTESTER 6L SCRIPT')
