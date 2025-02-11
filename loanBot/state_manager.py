import redis
import json

# Load State Configuration from JSON
with open("state_config.json", "r") as f:
    STATE_CONFIG = json.load(f)

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class StateManager:
    """Manages user state transitions based on configuration."""

    def __init__(self, user_id):
        """Load user state from Redis or initialize a new session."""
        self.user_id = user_id
        user_data = redis_client.get(user_id)
        if user_data:
            user_data = json.loads(user_data)
            self.state_name = user_data["state"]
            self.data = user_data["data"]
        else:
            self.state_name = "awaiting_eligibility_info"
            self.data = {}

    def get_state(self):
        """Return state-specific handler."""
        state_module = __import__(f"states.{self.state_name}", fromlist=[""])
        return getattr(state_module, self.state_name.title().replace("_", ""))(self)

    def update_state(self, new_data):
        """Update user data and determine next state."""
        self.data.update(new_data)
        missing_params = self.get_missing_params()
        
        if not missing_params:
            self.state_name = STATE_CONFIG[self.state_name]["next_state"]
        
        self._save_state()
        return missing_params

    def get_missing_params(self):
        """Check for missing mandatory parameters."""
        state_params = STATE_CONFIG.get(self.state_name, {}).get("parameters", {})
        missing = [param for param, rules in state_params.items() if rules["required"] and param not in self.data]
        return missing

    def _save_state(self):
        """Save user state in Redis."""
        redis_client.set(self.user_id, json.dumps({"state": self.state_name, "data": self.data}), ex=86400)
