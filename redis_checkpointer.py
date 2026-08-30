import os
import json
import logging
from typing import Dict, Any, Optional
import redis

# Environment Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

logger = logging.getLogger(__name__)


class RedisStateManager:
    #Step 6 State & Checkpoint Layer:
    #Persists agent thread state, handles human-in-the-loop state retrieval, 
    #and appends execution logs to Redis.
    

    def __init__(
        self, 
        host: str = REDIS_HOST, 
        port: int = REDIS_PORT, 
        db: int = REDIS_DB, 
        password: Optional[str] = REDIS_PASSWORD
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )

    #State Checkpoint Persistence
    def save_checkpoint(self, audit_id: str, state: Dict[str, Any], ttl_seconds: int = 86400) -> bool:
        """
        Saves the current pipeline state dictionary as a JSON blob.
        TTL defaults to 24 hours (86400 seconds).
        """
        try:
            key = f"audit_session:{audit_id}"
            serialized_state = json.dumps(state, default=str)
            self.client.set(key, serialized_state, ex=ttl_seconds)
            
            # Log event to session stream
            self.log_agent_action(audit_id, "CHECKPOINT_SAVED", {
                "current_step": state.get("target_loop_node", "unknown"),
                "security_retry": state.get("security_retry_count", 0),
                "optimizer_retry": state.get("optimizer_retry_count", 0)
            })
            return True
        except Exception as e:
            logger.error(f"Failed to save Redis checkpoint for audit_id {audit_id}: {str(e)}")
            return False

    def get_checkpoint(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the saved pipeline state from Redis.
        Used by human_review_pr.py when processing review actions.
        """
        try:
            key = f"audit_session:{audit_id}"
            raw_data = self.client.get(key)
            if raw_data:
                return json.loads(raw_data)
            return None
        except Exception as e:
            logger.error(f"Failed to fetch Redis checkpoint for audit_id {audit_id}: {str(e)}")
            return None

    # Audit Trail & Log Streaming
    def log_agent_action(self, audit_id: str, agent_name: str, payload: Dict[str, Any]) -> None:
        """
        Appends an execution log entry to a Redis List for UI monitoring.
        """
        try:
            log_key = f"audit_logs:{audit_id}"
            entry = {
                "agent": agent_name,
                "payload": payload
            }
            self.client.rpush(log_key, json.dumps(entry, default=str))
            self.client.expire(log_key, 604800)
        except Exception as e:
            logger.warning(f"Could not append action log to Redis: {str(e)}")

    def get_audit_logs(self, audit_id: str) -> list:
        #Retrieves complete chronological audit log history for an audit session.
        try:
            log_key = f"audit_logs:{audit_id}"
            logs = self.client.lrange(log_key, 0, -1)
            return [json.loads(log) for log in logs]
        except Exception as e:
            logger.error(f"Failed to fetch audit logs: {str(e)}")
            return []

    def clear_session(self, audit_id: str) -> bool:
        #Removes session keys upon deployment completion.
        try:
            self.client.delete(f"audit_session:{audit_id}", f"audit_logs:{audit_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear session {audit_id}: {str(e)}")
            return False


# Singleton instance helper
_state_manager_instance = None

def get_redis_state_manager() -> RedisStateManager:
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = RedisStateManager()
    return _state_manager_instance