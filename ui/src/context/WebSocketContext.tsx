import React, { createContext, useState, useContext, useEffect, ReactNode, useCallback } from 'react';

interface WebSocketContextType {
  ws: WebSocket | null;
  connectWebSocket: () => WebSocket;
  disconnectWebSocket: () => void;
  isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType>({
  ws: null,
  connectWebSocket: () => {
    throw new Error('WebSocket context not initialized');
  },
  disconnectWebSocket: () => {},
  isConnected: false,
});

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const connectWebSocket = useCallback(() => {
    // Close existing WebSocket if it exists
    if (ws) {
      ws.close();
    }

    const newWs = new WebSocket("ws://localhost:8000/ws");
    newWs.binaryType = "arraybuffer";

    newWs.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
    };

    newWs.onclose = () => {
      console.log('WebSocket connection closed');
      setIsConnected(false);
    };

    newWs.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnected(false);
    };

    setWs(newWs);
    return newWs;
  }, [ws]);

  const disconnectWebSocket = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
      setIsConnected(false);
    }
  }, [ws]);

  // Automatic reconnection mechanism
  useEffect(() => {
    if (!isConnected) {
      const reconnectTimer = setTimeout(() => {
        connectWebSocket();
      }, 1000);

      return () => clearTimeout(reconnectTimer);
    }
  }, [isConnected, connectWebSocket]);

  // Cleanup WebSocket on component unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  return (
    <WebSocketContext.Provider value={{ ws, connectWebSocket, disconnectWebSocket, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);