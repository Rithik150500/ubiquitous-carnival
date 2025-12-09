import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import type { Todo } from '../../types';

export const TodoPanel: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTodos();
    const interval = setInterval(loadTodos, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const loadTodos = async () => {
    try {
      const status = await api.getAgentStatus();
      setTodos(status.todos || []);
      setLoading(false);
    } catch (error) {
      console.error('Error loading todos:', error);
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'in_progress':
        return '⟳';
      default:
        return '○';
    }
  };

  return (
    <div className="todo-section">
      <div className="panel-header">Analysis Plan & Progress</div>
      <div className="panel-content">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            Loading...
          </div>
        ) : todos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-text">No analysis in progress</div>
          </div>
        ) : (
          todos.map((todo, index) => (
            <div key={index} className={`todo-item ${todo.status}`}>
              <span className="todo-status-icon">{getStatusIcon(todo.status)}</span>
              <span className="todo-text">{todo.task}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
