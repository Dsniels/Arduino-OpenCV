import matplotlib.pyplot as plt

asistencias_estudiantes = {
    'Daniel Salazar': [
        {'Fecha': '13-11-2023', 'Hora': '09:00:00'},
        {'Fecha': '14-11-2023', 'Hora': '09:15:00'},
        {'Fecha': '15-11-2023', 'Hora': '10:30:00'},    
        {'Fecha': '17-11-2023', 'Hora': '08:20:00'},  
    ],
    'The Rock': [
        {'Fecha': '13-11-2023', 'Hora': '09:10:00'},
        {'Fecha': '14-11-2023', 'Hora': '09:45:00'},  
        {'Fecha': '15-11-2023', 'Hora': '10:15:00'}, 
    ]
}


def Maximo_Clases():
    # Encuentra el máximo número de clases (basado en las fechas)
    max_clases = max(len(Asistencia) for Asistencia in asistencias_estudiantes.values())
    return max_clases

def dias_con_max_asistencias():
    max_clases_totales = Maximo_Clases()
    dias_por_asistencia = {i + 1: 0 for i in range(max_clases_totales)}
    
    for studiante in asistencias_estudiantes.values():
        dias_asistencia = len(studiante)
        if dias_asistencia == max_clases_totales:
            dias_por_asistencia[dias_asistencia] += 1
    
    return dias_por_asistencia



def Grafica_asistencias():
    dias = [str(day) for day in range(13, 18)]  # Días del 13 al 17 como strings
    asistencias = [0 for _ in range(13, 18)]  # Inicializar las asistencias para cada día

    for studiante in asistencias_estudiantes.values():
        for asistencia in studiante:
            fecha = asistencia['Fecha']
            dia = fecha.split('-')[0]  # Extraer el día de la fecha
            if dia in dias:
                index = dias.index(dia)
                asistencias[index] += 1

    plt.bar(dias, asistencias, color='skyblue')
    plt.xlabel('Días')
    plt.ylabel('Asistencias Registradas')
    plt.title('Asistencias por Día (13-17)')
    plt.show()

Grafica_asistencias()

def plot_asistencias_individuales():
    dias = [str(day) for day in range(13, 18)]  # Días del 13 al 17 como strings
    fechas = set()  # Conjunto para almacenar fechas únicas

    for attendance_list in asistencias_estudiantes.values():
        for asistencia in attendance_list:
            fecha = asistencia['Fecha']
            fechas.add(fecha)  # Almacenar fechas únicas en el conjunto

    max_clases = len(fechas)  # Determinar el total de fechas como el máximo de clases

    for student, attendance_list in asistencias_estudiantes.items():
        asistencias = [0 for _ in range(13, 18)]  # Inicializar las asistencias para el estudiante

        for asistencia in attendance_list:
            fecha = asistencia['Fecha']
            dia = fecha.split('-')[0]  # Extraer el día de la fecha
            if dia in dias:
                index = dias.index(dia)
                asistencias[index] += 1

        plt.plot(dias, asistencias, marker='o', label=student)  # Graficar las asistencias por día para el estudiante

    plt.xlabel('Días')
    plt.ylabel('Asistencias Registradas')
    plt.title('Asistencias Individuales por Estudiante')
    plt.legend()
    plt.yticks(range(max_clases + 1))  # Establecer los valores del eje y como enteros
    plt.show()

plot_asistencias_individuales()