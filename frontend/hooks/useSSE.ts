"use client";

import { useEffect, useState, useRef } from "react";

export interface SSEEvent {
  event: string;
  data: any;
  timestamp: string;
}

export function useSSE(onEvent?: (event: SSEEvent) => void) {
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const onEventRef = useRef(onEvent);

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    const sseUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api"}/events/sse`;
    const eventSource = new EventSource(sseUrl);

    eventSource.onopen = () => {
      setConnected(true);
    };

    eventSource.onerror = () => {
      setConnected(false);
    };

    const handleEvent = (event: MessageEvent, type: string) => {
      try {
        const data = JSON.parse(event.data);
        const sseEvt = { event: type, data, timestamp: new Date().toISOString() };
        setLastEvent(sseEvt);
        if (onEventRef.current) onEventRef.current(sseEvt);
      } catch (e) {
        // ignore parse error
      }
    };

    eventSource.addEventListener("new_article", (e) => handleEvent(e as MessageEvent, "new_article"));
    eventSource.addEventListener("check_completed", (e) => handleEvent(e as MessageEvent, "check_completed"));
    eventSource.addEventListener("connected", (e) => handleEvent(e as MessageEvent, "connected"));

    return () => {
      eventSource.close();
    };
  }, []); // Stable single-mount subscription

  return { connected, lastEvent };
}
