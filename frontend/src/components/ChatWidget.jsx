import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Bot, User, Minimize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { chatWithAI } from '../services/api';
import { useOptimization } from '../context/OptimizationContext';
import '../styles/ChatWidget.css';

export default function ChatWidget() {
  const { optimizationData } = useOptimization();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I\'m your OptiResume AI assistant. How can I help you with your career today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // Pass the current optimization context to the AI
      const response = await chatWithAI(
        input, 
        messages,
        optimizationData?.original_resume, // If we had it stored, but optimizationData usually has optimized_resume
        null, // JD context if available
        optimizationData
      );
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I\'m having trouble connecting right now. Please try again later.' 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-widget-container">
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="chat-bubble"
            onClick={() => setIsOpen(true)}
          >
            <MessageSquare size={28} />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0, transformOrigin: 'bottom right' }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="chat-window open"
          >
            <div className="chat-header">
              <div className="chat-header-title">
                <Bot size={20} />
                OptiResume AI <span>Expert</span>
              </div>
              <button className="chat-close" onClick={() => setIsOpen(false)}>
                <Minimize2 size={18} />
              </button>
            </div>

            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={index} className={`chat-message message-${msg.role}`}>
                  {msg.content}
                </div>
              ))}
              {isTyping && (
                <div className="typing-indicator">AI is thinking...</div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-area" onSubmit={handleSend}>
              <input
                type="text"
                className="chat-input"
                placeholder="Ask me anything..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isTyping}
              />
              <button type="submit" className="chat-send" disabled={!input.trim() || isTyping}>
                <Send size={18} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
