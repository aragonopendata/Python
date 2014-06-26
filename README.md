
##Carga de Contenidos en CKAN

Este repositorio contiene el código en lenguaje Python que permite la carga masiva de contenidos desde un RDF en el CMS de gestión de datos abiertos CKAN.


###Uso del código

Este conjunto de cuatro ficheros, permite conectarse a una URL desde la que se obtienen RDFs. Además, estos RDFs son leídos y subidos al servidor, ya sea como nuevo dataset o actualización de uno ya existente debido a algún cambio en sus datos.

Para obtener la información, se configura el archivo config.py donde debe especificarse:

URL_FILE: Localización del archivo url.properties
DOWNLOAD_PATH: Ruta a la carpeta donde se guardarán los RDFs descargados
API_KEY: API-KEY para la conexión al servidor
BASE_LOCATION= Localización base del servidor

En el fichero url.properties tenemos la URL a la que conectarnos para obtener los RDFs
El script es el fichero: rdf_downloader.py, el cual hace uso del archivo rdf_parser para parsear los RDfs que descarga y lee la configuración del archivo config.py
Para poder ejecutar este script periódicamente, se ha de poner en el CRON del sistema la llamada al script rdf_downloader con la frecuencia que deseemos

###Licencia

El Gobierno de Aragón a través de Aragón Open Data pone a disposición de usuarios, desarrolladores y comunidad en general este software bajo la Licencia Pública de la Unión Europea “European Union Public Licence – EUPL”. Esta licencia, desarrollada en el seno de la Unión Europea, nació con la intención de ser la licencia bajo la cuál se liberasen los programas y aplicaciones desarrolladas por la Administración Pública y con la característica específica de ser compatible con otras licencias denominadas libres, como la GNU General Public License (GNU/GPL). Estas características dotan, a las aplicaciones así liberadas, de mayor seguridad jurídica y fomentan la interoperabilidad de los servicios de la Administración Electrónica.

Que el código de esta aplicación esté publicado bajo la licencia abierta [EUPL 1.1] (European Union Public License 1.1), significa que puedes reutilizarlo, modificarlo y adaptarlo a tus necesidades de forma totalmente libre. Si utilizas el código, a modo de reconocimiento puedes hacernoslo saber o mencionarnos, te lo agradeceremos!
