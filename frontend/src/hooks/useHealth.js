import { useEffect, useState } from "react";
import { api } from "../api/client";

export function useHealth(intervalMs = 15000) {
  const [status, setStatus] = useState("checking"); // checking | online | offline

  useEffect(() => {
    let active = true;
    const check = async () => {
      try {
        await api.health();
        if (active) setStatus("online");
      } catch {
        if (active) setStatus("offline");
      }
    };
    check();
    const timer = setInterval(check, intervalMs);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [intervalMs]);

  return status;
}