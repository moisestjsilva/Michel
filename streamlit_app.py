import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Funções para carregar e salvar dados
def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame()

def save_data(data, filename):
    data.to_csv(filename, index=False)

# Carregar dados
groups = load_data('groups.csv')
students = load_data('students.csv')
attendance = load_data('attendance.csv')

# Funções auxiliares
def add_group(name):
    global groups
    new_id = groups['id'].max() + 1 if not groups.empty else 1
    new_group = pd.DataFrame({'id': [new_id], 'name': [name]})
    groups = pd.concat([groups, new_group], ignore_index=True)
    save_data(groups, 'groups.csv')

def add_student(name, group_id):
    global students
    new_id = students['id'].max() + 1 if not students.empty else 1
    new_student = pd.DataFrame({'id': [new_id], 'name': [name], 'group_id': [group_id]})
    students = pd.concat([students, new_student], ignore_index=True)
    save_data(students, 'students.csv')

def mark_attendance(student_id, date, present):
    global attendance
    new_id = attendance['id'].max() + 1 if not attendance.empty else 1
    new_attendance = pd.DataFrame({'id': [new_id], 'student_id': [student_id], 'date': [date], 'present': [present]})
    attendance = pd.concat([attendance, new_attendance], ignore_index=True)
    save_data(attendance, 'attendance.csv')

def calculate_attendance_rate(group_id):
    students_in_group = students[students['group_id'] == group_id]
    attendance_rates = []
    
    for _, student in students_in_group.iterrows():
        student_attendance = attendance[attendance['student_id'] == student['id']]
        total_classes = len(student_attendance)
        if total_classes > 0:
            present_classes = student_attendance['present'].sum()
            rate = (present_classes / total_classes) * 100
        else:
            rate = 0
        attendance_rates.append({'name': student['name'], 'rate': rate})
    
    return pd.DataFrame(attendance_rates)

def calculate_monthly_attendance_rate(group_id):
    students_in_group = students[students['group_id'] == group_id]
    group_attendance = attendance[attendance['student_id'].isin(students_in_group['id'])]
    
    if group_attendance.empty:
        return pd.DataFrame(columns=['month', 'rate'])
    
    group_attendance['date'] = pd.to_datetime(group_attendance['date'])
    monthly_attendance = group_attendance.groupby(group_attendance['date'].dt.to_period("M")).agg({
        'present': 'mean',
        'id': 'count'
    }).reset_index()
    
    monthly_attendance['rate'] = monthly_attendance['present'] * 100
    monthly_attendance['month'] = monthly_attendance['date'].dt.strftime('%Y-%m')
    
    return monthly_attendance[['month', 'rate']]

# Interface da aplicação
st.title('Sistema de Controle de Presença')

# Sidebar para navegação
page = st.sidebar.radio('Navegação', ['Dashboard', 'Cadastro de Grupos', 'Cadastro de Alunos'])

if page == 'Dashboard':
    st.header('Dashboard de Presença')
    
    # Seleção de grupo
    group_id = st.selectbox('Selecione o grupo', 
                            options=groups['id'], 
                            format_func=lambda x: groups[groups['id'] == x]['name'].iloc[0])
    
    # Data da aula
    class_date = st.date_input('Data da aula', datetime.now())
    
    # Lista de presença
    st.subheader('Lista de Presença')
    students_in_group = students[students['group_id'] == group_id]
    for _, student in students_in_group.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(student['name'])
        with col2:
            if st.button('Presente', key=f'present_{student["id"]}'):
                mark_attendance(student['id'], class_date, True)
                st.success(f'Presença marcada para {student["name"]}')
    
    # Gráfico de taxa de assiduidade
    st.subheader('Taxa de Assiduidade')
    attendance_data = calculate_attendance_rate(group_id)
    if not attendance_data.empty:
        fig, ax = plt.subplots()
        ax.bar(attendance_data['name'], attendance_data['rate'])
        ax.set_ylabel('Taxa de Assiduidade (%)')
        ax.set_title('Taxa de Assiduidade por Aluno')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    else:
        st.write('Não há dados de presença para este grupo ainda.')
    
    # Gráfico de evolução da assiduidade por mês
    st.subheader('Evolução da Assiduidade por Mês')
    monthly_attendance_data = calculate_monthly_attendance_rate(group_id)
    if not monthly_attendance_data.empty:
        fig, ax = plt.subplots()
        ax.plot(monthly_attendance_data['month'], monthly_attendance_data['rate'], marker='o')
        ax.set_xlabel('Mês')
        ax.set_ylabel('Taxa de Assiduidade (%)')
        ax.set_title('Evolução da Assiduidade do Grupo por Mês')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    else:
        st.write('Não há dados suficientes para mostrar a evolução da assiduidade.')

elif page == 'Cadastro de Grupos':
    st.header('Cadastro de Grupos')
    
    new_group_name = st.text_input('Nome do novo grupo')
    if st.button('Cadastrar Grupo'):
        if new_group_name:
            add_group(new_group_name)
            st.success(f'Grupo "{new_group_name}" cadastrado com sucesso!')
        else:
            st.error('Por favor, insira um nome para o grupo.')
    
    st.subheader('Grupos Cadastrados')
    st.dataframe(groups)

elif page == 'Cadastro de Alunos':
    st.header('Cadastro de Alunos')
    
    new_student_name = st.text_input('Nome do novo aluno')
    new_student_group = st.selectbox('Grupo do aluno', 
                                     options=groups['id'],
                                     format_func=lambda x: groups[groups['id'] == x]['name'].iloc[0])
    
    if st.button('Cadastrar Aluno'):
        if new_student_name and new_student_group:
            add_student(new_student_name, new_student_group)
            st.success(f'Aluno "{new_student_name}" cadastrado com sucesso!')
        else:
            st.error('Por favor, preencha todos os campos.')
    
    st.subheader('Alunos Cadastrados')
    st.dataframe(students.merge(groups, left_on='group_id', right_on='id', suffixes=('_student', '_group')))