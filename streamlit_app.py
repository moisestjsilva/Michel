import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Inicialização de dados (simulando um banco de dados)
if 'groups' not in st.session_state:
    st.session_state.groups = pd.DataFrame({
        'id': [1, 2],
        'name': ['Grupo 1', 'Grupo 2']
    })

if 'students' not in st.session_state:
    st.session_state.students = pd.DataFrame({
        'id': [1, 2],
        'name': ['João', 'Maria'],
        'group_id': [1, 2]
    })

if 'attendance' not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=['id', 'student_id', 'date', 'present'])

# Funções auxiliares
def add_group(name):
    new_id = st.session_state.groups['id'].max() + 1 if not st.session_state.groups.empty else 1
    st.session_state.groups = pd.concat([
        st.session_state.groups,
        pd.DataFrame({'id': [new_id], 'name': [name]})
    ], ignore_index=True)

def add_student(name, group_id):
    new_id = st.session_state.students['id'].max() + 1 if not st.session_state.students.empty else 1
    st.session_state.students = pd.concat([
        st.session_state.students,
        pd.DataFrame({'id': [new_id], 'name': [name], 'group_id': [group_id]})
    ], ignore_index=True)

def mark_attendance(student_id, date, present):
    new_id = st.session_state.attendance['id'].max() + 1 if not st.session_state.attendance.empty else 1
    st.session_state.attendance = pd.concat([
        st.session_state.attendance,
        pd.DataFrame({'id': [new_id], 'student_id': [student_id], 'date': [date], 'present': [present]})
    ], ignore_index=True)

def calculate_attendance_rate(group_id):
    students_in_group = st.session_state.students[st.session_state.students['group_id'] == group_id]
    attendance_rates = []
    
    for _, student in students_in_group.iterrows():
        student_attendance = st.session_state.attendance[st.session_state.attendance['student_id'] == student['id']]
        total_classes = len(student_attendance)
        if total_classes > 0:
            present_classes = student_attendance['present'].sum()
            rate = (present_classes / total_classes) * 100
        else:
            rate = 0
        attendance_rates.append({'name': student['name'], 'rate': rate})
    
    return pd.DataFrame(attendance_rates)

# Interface da aplicação
st.title('Sistema de Controle de Presença')

# Sidebar para navegação
page = st.sidebar.radio('Navegação', ['Dashboard', 'Cadastro de Grupos', 'Cadastro de Alunos'])

if page == 'Dashboard':
    st.header('Dashboard de Presença')
    
    # Seleção de grupo
    group_id = st.selectbox('Selecione o grupo', 
                            options=st.session_state.groups['id'], 
                            format_func=lambda x: st.session_state.groups[st.session_state.groups['id'] == x]['name'].iloc[0])
    
    # Lista de presença
    st.subheader('Lista de Presença')
    students_in_group = st.session_state.students[st.session_state.students['group_id'] == group_id]
    for _, student in students_in_group.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(student['name'])
        with col2:
            if st.button('Presente', key=f'present_{student["id"]}'):
                mark_attendance(student['id'], datetime.now().date(), True)
                st.success(f'Presença marcada para {student["name"]}')
    
    # Gráfico de taxa de assiduidade
    st.subheader('Taxa de Assiduidade')
    attendance_data = calculate_attendance_rate(group_id)
    if not attendance_data.empty:
        fig = px.bar(attendance_data, x='name', y='rate', title='Taxa de Assiduidade por Aluno')
        st.plotly_chart(fig)
    else:
        st.write('Não há dados de presença para este grupo ainda.')

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
    st.dataframe(st.session_state.groups)

elif page == 'Cadastro de Alunos':
    st.header('Cadastro de Alunos')
    
    new_student_name = st.text_input('Nome do novo aluno')
    new_student_group = st.selectbox('Grupo do aluno', 
                                     options=st.session_state.groups['id'],
                                     format_func=lambda x: st.session_state.groups[st.session_state.groups['id'] == x]['name'].iloc[0])
    
    if st.button('Cadastrar Aluno'):
        if new_student_name and new_student_group:
            add_student(new_student_name, new_student_group)
            st.success(f'Aluno "{new_student_name}" cadastrado com sucesso!')
        else:
            st.error('Por favor, preencha todos os campos.')
    
    st.subheader('Alunos Cadastrados')
    st.dataframe(st.session_state.students.merge(st.session_state.groups, left_on='group_id', right_on='id', suffixes=('_student', '_group')))