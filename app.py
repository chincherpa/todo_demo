import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title='todos',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Initialize database
def init_db():
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Add new todo
def add_todo(task, status):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('INSERT INTO todos (task, status) VALUES (?, ?)', (task, status))
    conn.commit()
    conn.close()

# Get all todos
def get_todos():
    conn = sqlite3.connect('demo.db')
    df = pd.read_sql_query('SELECT * FROM todos ORDER BY created_at DESC', conn)
    conn.close()
    return df

# Delete todo
def delete_todo(todo_id):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()

# Update todo status
def update_status(todo_id, new_status):
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('UPDATE todos SET status = ? WHERE id = ?', (new_status, todo_id))
    conn.commit()
    conn.close()

st.title('📝 Todo List App with SQLite')
st.markdown('---')

# Initialize database
init_db()

# Sidebar for adding new todos
with st.sidebar:
    st.header('Add New Todo')
    new_task = st.text_input('Task Description')
    status = st.selectbox('Status', ['Pending', 'In Progress', 'Completed'])
    
    if st.button('Add Todo', type='primary'):
        if new_task:
            add_todo(new_task, status)
            st.success('Todo added successfully!')
            st.rerun()
        else:
            st.error('Please enter a task description')

with st.container(border=True):
  # Main content area
  st.header('Your Todos')
  
  # Get and display todos
  todos_df = get_todos()

  if todos_df.empty:
      st.info('No todos yet. Add one using the sidebar!')
  else:
      # Display statistics
      col1, col2, col3 = st.columns(3)
      with col1:
          st.metric('Total Tasks', len(todos_df))
      with col2:
          st.metric('Completed', len(todos_df[todos_df['status'] == 'Completed']))
      with col3:
          st.metric('Pending', len(todos_df[todos_df['status'] == 'Pending']))
      
      st.markdown('---')
      
      # Display each todo
      for _, row in todos_df.iterrows():
          with st.container():
              col1, col2, col3, col4 = st.columns([3, 1.5, 1, 1])
              
              with col1:
                  st.write(f"**{row['task']}**")
              
              with col2:
                  # Status badge with color
                  if row['status'] == 'Completed':
                      st.success(row['status'])
                  elif row['status'] == 'In Progress':
                      st.info(row['status'])
                  else:
                      st.warning(row['status'])
              
              with col3:
                  # Update status
                  new_status = st.selectbox(
                      'Update',
                      ['Pending', 'In Progress', 'Completed'],
                      key=f"status_{row['id']}",
                      label_visibility='collapsed'
                  )
                  if new_status != row['status']:
                      update_status(row['id'], new_status)
                      st.rerun()
              
              with col4:
                  # Delete button
                  if st.button('🗑️', key=f"delete_{row['id']}"):
                      delete_todo(row['id'])
                      st.rerun()
              
              st.caption(f"Created: {row['created_at']}")
              st.markdown('---')
