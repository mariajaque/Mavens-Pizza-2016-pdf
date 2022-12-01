# Mavens-Pizza-2016-pdf
En este repositorio se recoge el código necesario para realizar una predicción de los ingredientes que deberá comprar 'Mavens Pizza'. Con eso se realiza un reporte ejecutivo en pdf con diversas gráficas.

Este repositorio contiene los siguientes ficheros necesarios para la ejecución:
- **"requirements.txt"**: contiene todas las librerías necesarias para la ejecución del programa
- **"orders.csv"**: contiene los datos relacionados a las fechas de cada pedido
- **"order_details.csv"**: contiene los datos relacionados a la cantidad y tipo de pizza de cada pedido concreto
- **"pizzas.csv"**: contiene información relacionada con los distintos tipos de pizza de la pizzería como su tamaño y su precio
- **"pizza_types.csv"**: incluye los datos relacionados con la categoría de cada tipo de pizza y los ingredientes que contiene
- **"logo_mavens.jpg"**: imágen con el logo de la pizzería que será necesaria a la hora de realizar el pdf.
- **"pizzas4.py"**: contiene el código que se debe de ejecutar para obtener la predicción de los ingredientes que deberá de comprar la pizzaría. El programa consta de dos ETL, una para la extracción y el tratado de los datos y otra para la elaboración de la predicción. En lo relacionado al tratado de los datos, el programa los manipula hasta obtener un único dataframe que contenga la información de cada pedido, la semana y día de la semana en el que se realizó y los ingredientes requeridos para la preparación de ese pedido en concreto. Para la realización de la predicción lo que hace el programa es establecer la predicción como la media de las modas de cada ingrediente por semana, es decir, calcula el total de cada ingrediente necesitado cada semana del año y se queda con la moda de cada ingrediente. En caso de empate hace la media de las modas. El programa también realiza un análisis de la calidad de los datos contenidos en los ".csv" de Mavens Pizza. Para dicho análisis tiene en cuenta valores como el número de nulls y de nans de cada fichero. Una vez realizado el análisis de los datos se procede a realizar una limpieza exhaustiva en las fechas, poniéndolas todas en el mismo formato, y en los pedidos, transformando valores de pedidos negativos a positivos y modificando los nombres de las pizzas pedidas para que todas estén escritas como en el csv de pizza_types (para ello se cambian espacios por "_", "0" por "o" y otros muchos caracteres más). La predicción se alamacena junto con un reporte ejecutivo en el fichero "reporte_ejecutivo.pdf".

Y tras su ejecución el programa genera los siguientes ficheros de salida:
- **"informe_calidad_datos.txt"**: contiene el análisis de la calidad de los datos de la pizzería
- **"evolucion_temporal_ingredientes.jpg"**: contiene una gráfica por cada ingrediente y que mide el número de unidades que se han requerido de ese ingrediente por semana durante el 2016.
- **"evolucion_temporal_pizzas.jpg"**: contiene una gráfica por cada tipo de pizza. Cada gráfica refleja el número de veces que se ha ido pidiendo cada pizza por semana durante el 2016.
- **"ingredientes_a_comprar.jpg"**: contiene un bar plot con las cantidades de cada ingrediente que se deben de comprar para una semana cualquiera, es decir, las cantidades de la predicción.
- **"peores_5_pizzas.jpg"**: contiene un gráfico de barras con las veces que se han pedido cada una de las 5 pizzas menos pedidas en un año.
- **"pizzas_compradas_anual.jpg"**: contiene un bar plot con el total de veces que se pidió cada tipo de pizza en 2016.
- **"top_5_pizzas.jpg"**: contiene un bar plot con el número de veces que se ha pedido cada una de las 5 pizzas más vendidas del 2016.
- **"reporte_ejecutivo.pdf"**: almacena las 6 gráficas anteriores a lo largo de un pdf para así almacenar la información de la pizzería en un único documento.

### Ejecución del programa:

Primero se deberá hacer un pip install - r requirements.txt para que se descarguen todas las librerías necesarias para el programa. Posteriormente ya se podrá ejecutar el fichero "pizzas4.py" que tardará aproximadamente un minuto en devolver la predicción.