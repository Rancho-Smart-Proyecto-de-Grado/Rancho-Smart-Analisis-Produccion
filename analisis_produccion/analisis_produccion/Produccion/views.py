import datetime
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Produccion, RegistroProduccion


import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from django.http import JsonResponse

registros_produccion = []

@api_view(['POST'])
def registrar_produccion(request):
    if request.method == 'POST':
        # Obtenemos los datos del request
        data = request.data

        # Verificación básica (puedes agregar más validaciones si lo deseas)
        if 'lote_id' not in data or 'animal_id' not in data or 'fecha' not in data or 'cantidad' not in data:
            return Response({"error": "Faltan datos en la solicitud."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear un nuevo registro
        nuevo_registro = {
            'lote_id': data['lote_id'],
            'animal_id': data['animal_id'],
            'fecha': data['fecha'],
            'cantidad': data['cantidad']
        }

        # Agregar el registro a la lista
        registros_produccion.append(nuevo_registro)

        return Response(nuevo_registro, status=status.HTTP_201_CREATED)

def filtrar_por_tiempo(queryset, tiempo):
    today = datetime.now().date()
    if tiempo == '7dias':
        start_date = today - timedelta(days=7)
    elif tiempo == '1mes':
        start_date = today - timedelta(days=30)
    elif tiempo == '1año':
        start_date = today - timedelta(days=365)
    elif tiempo == '5años':
        start_date = today - timedelta(days=5 * 365)
    return queryset.filter(fecha__gte=start_date)

def info_lote(request, tiempo):
    queryset = Produccion.objects.all()
    queryset = filtrar_por_tiempo(queryset, tiempo)
    df = pd.DataFrame(list(queryset.values()))

    # Agrupación para gráfica de línea
    df_agrupado = df.groupby('fecha')['cantidad'].sum().reset_index()
    fig_line = px.line(df_agrupado, x='fecha', y='cantidad', title=f'Producción en el tiempo - {tiempo}')

    # Gráfica de pastel para producción por vaca
    df_vaca = df.groupby('vaca_id')['cantidad'].sum().reset_index()
    fig_pie_vaca = px.pie(df_vaca, names='vaca_id', values='cantidad', title='Producción total por vaca')

    # Gráfica de pastel para producción por lote
    df_lote = df.groupby('lote_id')['cantidad'].sum().reset_index()
    fig_pie_lote = px.pie(df_lote, names='lote_id', values='cantidad', title='Producción total por lote')

    # Convertir gráficos a JSON para enviar al frontend
    response = {
        "line_graph": fig_line.to_json(),
        "pie_chart_vaca": fig_pie_vaca.to_json(),
        "pie_chart_lote": fig_pie_lote.to_json(),
    }
    return JsonResponse(response)


def produccion_por_lote(request, lote_id, tiempo):
    queryset = Produccion.objects.filter(lote_id=lote_id)
    queryset = filtrar_por_tiempo(queryset, tiempo)
    df = pd.DataFrame(list(queryset.values()))

    # Agrupar por fecha
    df_agrupado = df.groupby('fecha')['cantidad'].sum().reset_index()
    fig_line = px.line(df_agrupado, x='fecha', y='cantidad', title=f'Producción en el tiempo - Lote {lote_id} ({tiempo})')

    # Agrupación para gráfico de pastel por vaca
    df_vaca = df.groupby('vaca_id')['cantidad'].sum().reset_index()
    fig_pie = px.pie(df_vaca, names='vaca_id', values='cantidad', title=f'Producción total por vaca en lote {lote_id}')

    response = {
        "line_graph": fig_line.to_json(),
        "pie_chart": fig_pie.to_json(),
    }
    return JsonResponse(response)

def info_vaca(request, vaca_id, tiempo):
    queryset = Produccion.objects.filter(vaca_id=vaca_id)
    queryset = filtrar_por_tiempo(queryset, tiempo)
    df = pd.DataFrame(list(queryset.values()))

    # Agrupar por fecha
    df_agrupado = df.groupby('fecha')['cantidad'].sum().reset_index()
    fig_line = px.line(df_agrupado, x='fecha', y='cantidad', title=f'Producción en el tiempo - Vaca {vaca_id} ({tiempo})')

    # Gráfico de pastel por mes
    df['mes'] = pd.to_datetime(df['fecha']).dt.to_period('M').astype(str)
    df_mes = df.groupby('mes')['cantidad'].sum().reset_index()
    fig_pie = px.pie(df_mes, names='mes', values='cantidad', title=f'Producción por mes - Vaca {vaca_id}')

    response = {
        "line_graph": fig_line.to_json(),
        "pie_chart": fig_pie.to_json(),
    }
    return JsonResponse(response)

def comparar_lotes(request, lote_id1, lote_id2, tiempo='1mes'):
    queryset1 = Produccion.objects.filter(lote_id=lote_id1)
    queryset2 = Produccion.objects.filter(lote_id=lote_id2)
    queryset1 = filtrar_por_tiempo(queryset1, tiempo)
    queryset2 = filtrar_por_tiempo(queryset2, tiempo)
    df1 = pd.DataFrame(list(queryset1.values()))
    df2 = pd.DataFrame(list(queryset2.values()))

    # Agregar columnas de lote y combinar DataFrames
    df1['lote'] = f'Lote {lote_id1}'
    df2['lote'] = f'Lote {lote_id2}'
    df_combinado = pd.concat([df1, df2])

    # Gráfica de comparación de producción en el tiempo
    fig_line = px.line(df_combinado, x='fecha', y='cantidad', color='lote', title=f'Comparación de Producción en el Tiempo - Lotes {lote_id1} y {lote_id2}')

    # Gráfico de pastel para producción total por lote
    df_pie = pd.DataFrame({
        'lote': [f'Lote {lote_id1}', f'Lote {lote_id2}'],
        'cantidad': [df1['cantidad'].sum(), df2['cantidad'].sum()]
    })
    fig_pie = px.pie(df_pie, names='lote', values='cantidad', title='Comparación de Producción Total por Lote')

    response = {
        "line_graph": fig_line.to_json(),
        "pie_chart": fig_pie.to_json(),
    }
    return JsonResponse(response)
