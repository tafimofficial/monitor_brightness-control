import screen_brightness_control as sbc

class BrightnessController:
    def __init__(self):
        self.monitors = []

    def get_monitors(self):
        """
        Refreshes and returns the list of connected monitors.
        Returns a list of dictionaries with 'name', 'id', 'brightness'.
        """
        try:
            # Get all monitors
            # sbc.list_monitors() returns names, we need to correlate with brightness
            # A simpler way is to use get_brightness() with display kwarg if needed,
            # but sbc.get_brightness() returns a list of values for all monitors by default.
            
            # Let's try to bundle everything.
            # sbc.list_monitors() returns list of monitor names (strings)
            monitor_names = sbc.list_monitors()
            
            # Clean up monitor names that might contain "None"
            # e.g. "None Generic Monitor" -> "Generic Monitor"
            monitor_names = [name.replace("None ", "") if name.startswith("None ") else name for name in monitor_names]
            
            # sbc.get_brightness() returns a list of integers (current brightness)
            # If one monitor fails, it might throw or return None for that index depending on version,
            # but usually it returns a list equal to number of monitors.
            current_brightness_values = sbc.get_brightness()
            
            # Handle case where sbc returns a single int if only one monitor 
            if isinstance(current_brightness_values, int):
                current_brightness_values = [current_brightness_values]
                
            self.monitors = []
            if monitor_names and current_brightness_values:
                for i, name in enumerate(monitor_names):
                    # Safety check for index out of bounds if something is weird
                    if i < len(current_brightness_values):
                        b_val = current_brightness_values[i]
                    else:
                        b_val = 50 # Default fallback
                        
                    self.monitors.append({
                        'id': i,
                        'name': name,
                        'brightness': b_val
                    })
            
            return self.monitors
        except Exception as e:
            print(f"Error fetching monitors: {e}")
            return []

    def set_brightness(self, display_id, value):
        """
        Sets brightness for a specific monitor by index.
        """
        try:
            sbc.set_brightness(value, display=display_id)
        except Exception as e:
            print(f"Error setting brightness for display {display_id}: {e}")

    def get_brightness(self, display_id):
        try:
            values = sbc.get_brightness(display=display_id)
            if isinstance(values, list):
                return values[0]
            return values
        except Exception as e:
            print(f"Error getting brightness for display {display_id}: {e}")
            return 50
