import requests
import pandas as pd
import logging
import warnings

# Suprimir warnings específicos
warnings.simplefilter(action='ignore', category=UserWarning)  # Ignora UserWarnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)  # Ignora SettingWithCopyWarning


# Configurar el logger
logging.basicConfig(
    filename='log.log',  # Nombre del archivo de log
    level=logging.INFO,  # Nivel de registro (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d',
    encoding='utf-8'  # Formato del mensaje
)

class ReporteSulfoquimica:
    def __init__(self, api_key, bearer_token, empresa='SULFOQUIMICA SA'):
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.empresa = empresa
        self.url = f'https://wlvgmwuhfunnpddcgvzu.supabase.co/rest/v1/tareas?select=*'
        self.headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.bearer_token}'
        }
        self.df = None

    def obtener_datos(self):
        """Realiza la solicitud GET a la API y carga los datos en un DataFrame."""
        response = requests.get(self.url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            self.df = pd.DataFrame(data)
            logging.info("Datos obtenidos correctamente desde la API.")
        else:
            logging.error(f"Error {response.status_code}: No se pudo obtener los datos.")
            raise Exception(f"Error {response.status_code}: No se pudo obtener los datos.")
    
    def limpiar_fechas(self):
        """Convierte la columna 'fecha_inicio' a formato datetime y maneja las fechas fuera de rango."""
        if self.df is not None:
            self.df['fecha_inicio'] = pd.to_datetime(self.df['fecha_inicio'], errors='coerce')
            
            # Verificar fechas inválidas
            invalid_dates = self.df[self.df['fecha_inicio'].isna()]
            if not invalid_dates.empty:
                logging.warning("Fechas inválidas encontradas:")
                logging.warning(f"{invalid_dates}")
        else:
            logging.critical("No se han cargado datos. Ejecuta 'obtener_datos()' primero.")
            raise ValueError("No se han cargado datos. Ejecuta 'obtener_datos()' primero.")

    def filtrar_datos(self):
        """Filtra los datos según las condiciones de empresa, estado y año."""
        if self.df is not None:
            # Filtrar por empresa, estado y año actual
            self.df_filtered = self.df[
                (self.df['empresa'] == self.empresa) & 
                (self.df['estado'] == 'COMPLETADOS') & 
                (self.df['fecha_inicio'].dt.year == pd.to_datetime('today').year)
            ]
            logging.info("Datos filtrados correctamente.")
        else:
            logging.critical("No se han cargado datos. Ejecuta 'obtener_datos()' primero.")
            raise ValueError("No se han cargado datos. Ejecuta 'obtener_datos()' primero.")
    
    def generar_reporte(self):
        """Genera el reporte final agrupado por año, mes, código de proyecto y horas dedicadas."""
        if hasattr(self, 'df_filtered') and self.df_filtered is not None:
            # Crear las columnas 'anio' y 'mes' a partir de 'fecha_inicio'
            self.df_filtered.loc[:, 'anio'] = self.df_filtered['fecha_inicio'].dt.year
            self.df_filtered.loc[:, 'mes'] = self.df_filtered['fecha_inicio'].dt.strftime('%B')  # Mes en texto
            self.df_filtered.loc[:, 'mes_num'] = self.df_filtered['fecha_inicio'].dt.month       # Mes en número

            # Agrupar por año, mes, código de proyecto y sumar las horas dedicadas
            df_grouped = self.df_filtered.groupby(
                ['anio', 'mes', 'mes_num', 'codigo_proyecto'],
                as_index=False
            )['horas_dedicadas'].sum()

            # Ordenar por año y mes para mantener cronología
            df_grouped = df_grouped.sort_values(by=['anio', 'mes_num'])

            # Eliminar 'mes_num' si no es necesario en el resultado final
            df_grouped = df_grouped.drop(columns=['mes_num'])

            # Retornar los datos como lista de diccionarios (JSON-friendly)
            return df_grouped[['anio', 'mes', 'codigo_proyecto', 'horas_dedicadas']].to_dict(orient='records')
        else:
            logging.critical("No se han filtrado los datos. Ejecuta 'filtrar_datos()' primero.")
            raise ValueError("No se han filtrado los datos. Ejecuta 'filtrar_datos()' primero.")

        

    def generar_tabla_por_responsable(self):
        """Genera una tabla agrupada por responsable, año, mes y suma de horas dedicadas."""
        if self.df is not None:
            # Filtrar por empresa, estado y año actual
            df_filtrado = self.df[
                (self.df['empresa'] == self.empresa) & 
                (self.df['estado'] == 'COMPLETADOS') & 
                (self.df['fecha_inicio'].dt.year == pd.to_datetime('today').year)
            ]

            if df_filtrado.empty:
                logging.warning("No hay datos que coincidan con los filtros especificados.")
                return pd.DataFrame(columns=['responsable', 'anio', 'mes', 'total_horas_dedicadas'])

            # Crear columnas de año y mes
            df_filtrado = df_filtrado.copy()
            df_filtrado['anio'] = df_filtrado['fecha_inicio'].dt.year
            df_filtrado['mes'] = df_filtrado['fecha_inicio'].dt.strftime('%B')  # Mes en texto
            df_filtrado['mes_num'] = df_filtrado['fecha_inicio'].dt.month      # Mes en número (para ordenar)

            # Agrupar por responsable, año y mes
            df_responsable = df_filtrado.groupby(
                ['responsable', 'anio', 'mes', 'mes_num'],
                as_index=False
            )['horas_dedicadas'].sum()

            # Renombrar columna
            df_responsable = df_responsable.rename(columns={'horas_dedicadas': 'total_horas_dedicadas'})

            # Ordenar por año y número de mes
            df_responsable = df_responsable.sort_values(by=['anio', 'mes_num', 'responsable'])

            # Eliminar mes_num si no lo necesitas en la visualización final
            df_responsable = df_responsable.drop(columns=['mes_num'])

            logging.info("Tabla por responsable, año y mes generada correctamente.")
            return df_responsable

        else:
            logging.critical("No se han cargado datos. Ejecuta 'obtener_datos()' primero.")
            raise ValueError("No se han cargado datos. Ejecuta 'obtener_datos()' primero.")


