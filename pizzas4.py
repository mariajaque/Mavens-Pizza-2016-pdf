# Qué hay que comprar para la semana que viene
"""
- The order_details tables has 48621 rows containing order details regarding
pizza type and order quantity.
- The orders table record the datetime indicators of the 21351 orders.
- The pizza_types table specifies the category, ingredients information about
the 33 different pizza types offered by the pizza place.
- The pizzas table has 97 rows containing the pricing details of pizza based on
the size and pizza type
"""

import pandas as pd
import numpy as np
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import signal
import sys


warnings.filterwarnings("ignore")


def handler_signal(signal, frame):

    # Salida controlada del programa en caso de pulsar
    # control C

    print("\n\n [!] out .......\ n")

    sys.exit(1)


signal.signal(signal.SIGINT, handler_signal)


class PDF(FPDF):
    def portada(self):

        # Creamos la portada en la que venga el título del reporte, el año y
        # una fotografía del logo del equipo
        # Alineamos ambos textos en el centro

        self.set_font('times', 'b', 40)
        self.set_y(50)
        self.cell(0, 40, 'Mavens Pizza Report', ln=True, align='C')
        self.set_font('times', '', 25)
        self.cell(0, 25, '2016', ln=True, align='C')
        self.image('logo_mavens.jpg', x=25, y=120, w=150)

    def footer(self):

        # Establecemos como vamos a querer que sea el pie de página de nuestro documento
        # Primero le pasamos la posición en la que queremos que comience el pie
        # de página. En nuestro caso queremos que comience a 10 mm del final de la página

        self.set_y(-20)
        self.set_font('times', '', 8)

        # Añadimos el número de línea

        self.cell(0, 10, f'Página {str(self.page_no())}', align='C')


def extract_csv():

    fechas = pd.read_csv('orders.csv', sep=';')
    pedidos = pd.read_csv('pizzas.csv', sep=',')
    detalles = pd.read_csv('order_details.csv', sep=';')
    ingredientes = pd.read_csv('pizza_types.csv', sep=',', encoding='Windows-1252')

    informe = informe_de_datos(fechas, pedidos, detalles, ingredientes)

    return (fechas, pedidos, detalles, ingredientes, informe)


def transform_csv(fechas, pedidos, detalles, ingredientes):

    # Primero ordenamos los id y posteriormente reestablecemos
    # los índices del dataframe

    fechas = fechas.sort_values('order_id')
    fechas.index = [i for i in range(fechas.shape[0])]

    detalles = detalles.sort_values('order_details_id')
    detalles = detalles.dropna()
    detalles.index = [i for i in range(detalles.shape[0])]

    # En fechas no transformamos las horas ya que esa columna no se va a
    # utilizar para nada
    # Transformamos las fechas todas al mismo formato
    # Si en alguno da error lo cambiamos por un null

    for i in fechas.index:

        fechas.loc[i, 'date'] = pd.to_datetime(fechas['date'].iloc[i], errors='coerce')

    # Vamos a sustituir los nats por el valor que se haya podido transformar
    # antes

    fi = pd.to_datetime('2016-01-01')

    for i in fechas.index:

        if str(fechas['date'].iloc[i]) == str(pd.NaT):
            fechas.loc[i, 'date'] = fi

        else:
            fi = fechas['date'].iloc[i]

    # Para el dataframe de detalles, primero nos quitaremos todos los NaN
    # y posteriormente nos quitaremos todos los negativos en la columna de
    # orders, reemplazándolos por su valor absoluto -> Asumimos que se
    # equivocaron al introducir los datos

    # detalles = detalles.dropna()

    # Reemplazamos os números escritos con letras por números enteros
    # Habiendo visto los datos los únicos números que aparecen a mano
    # son one y two

    detalles['quantity'].replace(to_replace=r'[O-o][N-n][E-e]', value=1, regex=True,inplace=True)
    detalles['quantity'].replace(to_replace=r'[T-t][W-w][O-o]', value=2, regex=True,inplace=True)

    # Obtengo los índices de aquellos números negativos en cantidad

    for i in detalles.index:

        try:
            detalles.loc[i, 'quantity'] = abs(int(detalles['quantity'].iloc[i]))
        except:
            ...

    detalles['pizza_id'] = detalles['pizza_id'].str.replace(' ', '_')
    detalles['pizza_id'] = detalles['pizza_id'].str.replace('-', '_')
    detalles['pizza_id'] = detalles['pizza_id'].str.replace('@', 'a')
    detalles['pizza_id'] = detalles['pizza_id'].str.replace('0', 'o')
    detalles['pizza_id'] = detalles['pizza_id'].str.replace('3', 'e')

    # Vamos a querer tener todos los datos en un único dataframe
    # Modificaremos el de order details pues es el más completo
    # Le añadiremos una nueva columna que sea el número de la semana
    # asociado a la fecha del pedido. Añadiremos una
    # columna por cada posible ingrediente de la pizza

    dias = []
    num_semana = []

    for fecha in fechas['date']:
        dia = pd.to_datetime(fecha, dayfirst=True)
        dias.append(dia.day_of_week)
        num_semana.append(dia.week)

    fechas['semana'] = num_semana
    fechas['dia_semana'] = dias

    # Nos guardamos para cada order_id en detalles su fecha
    # asociada

    semanas = []
    dia_semana = []

    for s in detalles['order_id']:

        indice = fechas[fechas['order_id'] == s].index
        semana = fechas['semana'].iloc[indice]
        d = fechas['dia_semana'].iloc[indice]

        semanas.append(int(semana))
        dia_semana.append(int(d))

    detalles['semana'] = semanas
    detalles['dia'] = dia_semana

    # Obtenemos todos los posibles ingredientes que emplea
    # en la elaboración de sus pizzas

    lista_ingredientes = []
    for ingrediente in ingredientes['ingredients']:
        varios = ingrediente.split(',')
        lista_ingredientes += varios

    set_ingredientes = set(lista_ingredientes)

    # Creamos una columna por cada ingrediente en detalles
    # Almacenamos en un diccionario el índice de cada ingrediente

    indices = dict()

    for i in set_ingredientes:
        detalles[i] = [0 for i in detalles.index]
        indice = detalles.columns.get_loc(i)
        indices[i] = indice

    # Para cada tipo de pizza en order detail, les sumamos
    # las cantidades a sus ingredientes correspondientes
    # Para las s sumaremos una unidad de cada ingrediente
    # Para las m sumaremos 2 y para las L sumaremos 3

    tipos_de_pizzas = pedidos['pizza_id'].tolist()
    tamanos = ['s', 'm', 'l', 'xl', 'xxl']
    ing_asociados = dict()

    for tipo in tipos_de_pizzas:

        tamano = tipo.split('_')[-1]
        ingredientes_str = ingredientes[ingredientes['pizza_type_id'] == tipo[:-len(tamano)-1]]['ingredients'].tolist()[0]
        lista_ingredientes_comprar = ingredientes_str.split(',')
        ing_asociados[tipo] = lista_ingredientes_comprar

    # Sumamos la cantidad de cada ingrediente que ha necesitado cada pedido

    for i in detalles.index:

        try:
            pedido = detalles['pizza_id'].iloc[i]
            cantidad = detalles['quantity'].iloc[i]
            ing = ing_asociados[pedido]
            tamano = pedido.split('_')[-1]

            for j in ing:
                detalles.loc[i, j] += cantidad * (tamanos.index(tamano) + 1)

        except:
            ...

    return detalles


def load_csv(datos):

    # El dataframe obtenido en el transform csv
    pass


def extract():

    # Extrae los datos finales ya trabajados de la pizería
    pass


def transform(datos):

    ingredientes = datos.columns.values
    ingredientes = ingredientes[6:]

    # Nuestro predict será la media de las modas de cada ingrediente

    suma_semana = datos.pivot_table(index='semana', aggfunc='sum')
    suma_semana_ingredientes = suma_semana[ingredientes]
    modas = suma_semana_ingredientes.mode().mean().round().tolist()

    # Creamos un dataframe con el valor calculado para cada ingrediente

    d = {'Ingredientes:': ingredientes, 'Unidades a comprar:': modas}
    res = pd.DataFrame(data=d)

    return res


def load(res, datos):

    # Creamos las gráficas y las imágenes

    reporte(datos, res)

    # creamos un objeto pdf que por defecto será de tamaño A4
    # Determinamos que las medidas que le pasemos serán el milimtros

    pdf = PDF('P', 'mm')

    # Establecemos que cambie de página automáticamente
    # Establecemos que cambie de página cuando esté a 12mm del final de la
    # página
    pdf.set_auto_page_break(auto=True, margin=100)

    # Añadimos una página y la portada
    pdf.add_page()
    pdf.portada()
    pdf.add_page()

    # Vamos a querer que el tipo de fuente sea 'Helvetica'
    # El tamaño de la letra será de 20

    pdf.set_font('times', 'b', 20)

    # Añadimos las imágenes con las gráficas
    nombres = ['evolucion_temporal_ingredientes.jpg', 'evolucion_temporal_pizzas.jpg', 'ingredientes_a_comprar.jpg', 'pizzas_compradas_anual.jpg', 'top_5_pizzas.jpg', 'peores_5_pizzas.jpg']


    pdf.image('ingredientes_a_comprar.jpg', 30, 30, 150)

    pdf.image('pizzas_compradas_anual.jpg', 30, 160, 150)
    pdf.add_page()

    pdf.image('top_5_pizzas.jpg', 30, 30, 150)
    pdf.image('peores_5_pizzas.jpg', 30, 160, 150)
    pdf.add_page()

    pdf.cell(0, 20, 'Evolución temporal de los ingredientes empleados:')
    pdf.image('evolucion_temporal_ingredientes.jpg', 60, 50, 90)
    pdf.add_page()

    pdf.cell(0, 20, 'Evolución temporal de las pizzas pedidas:')
    pdf.image('evolucion_temporal_pizzas.jpg', 60, 50, 90)

    pdf.output('reporte_ejecutivo.pdf')


def informe_de_datos(fechas, pedidos, detalles, ingredientes):

    # Primero vemos el número de NaNs y de Nulls de cada df
    # Agregamos también el tipo de cada columna

    fichero = open('informe_calidad_datos.txt', 'w')
    informe = {}

    dfs = [fechas, pedidos, detalles, ingredientes]
    nombres = ['orders.csv', 'pizzas.csv', 'order_details.csv', 'pizza_types.csv']

    for df in range(len(dfs)):

        valores = {}

        null = {}
        nan = {}

        columnas = dfs[df].columns.values.tolist()

        tipos_columna = {}

        for c in columnas:

            tipos = dfs[df][c].dtypes
            nulls = dfs[df][c].isnull().sum()
            nans = dfs[df][c].isna().sum()

            tipos_columna[c] = tipos
            null[c] = nulls
            nan[c] = nans

        valores['Nulls'] = null
        valores['NaNs'] = nan
        valores['Tipos'] = tipos_columna

        informe[nombres[df]] = valores

    return informe


def reporte(datos, res):

    # Vamos a crear los siguientes gráficos:
    # - Tabla con los ingredientes a comprar -> res
    # - Evolución temporal de los ingredientes comprador por cada semana
    # - Evolución temporal de las pizzas más compradas (ignorando los tamaños)
    # - BarPlot con los ingredientes que se deben comprar
    # - Gráfica con las pizzas compradas en todo el año
    # - Gráfica con las 5 top pizzas

    sns.set_style('darkgrid')

    ingredientes = res['Ingredientes:'].unique().tolist()
    pizzas = datos['pizza_id'].unique().tolist()
    semanas = datos['semana'].unique().tolist()

    # Creamos un df con los ingredientes comprados en cada semana
    ing = datos[ingredientes + ['semana']]
    ing = ing.sort_values('semana')
    ing.index = [i for i in range(ing.shape[0])]
    ingredientes_semana = pd.DataFrame()
    for ingredient in ingredientes:
        ingredientes_semana[ingredient]=ing.groupby('semana')[ingredient].sum().tolist()


    # Gráfico de la evolución temporal de las compras de cada ingrediente
    ax = ingredientes_semana.plot(figsize=(35, 80), subplots=True, color='b')
    # plt.show()
    plt.savefig('evolucion_temporal_ingredientes.jpg',dpi=300, bbox_inches='tight')

    # Sacamos la cantidad que cada pizza pedidas por semana
    cantidad = datos.groupby(['semana', 'pizza_id']).count()
    dat = {'semana': [cantidad.index[i][0] for i in range(len(cantidad.index))], 'pizza_id': [cantidad.index[i][1] for i in range(len(cantidad.index))], 'cantidad': cantidad['quantity'].tolist()}
    c = pd.DataFrame(dat)

    plt.figure(figsize=(20,20))
    tipos = datos.pizza_id.values.tolist()
    tipos = list(set(tipos))

    fig, axis = plt.subplots(len(tipos), 1, figsize=(35,90))
    i = 0
    for t in tipos:
        ax = c[c['pizza_id'] == t].plot(x='semana', y='cantidad', ax=axis[i], label=t, color='b')
        i += 1
    # plt.show()
    plt.savefig('evolucion_temporal_pizzas.jpg', dpi=300, bbox_inches='tight')

    # Barplot de los ingredientes a comprar

    # Sacamos el orden en el que queremos que vayan las barras
    orden = res.groupby('Ingredientes:')['Unidades a comprar:'].sum().sort_values(ascending=False).index.values
    plt.figure(figsize=(15,10))
    plt.title("Ingredientes a comprar", fontsize=50, fontweight='bold')
    ax = sns.barplot(x='Ingredientes:', y='Unidades a comprar:', data=res,palette='Blues_d', order=orden)
    plt.xticks(rotation=90)
    #plt.show()
    plt.savefig('ingredientes_a_comprar.jpg', dpi=300, bbox_inches='tight')


    # Creamos una tabla con los ingredientes a comprar
    # table(ax, res)
    # print(table(ax,res))
    # plt.savefig('mytable.png')

    # Gráfica con las pizzas compradas en total
    # Sacamos el orden en el que queremos las columnas
    orden = datos.groupby('pizza_id')['quantity'].sum().sort_values(ascending=False).index.values
    plt.figure(figsize=(15, 10))
    plt.title("Pizzas compradas en total", fontsize=50, fontweight='bold')
    ax = sns.barplot(x='pizza_id', y='quantity', data=datos, palette='Blues_d', estimator=np.sum, order=orden)
    plt.xticks(rotation=90)
    #plt.show()
    plt.savefig('pizzas_compradas_anual.jpg', dpi=300, bbox_inches='tight')

    # Sacamos las 5 pizzas más populares y las 5 menos compradas

    # Creamos una lista con los nombres de las pizzas
    # Creamos otra lista con la cantidad de cada tipo de pizza

    tipos = datos.pizza_id.values.tolist()
    tipos = list(set(tipos))
    cant = []
    for t in tipos:

        cantidad = datos[datos['pizza_id'] == t]['quantity'].sum()
        cant.append(cantidad)

    # Extraemos el índice del valor máximo
    # Con el índice obtenemos el valor máximo y el nombre de la pizza con dicho valor
    # Sacamos ambos valores de la lista y lo repetimos hasta haber obtenido las cinco pizzas más compradas

    cant_max = []
    id_max = []

    for i in range(5):

        indice = cant.index(max(cant))
        cant_max.append(cant.pop(indice))
        id_max.append(tipos.pop(indice))


    # Hacemos lo mismo para obtener las cinco pizzas menos compradas
    cant_min = []
    id_min = []

    for i in range(5):

        indice = cant.index(min(cant))
        cant_min.append(cant.pop(indice))
        id_min.append(tipos.pop(indice))

    # Pintamos ambas gráficas

    # Gráfica de las 5 pizzas más pedidas en todo el año
    plt.figure(figsize=(15,10))
    plt.title("Top 5 pizzas", fontsize=50, fontweight='bold')
    ax = sns.barplot(x=id_max, y=cant_max, palette='Blues_d', estimator=np.sum)
    plt.xticks(rotation=90)
    # plt.show()
    plt.savefig('top_5_pizzas.jpg', dpi=300, bbox_inches='tight')

    # Gráfica de las 5 pizzas menos pedidas en todo el año
    plt.figure(figsize=(15,10))
    plt.title("5 peores pizzas", fontsize=50, fontweight='bold')
    ax = sns.barplot(x=id_min, y=cant_min, palette='Blues_d', estimator=np.sum)
    plt.xticks(rotation=90)
    # plt.show()
    plt.savefig('peores_5_pizzas.jpg',dpi=300, bbox_inches='tight')


if __name__ == '__main__':

    fechas, pedidos, detalles, ingredientes, informe = extract_csv()
    datos = transform_csv(fechas, pedidos, detalles, ingredientes)
    res = transform(datos)
    load(res, datos)
